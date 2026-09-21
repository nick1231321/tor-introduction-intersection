# Rotation evidence

Raw evidence that `HiddenServiceIntroCircuitRotation` does what the mitigation in
Section 5 of the paper ("Mitigation: Short-Lived Introduction Circuits") claims:
the onion service periodically rebuilds the **internal path** it uses to reach each
introduction point, while keeping the **same introduction point** and the **same
introduction auth key**, so the published descriptor never changes and clients are
never interrupted.

Everything here was captured from the live private Chutney network described in
`../README.md`, running the patched tor built from this tree at commit `9ce1470f1`.
Nothing here is simulated, reconstructed or estimated.


## Headline results

| claim | measured | file |
|---|---|---|
| the internal path changes | 38 consecutive rotations compared; a middle hop changed in 26, and the path was genuinely rebuilt in all 38 (new circuit each time) | `01-paths-per-auth-key.txt` |
| the entry guard does not change | 0 of 38 | `01-paths-per-auth-key.txt` |
| the introduction point does not change | 0 of 38 | `01-paths-per-auth-key.txt` |
| the auth key does not change | constant across every START / ESTABLISHED / SWAPPED, for every intro point, up to rotation #8 | `02-identity-unchanged.txt` |
| the descriptor does not change | client-fetched descriptor byte-identical across a rotation; revision counter unmoved | `02-identity-unchanged.txt` |
| no intro point retired by the 3-retry cap | rotation depth reached 8, cap is 3, 0 retirements | `02-identity-unchanged.txt` |
| clients are not interrupted | 75 fetches across a rotation: 74 succeeded, 1 failed 69 s away from any swap; 0 introductions lost at a swap | `03-continuity.txt` |
| the service never closes the live circuit | every intro-circuit close carried `REMOTE_REASON=DESTROYED` — the relay did it | `05-make-before-break.txt` |
| cost, rotation on | 18 intro circuits launched in 360 s (3 cycles x 6 intro points) | `04-cost.txt` |
| cost, rotation off | 0 intro circuits launched in 360 s | `04-cost.txt` |
| **the rotation period is the configured one** | rebuilds lost 14.2% -> 3.0%; interval max 480 s -> 121 s, mean 133.9 s -> 120.1 s, with 120 s configured | `06-rotation-period.txt` |

## The network these were taken from

| | |
|---|---|
| onion service | `xk335k6vqeexv3qpnn3jlvlbee4vcgp3lccmiusq5qem3wpxmr6cu7yd.onion:5858` |
| service node | `010h` (`/Users/nicolasconstantinides/Downloads/chutney/net/nodes/010h`) |
| client SOCKS | `127.0.0.1:9009` (node `009c`) |
| relays | `test004r`..`test008r` (5 relays, 4 dir auths) |
| rotation period | `HiddenServiceIntroCircuitRotation 120` |
| intro points | 3 for the current descriptor + 3 for the next one = 6 live at a time |

Relay fingerprint → nickname, used throughout:

```
F4F171D168A4E696805AB4248B119422A690B1D7  test004r   (this is also the service's entry guard)
95C37B1AC2F4587F039D174B52C2532A14EEBD40  test005r
1EA3B6AA5EBFD0EE36A41FEC3FE8188B0F4C3E6F  test006r
C9B264516E54A7B0598012DF992ABB985924B0AB  test007r
D7F2E6732DAEA3AF70F62A7F3DCBF6CFA0CFB3E3  test008r
```

## Files

