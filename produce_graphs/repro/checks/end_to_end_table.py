"""Claims for Table tab:end_to_end (sections/04-setup-and-evaluation.tex, lines 462-493).

Per paper run p (raw run r = p + 3), every row is recomputed from the raw data:
  * stage cells  : T_conv per stage (IP, M1, VG, EG) taken from the trajectory
                   (core.T_conv; it must equal the recorded trial count) with
                   the consensus weight from metrics in parentheses;
  * N            : sum of the four T_conv values;
  * v=0          : h = 31*N/3600 hours, printed at 2 decimals;
  * v=1 h        : h + 4  (rounded from the UNROUNDED h);
  * v=4 h        : h + 16 (rounded from the UNROUNDED h);
  * v_max        : (18 - h) / 4 (rounded from the UNROUNDED h).
The Median row is the column-wise median over the 9 runs (each column its own
median; the medians of the parts do not sum to the median of N by design).

All arithmetic is done EXACTLY on rationals (fractions.Fraction): h = 31*N/3600,
h+4, h+16 and (18-h)/4 are exact, and only the final quantisation to 2 decimals
uses Decimal ROUND_HALF_UP on the exact rational. This means a true tie such as
(18 - 4.34)/4 = 3.415 (run 5) prints as 3.42, matching the paper, and no binary
float representation error can flip a half-up decision for any N.
"""
from __future__ import annotations
import statistics as st
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

TEX = "sections/04-setup-and-evaluation.tex"

# (paper run, tex line, printed row) -- transcribed verbatim from the .tex
ROWS = [
    (1, 462, "285 (830); 5 (5000); 61 (1200); 31 (9300); 382; 3.29; 7.29; 19.29; 3.68"),
    (2, 465, "52 (850); 13 (5000); 4 (1200); 62 (9300); 131; 1.13; 5.13; 17.13; 4.22"),
    (3, 468, "163 (850); 7 (4000); 12 (1200); 78 (9300); 260; 2.24; 6.24; 18.24; 3.94"),
    (4, 471, "8 (850); 11 (4000); 10 (1200); 123 (9900); 152; 1.31; 5.31; 17.31; 4.17"),
    (5, 474, "178 (1500); 17 (4100); 142 (1200); 167 (4800); 504; 4.34; 8.34; 20.34; 3.42"),
    (6, 477, "324 (1400); 10 (4100); 251 (1200); 185 (4800); 770; 6.63; 10.63; 22.63; 2.84"),
    (7, 480, "11 (1900); 10 (4800); 24 (1300); 166 (4800); 211; 1.82; 5.82; 17.82; 4.05"),
    (8, 483, "8 (1900); 53 (4800); 6 (1300); 193 (4800); 260; 2.24; 6.24; 18.24; 3.94"),
    (9, 486, "10 (2000); 4 (4800); 3 (1300); 84 (4400); 101; 0.87; 4.87; 16.87; 4.28"),
]
MEDIAN_LINE = 491
MEDIAN_PAPER = "52; 10; 12; 123; 260; 2.24; 6.24; 18.24; 3.94"
LIFETIME_H = Fraction(18)      # HS descriptor lifetime used for v_max = (18 - h)/4
V_MAX_DIVISOR = Fraction(4)
SECONDS_PER_HOUR = 3600


def _seconds_per_iter(C) -> int:
    """core.SECONDS_PER_ITER as an exact integer (it is 31.0; assert integral)."""
    spi = C.SECONDS_PER_ITER
    assert float(spi).is_integer(), f"SECONDS_PER_ITER={spi!r} is not integral"
    return int(spi)


def exact_hours(C, N: int) -> Fraction:
    """Exact rational h = N * SECONDS_PER_ITER / 3600 (no float arithmetic)."""
    return Fraction(N * _seconds_per_iter(C), SECONDS_PER_HOUR)


