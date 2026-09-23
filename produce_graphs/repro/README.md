# Reproducibility toolkit: tables, figures and number verification

Everything printed in the paper's evaluation that derives from the nine
end-to-end experiments is recomputed here from the raw measurements in
`data/`. Nothing is hard-coded: `generate.py` writes the table bodies and
figures from the data, and `verify.py` recomputes every such number and
compares it with the paper text. The toolkit covers only the numbers derived
from the nine runs; protocol constants, cited figures and inputs outside this
dataset are not part of it.

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
    make verify     # recompute every claim; exit 1 on any FAIL

`make tables` regenerates, from `data/` alone:

- `end_to_end_body.tex` — the end-to-end cost table (iterations per stage, N,
  T = 31 s·N + 4v for v = 0, 1 h, 4 h, and the break-even v_max);
- `stage_contrasts_body.tex` — the representative within-stage convergence
  table (two column groups; per stage the runs with the minimum, median,
  second-largest and maximum T_conv);
- `run_stage_thresholds_body.tex` — the appendix table with all 36 run/stage rows;
- `threshold_summary.pdf`, `runs_grid_{a,b,c}.pdf` — the appendix figures.

`make verify` reports one row per claim with two statuses only: **PASS** (the
value recomputed from `data/` equals the one printed in the paper) or
**FAIL** (it does not; the note says why). Every `computed` value is a
function of the two CSVs alone, so every claim can be recomputed anywhere.
There are two modes:

- **With the paper sources** (`PAPER_ROOT=/path/to/paper make verify`): every
  printed value is read from the LaTeX text (a moved sentence is re-located, a
  sentence printed nowhere is FAIL) and compared with the recomputed one. This
  run also freezes each claim's sentence, location, printed value and
  recomputed value into `claims_snapshot.json`.
- **Without the sources (reviewer mode, the default from a clean clone):** the
  sentence and printed value of each claim come from `claims_snapshot.json`,
  which was frozen from the submitted version; the value is recomputed from
  `data/` now. PASS means the frozen comparison passed and today's
  recomputation equals the frozen one; a changed dataset or check, a claim
  missing from the snapshot, or a snapshot claim no module produces any more
  is FAIL. Both modes write `out/manual_checklist.md`: for every claim the
  sentence to look for in the PDF, the value printed there and the recomputed
  value, so each one can be checked by hand against the paper.

If neither the sources nor `claims_snapshot.json` are available there is
nothing to compare against: the run prints a `NO-SNAPSHOT` banner, lists every
claim with paper `n/a` and status FAIL (the recomputed values are still shown)
and exits with status 2.

The two table-body claims (`contr-body`, `app-body`) compare a digest
("`<n> lines, sha1 <12 hex>`" of the whitespace-normalised body lines) of the
table printed in the paper with the same digest of the body `generate.py`
emits, so `make tables` and the paper cannot drift apart.

## Layout

- `core.py` — data loading, statistics (`T_le`, `T_conv`, hours) and the shared
  LaTeX helpers: comment-stripped `tex_lines`, `paper_files` (main.tex and
  every active `\input`), and the single quote locator `locate_quote` /
  `relocate` / `search_paper` that every module uses. A claim's registered
  `file:line` is only the first place tried: the quote is then searched in the
  whole file and in every active file, so the report shows where the text is
  printed *now* (with a "moved from" note) and a quote printed nowhere is a
  stale anchor, never a silent PASS.
- `generate.py` — table bodies and figures.
- `verify.py` — data-integrity check (both CSVs cover the same 36 run/stage
  pairs; the metrics file carries no precomputed columns to compare), discovery
  of `checks/*.py`, snapshot replay, report and checklist.
- `checks/` — one module per section or table of the paper; each exposes
  `claims(C, traj, metrics)` returning `{id, location, quote, paper, computed,
  status, note}` records with status PASS or FAIL:
  - `convergence.py` (`conv-001..027`) — success and convergence statistics of
    the 36 stages (medians, thresholds, plateaus, collapses);
  - `timing_cost.py` (`time-001`, `time-006..012`) — the cost model
    T = 31 s·N + 4v applied to the nine run totals;
  - `end_to_end_table.py` (`e2e-001..010`) — every row of the end-to-end table;
  - `stage_contrasts_table.py` (`contr-001..016`, `contr-sel-*`, `contr-body`) —
    every row, the row selection per stage and the body of the within-stage table;
  - `appendix_run_table.py` (`app-002..037`, `app-body`) — all 36 rows and the
    body of the appendix run/stage table;
  - `setup_structure.py` (`setup-*`) — nine runs, four stages, 36 observations,
    stage order, run ids, date span and run schedule as stated in the text.
- `claims_snapshot.json` — sentence, printed value and recomputed value of every
  claim, frozen from the submitted version (input of reviewer mode).
- `out/tables/` — the table bodies as last generated (committed for reference);
  `out/verify_report.md` and `out/manual_checklist.md` — the last verify run.

## Adding a claim

Add a record to the module for that section (or a new `checks/<name>.py`; it is
discovered automatically). Its `computed` value must be derived from `traj` /
`metrics` only; parse the printed value from the `.tex` with `C.relocate` /
`C.search_paper` so that an edited or moved sentence is re-checked rather than
silently matched. Run `PAPER_ROOT=... make verify` to refresh the snapshot.

## Verification report for the submitted version

`out/verify_report.md` is the output of `make verify` run against the paper
sources of the submitted version (which are not part of this repository). It
lists every numeric claim with its location in the paper, the value printed
there, the value recomputed from `data/`, and its status, so the checks can be
inspected without the LaTeX sources.
