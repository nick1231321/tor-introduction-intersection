# Short-lived introduction circuits (`intro-path-rotation`)

Implementation and live test network for the mitigation in Section 5 of
*Attacks on Tor hidden services* ("Mitigation: Short-Lived Introduction
Circuits"): an onion service periodically **rebuilds the internal path** it
uses to reach each of its introduction points, while keeping the **same
introduction point** and the **same introduction auth key**, so the published
descriptor never changes and clients are never interrupted.

Everything in this document was actually run on this machine. Numbers are
measured, not estimated; the sections at the end say plainly what was *not*
done or *not* verified.

---

## 1. What this branch is

`intro-path-rotation` branches from **`33abc432ffff17a212771a696e9561366b47d5c9`**
("version: Bump version to 0.4.9.3-alpha-dev", 2025-09-16) — the **last pure
upstream commit** of this fork, i.e. the commit immediately *before* the first
intersection-attack experiment commit. None of the 15 experiment commits on
`main` are in this branch, deliberately: the mitigation is implemented against
clean upstream tor so it can be evaluated on its own, and so that the forced
relay selection, the hard-coded single intro point in `pick_needed_intro_points()`
and the deterministic client intro choice in `client_get_random_intro()` do not
interfere with the measurements.

`main` (`6893939d8`, the author's work) is untouched. Nothing has been pushed
anywhere: this branch, and the local chutney branch described in §5, exist only
on this machine.

Two commits sit on top of the base:

```
a7b9e6fa0  rotation-evidence: measurements from the running Chutney test network
9ce1470f1  hs-service: rotate the internal introduction circuit path periodically
33abc432f  version: Bump version to 0.4.9.3-alpha-dev      <- pure upstream base
```

`git diff 33abc432f` shows only this work.

## 2. What it changes, and why it is shaped this way

A rotation is nothing more than an `ESTABLISH_INTRO` cell, carrying the **same
auth key**, sent on a **fresh four-hop internal circuit**, answered by
`INTRO_ESTABLISHED`. There is no new cell type and no descriptor change: a relay
keys an introduction point by auth key, and `hs_circuitmap_register_impl()`
(`src/feature/hs/hs_circuitmap.c:143`) closes whatever circuit currently holds
that token when a new circuit registers it — "Kill old circuits with the same
token ... so that HSes and clients [can] reestablish killed circuits without
changing the HS token". So claiming the identity on a new circuit *is* the swap.

**Make before break.** The replacement circuit is built first, the identity is
claimed on it, and the introduction relay then drops the old circuit itself. The
service never closes the live circuit. If the replacement fails to build or
never establishes, the old circuit simply keeps serving.

That design runs into two things in upstream tor, both handled:

* **Obstacle 1 — service-side registration happens at launch.**
  `hs_circ_launch_intro_point()` calls `register_intro_circ()` immediately after
  `circuit_launch_by_extend_info()`, i.e. long before the circuit is usable.
  With the same auth key that registration would trip the duplicate-token kill
  above and close the *live* circuit while the replacement was still building —
  break before make. Fix: `hs_circ_launch_intro_point()` takes a new
  `bool is_rotation` argument; when set, the circuit is launched but **not**
  registered, and is marked with `hs_ident->is_intro_rotation`. Registration
  moves to `service_handle_intro_established()`, via the new
  `hs_circ_service_register_intro_circ()` — the moment `INTRO_ESTABLISHED`
  actually arrives. Both circuits are alive during the overlap.
  This is safe because `INTRO_ESTABLISHED` dispatch resolves the service and the
  intro point through `get_objects_from_ident()` → `service_intro_point_find()`
  on the descriptor maps, **not** through the circuitmap, so an unregistered
  replacement circuit is still recognised when its answer comes back.

* **Obstacle 2 — retry accounting.** `ip->circuit_retries` increments on every
  launch, and `should_remove_intro_point()` retires the intro point once it
  exceeds `MAX_INTRO_POINT_CIRCUIT_RETRIES` (3, `src/core/or/or.h:1079`) —
  which would change the descriptor after three rotations. Handled twice over:
  a rotation launch never touches `circuit_retries` at all, and (only when the
  option is enabled) a successful `INTRO_ESTABLISHED` resets it to 1, so an
  earlier run of genuine failures cannot accumulate across rotations. It is
  reset to 1 rather than 0 because `hs_circ_launch_intro_point()` carries
  `tor_assert_nonfatal(ip->circuit_retries > 0)`.

* **A third hazard, found during implementation and not in the original design.**
  `hs_circ_service_intro_has_opened()` repurposes a freshly opened intro circuit
  to `GENERAL` when the number of open intro circuits exceeds
  `num_intro_points`, and its caller then frees the intro point — changing the
  descriptor. Because the service launches spare intro points
  (`get_intro_point_num_extra()`), a rotation circuit opening can transiently
  push that count over the limit. The repurpose branch is now guarded by
  `&& !circ->hs_ident->is_intro_rotation`.

The timer is `run_intro_circuit_rotation()`, called from
`run_housekeeping_event()` (once per second, per service) *after*
`cleanup_intro_points()` and `remove_expired_failing_intro()` so the intro point
maps are settled. It rotates an intro point whose circuit has been established
for at least the configured interval, allows only one replacement in flight per
intro point, and abandons a replacement that has not established within
`HS_SERVICE_INTRO_ROTATION_TIMEOUT` (120 s) and retries next cycle. It returns
immediately for single onion services, which have no internal path to rebuild.

Files touched (`git show --stat 9ce1470f1`): 11 files, +407/−9 —
`hs_service.c` (+245), `hs_circuit.c` (+77), `hs_service.h`, `hs_circuit.h`,
`hs_config.c/.h`, `hs_ident.h`, `hs_options.inc`, `config.c`,
`doc/man/tor.1.txt`, `changes/ticket_intro_circuit_rotation`.

## 3. Prerequisites and build (macOS)

Homebrew packages: `openssl@3`, `libevent`, `autoconf`, `automake`, `libtool`,
`pkg-config`. For chutney (§5) also `python@3.11`.

```sh
brew install openssl@3 libevent autoconf automake libtool pkg-config python@3.11
```

Build, exactly as used here:

```sh
cd /Users/nicolasconstantinides/Downloads/tor-intro-rotation
git checkout intro-path-rotation
./autogen.sh
./configure --with-openssl-dir=$(brew --prefix openssl@3) \
            --with-libevent-dir=$(brew --prefix libevent) \
            --disable-asciidoc
make -j$(sysctl -n hw.ncpu)
```

Roughly 3 s + 37 s + 13 s on this machine; 971 compilation units, **0 errors,
0 warnings**. The binary is `src/app/tor` and reports:

```
Tor version 0.4.9.3-alpha-dev (git-33abc432ffff17a2).
```

(The embedded hash is the *base* commit; that is normal, it comes from the last
upstream commit recorded at configure time.)

Tests:

```sh
./src/test/test hs_service/..     # 23 tests ok. (0 skipped)
./src/test/test                   # 1509 tests, 1 failure (see below)
make check-spaces                 # clean
```

The single full-suite failure is `util/monotonic_time_add_msec`
(`src/test/test_util.c:6644`, macOS coarse-clock granularity). It was verified
to fail identically on the untouched base commit with all changes stashed, 3
runs out of 3. It is not caused by this work.

If you ever build the author's `main` instead, note that
`hs_service/build_update_descriptors` segfaults there via `node_get_by_nickname`
at `hs_service.c:2430` — that is the experiment code's forced-intro block, and
it is one of the reasons this branch starts from upstream.

## 4. The torrc option

```
HiddenServiceIntroCircuitRotation NUM
```

Per hidden service (it goes in the `HiddenServiceDir` block, like
`HiddenServiceNumIntroductionPoints`).

* `NUM` is **seconds** between rebuilds of an intro circuit's internal path.
* `0` disables the feature and is the **default**. With `0` the code path is
  fully inert: `run_intro_circuit_rotation()` returns immediately, no
  `circuit_retries` reset happens, and launches pass `is_rotation=false`, so
  upstream behaviour is unchanged.
* Any other value must be between **30 and 86400**; anything else is a config
  error:
  `HiddenServiceIntroCircuitRotation must be between 30 and 86400, not 10.`
* No effect on single onion services.
* Documented in `doc/man/tor.1.txt` next to `HiddenServiceNumIntroductionPoints`.

Check it exists:

```sh
./src/app/tor --list-torrc-options | grep IntroCircuitRotation
./src/app/tor --verify-config -f /path/to/torrc
```

Log lines it produces, all `[notice]`, all prefixed `[intro-rotation]`:

| line | what it tells you |
|---|---|
| `Service introduction circuit rotation enabled: ... every N seconds` | at startup, the feature is on |
| `START` | a rotation begins: intro point `$fingerprint`, auth key, current circuit id, its age, the interval, the rotation number |
| `BUILDING` | the replacement circuit id and its full four-hop path; notes that it is deliberately unregistered |
| `ESTABLISHED` | `INTRO_ESTABLISHED` arrived on the replacement; its established path |
| `SWAPPED` | the new circuit now serves the intro point; the old circuit, and the auth key repeated |
| `... did not establish within 120 seconds` | replacement abandoned, old circuit keeps serving, retry next cycle |

**The auth key printed in START, ESTABLISHED and SWAPPED is identical** — that
is the evidence, from the log alone, that the descriptor identity did not change
across the path change.

> **Note:** `HiddenServiceNumIntroductionPoints 1` is **rejected** by upstream
> tor (its lower bound is `NUM_INTRO_POINTS_DEFAULT` = 3). Leave it at 3 and
> follow one intro point in the logs. Do not "fix" that bound to work around it.

## 5. The Chutney test network

### 5.1 What is on the machine right now

**A network is running and rotating; you can look at it without setting anything
up.** 11 tor processes (4 dir authorities, 5 relays, 1 client, 1 onion service)
plus one small HTTP server behind the onion service.

| | |
|---|---|
| onion address | `xk335k6vqeexv3qpnn3jlvlbee4vcgp3lccmiusq5qem3wpxmr6cu7yd.onion` |
| onion port | `5858` → `127.0.0.1:4747` |
| client SOCKS | `127.0.0.1:9009` (node `009c`) |
| service node | `010h` |
| rotation period | `HiddenServiceIntroCircuitRotation 120` |
| chutney clone | `/Users/nicolasconstantinides/Downloads/chutney` |
| node data dirs | `/Users/nicolasconstantinides/Downloads/chutney/net/nodes` (symlink to `net/nodes.1789922797`) |

Try it:

```sh
curl --socks5-hostname 127.0.0.1:9009 \
  http://xk335k6vqeexv3qpnn3jlvlbee4vcgp3lccmiusq5qem3wpxmr6cu7yd.onion:5858/
# -> intro-rotation test network: hello from the onion service

# watch rotations arrive, live (one cycle every 120 s, 6 intro points each)
tail -f /Users/nicolasconstantinides/Downloads/chutney/net/nodes/010h/notice.log \
  | grep --line-buffered "intro-rotation"
```

The backend web server is a throwaway python script that lives in a
**session-scoped temp directory** and will disappear when that directory is
cleaned. If it is gone, any HTTP server on `127.0.0.1:4747` will do:

```sh
cd /tmp && printf 'intro-rotation test network: hello\n' > index.html
python3 -m http.server 4747 --bind 127.0.0.1 &
```

### 5.2 Cold start: building the network from nothing

Two local fixes were required before chutney worked at all on this machine.
Both are already applied in the clone above (branch `intro-rotation-local`,
commit `d54e31f`, local only). If you start from a fresh chutney clone you must
redo them.

```sh
git clone https://gitlab.torproject.org/tpo/core/chutney \
          /Users/nicolasconstantinides/Downloads/chutney
cd /Users/nicolasconstantinides/Downloads/chutney
```

**(a) Python.** chutney requires Python >= 3.11.2 with dependencies
(`cryptography`, `networkx`, `paramiko`, `rpyc`, `typeguard`, `tomli-w`);
macOS system python3 is 3.9.6.

```sh
/opt/homebrew/bin/python3.11 -m venv .venv
.venv/bin/pip install -e .
echo '.venv/' >> .git/info/exclude
```

Every chutney command below is therefore prefixed `PYTHON=.venv/bin/python3` —
**this is required**, because the `./chutney` wrapper otherwise picks
`/usr/bin/python3` (3.9), which lacks the dependencies.

**(b) chutney's launcher is Linux-only.** `lib/chutney/launcher.py::_closerange()`
iterates `/proc/self/fd`, which does not exist on macOS, so *every* node dies
instantly with `FileNotFoundError: '/proc/self/fd'` and `chutney bootstrap`
fails with "Some nodes couldn't start". This is a chutney portability bug,
nothing to do with the tor patch. Patch it to fall back to `/dev/fd`:

```python
    # in _closerange(), replacing:  for fd_s in os.listdir("/proc/self/fd"):
    fd_dir = None
    for candidate in ("/proc/self/fd", "/dev/fd"):
        if os.path.isdir(candidate):
            fd_dir = candidate
            break
    if fd_dir is None:
        import resource
        soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        os.closerange(start, min(end, soft) + 1)
        return
    for fd_s in os.listdir(fd_dir):
```

**(c) The network template.** No stock chutney network enables the option, so
this one was written; it is the stock `hs-v3` network plus one raw torrc line on
the onion service node. Save as
`lib/chutney/data/networks/hs-v3-rotation` (reachable as `networks/hs-v3-rotation`,
since `networks` is a symlink):

```python
# Seconds between rotations of an intro circuit's internal path.
# 0 disables the feature; otherwise it must be between 30 and 86400.
INTRO_CIRCUIT_ROTATION = 120

Authority = Node(tag="a", authority=1, relay=1)
ExitRelay = Node(tag="r", relay=1, exit=1)
Client    = Node(tag="c", client=1, launch_phase=2)
HS = Node(
    tag="h",
    hs=1,
    launch_phase=2,
    extra_raw_torrc=(
        "\n# --- introduction circuit path rotation (mitigation under test) ---\n"
        f"HiddenServiceIntroCircuitRotation {INTRO_CIRCUIT_ROTATION}\n"
    ),
)

# We need 5 authorities/relays/exits to ensure we can build HS connections
NODES = Authority.getN(4) + ExitRelay.getN(5) + Client.getN(1) + HS.getN(1)

ConfigureNodes(NODES)
```

### 5.3 Start, check, watch, stop

All from `/Users/nicolasconstantinides/Downloads/chutney`.

```sh
# create a FRESH network (new onion address; makes net/nodes.<timestamp>)
PYTHON=.venv/bin/python3 ./chutney init \
  --net-from-script-path networks/hs-v3-rotation \
  --tor          /Users/nicolasconstantinides/Downloads/tor-intro-rotation/src/app/tor \
  --tor-gencert  /Users/nicolasconstantinides/Downloads/tor-intro-rotation/src/tools/tor-gencert

# start it (on its own, this REUSES the existing keys and keeps the onion address)
PYTHON=.venv/bin/python3 ./chutney bootstrap

# is it up?
PYTHON=.venv/bin/python3 ./chutney status
PYTHON=.venv/bin/python3 ./chutney verify      # expect: successes:4 failures:0

# the onion address
cat net/nodes/010h/hidden_service/hostname

# stop everything
PYTHON=.venv/bin/python3 ./chutney stop
```

> `chutney verify` binds the hidden service's target port itself, so **stop the
> demo web server on 4747 first** (`pkill -f 'http.server 4747'`), otherwise
> verify dies with `[Errno 48] ... bind on address ('127.0.0.1', 4747): address
> already in use`.

> `init` changes the onion address. `bootstrap` alone does not.

Watching a rotation happen:

```sh
L=net/nodes/010h/notice.log

# the feature is on
grep "rotation enabled" $L

# every rotation, start to finish
grep "\[intro-rotation\]" $L

# attempted vs completed
grep -c "intro-rotation\] START"   $L
grep -c "intro-rotation\] SWAPPED" $L

# the auth key never changes
grep "\[intro-rotation\]" $L | grep -oE "auth key [A-Za-z0-9+/]+" | sort | uniq -c

# nobody was retired by the 3-retry cap
grep -icE "remov(e|ing) .*intro|retir|MAX_INTRO" $L

# who tore the old circuit down (info.log): every close is at the DESTROY-cell
# handler, i.e. the introduction relay did it, not the service
grep "command.c:682" net/nodes/010h/info.log
```

**Timing:** the first rotation fires one interval *after the intro circuits
establish*, i.e. roughly 2.5 minutes after bootstrap at a 120 s period. A cycle
rotates all 6 intro points (3 for the current descriptor + 3 for the next one)
within about 25 ms.

**Comparison run with the feature off:** set `INTRO_CIRCUIT_ROTATION = 0` in the
template, then `init` + `bootstrap` again. (For the cost measurement in §7 the
faster route was used instead: edit `net/nodes/010h/torrc` in place, kill and
restart just that node, which keeps the onion address; remember to rewrite
`010h/pid` with the new pid, because chutney's `status`/`stop` read it.)

## 6. Where the evidence lives

`rotation-evidence/` in this repo, committed as `a7b9e6fa0`. Its own
`rotation-evidence/README.md` is the index: headline table, the
fingerprint→nickname map for the test relays, per-file descriptions,
re-derivation commands, and a "things this evidence does not claim" section.

| file | what it shows |
|---|---|
| `01-paths-per-auth-key.txt` | every rotation's four-hop path, grouped by auth key, diffed hop by hop against that intro point's previous rotation |
| `01-intro-circuits-{BEFORE,AFTER}-2002.txt` | independent control-port (`GETINFO circuit-status`) cross-check, bracketing one cycle |
| `01-circuits-service-2000-after-cycle.txt` | an earlier control-port snapshot (named honestly: it is an *after*, not a before) |
| `02-identity-unchanged.txt` | auth key constant; descriptor unchanged; nothing retired by the retry cap; why the number of distinct auth keys grows over time |
| `02-desc-client-{BEFORE,AFTER}-2002.txt` | the descriptor the **client** fetched, around a rotation — byte-identical |
| `02-desc-service-{BEFORE,AFTER}-2002.txt`, `02-desc-*-T1-2000.txt` | the service-side dumps at the same moments |
| `02-desc-CONTROL-no-rotation.txt` | control test: two service-side dumps 3 s apart with **no** rotation also differ, because the service re-encrypts and re-signs per read |
| `03-continuity.txt`, `03-continuity-curl.log` | 75 client fetches across a rotation, per-probe timestamps and exit codes |
| `04-cost.txt`, `04-cost-rotation-{ON,OFF}.txt` | intro circuits built in a fixed 360 s window, option on vs off, raw `CIRC` events included |
| `05-make-before-break.txt` | who actually closes the old circuit, and why the `SWAPPED` line usually says "the previous circuit was already gone" |
| `logs/notice.log.rotation-ON`, `logs/info.log.rotation-ON.gz`, `logs/info.log.rotation-ON.relevant-lines.txt`, `logs/notice.log.rotation-OFF` | the raw service logs both runs were derived from |

## 7. What was measured

All from the live network above, with the patched binary. Nothing simulated.

| claim | measured |
|---|---|
| the internal path is rebuilt | 38 consecutive rotations compared; a new circuit every time, and at least one middle hop differed in **26 of 38** |
| the entry guard does not change | **0 of 38** |
| the introduction point does not change | **0 of 38** |
| the auth key does not change | constant across every START / ESTABLISHED / SWAPPED, every intro point, to rotation depth **#8** |
| the published descriptor does not change | client-fetched descriptor **byte-identical** across a rotation (sha256 `2b2ee871…`); revision counter unmoved on both sides |
| obstacle 2 is actually clear | rotation depth 8 against a cap of 3, **0** intro points retired |
| clients are not interrupted | 75 fetches every 2 s across a swap: **74 succeeded**; the 1 failure was 69 s away from any rotation; **0** introductions lost at a swap |
| make before break holds | **14/14** intro-circuit closes carried `REMOTE_REASON=DESTROYED` — the introduction relay closed them, the service closed none |
| cost, rotation on (120 s, 6 intro points) | **18** introduction circuits in 360 s (3 cycles × 6) = 180/hour |
| cost, rotation off (0) | **0** introduction circuits in 360 s |

In short: one extra four-hop circuit per introduction point per period, in
exchange for the internal path never living longer than that period — which is
exactly what the intersection observation in the paper needs in order to
accumulate.

## 8. Known limitations, and what was not done

These matter more than the table above; none of them are hidden in the evidence
files either.

1. **12 of 38 rotations re-picked an identical path.** The test network has 5
   relays; with hop 1 pinned to the guard and hop 4 to the introduction point,
   hops 2–3 are drawn from about 3 candidates, so an independent re-selection
   often lands on the same pair. The circuit is genuinely rebuilt every time
   (new circuit id, new ESTABLISH_INTRO). This is a property of a small test
   network, not of the patch — but it means the *unlinkability* benefit was not
   measured here, only the rebuild.
2. **Some rotation attempts do not complete** (1 observed in one log, 4 more in
   the 360 s cost window). The replacement hits tor's adaptive circuit-build
   timeout, tor converts it into a build-time measurement circuit
   (`circuit_build_times_mark_circ_as_measurement_only()`,
   `circuitstats.c:636`) and closes it at `circuitbuild.c:1112`. The cycle is
   simply skipped, the old circuit keeps serving, and the next cycle retries.
   No outage resulted, but the effective rotation period is therefore slightly
   longer than the configured one on a loaded network.
3. **The `SWAPPED` log line usually says "the previous circuit was already
   gone"** (58 of 61 lines in one run) instead of naming the old circuit id.
   That is because the relay's DESTROY for the old circuit arrives and
   unregisters it a few milliseconds *before* the service processes
   `INTRO_ESTABLISHED`, so the lookup at swap time is already NULL. The
   behaviour is correct — that is the duplicate-token kill doing its job — but
   the message is weaker than intended. **Not fixed.** The one-line fix is to
   stash the old circuit id into the intro point struct at START and print that
   at SWAPPED.
4. **`GETINFO hs/service/desc` cannot be diffed naively** — the service
   re-encodes and re-signs the descriptor on every read, so two reads differ
   whether or not anything rotated. Only the revision counter and the
   client-side `GETINFO hs/client/desc` are used as evidence.
   `02-desc-CONTROL-no-rotation.txt` is the control test for this.
5. **The number of distinct auth keys grows** (6 → 12 during the run). That is
   tor's own `rotate_all_descriptors` building the next time period's
   descriptor with three fresh intro points, not a rotation side effect; it was
   traced to the two rotate events in the log. The three current-descriptor
   auth keys never changed.
6. **Per-rotation "old circuit closed N ms after the replacement established"
   was attempted and abandoned.** The rotation log prints the wire circuit id
   while `circuit_mark_for_close_` prints the internal id (wire id already
   cleared), and six circuits launch within ~2 ms of each other, so matching the
   two id spaces by timestamp is ambiguous — a first attempt produced an
   obviously wrong 120-second row. The remote-vs-local claim needs no matching
   and stands; the timing table does not exist.
7. **Only tested on this private 5-relay chutney network, on macOS, with one
   service and 120 s.** Not tested against the real Tor network, not tested with
   vanguards enabled (these circuits are plain 4-hop internal circuits,
   `BUILD_FLAGS=IS_INTERNAL,NEED_UPTIME`), not tested with a single onion
   service (the code early-returns for those, which was read but not exercised),
   not tested with client authorization, and not tested across a tor restart.
8. **No unit test was added** for the rotation logic. The existing suites still
   pass (`hs_service/..` 23/23), but nothing new covers
   `run_intro_circuit_rotation()` directly.
9. **The measurement tooling is not committed.** The control-port client,
   circuit-event counter, snapshot and continuity-probe scripts used in §7 live
   in a session-scoped temp directory and will be cleaned up. The evidence files
   they produced are committed, and `rotation-evidence/README.md` lists the
   plain `grep` commands that re-derive the headline numbers from the logs.
10. **A correction to an earlier note in this work:** circuit close reason
    `523` is `END_CIRC_REASON_FLAG_REMOTE | END_CIRC_REASON_DESTROYED`
    (512 + 11), not `... | FINISHED` (that would be 521, and it also appears).
    Both are remote closes, which is the point; `rotation-evidence/README.md`
    still carries the older wording in one comment.

## 9. Hard rules, as followed

* The author's branches were never touched, rebased or deleted. `main` is still
  `6893939d8`.
* **Nothing was pushed.** No `git push`, no `git reset --hard` on the author's
  branches, no force flags. The chutney work is on a local-only branch too.
* The paper directory `/Users/nicolasconstantinides/Downloads/Attacks_on_Tor_hidden_services (11)`
  was not modified.

## 10. Branch log

```
a7b9e6fa0  rotation-evidence: measurements from the running Chutney test network
9ce1470f1  hs-service: rotate the internal introduction circuit path periodically
33abc432f  version: Bump version to 0.4.9.3-alpha-dev      (pure upstream base)
602c51658  Merge branch 'maint-0.4.8'
cea0ec283  version: Bump version to 0.4.8.18-dev
```

(plus this file, committed on top.)
