"""Checks for Table tab:stage-contrasts (sections/04-setup-and-evaluation.tex).

The table has two column groups per block (Introduction Point | Vanguard, then
Middle | Entry Guard); each tex line therefore carries two printed rows
"R{p} D{d} HH:MM & CW & |A~1| & T<=10 & T<=3 & T<=2 & Tconv".  The older
single-group spelling "R{p} (D{d}, HH:MM)" is also accepted.

Every printed row is parsed from the CURRENT active tex (comment blocks and
%-lines ignored) and recomputed from the data:
  * label: paper run p = raw run p+3; D{d}/HH:MM from the run's IP-stage row
    (ASSUMPTION: labels use the run start, not the stage start).
  * CW: consensus_weight for (run, stage) from run_stage_metrics.csv; |A~1| =
    seq[0]; T<=q = C.T_le(seq, q); Tconv = C.T_le(seq, 1), all from the trajectory.
  * row selection (contr-sel): the four runs shown per stage must be the ones
    generate.contrast_runs() picks (min, median, second-largest, max T_conv).
  * layout (contr-body): the whole tabular body must equal what generate.py
    emits, modulo whitespace, so `make tables` and the paper never drift.
Nothing computed is hard-coded.
"""
import re
import sys
from pathlib import Path

import core as _core

TEX = "sections/04-setup-and-evaluation.tex"
TABLE_LABEL = r"\label{tab:stage-contrasts}"
HEADER_TO_STAGE = {"Introduction Point": "IP", "Middle": "M1",
                   "Vanguard": "VG", "Entry Guard": "EG"}
_LABEL_RE = re.compile(r"R(\d+)\s*\(?\s*D(\d+),?\s*(\d\d:\d\d)\s*\)?")


