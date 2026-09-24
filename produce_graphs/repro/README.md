# Reproducing the evaluation tables and figures

`generate.py` regenerates, from the raw measurements of the nine end-to-end
experiments in `data/`, every data-derived table and figure of the paper.
Nothing is hard-coded: every value is computed from the two CSV files.

## Data (`data/`, the released dataset)

| file | contents |
|---|---|
| `trajectories_every_trial.csv` | `run_id,stage,trial,intersection_size` — the size of the running intersection after every iteration of every stage. Raw `run_id` 4..12 are paper runs 1..9; `stage` is `IP` (Introduction Point), `M1` (middle), `VG` (layer-2 vanguard), `EG` (entry guard). |
| `run_stage_metrics.csv` | `run_id,stage_code,experiment_date,day_label,experiment_time_utc,consensus_weight` — one row per run and stage: the stage's start day (`experiment_date`, YYYY-MM-DD; `day_label` = "Day N" with Day 1 = 7 January 2026) and start time (`experiment_time_utc`, "HH:MM UTC", minute resolution) and the monitored relay's stage-start consensus weight. A run is labelled by its `IP` row. The file carries no precomputed convergence columns: every `T_le_q`, `T_conv` and initial-set size is derived from the trajectories by `core.py`. |

Only aggregate values were ever written to disk during the experiments (see the
paper's ethics section): no addresses, pseudonyms or packet data exist in this
dataset.

## Requirements

Python 3.9+, `matplotlib` (figures only).

## Use

    make tables     # out/tables/*_body.tex (LaTeX table bodies) + out/figures/*.pdf

`make tables` writes:

- `out/tables/end_to_end_body.tex` — the end-to-end cost table: iterations to
  convergence per stage (with the monitored relay's consensus weight), their
  sum N, the time T = 31 s·N + 4v for v = 0, 1 h and 4 h, and the break-even
  v_max;
- `out/tables/stage_contrasts_body.tex` — the representative within-stage
  convergence table (per stage, the runs with the minimum, median,
  second-largest and maximum T_conv);
- `out/tables/run_stage_thresholds_body.tex` — the appendix table with all 36
  run/stage rows;
- `out/figures/threshold_summary.pdf`, `out/figures/runs_grid_{a,b,c}.pdf` —
  the convergence figures of the appendix.

The table bodies are the rows between `\midrule` and `\bottomrule` of the
corresponding tables in the paper and can be compared with them line by line.

## Files

- `core.py` — data loading and the derived quantities (`T_le`, `T_conv`,
  initial set size, per-run totals, hours).
- `generate.py` — table bodies and figures.
- `data/` — the dataset described above.
- `out/` — the tables and figures as last generated.
