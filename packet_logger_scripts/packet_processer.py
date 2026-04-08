#!/usr/bin/env python3
import os
import re
import time
import signal
import socket
import subprocess
from typing import Optional, Set
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
from hashlib import sha256
import base64
from Cryptodome.Math.Numbers import Integer
import csv
import errno
import ipaddress
from datetime import datetime, timezone
import uuid
import glob
import json
import urllib.parse
import urllib.request

EXCLUDED_IPS = [
    "137.184.86.173",
]
EXCLUDED_PSEUDONYMS: Set[str] = set()

TARGET_IP = "164.92.71.251"
TARGET_PSEUDONYM: Optional[str] = None

TCPDUMP = os.environ.get("TCPDUMP", "tcpdump")
IFACE = os.environ.get("IFACE", "")
CONTROL_SOCK = os.environ.get("CONTROL_SOCK", "/run/packet_logger.sock")

_key = RSA.generate(2048)
_pubkey = _key.publickey()
_cipher = PKCS1_v1_5.new(_pubkey)

def onionoo_get_bandwidth_by_fingerprint(fp: str, timeout: int = 6) -> Optional[dict]:
    """
    Query Onionoo /bandwidth endpoint by relay fingerprint and return the first relay entry.
    """
    base = "https://onionoo.torproject.org/bandwidth"
    params = {
        "lookup": fp,
        "limit": "1",
        "fields": "fingerprint,read_history,write_history",
    }
    url = base + "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "intersection-logger/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None

    relays = data.get("relays") or []
    if relays:
        return relays[0]
    return None


def latest_bps_from_history(history_root: dict, period_key: str = "1_month") -> Optional[float]:
    """
    Extract the most recent non-null value from an Onionoo graph history object (bytes per second).
    Onionoo stores 'values' normalized and a 'factor' to scale back: bps = value * factor.
    """
    if not isinstance(history_root, dict):
        return None

    hist = history_root.get(period_key)
    if not isinstance(hist, dict):
        return None

    values = hist.get("values")
    factor = hist.get("factor")
    if not isinstance(values, list) or factor is None:
        return None

    for v in reversed(values):
        if v is None:
            continue
        try:
            return float(v) * float(factor)
        except Exception:
            return None
    return None

def onionoo_get_details_by_ip(ip: str, timeout: int = 6) -> Optional[dict]:
    """
    Query Onionoo /details endpoint by IP and return the first relay entry.
    """
    base = "https://onionoo.torproject.org/details"
    params = {
        "search": ip,
        "limit": "5",
        "fields": (
            "fingerprint,nickname,"
            "guard_probability,"
            "middle_probability,"
            "consensus_weight,"
            "consensus_weight_fraction,"
            "first_seen,"
            "running"
        ),
    }
    url = base + "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "intersection-logger/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None

    relays = data.get("relays") or []
    if relays:
        return relays[0]
    return None


def next_numeric_prefix_csv() -> int:
    """
    Find the next numeric prefix for CSV files in the current directory.

    Rules:
      - Consider only files ending with .csv that START with a number (optionally followed by '-').
        Examples counted: "1-foo.csv", "12-bar.csv", "7.csv"
        Examples ignored:  "intersections.csv", "run-1.csv"
      - If none exist, return 1.
      - Otherwise return (max_prefix + 1).
    """
    max_n = 0
    for path in glob.glob("*.csv"):
        name = os.path.basename(path)

        # Extract leading integer from the beginning of the filename
        i = 0
        while i < len(name) and name[i].isdigit():
            i += 1

        if i == 0:
            continue  # does not start with a digit -> ignore

        # Parse that leading integer
        try:
            n = int(name[:i])
        except ValueError:
            continue

        if n > max_n:
            max_n = n

    return 1 if max_n == 0 else (max_n + 1)


def make_csv_path_with_numeric_prefix() -> tuple[str, str]:
    """
    Create a unique CSV filename prefixed with an auto-incrementing integer and a dash.

    Example output:
      "3-intersections_20260104_153012_4321_ab12cd.csv"
    """
    # UTC start time (safe for cron)
    from datetime import datetime, timezone
    import uuid

    start = datetime.now(timezone.utc)
    start_iso = start.isoformat(timespec="seconds")
    stamp = start.strftime("%Y%m%d_%H%M%S")

    run_id = os.environ.get("RUN_ID", "").strip()
    if not run_id:
        run_id = f"{os.getpid()}_{uuid.uuid4().hex[:6]}"

    base_name = f"intersections_{stamp}_{run_id}.csv"

    prefix = next_numeric_prefix_csv()
    csv_name = f"{prefix}-{base_name}"
    return csv_name, start_iso


def rsa_encrypt_no_padding(pubkey: RSA.RsaKey, message: bytes) -> bytes:
    m = Integer.from_bytes(message)
    e = Integer(pubkey.e)
    n = Integer(pubkey.n)
    c = pow(m, e, n)
    return c.to_bytes(pubkey.size_in_bytes())


