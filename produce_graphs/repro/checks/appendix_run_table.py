"""Checks for the appendix run/stage table (tab:run-stage-thresholds).

Covers sections/appendix_results.tex lines 16-17 and 26-77: the column
definitions (app-001) and the 36 per-run/per-stage rows (app-002..app-037).

The "paper" side of every row claim is PARSED FROM THE CURRENT .tex LINE
(not from a transcription): each row is split on '&', the IP row's
"Rp (Day d, HH:MM)" prefix gives the run number, day label and start time,
the stage cell must match the expected stage label, and the remaining seven
cells must be integers (|A_1|, T<=10, T<=5, T<=3, T<=2, T_conv, CW).
The TABLE dict below is kept only as a secondary guard: if the parsed row
differs from it (or fails to parse), the claim FAILs with a
"transcription stale" note so a silent edit of the .tex cannot pass.

The "computed" side comes from run_stage_metrics.csv MET[(p+3, s)] and every
T column plus |A_1| is independently recomputed from the raw trajectory
TRAJ[(p+3, s)] (T<=q = min t with |I_t| <= q; |A_1| = |I_1|).  The IP row's
day label and start time are DERIVED FROM started_at_utc (Day N = 1 + days
since the earliest IP start over all runs; HH:MM = the timestamp's hour and
minute) and must also agree with the pre-labelled day_label /
experiment_time_utc columns.

Every printed value is compared as an exact integer (the table prints
integers), except Day/time which are compared as strings.
"""
from __future__ import annotations

import re
from datetime import date

import core as _core   # shared tex helpers (single copy in core.py)

FILE = "sections/appendix_results.tex"
STAGE_LABEL = {"IP": "Intro. Point", "M1": "Middle 1",
               "VG": "Vanguard", "EG": "Entry Guard"}
QS = [10, 5, 3, 2]
COLS = ["|A1|", "T<=10", "T<=5", "T<=3", "T<=2", "Tconv", "CW"]

# Definition lines (app-001) that must still be present in the current .tex.
DEF_LINES = {
    16: r"$T_{\leq q}=\min\{t:|\mathcal{I}_t|\leq q\}$;",
    17: r"$T_{\mathrm{conv}}=\min\{t:|\mathcal{I}_t|=1\}$; and",
}

