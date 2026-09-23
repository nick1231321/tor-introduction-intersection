#!/usr/bin/env python3
"""Regenerate every data-derived table body and figure from ../generated/.

Tables are written as \\input-able tabular bodies to repro/out/tables/, figures to
../figures/ (the paths the paper references). Numbers come only from the raw data,
so the paper stays in lockstep with the measurements. Deterministic output.

Artifacts needing the Onionoo snapshot (tor_top15_countries, 14_eyes_probabilities)
are skipped with a message, since that raw file is not in the project.
"""
from __future__ import annotations
import os
import statistics as st
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import core as C

ROOT = C.ROOT
OUT_T = Path(__file__).resolve().parent / "out" / "tables"
# figures go to the paper's figures/ dir when it exists, else to ./out/figures
FIGS = Path(os.environ.get("REPRO_FIGS") or
            (ROOT / "figures" if (ROOT / "figures").is_dir() else OUT_T.parent / "figures"))
OUT_T.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(exist_ok=True)

traj = C.load_trajectories()
metrics = C.load_metrics()
STAGE_TITLE = ["Introduction Point", "Middle 1", "Vanguard", "Entry Guard"]
COLORS = {"IP": "#000000", "M1": "#4477AA", "VG": "#CC7722", "EG": "#CC79A7"}


def w(name, text):
    (OUT_T / name).write_text(text)
    print("wrote", OUT_T / name)


# ---------- Table: end_to_end ----------
def table_end_to_end():
    lines = []
    for rid in C.RUN_IDS:
        cells = []
        for s in C.STAGES:
            tc = C.T_conv(traj[(rid, s)])
            cw = int(metrics[(rid, s)]["consensus_weight"])
            cells.append(f"{tc} ({cw})")
        total = C.per_run_total(traj, rid)
        t = metrics[(rid, "IP")]["experiment_time_utc"]
        lines.append(f"{C.PAPER_RUN[rid]} & {t.replace(' UTC','')} & "
                     + " & ".join(cells) + f" & {total} & {C.hours(total):.2f} \\\\")
    # median row
    med = [int(st.median([C.T_conv(traj[(rid, s)]) for rid in C.RUN_IDS])) for s in C.STAGES]
    tot_med = int(st.median([C.per_run_total(traj, rid) for rid in C.RUN_IDS]))
    h_med = st.median([C.hours(C.per_run_total(traj, rid)) for rid in C.RUN_IDS])
    lines.append("\\midrule")
    lines.append("\\textbf{Median} & & " + " & ".join(str(m) for m in med)
                 + f" & {tot_med} & {h_med:.2f} \\\\")
    w("end_to_end_body.tex", "\n".join(lines) + "\n")


# ---------- Table: run_stage_thresholds (tab:run-stage-thresholds, all 36 rows) ----------
THRESHOLD_STAGE_LABEL = {"IP": "Intro. Point", "M1": "Middle 1",
                         "VG": "Vanguard", "EG": "Entry Guard"}
THRESHOLD_QS = (10, 5, 3, 2, 1)          # T<=10, T<=5, T<=3, T<=2, T_conv


def thresholds_body(traj, metrics):
    """The tabular body of tab:run-stage-thresholds in the paper's exact layout:
    per run four stage rows 'label  & stage  & |A_1|  & T<=10  & T<=5  & T<=3
    & T<=2  & T_conv  & CW \\\\' (two spaces before every '&'; the label
    'Rp (Day d, HH:MM)' only on the IP row, taken from that run's IP-stage
    day_label / experiment_time_utc), runs separated by '\\addlinespace' and a
    blank line."""
    blocks = []
    for rid in C.RUN_IDS:
        ip = metrics[(rid, "IP")]
        label = f"R{C.PAPER_RUN[rid]} ({ip['day_label']}, {ip['experiment_time_utc'].replace(' UTC', '')})"
        rows = []
        for j, s in enumerate(C.STAGES):
            seq = traj[(rid, s)]
            cells = [label if j == 0 else "", THRESHOLD_STAGE_LABEL[s], str(C.initial_set_size(seq))]
            cells += [str(C.T_le(seq, q)) for q in THRESHOLD_QS]
            cells.append(str(int(round(float(metrics[(rid, s)]["consensus_weight"])))))
            rows.append("  & ".join(cells) + " \\\\")
        blocks.append("\n".join(rows))
    return "\n\\addlinespace\n\n".join(blocks) + "\n"


def table_thresholds():
    w("run_stage_thresholds_body.tex", thresholds_body(traj, metrics))


# ---------- Table: stage_contrasts (tab:stage-contrasts, two column groups) ----------
CONTRAST_PAIRS = [("IP", "VG"), ("M1", "EG")]        # left group, right group per block
CONTRAST_HEADER = {"IP": "Introduction Point", "M1": "Middle",
                   "VG": "Vanguard", "EG": "Entry Guard"}