def pseudonymize_ip(ip: str) -> str:
    encrypted = rsa_encrypt_no_padding(_pubkey, ip.encode("utf-8"))
    hashed = sha256(encrypted).digest()
    return base64.urlsafe_b64encode(hashed).decode("utf-8").rstrip("=")


def safe_send(conn: socket.socket, data: bytes) -> None:
    """Best-effort send; don't crash if peer closes immediately."""
    try:
        conn.sendall(data)
    except BrokenPipeError:
        return
    except OSError as e:
        if e.errno in (errno.EPIPE, errno.ECONNRESET):
            return
        raise


TCPDUMP_RE = re.compile(
    r"""^(?P<epoch>\d+(?:\.\d+)?)\s+IP6?\s+
        (?P<src>[^ ]+)\s+>\s+(?P<dst>[^ ]+)
    """,
    re.VERBOSE,
)


def discover_iface() -> str:
    if IFACE:
        return IFACE
    try:
        out = subprocess.check_output(
            ["ip", "-o", "route", "get", "1.1.1.1"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        parts = out.split()
        for i, tok in enumerate(parts):
            if tok == "dev" and i + 1 < len(parts):
                return parts[i + 1]
    except Exception:
        pass
    return "eth0"


def normalize_ipv4(hostport: str) -> Optional[str]:
    s = hostport.strip().rstrip(":,")
    if ":" in s:
        return None
    chunks = s.split(".")
    if len(chunks) < 4:
        return None
    ip = ".".join(chunks[:4])
    try:
        if all(0 <= int(o) <= 255 for o in ip.split(".")):
            return ip
    except ValueError:
        return None
    return None


def fetch_public_ipv4() -> Optional[str]:
    """
    Best-effort: discover this machine's public IPv4 and return it.
    Uses curl with short timeout. Returns None on failure.
    """
    try:
        out = subprocess.check_output(
            ["curl", "-4", "-s", "--max-time", "2", "ifconfig.me"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if not out:
            return None
        # validate IPv4
        ip = ipaddress.ip_address(out)
        if ip.version == 4:
            return str(ip)
        return None
    except Exception:
        return None


# Global variable to store intersected set across sessions
intersected_set: Optional[Set[str]] = None


class PacketPrinter:
    def __init__(self) -> None:
        self.iface = discover_iface()
        self.capturing = False  # don't capture until we receive "start"
        self.proc: Optional[subprocess.Popen] = None
        self.current_set: Set[str] = set()  # stores pseudonyms only
        self.iteration = 0
        self.csv_path, self.start_iso_utc = make_csv_path_with_numeric_prefix()
        self.csv_file = open(self.csv_path, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)

        # Header lines at the top of the CSV
        self.csv_writer.writerow(["# started_at_utc", self.start_iso_utc])
        self.csv_writer.writerow(["# iface", self.iface])
        self.csv_writer.writerow(["# track", "dst_only"])
        self.csv_writer.writerow([])
        # --- Onionoo metadata block ---
        pub = fetch_public_ipv4()

        self.csv_writer.writerow([
            "entry",
            "guard_probability",
            "middle_probability",
            "consensus_weight",
            "consensus_weight_fraction",
            "first_seen",
            "read_bytes_per_second",
            "write_bytes_per_second",
        ])

        if pub:
            o = onionoo_get_details_by_ip(pub)
            if o:
                fingerprint = o.get("fingerprint") or ""
                entry = fingerprint or (o.get("nickname") or "")
                entry_p = o.get("guard_probability", "")
                middle_p = o.get("middle_probability", "")
                cw = o.get("consensus_weight", "")
                cwf = o.get("consensus_weight_fraction", "")
                first_seen = o.get("first_seen", "")

                # Default empty if bandwidth not available
                read_bps = ""
                write_bps = ""

                # Pull read/write bytes per second from Onionoo /bandwidth histories
                if fingerprint:
                    bw = onionoo_get_bandwidth_by_fingerprint(fingerprint)
                    if bw:
                        rh = bw.get("read_history") or {}
                        wh = bw.get("write_history") or {}

                        rb = latest_bps_from_history(rh, period_key="1_month")
                        wb = latest_bps_from_history(wh, period_key="1_month")

                        if rb is not None:
                            read_bps = f"{rb:.2f}"
                        if wb is not None:
                            write_bps = f"{wb:.2f}"

                self.csv_writer.writerow([
                    entry,
                    entry_p,
                    middle_p,
                    cw,
                    cwf,
                    first_seen,
                    read_bps,
                    write_bps,
                ])
            else:
                self.csv_writer.writerow(["no_match", "", "", "", "", "", "", ""])
        else:
            self.csv_writer.writerow(["no_public_ip", "", "", "", "", "", "", ""])

        self.csv_writer.writerow([])  # blank line before normal data
        self.csv_file.flush()
        os.fsync(self.csv_file.fileno())


        self.csv_writer.writerow(["iteration", "intersection_size"])
        self.csv_file.flush()
        os.fsync(self.csv_file.fileno())

        print(f"[INFO] Writing CSV to: {self.csv_path}", flush=True)
        print(f"[INFO] Run started at (UTC): {self.start_iso_utc}", flush=True)

    def start_tcpdump(self) -> None:
        if self.proc and self.proc.poll() is None:
            return
        cmd = [TCPDUMP, "-tt", "-n", "-l", "-i", self.iface, "ip"]
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

    def stop_tcpdump(self) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None

    def ensure_control_socket(self) -> socket.socket:
        try:
            os.unlink(CONTROL_SOCK)
        except FileNotFoundError:
            pass
        os.makedirs(os.path.dirname(CONTROL_SOCK), exist_ok=True)
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(CONTROL_SOCK)
        os.chmod(CONTROL_SOCK, 0o666)
        srv.listen(5)
        srv.setblocking(False)
        return srv

    def handle_control_conn(self, conn: socket.socket) -> bool:
        global intersected_set

        data = conn.recv(4096)
        if not data:
            return False

        cmd = data.decode("utf-8", errors="ignore").strip().lower()

        if cmd == "start":
            self.capturing = True
            self.current_set = set()
            safe_send(conn, b"OK capturing=on\n")

        elif cmd == "stop":
            self.capturing = False

            filtered_set = {p for p in self.current_set if p not in EXCLUDED_PSEUDONYMS}

            if intersected_set is None:
                intersected_set = set(filtered_set)
            else:
                intersected_set &= filtered_set
            # ---- Target presence check ----
            if TARGET_PSEUDONYM:
                in_current = TARGET_PSEUDONYM in filtered_set
                in_intersection = TARGET_PSEUDONYM in intersected_set

                if not in_current or not in_intersection:
                    self.csv_writer.writerow([self.iteration, "FAIL"])
                    self.csv_file.flush()
                    os.fsync(self.csv_file.fileno())

                    print("[INFO] Target pseudonym missing -> FAIL. Exiting.", flush=True)
                    try:
                        self.csv_file.close()
                    finally:
                        os._exit(1)

            self.iteration += 1
            intersection_size = len(intersected_set)

            self.csv_writer.writerow([self.iteration, intersection_size])
            self.csv_file.flush()
            os.fsync(self.csv_file.fileno())

            safe_send(conn, b"OK capturing=off\n")
            print(f"[DEBUG] Current set size: {len(filtered_set)}")
            print(f"[DEBUG] Intersected set size: {intersection_size}")

            if intersection_size == 1:
                print("[INFO] Intersection reduced to 1. Exiting.")
                try:
                    self.csv_file.close()
                finally:
                    os._exit(0)

        elif cmd == "status":
            msg = f"capturing={'on' if self.capturing else 'off'} iface={self.iface}\n"
            safe_send(conn, msg.encode("utf-8"))

        elif cmd in ("quit", "exit"):
            safe_send(conn, b"OK bye\n")
            return True

        else:
            safe_send(conn, b"ERR use: start|stop|status|quit\n")

        return False

    def run(self) -> None:
        self.start_tcpdump()
        srv = self.ensure_control_socket()

        running = True

        def _shutdown(_signum, _frame):
            nonlocal running
            running = False

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        try:
            while running:
                try:
                    conn, _ = srv.accept()
                except BlockingIOError:
                    conn = None

                if conn:
                    with conn:
                        if self.handle_control_conn(conn):
                            running = False

                if not self.proc or self.proc.poll() is not None:
                    self.start_tcpdump()
                    time.sleep(0.1)
                    continue

                line = self.proc.stdout.readline() if self.proc.stdout else ""
                if not line:
                    time.sleep(0.01)
                    continue

                m = TCPDUMP_RE.match(line)
                if not m:
                    continue

                dst_ip = normalize_ipv4(m.group("dst"))
                if not dst_ip:
                    continue

                if self.capturing:
                    pseudo = pseudonymize_ip(dst_ip)
                    if pseudo not in EXCLUDED_PSEUDONYMS:
                        self.current_set.add(pseudo)
#                        print(pseudo, flush=True)

        finally:
            self.stop_tcpdump()
            try:
                srv.close()
            except Exception:
                pass
            try:
                os.unlink(CONTROL_SOCK)
            except Exception:
                pass


if __name__ == "__main__":
    pub = fetch_public_ipv4()
    if pub:
        if pub not in EXCLUDED_IPS:
            EXCLUDED_IPS.append(pub)
        print(f"[INFO] Detected public IPv4: {pub} (added to exclusions)")
    else:
        print("[WARN] Could not detect public IPv4 via ifconfig.me; continuing without it")

    EXCLUDED_PSEUDONYMS = {pseudonymize_ip(ip) for ip in EXCLUDED_IPS}
    if TARGET_IP:
        TARGET_PSEUDONYM = pseudonymize_ip(TARGET_IP)
        print("[INFO] Target IP pseudonym initialized", flush=True)
    else:
        print("[INFO] No target IP set", flush=True)

    PacketPrinter().run()