def _generate():
    """Import the generator without running its module-level figure code twice."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import generate  # noqa: E402  (loads data itself; cheap)
    return generate


def _table_lines():
    lines = _core.tex_lines(TEX)
    if lines is None:
        return None, None, None
    active = [True] + [bool(l.strip()) for l in lines]
    lab = next((i for i, l in enumerate(lines, 1) if active[i] and TABLE_LABEL in l), None)
    if lab is None:
        return lines, None, None
    lo = next(i for i in range(lab, 0, -1) if active[i] and lines[i - 1].strip().startswith(r"\begin{table"))
    hi = next(i for i in range(lab, len(lines) + 1) if active[i] and lines[i - 1].strip().startswith(r"\end{table"))
    return lines, lo, hi


def _parse_table(lines, lo, hi):
    """Return (rows, body_lines): rows = [(lineno, stage, dict)], body_lines =
    the active tabular body lines between \\midrule after the header and
    \\bottomrule (for the layout comparison)."""
    rows, body, stages, in_body = [], [], None, False
    for i in range(lo, hi + 1):
        s = lines[i - 1].strip()
        if not s:
            continue
        if s.startswith(r"\multicolumn"):
            hdrs = re.findall(r"\\textit\{([^}]*)\}", s)
            stages = [HEADER_TO_STAGE.get(h) for h in hdrs]
            in_body = True
        if in_body and not s.startswith((r"\end{tabular}", r"\bottomrule", "}")):
            body.append(s)
        if s.startswith(r"\bottomrule"):
            in_body = False
        if not s.startswith("R") or stages is None:
            continue
        cells = [c.strip() for c in s.rstrip("\\").split("&")]
        if len(cells) % 7:
            raise ValueError(f"line {i}: {len(cells)} cells, expected a multiple of 7")
        for g in range(len(cells) // 7):
            c = cells[7 * g: 7 * g + 7]
            m = _LABEL_RE.match(c[0])
            if not m:
                raise ValueError(f"line {i}: cannot parse run label {c[0]!r}")
            rows.append((i, stages[g], dict(
                run=int(m.group(1)), day=int(m.group(2)), time=m.group(3),
                cw=int(c[1]), a1=int(c[2]), t10=int(c[3]), t3=int(c[4]),
                t2=int(c[5]), tconv=int(c[6]))))
    return rows, body


def _vals(d):
    return (f"R{d['run']}; D{d['day']} {d['time']}; {d['cw']}; {d['a1']}; "
            f"{d['t10']}; {d['t3']}; {d['t2']}; {d['tconv']}")


def claims(C, traj, metrics):
    out = []
    lines, lo, hi = _table_lines()
    gen = _generate()
    if lines is None or lo is None:
        # No paper sources: emit the data side of every row the generator would
        # print (same order as the table), so reviewer mode can replay them.
        k = 0
        for left, right in gen.CONTRAST_PAIRS:
            for rl, rr in zip(gen.contrast_runs(traj, left), gen.contrast_runs(traj, right)):
                for rid, stage in ((rl, left), (rr, right)):
                    k += 1
                    ip, met, seq = metrics[(rid, "IP")], metrics[(rid, stage)], traj[(rid, stage)]
                    comp = dict(run=C.PAPER_RUN[rid],
                                day=int(re.search(r"(\d+)", ip["day_label"]).group(1)),
                                time=re.search(r"(\d\d:\d\d)", ip["experiment_time_utc"]).group(1),
                                cw=int(float(met["consensus_weight"])), a1=C.initial_set_size(seq),
                                t10=C.T_le(seq, 10), t3=C.T_le(seq, 3), t2=C.T_le(seq, 2), tconv=C.T_conv(seq))
                    out.append(dict(id=f"contr-{k:03d}", location=TEX, quote="", paper="n/a",
                                    computed=_vals(comp), status="UNVERIFIABLE",
                                    note="paper sources not available"))
        for stage in C.STAGES:
            want = gen.contrast_runs(traj, stage)
            out.append(dict(id=f"contr-sel-{stage}", location=TEX, quote="", paper="n/a",
                            computed="R" + ",R".join(str(r - 3) for r in want),
                            status="UNVERIFIABLE", note="paper sources not available"))
        out.append(dict(id="contr-body", location=TEX, quote=TABLE_LABEL, paper="n/a",
                        computed="n/a", status="UNVERIFIABLE", note="active tab:stage-contrasts table not found"))
        return out
    try:
        rows, body = _parse_table(lines, lo, hi)
    except ValueError as e:
        out.append(dict(id="contr-body", location=f"{TEX}:{lo}", quote=TABLE_LABEL,
                        paper="n/a", computed="n/a", status="UNVERIFIABLE", note=str(e)))
        return out

    seen = {}
    for k, (lineno, stage, paper) in enumerate(rows, 1):
        cid = f"contr-{k:03d}"
        p = paper["run"]; rid = p + 3
        location = f"{TEX}:{lineno}"
        quote = f"R{p} D{paper['day']} {paper['time']} ({C.STAGE_NAME[stage]})"
        seen.setdefault(stage, []).append(rid)
        ip, met, seq = metrics.get((rid, "IP")), metrics.get((rid, stage)), traj.get((rid, stage))
        if ip is None or met is None or seq is None:
            out.append(dict(id=cid, location=location, quote=quote, paper=_vals(paper),
                            computed="n/a", status="UNVERIFIABLE",
                            note=f"missing data for raw run {rid} stage {stage}"))
            continue
        comp = dict(run=p,
                    day=int(re.search(r"(\d+)", ip["day_label"]).group(1)),
                    time=re.search(r"(\d\d:\d\d)", ip["experiment_time_utc"]).group(1),
                    cw=int(float(met["consensus_weight"])), a1=C.initial_set_size(seq),
                    t10=C.T_le(seq, 10), t3=C.T_le(seq, 3), t2=C.T_le(seq, 2),
                    tconv=C.T_conv(seq))
        notes = []
        sd = re.search(r"(\d+)", met["day_label"]); st_ = re.search(r"(\d\d:\d\d)", met["experiment_time_utc"])
        if (int(sd.group(1)), st_.group(1)) != (comp["day"], comp["time"]):
            notes.append(f"label uses run start D{comp['day']} {comp['time']}; stage started "
                         f"D{sd.group(1)} {st_.group(1)}")
        mism = [f"{kk}: paper {paper[kk]} vs computed {comp[kk]}"
                for kk in ("day", "time", "cw", "a1", "t10", "t3", "t2", "tconv") if paper[kk] != comp[kk]]
        note = f"{C.STAGE_NAME[stage]} of paper run {p} (raw run {rid}). "
        if mism:
            note += "MISMATCH: " + "; ".join(mism) + ". "
        if notes:
            note += "; ".join(notes) + "."
        out.append(dict(id=cid, location=location, quote=quote, paper=_vals(paper),
                        computed=_vals(comp), status="FAIL" if mism else "PASS", note=note.strip()))

    # row selection per stage must match the generator's rule
    for stage in C.STAGES:
        want = gen.contrast_runs(traj, stage)
        got = seen.get(stage, [])
        out.append(dict(id=f"contr-sel-{stage}", location=f"{TEX}:{lo}",
                        quote=f"rows shown for {C.STAGE_NAME[stage]}",
                        paper="R" + ",R".join(str(r - 3) for r in got),
                        computed="R" + ",R".join(str(r - 3) for r in want),
                        status="PASS" if got == want else "FAIL",
                        note="representative rows = runs with min, median, second-largest and "
                             "max T_conv (ties -> lowest run), in that order (generate.contrast_runs)"))

    # whole body must equal generate.py output (modulo whitespace)
    gen_body = [l.strip() for l in gen.stage_contrasts_body(traj, metrics).splitlines() if l.strip()]
    same = [_core.norm_ws(l) for l in body] == [_core.norm_ws(l) for l in gen_body]
    out.append(dict(id="contr-body", location=f"{TEX}:{lo}", quote=TABLE_LABEL,
                    paper=f"{len(body)} body lines", computed=f"{len(gen_body)} body lines from generate.py",
                    status="PASS" if same else "FAIL",
                    note="tabular body of tab:stage-contrasts equals repro/out/tables/stage_contrasts_body.tex "
                         "(make tables) modulo whitespace" if same else
                         "tabular body differs from generate.py output; run `make tables` and paste "
                         "out/tables/stage_contrasts_body.tex into the table"))
    return out
