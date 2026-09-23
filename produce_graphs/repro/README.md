# Reproducibility toolkit: tables, figures and number verification

Everything printed in the paper's evaluation that derives from the nine
end-to-end experiments is recomputed here from the raw measurements in
`data/`. Nothing is hard-coded: `generate.py` writes the table bodies and
figures from the data, and `verify.py` recomputes every stated number and
compares it with the paper text.

## Data (`data/`, the released dataset)

| file | contents |
|---|---|
| `trajectories_every_trial.csv` | `run_id,stage,trial,intersection_size` — the size of the running intersection after every iteration of every stage. Raw `run_id` 4..12 are paper runs 1..9; `stage` is `IP` (Introduction Point), `M1` (middle), `VG` (layer-2 vanguard), `EG` (entry guard). |
| `run_stage_metrics.csv` | `run_id,stage_code,experiment_date,day_label,experiment_time_utc,consensus_weight` — one row per run and stage: the stage's start day (`experiment_date`, YYYY-MM-DD; `day_label` = "Day N" with Day 1 = 7 January 2026) and start time (`experiment_time_utc`, "HH:MM UTC", minute resolution) and the monitored relay's stage-start consensus weight. A run is labelled by its `IP` row. The file carries no precomputed convergence columns: every `T_le_q`, `T_conv` and initial-set size is derived from the trajectories by `core.py`. |

Only aggregate values were ever written to disk during the experiments (see the
paper's ethics section): no addresses, pseudonyms or packet data exist in this
dataset.

## Requirements

Python 3.9+, `matplotlib` (figures only). `poppler` (`pdftotext`) is optional
and only used to check the labels inside the generated figure PDFs.

## Use

    make tables     # out/tables/*_body.tex (LaTeX table bodies) + out/figures/*.pdf
    make verify     # recompute every claim; exit 1 on any FAIL

`make tables` regenerates, from `data/` alone:

- `end_to_end_body.tex` — the end-to-end cost table (iterations per stage, N,
  T = 31 s·N + 4v for v = 0, 1 h, 4 h, and the break-even v_max);
- `stage_contrasts_body.tex` — the representative within-stage convergence
  table (two column groups; per stage the runs with the minimum, median,
  second-largest and maximum T_conv);
- `run_stage_thresholds_body.tex` — the appendix table with all 36 run/stage rows;
- `threshold_summary.pdf`, `runs_grid_{a,b,c}.pdf` — the appendix figures.

`make verify` needs the paper sources to read the printed values. Point it at
the directory that holds `main.tex` and `sections/`:

    PAPER_ROOT=/path/to/paper make verify

Without the sources it still runs, prints every recomputed value, and reports
the claims as UNVERIFIABLE instead of PASS/FAIL. The report is written to
`out/verify_report.md`. Claims whose inputs are not part of this dataset (the
Onionoo snapshot behind the jurisdiction appendix, the raw introduction-latency
trials, the operated relays' ages) are reported as UNVERIFIABLE with the recipe
to compute them once those inputs are available.

## Layout

- `core.py` — data loading, statistics (`T_le`, `T_conv`, hours) and the shared
  LaTeX helpers (comment-stripped `tex_lines`, `find_quote`, ...).
- `generate.py` — table bodies and figures.
- `verify.py` — data-integrity check (both CSVs cover the same 36 run/stage
  pairs; the metrics file carries no precomputed columns to compare), discovery
  of `checks/*.py`, report.
- `checks/` — one module per section or table of the paper; each exposes
  `claims(C, traj, metrics)` returning `{id, location, quote, paper, computed,
  status, note}` records.
- `out/tables/` — the table bodies as last generated (committed for reference).

## Adding a claim

Add a record to the module for that section (or a new `checks/<name>.py`; it is
discovered automatically). Recompute the value from `traj` / `metrics`; parse
the printed value from the `.tex` with `C.find_quote` so that an edited sentence
is re-checked rather than silently matched. Run `make verify`.

## Verification report for the submitted version

`out/verify_report.md` is the output of `make verify` run against the paper
sources of the submitted version (which are not part of this repository). It
lists every numeric claim with its location in the paper, the value printed
there, the value recomputed from `data/`, and its status, so the checks can be
inspected without the LaTeX sources.
