"""Checks for the appendix run/stage table (tab:run-stage-thresholds).

Covers sections/appendix_results.tex lines 26-77: the 36 per-run/per-stage
rows (app-002..app-037) and the whole tabular body against generate.py's
output (app-body, reported as a digest "<n> lines, sha1 <12 hex>" of the
whitespace-normalised body lines on both sides).

Without the paper sources the module still emits the data side of all 36
rows (same ids, same order) and the generated-body digest, with status FAIL
and the note "paper sources not available"; verify.py's reviewer mode then
compares them with claims_snapshot.json.

The "paper" side of every row claim is PARSED FROM THE CURRENT .tex LINE
(not from a transcription): each row is split on '&', the IP row's
"Rp (Day d, HH:MM)" prefix gives the run number, day label and start time,
the stage cell must match the expected stage label, and the remaining seven
cells must be integers (|A_1|, T<=10, T<=5, T<=3, T<=2, T_conv, CW).
The TABLE dict below is kept only as a secondary guard: if the parsed row
differs from it (or fails to parse), the claim FAILs with a
"transcription stale" note so a silent edit of the .tex cannot pass.

The "computed" side: every T column plus |A_1| is recomputed from the raw
trajectory TRAJ[(p+3, s)] (T<=q = min t with |I_t| <= q; |A_1| = |I_1|;
T_conv = T<=1) and CW comes from run_stage_metrics.csv MET[(p+3, s)]
consensus_weight.  The IP row's day label and start time come from the IP
row's day_label / experiment_time_utc columns of MET (a stage's own row gives
that stage's start day and time; the run is labelled by its IP-stage start).
The released metrics file carries no precomputed convergence columns, so the
trajectory-derived values are the only source for the T columns.

Every printed value is compared as an exact integer (the table prints
integers), except Day/time which are compared as strings.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import core as _core   # shared tex helpers (single copy in core.py)

FILE = "sections/appendix_results.tex"
TABLE_LABEL = r"\label{tab:run-stage-thresholds}"
STAGE_LABEL = {"IP": "Intro. Point", "M1": "Middle 1",
               "VG": "Vanguard", "EG": "Entry Guard"}
QS = [10, 5, 3, 2]
COLS = ["|A1|", "T<=10", "T<=5", "T<=3", "T<=2", "Tconv", "CW"]

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
    """'HH:MM' from the experiment_time_utc column ('HH:MM UTC'; minute resolution)."""
    t = (row.get("experiment_time_utc") or "").strip()
    return t.split()[0][:5] if t else ""


def _day_label(row: dict) -> str:
    return (row.get("day_label") or "").strip()


def _run_day_time(metrics, rid: int):
    """(Day label, HH:MM) of run `rid` = day_label / experiment_time_utc of its
    IP-stage row (the run is labelled by the start of its first stage)."""
    m = metrics[(rid, "IP")]
    return _day_label(m), _hhmm_label(m)


def _computed_row(C, traj, metrics, rid: int, s: str):
    """The seven integer cells of a printed row: |A_1|, T<=10, T<=5, T<=3,
    T<=2 and T_conv from the trajectory, CW from the metrics row."""
    seq = traj[(rid, s)]
    return ([C.initial_set_size(seq)] + [C.T_le(seq, q) for q in QS] +
            [C.T_conv(seq), _fmt_cw(metrics[(rid, s)]["consensus_weight"])])


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


def _table_body(lines):
    """(first line no, [(line no, text)] of the active body) of
    tab:run-stage-thresholds: the non-blank lines strictly between the header's
    \\midrule and \\bottomrule, or (None, None) if the table cannot be located."""
    if lines is None:
        return None, None
    lab = next((i for i, l in enumerate(lines, 1) if TABLE_LABEL in l), None)
    if lab is None:
        return None, None
    mid = next((i for i in range(lab, len(lines) + 1) if lines[i - 1].strip().startswith(r"\midrule")), None)
    bot = next((i for i in range(lab, len(lines) + 1) if lines[i - 1].strip().startswith(r"\bottomrule")), None)
    if mid is None or bot is None or bot <= mid:
        return None, None
    body = [(i, lines[i - 1].strip()) for i in range(mid + 1, bot) if lines[i - 1].strip()]
    return mid + 1, body


def _row_lines(body):
    """{(paper run, stage): line no} of the printed rows, located in the CURRENT
    table body: an 'Rp (...)' row starts run p (IP), the following non-run rows
    are its M1, VG, EG rows in order. Rows that are not data rows (\\midrule
    separators) are skipped."""
    found, p, k = {}, None, 0
    for ln, txt in body or []:
        if not txt.endswith("\\\\"):
            continue
        first = txt.split("&", 1)[0].strip()
        m = _IP_RE.match(first)
        if m:
            p, k = int(m.group(1)), 0
        elif first != "" or p is None:
            continue
        else:
            k += 1
        if k < len(STAGE_LABEL):
            found[(p, list(STAGE_LABEL)[k])] = ln
    return found


def _generate():
    """Import the generator (it loads the data itself; figures are not drawn)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import generate  # noqa: E402
    return generate


