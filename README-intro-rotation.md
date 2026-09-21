# Short-Lived Introduction Circuits

This repository contains a modification of Tor that periodically rebuilds the
internal path of an onion service's introduction circuit while keeping the same
Introduction Point, together with a private test network that demonstrates it.
It accompanies the mitigation proposed in *Deanonymizing Onion Services Through
Long-Lived Introduction Circuits*.

An onion service keeps an introduction circuit to each of its Introduction
Points for 18–24 hours. Every introduction handshake sent through a given
Introduction Point traverses the same service-side relays for that whole period,
which is what allows an adversary observing one relay at a time to reconstruct
the path hop by hop. The modification bounds that exposure: the service rebuilds
the internal path on a configurable interval, so no path is reused for longer
than that interval, while the Introduction Point, the descriptor and the onion
address stay unchanged.

---

## 1. What the modification does

A rebuild is an `ESTABLISH_INTRO` cell carrying the **same auth key**, sent on a
**fresh four-hop internal circuit** and answered by `INTRO_ESTABLISHED`. No new
cell type is introduced and the descriptor does not change. A relay keys an
Introduction Point by auth key, and `hs_circuitmap_register_impl()`
(`src/feature/hs/hs_circuitmap.c`) closes whatever circuit currently holds that
token when a new circuit registers it:

> "Kill old circuits with the same token … so that HSes and clients [can]
> reestablish killed circuits without changing the HS token."

Claiming the identity on a new circuit is therefore itself the swap, and the
mechanism is the one Tor already uses to recover a failed introduction circuit.

**Make before break.** The replacement circuit is built first, the identity is
claimed on it, and the Introduction Point then drops the old circuit. The
service never closes the live circuit itself. If the replacement fails to build
or never establishes, the old circuit keeps serving introductions.

Three properties of upstream Tor have to be accommodated.

**Registration happens at launch.** `hs_circ_launch_intro_point()` registers a
new introduction circuit immediately after `circuit_launch_by_extend_info()`,
long before the circuit is usable. With the same auth key, that registration
would trigger the duplicate-token close above and tear down the *live* circuit
while the replacement was still building, which is break-before-make.
`hs_circ_launch_intro_point()` therefore takes an `is_rotation` argument: a
rotation circuit is launched but not registered, and is marked in its
`hs_ident`. Registration moves to `service_handle_intro_established()`, the
moment `INTRO_ESTABLISHED` arrives, so both circuits are alive during the
overlap. This is sound because `INTRO_ESTABLISHED` dispatch resolves the service
and the Introduction Point through the descriptor maps rather than the circuit
map, so an unregistered replacement is still recognised when its answer returns.

**Retry accounting.** `ip->circuit_retries` increments on every launch, and
`should_remove_intro_point()` retires an Introduction Point once it exceeds
`MAX_INTRO_POINT_CIRCUIT_RETRIES` (3), which would change the descriptor after
three rebuilds. A rotation launch does not touch the counter, and a successful
`INTRO_ESTABLISHED` resets it, so genuine earlier failures cannot accumulate
across rebuilds.

**Spare introduction circuits.** `hs_circ_service_intro_has_opened()` repurposes
a freshly opened introduction circuit to `GENERAL` when the number of open
introduction circuits exceeds `num_intro_points`, and the caller then frees the
Introduction Point, changing the descriptor. Because the service launches spare
Introduction Points, a rotation circuit opening can transiently exceed that
limit, so the repurpose branch excludes rotation circuits.

The scheduler, `run_intro_circuit_rotation()`, runs from
`run_housekeeping_event()` once per second per service, after the Introduction
Point maps have settled. It rebuilds the path of any Introduction Point whose
circuit has been established for at least the configured interval, and allows
one replacement in flight per Introduction Point. Single onion services have no
internal path and are excluded.

So that the period follows the configured value and nothing else, a replacement
circuit is exempt from Tor's adaptive circuit-build timeout, in both places that
can convert a building circuit into a measurement-only one
(`circuit_expire_building()` and `circuit_build_times_handle_completed_hop()`).
The exemption is keyed on the `is_intro_rotation` flag, which is only ever set
when the option is enabled, and on the service-side establish-intro purpose, so
no other circuit is affected and the timeout is still learned as usual. The
service applies its own bound instead: a replacement that has not answered
`INTRO_ESTABLISHED` within half the configured interval, clamped to 30-120
seconds, is abandoned and closed, and a new attempt starts on the next
housekeeping tick one second later rather than a whole interval later. Three
consecutive failures on one Introduction Point fall back to one attempt per
interval, so this cannot spin.

---

## 2. Configuration

