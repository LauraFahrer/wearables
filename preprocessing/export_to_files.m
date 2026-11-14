%% Export pupil_adhd_dataset.mat to CSV/Parquet for use in Python
% One-off conversion: MATLAB tables cannot be read directly in Python.

repo     = fileparts(fileparts(mfilename('fullpath')));   % repo root, found from the script's own location
datafile = fullfile(repo, 'data', 'pupil_adhd_data', 'pupil_adhd_dataset.mat');
outdir   = fullfile(repo, 'data', 'pupil_adhd_data', 'export');

% Test with one session first; afterwards change to: 1:numel(Pupil_data)
sessions = 1:numel(Pupil_data);

%% Load data (skipped if already in workspace)
if ~exist('Pupil_data', 'var')
    load(datafile)
end
if ~exist(fullfile(outdir, 'raw'), 'dir')
    mkdir(fullfile(outdir, 'raw'));
end

%% Export
meta = table(); trials = table();
for s = sessions
    P = Pupil_data(s);

    % session info
    m = table(s, P.Subject, string(P.Group), P.Age, ...
        'VariableNames', {'session','subject','group','age'});
    meta = [meta; [m P.Wisc]];

    % trials (without the 8 s pupil epochs)
    E = removevars(P.Task_epocs, 'Pupil');
    E.session = repmat(s, height(E), 1);
    trials = [trials; E];

    % raw samples, one file per session
    D = P.Task_data;
    R = table(D.Time, D.Diameter, D.Position(:,1), D.Position(:,2), D.Events, ...
        'VariableNames', {'time','diameter','x','y','event'});
    parquetwrite(fullfile(outdir, 'raw', sprintf('session_%02d.parquet', s)), R);

    fprintf('Session %d done\n', s);
end

writetable(meta,   fullfile(outdir, 'meta.csv'));
writetable(trials, fullfile(outdir, 'trials.csv'));
disp('Export finished')