# Secondary guard only (NOT the paper side): (paper_run, stage) ->
# (line, day, time, A1, T10, T5, T3, T2, Tconv, CW); day/time only on IP rows.
TABLE = {
    (1, "IP"): (26, "Day 1", "02:00", 79, 3, 4, 42, 245, 285, 830),
    (1, "M1"): (27, None, None, 137, 3, 3, 4, 5, 5, 5000),
    (1, "VG"): (28, None, None, 112, 2, 61, 61, 61, 61, 1200),
    (1, "EG"): (29, None, None, 218, 8, 16, 16, 31, 31, 9300),
    (2, "IP"): (32, "Day 1", "10:00", 101, 2, 3, 9, 52, 52, 850),
    (2, "M1"): (33, None, None, 192, 4, 5, 7, 13, 13, 5000),
    (2, "VG"): (34, None, None, 76, 3, 3, 3, 3, 4, 1200),
    (2, "EG"): (35, None, None, 284, 10, 17, 17, 21, 62, 9300),
    (3, "IP"): (38, "Day 1", "18:00", 74, 3, 9, 11, 163, 163, 850),
    (3, "M1"): (39, None, None, 129, 3, 5, 6, 7, 7, 4000),
    (3, "VG"): (40, None, None, 85, 2, 2, 4, 12, 12, 1200),
    (3, "EG"): (41, None, None, 249, 11, 25, 26, 26, 78, 9300),
    (4, "IP"): (44, "Day 2", "02:00", 81, 3, 4, 4, 4, 8, 850),
    (4, "M1"): (45, None, None, 148, 4, 7, 8, 8, 11, 4000),
    (4, "VG"): (46, None, None, 107, 3, 5, 5, 6, 10, 1200),
    (4, "EG"): (47, None, None, 256, 13, 21, 45, 49, 123, 9900),
    (5, "IP"): (50, "Day 2", "10:00", 101, 6, 11, 30, 178, 178, 1500),
    (5, "M1"): (51, None, None, 158, 6, 10, 13, 16, 17, 4100),
    (5, "VG"): (52, None, None, 148, 38, 60, 61, 76, 142, 1200),
    (5, "EG"): (53, None, None, 180, 7, 11, 14, 15, 167, 4800),
    (6, "IP"): (56, "Day 2", "18:00", 84, 3, 14, 233, 324, 324, 1400),
    (6, "M1"): (57, None, None, 147, 3, 4, 9, 10, 10, 4100),
    (6, "VG"): (58, None, None, 161, 11, 19, 49, 66, 251, 1200),
    (6, "EG"): (59, None, None, 98, 7, 14, 23, 177, 185, 4800),
    (7, "IP"): (62, "Day 3", "18:00", 75, 3, 4, 4, 4, 11, 1900),
    (7, "M1"): (63, None, None, 164, 4, 6, 7, 9, 10, 4800),
    (7, "VG"): (64, None, None, 95, 3, 3, 6, 20, 24, 1300),
    (7, "EG"): (65, None, None, 212, 14, 21, 73, 166, 166, 4800),
    (8, "IP"): (68, "Day 4", "02:00", 91, 3, 5, 6, 6, 8, 1900),
    (8, "M1"): (69, None, None, 198, 7, 11, 14, 14, 53, 4800),
    (8, "VG"): (70, None, None, 89, 3, 3, 4, 4, 6, 1300),
    (8, "EG"): (71, None, None, 191, 16, 28, 62, 62, 193, 4800),
    (9, "IP"): (74, "Day 4", "10:00", 50, 2, 2, 3, 6, 10, 2000),
    (9, "M1"): (75, None, None, 90, 2, 3, 3, 3, 4, 4800),
    (9, "VG"): (76, None, None, 48, 2, 2, 3, 3, 3, 1300),
    (9, "EG"): (77, None, None, 86, 5, 18, 40, 40, 84, 4400),
}

_IP_RE = re.compile(r"^R(\d+)\s*\((Day \d+),\s*(\d\d:\d\d)\)$")


def _fmt_cw(x: str) -> int:
    """consensus_weight is stored as a numeric string; the table prints an int."""
    return int(round(float(x)))


def _hhmm_label(row: dict) -> str:
    """'HH:MM' from the pre-labelled experiment_time_utc column ('HH:MM UTC')."""
    t = (row.get("experiment_time_utc") or "").strip()
    return t.split()[0][:5] if t else ""


def _start_date(row: dict) -> date:
    return date.fromisoformat(row["started_at_utc"][:10])


def _derived_day_time(C, metrics, rid: int):
    """(Day label, HH:MM) derived purely from started_at_utc of the IP stage.

    Day 1 is the calendar date (UTC) of the earliest IP start over all runs.
    All IP starts are within a few seconds of the hour, so HH:MM truncation
    of the timestamp is exact.
    """
    d0 = min(_start_date(metrics[(r, "IP")]) for r in C.RUN_IDS)
    m = metrics[(rid, "IP")]
    day = f"Day {(_start_date(m) - d0).days + 1}"
    hhmm = m["started_at_utc"][11:16]
    return day, hhmm


def _computed_row(C, traj, metrics, rid: int, s: str):
    """Return (values from MET, values recomputed from TRAJ, cross-check ok?)."""
    m = metrics[(rid, s)]
    seq = traj[(rid, s)]
    met = [int(m["initial_intersection_size"])] + \
          [int(m[f"T_le_{q}"]) for q in QS] + \
          [int(m["trials_to_convergence"]), _fmt_cw(m["consensus_weight"])]
    trj = [C.initial_set_size(seq)] + [C.T_le(seq, q) for q in QS] + [C.T_conv(seq)]
    # CW is not derivable from the trajectory; compare the first 6 entries only
    xcheck = met[:6] == trj and int(m["T_le_1"]) == trj[5]
    return met, trj, xcheck


