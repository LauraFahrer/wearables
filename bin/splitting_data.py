# splitting data either randomly into test and train set or using the parameter
# --group-column subject_id if multiple measurements of one person are in the dataset
# preventing data leakage

import argparse
import csv
import random
from pathlib import Path


def split_data(input_file, test_size=0.2, seed=42, group_column=None):

    rng = random.Random(seed)

    # Read dataset
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not rows:
        raise ValueError("The input dataset is empty.")

    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    # Split data
    if group_column:
        if group_column not in fieldnames:
            raise ValueError(
                f"Column '{group_column}' not found in dataset."
            )

        groups = {}

        for index, row in enumerate(rows):
            group = row[group_column]
            groups.setdefault(group, []).append(index)

        if len(groups) < 2:
            raise ValueError(
                "At least two different groups are required."
            )

        # Randomly assign complete groups to train/test
        group_names = list(groups.keys())
        rng.shuffle(group_names)

        target_test_rows = round(len(rows) * test_size)

        test_groups = set()
        current_test_rows = 0

        for group in group_names:
            current_distance = abs(
                current_test_rows - target_test_rows
            )
            new_distance = abs(
                current_test_rows + len(groups[group])
                - target_test_rows
            )

            if new_distance < current_distance:
                test_groups.add(group)
                current_test_rows += len(groups[group])

        test_indices = {
            index
            for group in test_groups
            for index in groups[group]
        }

    else:
        # Random row-level split
        indices = list(range(len(rows)))
        rng.shuffle(indices)

        n_test = round(len(rows) * test_size)
        test_indices = set(indices[:n_test])

    # Keep original row order within each split
    train_rows = [
        row for i, row in enumerate(rows)
        if i not in test_indices
    ]

    test_rows = [
        row for i, row in enumerate(rows)
        if i in test_indices
    ]

    # Write output files
    for filename, data in [
        ("train_data.tsv", train_rows),
        ("test_data.tsv", test_rows),
    ]:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                delimiter="\t"
            )
            writer.writeheader()
            writer.writerows(data)

    print(f"Total samples: {len(rows)}")
    print(f"Training samples: {len(train_rows)}")
    print(f"Test samples: {len(test_rows)}")
    print(f"Random seed: {seed}")
    print(f"Group column: {group_column or 'None'}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Split a TSV dataset into training and test data."
    )

    parser.add_argument("input_file", type=Path)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--group-column", type=str, default=None)

    args = parser.parse_args()

    split_data(
        input_file=args.input_file,
        test_size=args.test_size,
        seed=args.seed,
        group_column=args.group_column
    )
