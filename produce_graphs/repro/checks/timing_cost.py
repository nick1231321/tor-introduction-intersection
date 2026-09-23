"""Cost-model (timing) claims: T = (31 s) N + 4 v.

Definitions (all recomputed from the raw trajectories):
    N(r)      = sum over the four stages of T_conv (first trial with |I_t| <= 1)
    h(r)      = SECONDS_PER_ITER * N(r) / 3600     hours at v = 0
    T(r, v)   = h(r) + 4 v                         four stages, visibility cost v each
    v_max(r)  = (18 - h(r)) / 4                    largest v with T <= 18 h

SECONDS_PER_ITER (31 s), the number of stages (4) and the 18 h bound are the
paper's model parameters and are taken from core.py; only the numbers the
paper derives from the nine runs with them are checked here.

Rounding follows the paper: Python round(x, 2) (half-even on the binary
float) for hours, round(x, 0) for percentages, round(x, 1) for the abstract.

Live quote check: after building every record, the stored "quote" is re-located
(core.relocate: whitespace-normalised, comments and \\begin{comment} blocks
stripped) in the CURRENT paper: first near the registered line of the file
named in "location", then in that whole file, then in every active .tex file.
The reported location is where the quote is printed now ("moved from" is
noted when that differs); a quote printed nowhere downgrades the record to
FAIL. Without the paper sources the numeric status is kept (the printed
value is hard-coded here) and the note says the quote was not verified.
"""
from __future__ import annotations

import math
import statistics as st

import core as _core

SETUP = "sections/04-setup-and-evaluation.tex"
MAIN = "main.tex"

SEC_PER_ITER = _core.SECONDS_PER_ITER   # single source of truth shared with generate.py
K_STAGES = len(_core.STAGES)            # four stages
BOUND_H = 18.0                          # lower end of the 18--24 h circuit lifetime
LINE_TOL = 3                            # quote may sit this many lines from the stated one


# ---------------------------------------------------------------- helpers
_N = lambda C, traj: C.per_run_totals(traj)   # {raw run id: N(r)}
_h = _core.hours                               # h = SECONDS_PER_ITER * N / 3600


def _T(N, v):
    return _h(N) + K_STAGES * v


def _vmax(N):
    return (BOUND_H - _h(N)) / K_STAGES


def _live_quote_check(claim):
    """Re-locate the stored quote in the CURRENT paper (core.relocate: the
    registered file:line first, then the whole file, then every active file).
    The reported location is where the quote is printed now."""
    st, where, mv = _core.relocate(claim["location"], claim["quote"], window=LINE_TOL)
    if st == "nofile":
        claim["note"] = f"{mv}; quote not verified; " + claim["note"]
    elif st == "absent":
        claim["status"] = "FAIL"
        claim["note"] = f"STALE claim: {mv}; " + claim["note"]
        claim["location"] = where
    else:
        claim["location"] = where
        claim["note"] += (f" [{mv}]" if mv else "") + " [quote verified in current tex]"
    return claim


def _claim(cid, loc, quote, paper, computed, status, note=""):
    return {"id": cid, "location": loc, "quote": quote, "paper": paper,
            "computed": computed, "status": status, "note": note}