def _tex_lines() -> list[str] | None:
    """Current (comment-stripped) lines of the appendix, line numbers preserved."""
    return _core.tex_lines(FILE)


def _quote(lines, line_no: int) -> str:
    if lines is None or line_no < 1 or line_no > len(lines):
        return ""
    return lines[line_no - 1].strip()


def _parse_row(quote: str, p: int, s: str):
    """Parse a printed table row into (day, hhmm, [7 ints]) or raise ValueError.

    Format: '[Rp (Day d, HH:MM)] & <stage label> & A1 & T10 & T5 & T3 & T2 & Tconv & CW \\\\'
    """
    if not quote:
        raise ValueError("empty/unreadable .tex line")
    body = quote.strip()
    if not body.endswith("\\\\"):
        raise ValueError("row does not end with '\\\\'")
    body = body[:-2]
    cells = [c.strip() for c in body.split("&")]
    if len(cells) != 9:
        raise ValueError(f"expected 9 cells, got {len(cells)}")
    day = hhmm = None
    if s == "IP":
        mo = _IP_RE.match(cells[0])
        if not mo:
            raise ValueError(f"IP row prefix {cells[0]!r} does not match 'Rp (Day d, HH:MM)'")
        if int(mo.group(1)) != p:
            raise ValueError(f"run number R{mo.group(1)} != expected R{p}")
        day, hhmm = mo.group(2), mo.group(3)
    else:
        if cells[0] != "":
            raise ValueError(f"non-IP row has a non-empty run cell {cells[0]!r}")
    if cells[1] != STAGE_LABEL[s]:
        raise ValueError(f"stage label {cells[1]!r} != {STAGE_LABEL[s]!r}")
    try:
        nums = [int(x) for x in cells[2:]]
    except ValueError as e:
        raise ValueError(f"non-integer numeric cell: {e}")
    if len(nums) != 7:
        raise ValueError(f"expected 7 numeric cells, got {len(nums)}")
    return day, hhmm, nums