| file | what it is |
|---|---|
| `01-paths-per-auth-key.txt` | **Claim 1.** Every rotation's four-hop path, grouped by auth key, with a hop-by-hop diff against the previous rotation of the same intro point. |
| `01-intro-circuits-BEFORE-2002.txt`, `01-intro-circuits-AFTER-2002.txt` | Independent cross-check of claim 1 from the control port (`GETINFO circuit-status`), captured 8 s before and 12 s after the 20:02:13 cycle. |
| `01-circuits-service-2000-after-cycle.txt` | An earlier control-port snapshot, taken 5 s *after* the 20:00:13 cycle. Kept and named honestly: it is not a "before". |
| `02-identity-unchanged.txt` | **Claim 2.** Auth keys constant; why the number of distinct keys grows (tor's own time-period rotation, not this patch); no intro point retired despite the 3-retry cap; descriptor byte-identical across a rotation. |
| `02-desc-service-BEFORE-2002.txt`, `02-desc-service-AFTER-2002.txt` | Service-side descriptor dumps around the 20:02:13 cycle. |
| `02-desc-client-BEFORE-2002.txt`, `02-desc-client-AFTER-2002.txt` | The descriptor **the client actually fetched**, same two moments. These are byte-identical. |
| `02-desc-service-T1-2000.txt`, `02-desc-client-T1-2000.txt` | An earlier descriptor pair (20:00:18), kept for a second data point on the revision counter. |
| `02-desc-CONTROL-no-rotation.txt` | Control experiment: two service-side dumps 3 s apart with **no** rotation in between also differ in ciphertext and signature. This is why only the revision counter and the client-side dump are treated as evidence. |
| `03-continuity.txt` | **Claim 3.** Success/failure counts for a client fetching across a rotation, plus the one rotation attempt that did not complete and what it cost (nothing). |
| `03-continuity-curl.log` | Raw per-probe log behind `03-continuity.txt`: 75 probes, timestamps, curl exit codes, response bodies. |
| `04-cost.txt` | **Claim 4.** Intro circuits built in a fixed 360 s window with rotation on and with rotation off. |
| `04-cost-rotation-ON.txt`, `04-cost-rotation-OFF.txt` | Raw control-port `CIRC` event counts behind `04-cost.txt`, including every raw event line. |
| `05-make-before-break.txt` | **Supporting.** Who actually tears the old circuit down, and why the `SWAPPED` line usually says "the previous circuit was already gone". |
| `logs/notice.log.rotation-ON` | The service's notice log for the whole rotation-on run. Most claims above are derived from this. |
| `logs/info.log.rotation-ON.gz` | The matching info log, gzipped (1.6 MB raw). |
| `logs/info.log.rotation-ON.relevant-lines.txt` | The same info log filtered to the lines the evidence cites (rotation, descriptor, circuit-close). |
| `logs/notice.log.rotation-OFF` | The service's notice log for the rotation-off comparison run. Contains zero `intro-rotation` lines, which is the point. |
| `06-rotation-period.txt` | **Claim 6.** Before/after the adaptive-circuit-build-timeout fix: rebuilds attempted vs completed, why the lost ones were lost (traced circuit by circuit), and the distribution of real intervals between consecutive swaps. |
| `rotation-interval-stats.py` | Script behind 6a, 6c and 6e: counts rotation events in a notice log and prints the interval distribution per introduction point (keyed by auth key). |
| `rotation-timeout-correlate.py` | Script behind 6b: joins the `[intro-rotation]` notices to the info log's circuit-build-timeout decisions and says which rebuilds the timeout claimed. |
| `logs/notice.log.period-BEFORE.gz` | Service notice log for the 17-hour run BEFORE the fix (commit `b63417722`). |
| `logs/notice.log.period-AFTER` | Service notice log for the 73.5-minute run AFTER the fix (commit `f68858718`). |
| `logs/info.log.period-BEFORE.timeout-lines.txt.gz` | The BEFORE info log filtered to the circuit-build-timeout and intro-point-removal lines that 6b cites. |
| `logs/info.log.period-AFTER.relevant-lines.txt.gz` | The AFTER info log filtered to the rotation, timeout, descriptor-rotation and circuit-creation lines that 6b and 6d cite. |

## How to re-derive the headline numbers

```sh
L=/Users/nicolasconstantinides/Downloads/chutney/net/nodes/010h/notice.log   # or logs/notice.log.rotation-ON

# every rotation, start to finish
grep "\[intro-rotation\]" "$L"

# rotations attempted vs rotations completed
grep -c "intro-rotation\] START"   "$L"
grep -c "intro-rotation\] SWAPPED" "$L"

# the auth key never changes
grep "\[intro-rotation\]" "$L" | grep -oE "auth key [A-Za-z0-9+/]+" | sort | uniq -c

# how deep rotation got per intro point (the 3-retry cap would have stopped it at 3)
grep "intro-rotation\] START" "$L" | grep -oE "rotation #[0-9]+" | sort -t'#' -k2 -n | uniq -c

# no intro point was ever retired
grep -icE "remov(e|ing) .*intro|retir|MAX_INTRO" "$L"

# the intro relay, not the service, tears the old circuit down
#   reason 523 = END_CIRC_REASON_FLAG_REMOTE|END_CIRC_REASON_FINISHED
grep "command.c:682" /Users/nicolasconstantinides/Downloads/chutney/net/nodes/010h/info.log
```

## Things this evidence does not claim

These are stated in full in the individual files; collected here so they are not missed.

1. **12 of 38 consecutive rotations re-picked an identical path.** This network has 5
   relays; with hop 1 pinned to the guard and hop 4 pinned to the intro point, hops 2
   and 3 come from a pool of ~3. The circuit is genuinely rebuilt every time (new
   circuit id every time), but on a 5-relay network a fresh draw often lands on the
   same middles. This is a property of the test network, not of the patch.
2. **The service-side descriptor dump changes across any two reads**, rotation or not,
   because it is re-encoded and re-signed per read. Only the revision counter and the
   client-fetched descriptor are used as evidence of "unchanged".
3. **Some rotation attempts do not complete.** One was caught in the log at 20:02:17, and
   4 more in the 360 s cost window. The cause is traced in `03-continuity.txt`: the
   replacement circuit hits tor's adaptive circuit-build timeout while building, and tor
   converts it into a build-time measurement circuit. None caused an outage — the old
   circuit was still serving — and the next cycle retried successfully.
   **This has since been fixed** (commit `f68858718`) and re-measured: see
   `06-rotation-period.txt`. Everything in files 1–5 was collected before that fix, so
   the loss rate it describes is the pre-fix one.
4. The cost comparison restarts the service node to flip the option. The measurement
   window in both cases starts after the service has settled, so neither number
   includes the initial burst of intro-circuit builds at startup.

## State of the network after this was collected

The comparison run in `04-cost.txt` required restarting the onion service node with the
option set to `0`. That was undone afterwards: `010h/torrc` was restored byte-identically
to its original (verified with `diff` against a backup), the node was restarted, and the
network was left running with `HiddenServiceIntroCircuitRotation 120` and rotating
normally. Verified at 20:23:43:

```
Service introduction circuit rotation enabled: the internal path to each introduction
point will be rebuilt every 120 seconds, keeping the same introduction point and
authentication key.

live introduction circuits : 6
tor nodes running          : 11
curl through client SOCKS  : "intro-rotation test network: hello from the onion service"
```

The onion address is unchanged (`xk335k6...cu7yd.onion`) because the service keys live on
disk and only that one node was restarted; the other ten nodes never stopped.