```
HiddenServiceIntroCircuitRotation NUM
```

Set per service, inside the `HiddenServiceDir` block.

* `NUM` is the number of **seconds** between rebuilds of an introduction
  circuit's internal path.
* `0` disables the feature and is the **default**. Behaviour is then identical
  to upstream: the scheduler returns immediately, the retry counter is not
  touched, and circuits are launched exactly as before.
* Any other value must lie between **30 and 86400**; other values are rejected
  at startup.
* The option has no effect on single onion services.

To confirm the binary supports it:

```sh
./src/app/tor --list-torrc-options | grep IntroCircuitRotation
./src/app/tor --verify-config -f /path/to/torrc
```

Every rebuild is logged at notice level with the prefix `[intro-rotation]`:

| line | meaning |
|---|---|
| `... rotation enabled: ... every N seconds` | the feature is active for this service |
| `START` | a rebuild begins: Introduction Point, auth key, current circuit, its age |
| `BUILDING` | the replacement circuit and its four-hop path |
| `ESTABLISHED` | `INTRO_ESTABLISHED` arrived on the replacement |
| `SWAPPED` | the replacement now serves the Introduction Point |
| `ABANDONED` | the replacement missed the deadline (half the interval, clamped to 30-120 s); it is closed, the old circuit keeps serving, a new attempt starts on the next tick |
| `FAILED` | the replacement died before establishing; same handling |
| `BACKOFF` | three consecutive failed attempts on one Introduction Point; wait one full interval before trying again |

The auth key printed in `START`, `ESTABLISHED` and `SWAPPED` is identical, which
shows from the log alone that the published identity did not change while the
path did.

---

## 3. Building

Prerequisites on macOS (Homebrew): `autoconf`, `automake`, `libtool`,
`pkg-config`, `openssl@3`, `libevent`. On Debian or Ubuntu the equivalents are
`build-essential automake libevent-dev libssl-dev zlib1g-dev`.

```sh
./autogen.sh
./configure --disable-asciidoc \
            --with-openssl-dir="$(brew --prefix openssl@3)" \
            --with-libevent-dir="$(brew --prefix libevent)"
make -j"$(sysctl -n hw.ncpu)"
./src/app/tor --version
```

---

## 4. Running the test network

