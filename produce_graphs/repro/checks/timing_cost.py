"""Cost-model (timing) claims: T = (31 s) N + 4 v.

Definitions (all recomputed from the raw trajectories):
    N(r)      = sum over the four stages of T_conv (first trial with |I_t| <= 1)
    h(r)      = SECONDS_PER_ITER * N(r) / 3600     hours at v = 0
    T(r, v)   = h(r) + 4 v                         four stages, visibility cost v each
    v_max(r)  = (18 - h(r)) / 4                    largest v with T <= 18 h

SECONDS_PER_ITER is taken from core.py (single source of truth shared with
generate.py) and is itself checked in time-002: it must equal
delta (30 s) + round(mean handshake latency), where the latency comes from the
16 "Avg dt" values printed in the introduction-latency appendix.

Rounding follows the paper: Python round(x, 2) (half-even on the binary
float) for hours, round(x, 0) for percentages, round(x, 1) for the abstract.

Every record carries a "basis" key so the aggregator can separate them:
    "data"           computed side recomputed from generated/*.csv
    "paper-internal" computed side comes from numbers printed elsewhere in the
                     paper (the appendix latency table); raw per-trial
                     handshake measurements are NOT in the repository
    "constant"       definitional / implementation parameter
The "computed" string of paper-internal records is prefixed "appendix-table:".

Live quote check: after building every record, the stored "quote" is re-located
(core.relocate: whitespace-normalised, comments and \\begin{comment} blocks
stripped) in the CURRENT paper: first near the registered line of the file
named in "location", then in that whole file, then in every active .tex file.
The reported location is where the quote is printed now ("moved from" is
noted when that differs); a quote printed nowhere downgrades the record to
FAIL. The hard-coded quotes are therefore checked at run time, not just
documented.
"""
from __future__ import annotations

import math
import re
import statistics as st

import core as _core

SETUP = "sections/04-setup-and-evaluation.tex"
ATTACK = "sections/03-attack.tex"
APPX = "sections/appendix_time_of_introduction_handshake_completion.tex"
MAIN = "main.tex"

SEC_PER_ITER = _core.SECONDS_PER_ITER   # single source of truth (checked in time-002)
DELTA = 30.0                            # implementation parameter delta
K_STAGES = 4                            # checked against len(core.STAGES) in time-002
BOUND_H = 18.0                          # lower end of the 18--24 h circuit lifetime
LINE_TOL = 3                            # quote may sit this many lines from the stated one


# ---------------------------------------------------------------- helpers
_N = lambda C, traj: C.per_run_totals(traj)   # {raw run id: N(r)}
_h = _core.hours                               # h = SECONDS_PER_ITER * N / 3600


def _T(N, v):
    return _h(N) + K_STAGES * v


def _vmax(N):
    return (BOUND_H - _h(N)) / K_STAGES


def _read_tex(rel):
    """Current (comment-stripped) text of a .tex file, or None."""
    lines = _core.tex_lines(rel)
    return None if lines is None else "\n".join(lines)


_norm = _core.norm_ws


def _live_quote_check(claim):
    """Re-locate the stored quote in the CURRENT paper (core.relocate: the
    registered file:line first, then the whole file, then every active file).
    The reported location is where the quote is printed now."""
    st, where, mv = _core.relocate(claim["location"], claim["quote"], window=LINE_TOL)
    if st == "nofile":
        claim["status"] = "UNVERIFIABLE"
        claim["note"] = f"{mv}; " + claim["note"]
    elif st == "absent":
        claim["status"] = "FAIL"
        claim["note"] = f"STALE claim: {mv}; " + claim["note"]
        claim["location"] = where
    else:
        claim["location"] = where
        claim["note"] += (f" [{mv}]" if mv else "") + " [quote verified in current tex]"
    return claim


def _appendix_latencies():
    """The 16 'Avg dt (s)' values printed in the handshake-latency table."""
    txt = _read_tex(APPX)
    if txt is None:
        return None
    vals = []
    in_tab = False
    for line in txt.splitlines():
        if r"\begin{tabular}" in line:
            in_tab = True
            continue
        if r"\end{tabular}" in line:
            in_tab = False
            continue
        if not in_tab or line.lstrip().startswith("%"):
            continue
        cells = [c.strip() for c in line.split("&")]
        if len(cells) == 3:
            m = re.match(r"^(\d+\.\d+)\s*\\\\", cells[2])
            if m:
                vals.append(float(m.group(1)))
    return vals or None