def contrast_runs(traj, stage):
    """Representative runs for a stage, in increasing T_conv: the run with the
    minimum T_conv, the run at the median T_conv, the second-largest and the
    maximum.  Ties on a value are broken by the lowest run number."""
    tc = {rid: C.T_conv(traj[(rid, stage)]) for rid in C.RUN_IDS}
    order = sorted(C.RUN_IDS, key=lambda rid: (tc[rid], rid))
    n = len(order)
    first = lambda val: min(rid for rid in C.RUN_IDS if tc[rid] == val)
    return [first(tc[order[0]]), first(tc[order[n // 2]]), order[n - 2], order[n - 1]]


def contrast_cells(traj, metrics, rid, stage):
    seq = traj[(rid, stage)]
    ip = metrics[(rid, "IP")]                         # labels use the run (IP-stage) start
    day = "".join(ch for ch in ip["day_label"] if ch.isdigit())
    hhmm = ip["experiment_time_utc"].replace(" UTC", "")
    return [f"R{C.PAPER_RUN[rid]} D{day} {hhmm}", metrics[(rid, stage)]["consensus_weight"],
            str(C.initial_set_size(seq))] + [str(C.T_le(seq, q)) for q in (10, 3, 2, 1)]


def stage_contrasts_body(traj, metrics):
    """The tabular body of tab:stage-contrasts, one line per printed row; each
    line carries a left-group row and a right-group row."""
    lines = []
    for bi, (left, right) in enumerate(CONTRAST_PAIRS):
        if bi:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{7}}{{@{{}}l}}{{\\textit{{{CONTRAST_HEADER[left]}}}}} & "
                     f"\\multicolumn{{7}}{{l}}{{\\textit{{{CONTRAST_HEADER[right]}}}}} \\\\")
        for rl, rr in zip(contrast_runs(traj, left), contrast_runs(traj, right)):
            cells = contrast_cells(traj, metrics, rl, left) + contrast_cells(traj, metrics, rr, right)
            lines.append(" & ".join(cells) + " \\\\")
    return "\n".join(lines) + "\n"


def table_stage_contrasts():
    w("stage_contrasts_body.tex", stage_contrasts_body(traj, metrics))


# ---------- Figure: threshold_summary.pdf ----------
def fig_threshold_summary():
    med = {s: [st.median([C.T_le(traj[(rid, s)], q) for rid in C.RUN_IDS])
               for q in C.THRESHOLDS] for s in C.STAGES}
    x = range(len(C.THRESHOLDS)); nb = len(C.STAGES); wbar = 0.8 / nb
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for i, s in enumerate(C.STAGES):
        ax.bar([xi + (i - (nb - 1) / 2) * wbar for xi in x], med[s], wbar,
               label=STAGE_TITLE[i], color=COLORS[s])
    ax.set_yscale("log")
    ax.set_xticks(list(x)); ax.set_xticklabels([f"$\\leq{q}$" for q in C.THRESHOLDS])
    ax.set_xlabel(r"Threshold on $|\mathcal{I}_t|$"); ax.set_ylabel("Median trial $t$")
    ax.legend(ncol=2, frameon=False, fontsize=9)
    ax.grid(axis="y", ls=":", alpha=.5)
    fig.tight_layout(); fig.savefig(FIGS / "threshold_summary.pdf"); plt.close(fig)
    print("wrote", FIGS / "threshold_summary.pdf")


# ---------- Figures: runs_grid_{a,b,c}.pdf ----------
def figs_runs_grid():
    groups = {"a": [4, 5, 6], "b": [7, 8, 9], "c": [10, 11, 12]}
    for suffix, rids in groups.items():
        fig, axes = plt.subplots(len(rids), len(C.STAGES),
                                 figsize=(7.2, 5.4), squeeze=False)
        for r, rid in enumerate(rids):
            for cc, s in enumerate(C.STAGES):
                ax = axes[r][cc]; seq = traj[(rid, s)]
                ax.plot(range(1, len(seq) + 1), seq, marker="o", ms=2,
                        color=COLORS[s], lw=1)
                ax.set_yscale("log"); ax.grid(ls=":", alpha=.4)
                if r == 0:
                    ax.set_title(STAGE_TITLE[cc], fontsize=12)
                if cc == 0:
                    ax.set_ylabel(f"R{C.PAPER_RUN[rid]}\n$|\\mathcal{{I}}_t|$", fontsize=11)
                cw = metrics[(rid, s)]["consensus_weight"]
                ax.text(.95, .9, f"CW {cw}\n$T$={C.T_conv(seq)}", ha="right", va="top",
                        transform=ax.transAxes, fontsize=8)
                ax.tick_params(labelsize=9)
                ax.xaxis.set_major_locator(plt.MaxNLocator(4))
        fig.tight_layout(); fig.savefig(FIGS / f"runs_grid_{suffix}.pdf"); plt.close(fig)
        print("wrote", FIGS / f"runs_grid_{suffix}.pdf")


if __name__ == "__main__":
    table_end_to_end()
    table_thresholds()
    table_stage_contrasts()
    fig_threshold_summary()
    figs_runs_grid()
    print("\nNOTE: tor_top15_countries.png and 14_eyes_probabilities.png require the "
          "raw Onionoo snapshot (not in project) and were not regenerated.")