The demonstration uses [Chutney](https://gitlab.torproject.org/tpo/core/chutney),
which runs a complete private Tor network of local processes: four directory
authorities, five relays, a client and an onion service, with their own
consensus. Nothing touches the public Tor network.

### 4.1 Preparing Chutney

```sh
git clone https://gitlab.torproject.org/tpo/core/chutney
cd chutney
python3.11 -m venv .venv && .venv/bin/pip install -e .
```

Chutney needs Python 3.11 or later, so every command below is prefixed
`PYTHON=.venv/bin/python3`; without it the wrapper selects the system
interpreter, which lacks the dependencies.

On macOS, Chutney's process launcher enumerates `/proc/self/fd`, which does not
exist, and every node exits immediately. In `lib/chutney/launcher.py`,
`_closerange()` needs to fall back to `/dev/fd`:

```python
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

This is a Chutney portability issue and is unrelated to the modification.

### 4.2 The network definition

No stock Chutney network enables the option. Save the following as
`lib/chutney/data/networks/hs-v3-rotation`; it is the stock `hs-v3` network with
one additional torrc line on the onion service:

```python
INTRO_CIRCUIT_ROTATION = 120   # seconds between rebuilds; 0 disables

Authority = Node(tag="a", authority=1, relay=1)
ExitRelay = Node(tag="r", relay=1, exit=1)
Client    = Node(tag="c", client=1, launch_phase=2)
HS = Node(
    tag="h",
    hs=1,
    launch_phase=2,
    extra_raw_torrc=(
        "\nHiddenServiceIntroCircuitRotation "
        f"{INTRO_CIRCUIT_ROTATION}\n"
    ),
)

NODES = Authority.getN(4) + ExitRelay.getN(5) + Client.getN(1) + HS.getN(1)
ConfigureNodes(NODES)
```

Five relays are the minimum for onion-service circuits to build.

### 4.3 Start, verify, observe, stop

From the Chutney directory, with `TOR` pointing at the binary built in §3:

```sh
# create the network (this generates a new onion address)
PYTHON=.venv/bin/python3 ./chutney init \
  --net-from-script-path networks/hs-v3-rotation \
  --tor         /path/to/tor/src/app/tor \
  --tor-gencert /path/to/tor/src/tools/tor-gencert

# start it; on its own this reuses the existing keys and onion address
PYTHON=.venv/bin/python3 ./chutney bootstrap

PYTHON=.venv/bin/python3 ./chutney status
PYTHON=.venv/bin/python3 ./chutney verify     # expect successes:4 failures:0

cat net/nodes/010h/hidden_service/hostname    # the onion address

PYTHON=.venv/bin/python3 ./chutney stop
```

To reach the service, run any HTTP server on the service's target port and fetch
through the client's SOCKS port:

```sh
curl --socks5-hostname 127.0.0.1:9009 http://<address>.onion:5858/
```

Note that `chutney verify` binds the service's target port itself, so stop any
server on that port before verifying.

### 4.4 Observing a rebuild

The first rebuild occurs one interval after the introduction circuits establish,
roughly two and a half minutes after bootstrap at a 120-second period. Each
cycle rebuilds every Introduction Point of both the current and the next
descriptor.

```sh
L=net/nodes/010h/notice.log

tail -f $L | grep --line-buffered "intro-rotation"   # watch live
grep "rotation enabled" $L                           # the feature is active
grep -c "intro-rotation\] START"   $L                # rebuilds attempted
grep -c "intro-rotation\] SWAPPED" $L                # rebuilds completed

# the auth key is constant across every rebuild
grep "\[intro-rotation\]" $L | grep -oE "auth key [A-Za-z0-9+/]+" | sort | uniq -c

# no Introduction Point was retired by the retry cap
grep -icE "remov(e|ing) .*intro|retir" $L
```

For a comparison run, set `INTRO_CIRCUIT_ROTATION = 0` in the network definition
and recreate the network; the log then contains no `[intro-rotation]` lines and
no introduction circuits are rebuilt.

---

## 5. Observed behaviour

Measurements from the private network described above, with the patched binary.

| property | observed |
|---|---|
| the internal path is rebuilt | 38 consecutive rebuilds, a new circuit each time; at least one middle hop differed in 26 of 38 |
| the entry guard is unchanged | 0 of 38 changed |
| the Introduction Point is unchanged | 0 of 38 changed |
| the auth key is unchanged | constant across every rebuild, to depth 8 |
| the published descriptor is unchanged | client-fetched descriptor byte-identical across a rebuild; revision counter unmoved |
| Introduction Points survive the retry cap | depth 8 against a cap of 3, 0 retired |
| clients are uninterrupted | 75 fetches at 2-second intervals across a swap: 74 succeeded, 0 introductions lost at a swap |
| the relay performs the close | 14 of 14 closes were remote, none initiated by the service |
| cost with rotation enabled (120 s, 6 Introduction Points) | 18 introduction circuits in 360 s, i.e. 180 per hour |
| cost with rotation disabled | 0 rebuilt circuits in 360 s |

The cost is therefore one additional four-hop circuit per Introduction Point per
interval, in exchange for no internal path outliving that interval.

Raw evidence, including per-rebuild path comparisons, control-port
cross-checks and descriptor dumps, is under `rotation-evidence/`, with an index
describing each file and the commands that re-derive the numbers.

---

## 6. Limitations of this demonstration

* **Path diversity is limited by the test network.** Twelve of the 38 rebuilds
  drew an identical path. With five relays, and the first and last hops pinned
  to the guard and the Introduction Point, the intermediate hops are drawn from
  roughly three candidates. The circuit is genuinely rebuilt each time; what the
  small network cannot demonstrate is the unlinkability of successive paths.
* **A rebuild can still be dropped when its Introduction Point disappears.**
  When Tor's own time-period rotation retires a descriptor, any replacement in
  flight for one of that descriptor's Introduction Points has nothing left to
  replace and is closed. Measured at 6 occurrences in 73 minutes on the test
  network, whose descriptor rotates every 8 minutes; three per descriptor
  rotation. This does not lengthen any Introduction Point's rotation interval,
  because the Introduction Point itself is gone.
  The adaptive-circuit-build-timeout loss that this section previously
  described has been fixed and re-measured: rebuilds lost fell from 14.2% to
  3.0%, and the maximum interval between consecutive swaps from 480 s to 121 s
  with 120 s configured. See `rotation-evidence/06-rotation-period.txt`.
* **Scope.** The modification was exercised on a private five-relay network with
  a single service and a 120-second interval. It has not been evaluated on the
  public network, with vanguards enabled, with client authorization, or with
  single onion services, and no unit test covers the scheduler directly.
* **The security benefit is argued, not measured here.** This artifact shows
  that the path is rebuilt while the published identity is preserved, and at
  what cost. It does not measure the effect on an adversary's ability to
  reconstruct a path, which would require a network carrying realistic
  background traffic.