def r2(fr) -> str:
    """Quantise an exact rational to 2 decimals with ROUND_HALF_UP, paper-style."""
    fr = Fraction(fr)
    d = Decimal(fr.numerator) / Decimal(fr.denominator)
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _row_values(C, traj, metrics, rid):
    """Return (tconv dict, cw dict, N, h) for raw run rid, purely from data.

    h is an exact Fraction; it is also cross-checked against core.hours(N)
    (float) to make sure the two never drift apart beyond float error.
    """
    tconv, cw = {}, {}
    for s in C.STAGES:
        seq = traj[(rid, s)]
        t = C.T_conv(seq)
        tconv[s] = t
        cw[s] = int(float(metrics[(rid, s)]["consensus_weight"]))
    N = sum(tconv[s] for s in C.STAGES)
    h = exact_hours(C, N)
    assert abs(float(h) - C.hours(N)) < 1e-9, f"exact h {h} != core.hours({N})"
    return tconv, cw, N, h


def _fmt_row(C, tconv, cw, N, h: Fraction):
    cells = [f"{tconv[s]} ({cw[s]})" for s in C.STAGES]
    cells += [str(N), r2(h), r2(h + 4), r2(h + 16), r2((LIFETIME_H - h) / V_MAX_DIVISOR)]
    return "; ".join(cells)


def claims(C, traj, metrics):
    out = []
    per_run = {}
    for p, line, paper in ROWS:
        rid = p + 3
        tconv, cw, N, h = _row_values(C, traj, metrics, rid)
        per_run[rid] = (tconv, N, h)
        computed = _fmt_row(C, tconv, cw, N, h)
        notes = []
        # consistency: trajectory-derived T_conv == number of recorded trials
        for s in C.STAGES:
            if len(traj[(rid, s)]) != tconv[s]:
                notes.append(f"{s}: trajectory T_conv={tconv[s]}, len(seq)={len(traj[(rid, s)])}")
        status = "PASS" if computed == paper and not notes else "FAIL"
        note = (f"raw run {rid}; h={h} = {float(h):.6f} exact; v=1h/v=4h/v_max computed "
                f"exactly on rationals, then ROUND_HALF_UP to 2 dp.")
        if notes:
            note += " Inconsistency: " + "; ".join(notes)
        # Report any exact decimal tie (x*1000 is an odd multiple of 5) so the
        # half-up decision is visible rather than hidden (run 5: 3.415 -> 3.42).
        for lbl, x in (("h", h), ("h+4", h + 4), ("h+16", h + 16),
                       ("(18-h)/4", (LIFETIME_H - h) / V_MAX_DIVISOR)):
            if (x * 1000).denominator == 1 and (x * 1000).numerator % 10 == 5:
                note += f" {lbl} = {float(x)} is an exact tie: half-up -> {r2(x)}."
        out.append({"id": f"e2e-{p:03d}", "location": f"{TEX}:{line}",
                    "quote": f"Table tab:end_to_end row {p}", "paper": paper,
                    "computed": computed, "status": status, "note": note})

    # Median row: column-wise medians over the 9 runs (exact: statistics.median
    # on ints / Fractions never touches floats; n=9 is odd so no averaging).
    med_t = {s: st.median([per_run[r][0][s] for r in C.RUN_IDS]) for s in C.STAGES}
    med_N = st.median([per_run[r][1] for r in C.RUN_IDS])
    hs = [per_run[r][2] for r in C.RUN_IDS]            # exact Fractions
    med_h = st.median(hs)
    med_h1 = st.median([h + 4 for h in hs])
    med_h4 = st.median([h + 16 for h in hs])
    med_vmax = st.median([(LIFETIME_H - h) / V_MAX_DIVISOR for h in hs])

    def _int(x):
        x = Fraction(x)
        return str(x.numerator) if x.denominator == 1 else str(x)

    computed = "; ".join([_int(med_t[s]) for s in C.STAGES] +
                         [_int(med_N), r2(med_h), r2(med_h1), r2(med_h4), r2(med_vmax)])
    out.append({"id": "e2e-010", "location": f"{TEX}:{MEDIAN_LINE}",
                "quote": "Table tab:end_to_end Median row", "paper": MEDIAN_PAPER,
                "computed": computed,
                "status": "PASS" if computed == MEDIAN_PAPER else "FAIL",
                "note": "Column-wise medians over 9 runs (each column independently; "
                        "stage medians need not sum to median N). Odd n=9 so medians are "
                        "exact data values."})
    return out