def _table_rows():
    """Parse tab:end_to_end body: {run label: (N, [cells as str for v=0,v=1,v=4,vmax])}.

    Returns (rows, error) where rows maps '1'..'9' and 'Median'.
    """
    txt = _read_tex(SETUP)
    if txt is None:
        return None, "tex file not found"
    m = re.search(r"\\label\{tab:end_to_end\}(.*?)\\end\{tabular\}", txt, re.S)
    if not m:
        return None, "tab:end_to_end not found"
    body = m.group(1)
    # strip comments, then join continuation lines: a row ends with '\\'
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("%"))
    body = body.replace("\n", " ")
    rows = {}
    for raw in body.split(r"\\"):
        cells = [c.strip() for c in raw.split("&")]
        if len(cells) != 10:
            continue
        label = re.sub(r"\\(top|mid|bottom)rule|\\cmidrule(\([^)]*\))?\{[^}]*\}", "", cells[0])
        label = re.sub(r"\\textbf\{([^}]*)\}", r"\1", label).strip()
        if not (label.isdigit() or label == "Median"):
            continue
        try:
            N = int(re.sub(r"\\[a-zA-Z]+\[.\]\{.*?\}", "", cells[5]).strip())
        except ValueError:
            continue
        rows[label] = (N, cells[6:10])
    return rows, None


def _fmt(x, nd=2):
    return f"{round(x, nd):.{nd}f}"