# ---------------------------------------------------------------- claims
def claims(C, traj, metrics):
    out = []
    N = _N(C, traj)
    runs = C.RUN_IDS
    hs = {r: _h(N[r]) for r in runs}
    med_h = st.median(hs.values())
    max_r = max(runs, key=lambda r: (N[r], -r))
    min_r = min(runs, key=lambda r: (N[r], r))
    vmax = {r: _vmax(N[r]) for r in runs}
    med_vmax = st.median(vmax.values())
    n_str = ", ".join(f"{C.PAPER_RUN[r]}:{N[r]}" for r in runs)

    # ---- time-001: abstract median 2.2 h
    comp = round(med_h, 1)
    out.append(_claim(
        "time-001", f"{MAIN}:80",
        "with an estimated median time of $2.2$~h.",
        "2.2", f"{comp:.1f}",
        "PASS" if comp == 2.2 else "FAIL",
        f"median({SEC_PER_ITER:g}*N/3600 over 9 runs) = {med_h:.4f} h (median N = "
        f"{st.median(N.values()):g}); assumes v=0 and {SEC_PER_ITER:g} s/iteration. "
        f"N by paper run: {n_str}."))

    # ---- time-006: median 2.24, max 6.63
    c_med, c_max = round(med_h, 2), round(hs[max_r], 2)
    out.append(_claim(
        "time-006", f"{SETUP}:390",
        "when $v=0$, the median\nreconstruction takes $2.24$~h and the slowest takes $6.63$~h.",
        "2.24; 6.63", f"{c_med:.2f}; {c_max:.2f}",
        "PASS" if (c_med, c_max) == (2.24, 6.63) else "FAIL",
        f"median h = {med_h:.4f} h (N={st.median(N.values()):g}); max h = {hs[max_r]:.4f} h "
        f"(paper run {C.PAPER_RUN[max_r]}, N={N[max_r]})."))

    # ---- time-007: 12% and 37% of 18 h
    p_med = round(100 * med_h / BOUND_H, 0)
    p_max = round(100 * hs[max_r] / BOUND_H, 0)
    out.append(_claim(
        "time-007", f"{SETUP}:391",
        "correspond to approximately $12\\%$ and $37\\%$, respectively, of $18$~h",
        "12%; 37%", f"{p_med:.0f}%; {p_max:.0f}%",
        "PASS" if (p_med, p_max) == (12, 37) else "FAIL",
        f"100*{med_h:.4f}/18 = {100 * med_h / BOUND_H:.2f}; 100*{hs[max_r]:.4f}/18 = "
        f"{100 * hs[max_r] / BOUND_H:.2f}; nearest integer; 18 h = lower end of the "
        f"circuit lifetime (model parameter)."))

    # ---- time-008: median v_max = 3.94
    c = round(med_vmax, 2)
    out.append(_claim(
        "time-008", f"{SETUP}:397",
        "The median run permits\n$v_{\\max}=3.94$~h per relay",
        "3.94", f"{c:.2f}",
        "PASS" if c == 3.94 else "FAIL",
        f"median of per-run v_max = (18-h)/4 = {med_vmax:.4f} h; identical to v_max of the "
        f"median-N run since v_max is monotone in N. ASSUMPTION: median of per-run v_max."))

    # ---- time-009: experiment 6, v_max 2.84
    c = round(vmax[max_r], 2)
    ok = (C.PAPER_RUN[max_r] == 6) and (c == 2.84)
    out.append(_claim(
        "time-009", f"{SETUP}:398",
        "the most iteration-intensive run,\nexperiment~6, permits $2.84$~h.",
        "6; 2.84", f"{C.PAPER_RUN[max_r]}; {c:.2f}",
        "PASS" if ok else "FAIL",
        f"argmax N = raw run {max_r} (paper {C.PAPER_RUN[max_r]}), N={N[max_r]}, "
        f"h={hs[max_r]:.4f}; v_max = (18-h)/4 = {vmax[max_r]:.4f}."))

    # ---- time-010: five of nine exceed 18 h at v=4
    exceed = [r for r in runs if _T(N[r], 4.0) > BOUND_H]
    out.append(_claim(
        "time-010", f"{SETUP}:398",
        "At $v=4$~h, five of the nine runs exceed\nthe $18$~h bound.",
        "five of nine", f"{len(exceed)} of {len(runs)}",
        "PASS" if len(exceed) == 5 and len(runs) == 9 else "FAIL",
        f"runs with h+16 > 18 (N > {(BOUND_H - 16) * 3600 / SEC_PER_ITER:.2f}): raw "
        f"{exceed} = paper {[C.PAPER_RUN[r] for r in exceed]}."))

    # ---- time-011: visibility share 64% / 88% for the median run
    med_N = st.median(N.values())
    med_runs = [C.PAPER_RUN[r] for r in runs if N[r] == med_N]
    h_med = _h(med_N)
    s1 = 100 * (K_STAGES * 1.0) / _T(med_N, 1.0)
    s4 = 100 * (K_STAGES * 4.0) / _T(med_N, 4.0)
    c1, c4 = round(s1, 0), round(s4, 0)
    out.append(_claim(
        "time-011", f"{SETUP}:403",
        "visibility accounts for approximately $64\\%$ of the total time at\n$v=1$~h "
        "and $88\\%$ at $v=4$~h.",
        "64%; 88%", f"{c1:.0f}%; {c4:.0f}%",
        "PASS" if (c1, c4) == (64, 88) else "FAIL",
        f"median N = {med_N:g} (paper runs {med_runs}), h = {h_med:.4f}; "
        f"100*4/(h+4) = {s1:.2f}; 100*16/(h+16) = {s4:.2f}. ASSUMPTION: 'median run' = "
        f"the run(s) with median N (integer median exists since two runs tie)."))

    # ---- time-012: v_max range 2.84..4.28, "more than sevenfold" N spread
    #   integer-fold precision: floor(N_max / N_min) == 7, i.e. 7 < ratio < 8
    lo, hi = round(min(vmax.values()), 2), round(max(vmax.values()), 2)
    ratio = N[max_r] / N[min_r]
    ok = (lo, hi) == (2.84, 4.28) and math.floor(ratio) == 7
    out.append(_claim(
        "time-012", f"{SETUP}:404--405",
        "$v_{\\max}$ ranges from\n$2.84$ to $4.28$~h despite a more than sevenfold "
        "difference in total\niteration counts.",
        "2.84--4.28; sevenfold", f"{lo:.2f}--{hi:.2f}; {ratio:.2f}-fold",
        "PASS" if ok else "FAIL",
        f"min v_max at paper run {C.PAPER_RUN[max_r]} (N={N[max_r]}), max v_max at paper run "
        f"{C.PAPER_RUN[min_r]} (N={N[min_r]}); N ratio {N[max_r]}/{N[min_r]} = {ratio:.3f}; "
        f"'more than sevenfold' = floor(N_max/N_min) == 7 (7 < ratio < 8), "
        f"floor = {math.floor(ratio)}."))

    # ---- live check: every stored quote must exist near its stated line in the CURRENT tex
    return [_live_quote_check(c) for c in out]
