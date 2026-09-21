#!/usr/bin/env python3
"""Summarise [intro-rotation] activity in a tor notice.log.

An introduction point is identified by its AUTH KEY, not by the relay
fingerprint: a service keeps two descriptors (current and next time period)
at once, so the same relay can be two distinct introduction points with two
distinct auth keys, and their rotations are independent.
"""
import re, sys, datetime, statistics, collections

TS = re.compile(r'^(\w{3}) (\d{2}) (\d{2}):(\d{2}):(\d{2})\.\d+ \[(\w+)\] (.*)$')
YEAR = 2026
MONTHS = {m: i+1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
KIND = re.compile(r'\[intro-rotation\] ([A-Z]+)')
IP = re.compile(r'intro point (\$[0-9A-F]{40})')
AK = re.compile(r'[Aa]uth key (?:is still )?([A-Za-z0-9+/]{43})')

def parse(path, start=None, end=None):
    out = []
    for line in open(path, errors='replace'):
        m = TS.match(line)
        if not m:
            continue
        mon, day, h, mi, se, _lvl, msg = m.groups()
        t = datetime.datetime(YEAR, MONTHS[mon], int(day), int(h), int(mi), int(se))
        if start and t < start: continue
        if end and t > end: continue
        out.append((t, msg))
    return out

def report(path, label, start=None, end=None):
    all_ev = parse(path, start, end)
    ev = [(t, m) for t, m in all_ev if '[intro-rotation]' in m]
    if not ev:
        print(f"== {label}: no [intro-rotation] events found =="); return
    counts = collections.Counter(
        KIND.search(m).group(1) for _, m in ev if KIND.search(m))
    t0, t1 = all_ev[0][0], all_ev[-1][0]
    span = (t1 - t0).total_seconds()
    att, done = counts.get('START', 0), counts.get('SWAPPED', 0)

    print(f"== {label} ==")
    print(f"log                 : {path}")
    print(f"window              : {t0} .. {t1}   ({span:.0f} s = {span/60:.1f} min)")
    print()
    print(f"rebuilds attempted   (START)     : {att}")
    print(f"rebuilds completed   (SWAPPED)   : {done}")
    print(f"rebuilds LOST        (difference): {att-done}"
          + (f"   = {100.0*(att-done)/att:.1f}% of attempts" if att else ""))
    print(f"  of which abandoned on our deadline (ABANDONED) : {counts.get('ABANDONED',0)}")
    print(f"  of which the replacement died early (FAILED)   : {counts.get('FAILED',0)}")
    print(f"  interval fallback after max failures (BACKOFF) : {counts.get('BACKOFF',0)}")
    print(f"  ESTABLISHED (sanity: must equal SWAPPED)       : {counts.get('ESTABLISHED',0)}")
    print()

    # ---- per introduction point (auth key) ----
    swaps = collections.defaultdict(list)     # authkey -> [t]
    relay = {}                                # authkey -> relay fp
    gone  = collections.Counter()             # authkey -> swaps w/ old circ already gone
    for t, m in ev:
        k = KIND.search(m)
        if not k or k.group(1) != 'SWAPPED':
            continue
        a, r = AK.search(m), IP.search(m)
        if not a:
            continue
        swaps[a.group(1)].append(t)
        if r: relay[a.group(1)] = r.group(1)
        if 'already gone' in m: gone[a.group(1)] += 1

    print("Intervals between consecutive SWAPPED events, per introduction point")
    print("(an introduction point == one auth key; this is the number that shows")
    print(" whether the rotation period is driven by the configured parameter):")
    print()
    print(f"  {'auth key':45} {'relay':10} {'swaps':>5} {'min':>5} {'med':>7} {'max':>6} {'oldgone':>7}")
    alld = []
    for a in sorted(swaps, key=lambda x: -len(swaps[x])):
        ts, r = swaps[a], relay.get(a, '?')[1:9]
        if len(ts) < 2:
            print(f"  {a:45} {r:10} {len(ts):>5} {'-':>5} {'-':>7} {'-':>6} {gone[a]:>7}")
            continue
        d = [(b-x).total_seconds() for x, b in zip(ts, ts[1:])]
        alld += d
        print(f"  {a:45} {r:10} {len(ts):>5} {min(d):>5.0f} {statistics.median(d):>7.1f}"
              f" {max(d):>6.0f} {gone[a]:>7}")
    if alld:
        print()
        print(f"  pooled over all introduction points: n={len(alld)} "
              f"min={min(alld):.0f}s median={statistics.median(alld):.1f}s "
              f"max={max(alld):.0f}s mean={statistics.mean(alld):.1f}s")
        hist = collections.Counter(int(x) for x in alld)
        print("  interval histogram (seconds: count): "
              + ", ".join(f"{k}:{v}" for k, v in sorted(hist.items())))
    print()
    print(f"distinct introduction points (auth keys) that ever swapped: {len(swaps)}")
    print("  (a service keeps 2 descriptors x 3 intro points = 6 at a time)")

    # ---- intro point retirement / auth key stability ----
    print()
    print("Introduction point continuity:")
    retired = [m for _, m in all_ev if 'Removing' in m and 'intro' in m.lower()]
    print(f"  log lines about removing/retiring an intro point : {len(retired)}")
    for m in retired[:5]:
        print(f"    {m[:150]}")
    for a in sorted(swaps, key=lambda x: swaps[x][0]):
        ts = swaps[a]
        print(f"  {a}  relay {relay.get(a,'?')}  first swap {ts[0].time()}  "
              f"last swap {ts[-1].time()}  n={len(ts)}")
    print()

if __name__ == '__main__':
    a = sys.argv[1:]
    s = datetime.datetime.fromisoformat(a[2]) if len(a) > 2 and a[2] != '-' else None
    e = datetime.datetime.fromisoformat(a[3]) if len(a) > 3 and a[3] != '-' else None
    report(a[0], a[1], s, e)