def body_digest(lines):
    """'<n> lines, sha1 <12 hex>' of a tabular body: the non-blank lines,
    whitespace-normalised, joined by newlines."""
    norm = [_core.norm_ws(l) for l in lines if _core.norm_ws(l)]
    h = hashlib.sha1("\n".join(norm).encode("utf-8")).hexdigest()[:12]
    return f"{len(norm)} lines, sha1 {h}"


def generated_digest(traj, metrics):
    return body_digest(_generate().thresholds_body(traj, metrics).splitlines())


def claims(C, traj, metrics) -> list[dict]:
    out = []
    lines = _tex_lines()

    # ---- app-002..app-037: one claim per table row, in paper order (run-major, stage order)
    # Each row is located in the CURRENT table body (run label + stage order);
    # the TABLE line is only the fallback anchor.
    body_line, body = _table_body(lines)
    row_at = _row_lines(body)
    cid = 2
    for p in range(1, 10):
        rid = p + 3
        for s in C.STAGES:
            reg_line, g_day, g_hhmm, *g_nums = TABLE[(p, s)]
            line = row_at.get((p, s), reg_line)
            quote = _quote(lines, line)
            comp = _computed_row(C, traj, metrics, rid, s)
            comp_parts = []
            note_parts = []
            status = "PASS"
            if (p, s) not in row_at and lines is not None:
                note_parts.append(f"row not located in the current table body; registered "
                                  f"line {reg_line} read instead")
            elif line != reg_line:
                note_parts.append(f"[moved from {FILE}:{reg_line}]")

            # -- paper side: parsed from the current .tex line
            try:
                day, hhmm, paper_nums = _parse_row(quote, p, s)
                parse_err = None
            except ValueError as e:
                day, hhmm, paper_nums = None, None, None
                parse_err = str(e)

            if parse_err is not None:
                status = "FAIL"
                if lines is None:
                    note_parts.append("paper sources not available")
                else:
                    note_parts.append(f"transcription stale: tex row on line {line} "
                                      f"failed to parse ({parse_err})")
                paper_str = quote or "n/a"
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
                comp_day, comp_time = _run_day_time(metrics, rid)
                comp_parts.append(f"{comp_day} {comp_time} (IP row day_label / experiment_time_utc)")
                if parse_err is None and (comp_day != day or comp_time != hhmm):
                    status = "FAIL"
                    note_parts.append(f"Day/time: paper '{day} {hhmm}' vs computed "
                                      f"'{comp_day} {comp_time}'")
            comp_parts += [str(v) for v in comp]

            note_parts.append(f"printed row parsed from {FILE}:{line}; |A_1| and T columns "
                              f"derived from TRAJ ({rid},{s}), CW from MET")
            if parse_err is None and comp != paper_nums:
                status = "FAIL"
                diffs = [f"{name}: paper {pv} vs computed {cv}"
                         for name, pv, cv in zip(COLS, paper_nums, comp) if pv != cv]
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

    # ---- app-body: the whole tabular body equals generate.py's output (modulo
    #      whitespace); both sides reported as a digest of the normalised body lines
    gen_digest = generated_digest(traj, metrics)
    if body is None:
        out.append({"id": "app-body", "location": f"{FILE}:?", "quote": TABLE_LABEL,
                    "paper": "n/a", "computed": gen_digest, "status": "FAIL",
                    "note": ("paper sources not available" if lines is None else
                             "tab:run-stage-thresholds body (\\midrule .. \\bottomrule) not found")})
        return out
    gen_body = [l.strip() for l in _generate().thresholds_body(traj, metrics).splitlines() if l.strip()]
    norm_tex = [_core.norm_ws(l) for _, l in body]
    norm_gen = [_core.norm_ws(l) for l in gen_body]
    diffs = [f"body line {i + 1}: tex {a!r} vs generate.py {b!r}"
             for i, (a, b) in enumerate(zip(norm_tex, norm_gen)) if a != b]
    if len(norm_tex) != len(norm_gen):
        diffs.append(f"{len(norm_tex)} tex body lines vs {len(norm_gen)} generated")
    tex_digest = body_digest(l for _, l in body)
    same = not diffs and tex_digest == gen_digest
    out.append({"id": "app-body", "location": f"{FILE}:{body_line}", "quote": TABLE_LABEL,
                "paper": tex_digest,
                "computed": gen_digest,
                "status": "PASS" if same else "FAIL",
                "note": ("tabular body of tab:run-stage-thresholds equals "
                         "repro/out/tables/run_stage_thresholds_body.tex (make tables) modulo whitespace"
                         if same else
                         "tabular body differs from generate.py output; run `make tables` and paste "
                         "out/tables/run_stage_thresholds_body.tex into the table. "
                         + "; ".join(diffs[:6]))})
    return out
