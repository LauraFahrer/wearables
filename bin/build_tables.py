"""Build trial- and window-level tables (features + labels) from the exported dataset.

Usage: python build_tables.py <export_dir> <out_dir> [--window-size 10]
"""
import argparse
import numpy as np
import pandas as pd

FIX_MS = 500     # fixation period directly before the first memory array
PRE_MS = 1500    # whole gap between previous trial and first memory array (~1533 ms)
BLINK_MIN_MS = 50


def zero_runs(mask):
    """Lengths of consecutive True runs in a boolean array."""
    d = np.diff(np.r_[0, mask.astype(int), 0])
    return np.where(d == -1)[0] - np.where(d == 1)[0]


def session_features(raw, session):
    raw = raw[raw.time.notna()].reset_index(drop=True)
    pupil = raw.diameter.where(raw.diameter > 0)              # 0 = blink / tracking loss
    raw["pupil_z"] = (pupil - pupil.mean()) / pupil.std()     # normalise within session

    mem = raw.index[raw.event.isin([1, 2])]
    onsets = mem[::3]                                         # first of three memory arrays
    assert len(onsets) == 160, f"session {session}: {len(onsets)} trial onsets"

    rows = []
    for k, i in enumerate(onsets):
        fix = raw.iloc[max(i - FIX_MS, 0):i]
        pre = raw.iloc[max(i - PRE_MS, 0):i]
        valid = fix.pupil_z.notna()
        y = fix.pupil_z[valid].values
        runs = zero_runs(pre.pupil_z.isna().values)
        rows.append(dict(
            session=session,
            Trial=k + 1,
            onset_code=int(raw.event[i]),
            pupil_mean=y.mean() if len(y) else np.nan,
            pupil_slope=np.polyfit(np.arange(len(y)), y, 1)[0] * 1000 if len(y) > 50 else np.nan,  # z per second
            missing_share=1 - valid.mean(),
            blink_count=int((runs >= BLINK_MIN_MS).sum()),
            gaze_sd_x=fix.x[valid].std(),
            gaze_sd_y=fix.y[valid].std(),
        ))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--window-size", type=int, default=10)
    a = ap.parse_args()

    trials = pd.read_csv(f"{a.export_dir}/trials.csv")
    meta = pd.read_csv(f"{a.export_dir}/meta.csv")[["session", "subject", "group"]]

    feats = pd.concat(
        session_features(pd.read_parquet(f"{a.export_dir}/raw/session_{s:02d}.parquet"), s)
        for s in sorted(trials.session.unique()))

    t = trials.merge(feats, on=["session", "Trial"]).merge(meta, on="session")
    assert (t.onset_code == t.Load).all(), "trial alignment check failed"
    t = t.drop(columns="onset_code")

    # trial-level labels
    t["no_response"] = t.Perform.isna().astype(int)
    t["error"] = (t.Perform != 1).astype(int)                 # wrong or no response
    t["prev_error"] = t.groupby("session").error.shift(1)     # behaviour-only baseline feature
    t["prev_rt"] = t.groupby("session").Rtime.shift(1)

    # window-level labels: windows never cross 20-trial blocks if size divides 20
    n = a.window_size
    t["window"] = (t.Trial - 1) // n
    w = (t.groupby(["session", "window"])
          .agg(subject=("subject", "first"), group=("group", "first"),
               n_errors=("error", "sum"), share_hard=("Load", lambda x: (x == 2).mean()))
          .reset_index())
    # lapse window = more errors than this session's median window (relative to the child)
    w["lapse_window"] = (w.n_errors > w.groupby("session").n_errors.transform("median")).astype(int)
    # features of the window = pre-trial features of its first trial
    first = t[(t.Trial - 1) % n == 0][["session", "window", "pupil_mean", "pupil_slope",
                                       "missing_share", "blink_count", "gaze_sd_x", "gaze_sd_y",
                                       "prev_error", "prev_rt"]]
    w = w.merge(first, on=["session", "window"])

    t.to_csv(f"{a.out_dir}/trial_table.csv", index=False)
    w.to_csv(f"{a.out_dir}/window_table.csv", index=False)
    print(f"trial_table: {t.shape}, window_table: {w.shape}")


if __name__ == "__main__":
    main()