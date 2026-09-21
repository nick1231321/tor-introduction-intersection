#!/usr/bin/env python3
"""For a tor info.log that also carries the [intro-rotation] notices, decide
what happened to every replacement ("rotation") introduction circuit.

A rotation circuit's global identifier is taken from the origin_circuit_new
line that immediately precedes its BUILDING notice (hs_circ_launch_intro_point
logs BUILDING right after circuit_launch_by_extend_info created the circuit).
That is what lets us join the notice log, which prints the WIRE circuit id,
to the info log, which prints the GLOBAL one.
"""
import re, sys, collections

def main(path):
    gid = None
    wire2gid, built, est = {}, {}, set()
    deciding, expire_marked = set(), set()
    for line in open(path, errors='replace'):
        m = re.search(r'origin_circuit_new: Circuit (\d+) chose', line)
        if m: gid = m.group(1); continue
        m = re.search(r'\[intro-rotation\] BUILDING replacement circuit (\d+)', line)
        if m:
            wire2gid[m.group(1)] = gid; built[m.group(1)] = line[:19]; continue
        m = re.search(r'\[intro-rotation\] ESTABLISHED .* on replacement circuit (\d+)', line)
        if m: est.add(m.group(1)); continue
        m = re.search(r'Deciding to timeout circuit (\d+)', line)
        if m: deciding.add(m.group(1)); continue
        m = re.search(r'Deciding to count the timeout for circuit (\d+)', line)
        if m: expire_marked.add(m.group(1))

    lost = [w for w in built if w not in est]
    ok   = [w for w in built if w in est]
    print(f"log: {path}")
    print(f"replacement introduction circuits launched : {len(built)}")
    print(f"  established (rebuild completed)          : {len(ok)}")
    print(f"  never established (rebuild lost)         : {len(lost)}")
    print()
    print("Where the adaptive circuit build timeout would have taken them:")
    print(f"  'Deciding to timeout circuit N' lines, all circuits   : "
          f"{len(deciding)} distinct circuits")
    print(f"    (circuit_build_times_handle_completed_hop(), circuitstats.c)")
    print(f"  'Deciding to count the timeout for circuit N', all    : "
          f"{len(expire_marked)} distinct circuits")
    print(f"    (circuit_expire_building(), circuituse.c)")
    print()
    hit  = sum(1 for w in lost if wire2gid[w] in deciding or wire2gid[w] in expire_marked)
    hit2 = sum(1 for w in ok   if wire2gid[w] in deciding or wire2gid[w] in expire_marked)
    print(f"  LOST rebuilds whose circuit the timeout claimed       : {hit} / {len(lost)}")
    print(f"  COMPLETED rebuilds whose circuit the timeout claimed  : {hit2} / {len(ok)}")
    print()
    tim = re.compile(r'circuit_build_times_set_timeout: Set circuit build timeout to (\d+)ms')
    vals = []
    for line in open(path, errors='replace'):
        m = tim.search(line)
        if m: vals.append(int(m.group(1)))
    if vals:
        print(f"adaptive circuit build timeout on this network: "
              f"{min(vals)}..{max(vals)} ms over {len(vals)} updates "
              f"(last: {vals[-1]} ms)")
    if lost:
        print()
        print("first 10 lost rebuilds (time, wire id, global id, claimed by timeout?):")
        for w in sorted(lost, key=lambda x: built[x])[:10]:
            g = wire2gid[w]
            print(f"  {built[w]}  wire={w:>10}  gid={g:>6}  "
                  f"{'yes' if (g in deciding or g in expire_marked) else 'no'}")

main(sys.argv[1])