def _claim(cid, loc, quote, paper, computed, status, note="", basis="data"):
    return {"id": cid, "location": loc, "quote": quote, "paper": paper,
            "computed": computed, "status": status, "note": note, "basis": basis}


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

    lat = _appendix_latencies()          # paper-internal: printed appendix values
    lat_note = ""
    if lat:
        lat_note = (f"; handshake ~1 s is PAPER-INTERNAL (appendix table, raw per-trial "
                    f"data absent): n={len(lat)}, mean={st.mean(lat):.3f} s, "
                    f"median={st.median(lat):.3f} s")

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

    # ---- time-002: coefficients 31 and 4, DERIVED not asserted
    #   31 must equal delta + round(mean appendix latency) AND core.SECONDS_PER_ITER;
    #   4 must equal len(core.STAGES).
    if lat:
        derived = DELTA + round(st.mean(lat))
        ok_31 = (derived == 31.0) and (SEC_PER_ITER == derived)
        ok_4 = (K_STAGES == 4) and (len(C.STAGES) == K_STAGES)
        out.append(_claim(
            "time-002", f"{SETUP}:364",
            "T=(31\\,\\mathrm{s})N+4v,",
            "31; 4", f"appendix-table:{derived:g}; {len(C.STAGES)}",
            "CONSTANT" if (ok_31 and ok_4) else "FAIL",
            f"31 derived as delta {DELTA:g} s + round(mean handshake {st.mean(lat):.3f} s) = "
            f"{derived:g}; core.SECONDS_PER_ITER = {SEC_PER_ITER:g}"
            + ("" if ok_31 else " (MISMATCH: core.py and the paper coefficient diverge)")
            + f"; 4 = number of stages K = len(core.STAGES) = {len(C.STAGES)}"
            + ("" if ok_4 else " (MISMATCH)") + ".",
            basis="paper-internal"))
    else:
        out.append(_claim(
            "time-002", f"{SETUP}:364",
            "T=(31\\,\\mathrm{s})N+4v,",
            "31; 4", f"n/a; {len(C.STAGES)}", "UNVERIFIABLE",
            f"could not parse the latency table in {APPX}, so 31 = 30 + round(latency) cannot "
            f"be derived; core.SECONDS_PER_ITER = {SEC_PER_ITER:g}; len(core.STAGES) = "
            f"{len(C.STAGES)}.", basis="paper-internal"))

    # ---- time-003: 31 = 30 + 1
    out.append(_claim(
        "time-003", f"{SETUP}:368",
        "The $31$~s iteration cost consists of the $\\delta=30$~s\ndelay between "
        "iterations in our experimental setup and approximately $1$~s\nfor the "
        "introduction handshake itself.",
        "31; 30; 1", f"{DELTA + 1:g}; {DELTA:g}; 1", "CONSTANT",
        "arithmetic 30 + 1 = 31; 30 s is the implementation parameter delta"
        + lat_note + ".", basis="constant"))

    # ---- time-004: handshake ~1 s (appendix table mean) -- PAPER-INTERNAL
    q004 = ("approximately $1$~s handshake duration is based on measurements of "
            "public\nonion services reported in Appendix~\\ref{app:introduction-latency}")
    if lat:
        mean_lat = st.mean(lat)
        comp = round(mean_lat, 0)
        out.append(_claim(
            "time-004", f"{SETUP}:372", q004,
            "1", f"appendix-table:{comp:.0f}",
            "PASS" if comp == 1 else "FAIL",
            f"PAPER-INTERNAL consistency (appendix table vs. text), not raw data: mean of the "
            f"{len(lat)} printed Avg dt values = {mean_lat:.3f} s, median = "
            f"{st.median(lat):.3f} s, range [{min(lat):.3f}, {max(lat):.3f}] s; "
            f"'approximately 1 s' = mean rounded to 0 dp. The 160 raw per-trial handshake "
            f"measurements are not in the repository.", basis="paper-internal"))
    else:
        out.append(_claim(
            "time-004", f"{SETUP}:372", q004,
            "1", "n/a", "UNVERIFIABLE",
            f"could not parse the latency table in {APPX}; no raw per-trial data.",
            basis="paper-internal"))

    # ---- time-005: window ~ one second -- PAPER-INTERNAL
    q005 = "Each window spans a single handshake, lasting approximately one second"
    if lat:
        mean_lat = st.mean(lat)
        comp = round(mean_lat, 0)
        out.append(_claim(
            "time-005", f"{ATTACK}:477", q005,
            "one second (approx.)", f"appendix-table:{comp:.0f} s",
            "PASS" if comp == 1 else "FAIL",
            f"PAPER-INTERNAL, same basis as time-004: mean {mean_lat:.3f} s of the {len(lat)} "
            f"appendix values; raw per-trial data absent.", basis="paper-internal"))
    else:
        out.append(_claim(
            "time-005", f"{ATTACK}:477", q005,
            "one second (approx.)", "n/a", "UNVERIFIABLE",
            f"could not parse the latency table in {APPX}.", basis="paper-internal"))

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
        "12%; 37%; 18", f"{p_med:.0f}%; {p_max:.0f}%; {BOUND_H:g}",
        "PASS" if (p_med, p_max) == (12, 37) else "FAIL",
        f"100*{med_h:.4f}/18 = {100 * med_h / BOUND_H:.2f}; 100*{hs[max_r]:.4f}/18 = "
        f"{100 * hs[max_r] / BOUND_H:.2f}; nearest integer. 18 h is a CONSTANT "
        f"(lower end of the 18--24 h circuit lifetime)."))

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
        "five of nine; 4; 18", f"{len(exceed)} of {len(runs)}; 4; 18",
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

    # ---- time-013: bold cells == T > 18 in tab:end_to_end
    #   anchored to the table caption's bold rule: "... costs $v$ (bold: exceeds $18$~h)"
    q013 = "costs $v$ (bold: exceeds $18$~h)."
    rows, err = _table_rows()
    if rows is None:
        out.append(_claim(
            "time-013", f"{SETUP}:421", q013,
            "18", "n/a", "UNVERIFIABLE", f"could not parse tab:end_to_end: {err}"))
    else:
        problems = []
        checked = 0
        expected_labels = {str(C.PAPER_RUN[r]): N[r] for r in runs}
        expected_labels["Median"] = med_N
        for label, N_exp in expected_labels.items():
            if label not in rows:
                problems.append(f"row {label} missing from table")
                continue
            N_tab, cells = rows[label]
            if N_tab != N_exp:
                problems.append(f"row {label}: table N={N_tab}, data N={N_exp:g}")
            for cell, v in zip(cells[:3], (0.0, 1.0, 4.0)):
                bold = r"\textbf" in cell
                val_s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cell).strip()
                T = _T(N_exp, v)
                checked += 1
                try:
                    val = float(val_s)
                except ValueError:
                    problems.append(f"row {label} v={v:g}: unparsable cell {cell!r}")
                    continue
                if abs(val - round(T, 2)) > 1e-9:
                    problems.append(f"row {label} v={v:g}: table {val_s}, computed {round(T, 2):.2f}")
                if bold != (T > BOUND_H):
                    problems.append(f"row {label} v={v:g}: bold={bold} but T={T:.2f}")
            vm_s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cells[3]).strip()
            try:
                if abs(float(vm_s) - round(_vmax(N_exp), 2)) > 1e-9:
                    problems.append(f"row {label} v_max: table {vm_s}, computed {round(_vmax(N_exp), 2):.2f}")
            except ValueError:
                problems.append(f"row {label} v_max: unparsable {cells[3]!r}")
        n_bold = sum(1 for lab, (_, cells) in rows.items()
                     for c in cells[:3] if r"\textbf" in c)
        n_exceed = sum(1 for N_exp in expected_labels.values()
                       for v in (0.0, 1.0, 4.0) if _T(N_exp, v) > BOUND_H)
        out.append(_claim(
            "time-013", f"{SETUP}:421", q013,
            "18", f"bold cells: {n_bold}; cells with T>18: {n_exceed}",
            "PASS" if not problems else "FAIL",
            (f"checked {checked} T cells + {len(expected_labels)} v_max cells in "
             f"tab:end_to_end against T={SEC_PER_ITER:g}N/3600+4v; bold <=> T>18; max T at "
             f"v<=1 is {max(_T(N[r], 1.0) for r in runs):.2f} h"
             + ("; problems: " + "; ".join(problems) if problems else "") + ".")))

    # ---- live check: every stored quote must exist near its stated line in the CURRENT tex
    return [_live_quote_check(c) for c in out]