def claims(C, traj, metrics) -> list[dict]:
    out = []
    lines = _tex_lines()

    # ---- app-001: column definitions / consistency of MET with TRAJ over all 36 rows
    n_ok = 0
    mism = []
    for rid in C.RUN_IDS:
        for s in C.STAGES:
            m = metrics[(rid, s)]
            seq = traj[(rid, s)]
            ok = True
            for q in C.THRESHOLDS:            # 10,5,3,2,1
                if C.T_le(seq, q) != int(m[f"T_le_{q}"]):
                    ok = False
            if C.T_conv(seq) != int(m["trials_to_convergence"]) or \
               int(m["T_le_1"]) != int(m["trials_to_convergence"]):
                ok = False
            if C.initial_set_size(seq) != int(m["initial_intersection_size"]):
                ok = False
            n_ok += ok
            if not ok:
                mism.append(f"R{C.PAPER_RUN[rid]}/{s}")
    # the definitions must still be printed on lines 16-17 of the current .tex
    def_ok = True
    def_note = ""
    q16, q17 = _quote(lines, 16), _quote(lines, 17)
    if lines is None:
        def_ok = False
        def_note = "could not read the .tex file"
    else:
        missing = [str(n) for n, txt in DEF_LINES.items() if _quote(lines, n) != txt]
        if missing:
            def_ok = False
            def_note = ("definition text stale: line(s) " + ", ".join(missing) +
                        " no longer contain the expected T<=q / Tconv definitions")
    if lines is None:
        status = "UNVERIFIABLE"
    elif def_ok and n_ok == 36:
        status = "PASS"
    else:
        status = "FAIL"
    out.append({
        "id": "app-001",
        "location": f"{FILE}:16-17",
        "quote": (q16 + " " + q17).strip() or r"$T_{\leq q}=\min\{t:|\mathcal{I}_t|\leq q\}$;",
        "paper": "T<=q = min t with |I_t|<=q; Tconv = min t with |I_t|=1; 36 rows",
        "computed": f"{n_ok}/36 run-stage rows: TRAJ-derived T<=q (q in 10,5,3,2,1), "
                    f"Tconv and |A_1| equal MET columns"
                    + (f"; mismatches: {', '.join(mism)}" if mism else "")
                    + f"; definitions on lines 16-17 {'present' if def_ok else 'MISSING'}",
        "status": status,
        "note": "Definitional check: asserts lines 16-17 of the current .tex still carry "
                "the T<=q and Tconv definitions, then recomputes every threshold column "
                "from the raw trajectories and asserts agreement with run_stage_metrics.csv "
                "(T_le_q, trials_to_convergence == T_le_1, initial_intersection_size)."
                + (f" {def_note}" if def_note else ""),
    })

    # ---- app-002..app-037: one claim per table row, in paper order (run-major, stage order)
    cid = 2
    for p in range(1, 10):
        rid = p + 3
        for s in C.STAGES:
            line, g_day, g_hhmm, *g_nums = TABLE[(p, s)]
            quote = _quote(lines, line)
            met, trj, xcheck = _computed_row(C, traj, metrics, rid, s)
            m = metrics[(rid, s)]
            comp_parts = []
            note_parts = []
            status = "PASS"

            # -- paper side: parsed from the current .tex line
            try:
                day, hhmm, paper_nums = _parse_row(quote, p, s)
                parse_err = None
            except ValueError as e:
                day, hhmm, paper_nums = None, None, None
                parse_err = str(e)

            if parse_err is not None:
                if lines is None:
                    status = "UNVERIFIABLE"
                    note_parts.append(f"could not read {FILE}: {parse_err}")
                else:
                    status = "FAIL"
                    note_parts.append(f"transcription stale: tex row on line {line} "
                                      f"failed to parse ({parse_err})")
                paper_str = quote or "(unreadable)"
            else:
                if (day, hhmm, paper_nums) != (g_day, g_hhmm, list(g_nums)):
                    status = "FAIL"
                    note_parts.append("transcription stale: tex row differs from TABLE "
                                      f"(tex={day} {hhmm} {paper_nums}; "
                                      f"TABLE={g_day} {g_hhmm} {list(g_nums)})")
                paper_parts = ([f"{day} {hhmm}"] if s == "IP" else []) + \
                              [str(v) for v in paper_nums]
                paper_str = "; ".join(paper_parts)

            # -- computed side
            if s == "IP":
                comp_day, comp_time = _derived_day_time(C, metrics, rid)
                lab_day = m["day_label"].strip()
                lab_time = _hhmm_label(m)
                comp_parts.append(f"{comp_day} {comp_time} (from started_at_utc="
                                  f"{m['started_at_utc']}; labels: {lab_day} {lab_time})")
                if comp_day != lab_day or comp_time != lab_time:
                    if status != "UNVERIFIABLE":
                        status = "FAIL"
                    note_parts.append(f"started_at_utc-derived '{comp_day} {comp_time}' "
                                      f"disagrees with label columns '{lab_day} {lab_time}'")
                if parse_err is None and (comp_day != day or comp_time != hhmm):
                    status = "FAIL"
                    note_parts.append(f"Day/time: paper '{day} {hhmm}' vs computed "
                                      f"'{comp_day} {comp_time}'")
            comp_parts += [str(v) for v in met]

            note_parts.append(f"MET ({rid},{s}) vs printed row parsed from {FILE}:{line}; "
                              f"T columns and |A_1| cross-checked on TRAJ: "
                              f"{'agree' if xcheck else 'DISAGREE ' + str(trj)}")
            if not xcheck and status != "UNVERIFIABLE":
                status = "FAIL"
            if parse_err is None and met != paper_nums:
                status = "FAIL"
                diffs = [f"{name}: paper {pv} vs computed {cv}"
                         for name, pv, cv in zip(COLS, paper_nums, met) if pv != cv]
                note_parts.append("; ".join(diffs))

            out.append({
                "id": f"app-{cid:03d}",
                "location": f"{FILE}:{line}",
                "quote": quote,
                "paper": paper_str,
                "computed": "; ".join(comp_parts),
                "status": status,
                "note": "; ".join(note_parts),
            })
            cid += 1
    return out
