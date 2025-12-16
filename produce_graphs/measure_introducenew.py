#!/usr/bin/env python3
import os
import time
import socket
import subprocess
import csv
import logging
import signal
from datetime import datetime

# ---------------- CONSTANTS ----------------
CSV_PATH = "/tmp/tor_hs_timing.csv"
PROXY_CMD = ["./src/app/tor"]
PROXY_PORT = 9050
PORT_WAIT_TIMEOUT = 120
CURL_TIMEOUT = 30
STARTUP_LOG = "/tmp/proxy_startup.log"

# List of .onion URLs to test
TARGET_URLS = [
    "bbzzzsvqcrqtki6iumym6itiixfhni3rybtt7mkbjyxn2pgllzxf2qgyd.onion",
    "bcloudenvgjxcxh6jhuheyt7za5isimzgg4kv5u74jb522ey3hzpwh6id.onion",
    "juhanumktlxp7nkq76ybqaezldylbmlenowu2e5andkldbsotc4syd.onion",
    "chatorcvclv52nslktysouzgy36plnrwpbgowbh6my5z2bq24hkyyd.onion",
    "nv3x2jozywh63fokhn5mwp2d73vasilxw3etueof52fmbjsiw6sad.onion",
    "lghaesouqrrtww3s4nurujcgimr53ba5vjis5knfdpo33ql67bwyd.onion",
    "dkarzqtmdbamq6zmseeuqhet4e2tpj45bmw5ak3ofx2vgqceoeqyd.onion",
    "dreadytofatroptsdj6iot7axbtet6tonynoy2vjicoxhwyazubrad.onion",
    "mail2torjgmwxenntmrbnvlavnh7jouul5yarl6oyblvjxkwqf6ikwyd.onion",
    "qakltlwmuavvvqg4ybvgvtityoa4hjl5x6yfupdf6tjiqcwgdbym2gad.onion/wiki/index.php/Main_Page",
    "wamu5mpgden7jb55etmdh6m6v4twb7iuszl0mb3ltgqts5gd.onion",
    "ez37hmmeh9nadixctfeaqn7ky1al2vyksgbwel4bcgi1krgr5gid.onion",
    "endtovmu7s8ajpu1b8i9et4v2b4yybbioeisa4ptrvehncgevd.onion",
    "awswcz7occc2j2yeyqewyw7j5eujyfodhmd5hqnupxwsucno7id.onion",
    "ujsidjlntv5ku1t5w6fx0bv7xnowet7x30sbgtsz2dgugsst3ntfualg2yd.onion",
    "bmgunsyop5qa34znrayd6shosvukwbascyo2hbu3ri7b2ghw65jgrad.onion",
]

REQUESTS_PER_URL = 10
FULL_LOG_CSV = "/tmp/full_log.csv"
SUMMARY_CSV = "/tmp/summary.csv"
# -------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

signal.signal(signal.SIGINT, lambda s, f: exit(0))


def start_proxy_and_log(cmd, log_path):
    logfile = open(log_path, "wb")
    proc = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
    return proc, logfile


def stop_proxy(proc, logfile=None):
    try:
        if proc and proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
    except Exception:
        pass
    if logfile:
        logfile.close()


def wait_for_port(host, port, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except Exception:
            time.sleep(1)
    return False


def remove_csv_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


def run_curl_via_socks(port, target, timeout):
    url = target if target.startswith("http") else f"http://{target}/"
    cmd = ["curl", "--socks5-hostname", f"127.0.0.1:{port}", "--max-time", str(timeout), "-sS", url]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    return cp.returncode == 0


def parse_hs_timing_csv(path):
    if not os.path.exists(path):
        return None, None
    intro, rend = None, None
    try:
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                ts, _, event = row[:3]
                event = event.strip().upper()
                if event == "INTRODUCE1_SENT" and intro is None:
                    intro = ts
                elif event.startswith("RENDEZVOUS2") and rend is None:
                    rend = ts
                if intro and rend:
                    break
    except Exception:
        return None, None

    def parse_iso_z(s):
        if not s:
            return None
        s = s.rstrip("Z")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    return parse_iso_z(intro), parse_iso_z(rend)


def measure_latency_once(url):
    proc, logfile = start_proxy_and_log(PROXY_CMD, STARTUP_LOG)
    if not wait_for_port("127.0.0.1", PROXY_PORT, timeout=PORT_WAIT_TIMEOUT):
        stop_proxy(proc, logfile)
        return None, None, False

    remove_csv_if_exists(CSV_PATH)
    ok = run_curl_via_socks(PROXY_PORT, url, CURL_TIMEOUT)
    intro, rend = parse_hs_timing_csv(CSV_PATH)
    remove_csv_if_exists(CSV_PATH)
    stop_proxy(proc, logfile)

    if not ok or not intro or not rend:
        return None, None, False

    delta = (rend - intro).total_seconds()
    return intro, delta, True


def write_csv_row(path, row, header=None):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists and header:
            writer.writerow(header)
        writer.writerow(row)


def main():
    # Prepare logs
    if os.path.exists(FULL_LOG_CSV):
        os.remove(FULL_LOG_CSV)
    if os.path.exists(SUMMARY_CSV):
        os.remove(SUMMARY_CSV)

    write_csv_row(
        FULL_LOG_CSV,
        ["url", "attempt", "introduce_time", "delta_seconds", "status"],
        header=["url", "attempt", "introduce_time", "delta_seconds", "status"]
    )
    write_csv_row(
        SUMMARY_CSV,
        ["url", "samples", "avg_delta_s", "avg_intro_time_iso", "min_delta", "max_delta"],
        header=["url", "samples", "avg_delta_s", "avg_intro_time_iso", "min_delta", "max_delta"]
    )

    for url in TARGET_URLS:
        deltas = []
        intro_times = []
        start_time = datetime.utcnow()

        logging.info("=== Measuring %s ===", url)

        for i in range(1, REQUESTS_PER_URL + 1):
            logging.info("[%s] Attempt %d/%d", url, i, REQUESTS_PER_URL)
            intro, delta, ok = measure_latency_once(url)

            if ok and delta is not None:
                deltas.append(delta)
                intro_times.append(intro.timestamp())
                logging.info("Δt = %.3f s", delta)
            else:
                logging.warning("Attempt %d failed for %s", i, url)

            write_csv_row(
                FULL_LOG_CSV,
                [url, i, intro.isoformat() if intro else "", f"{delta:.3f}" if delta else "", "OK" if ok else "FAIL"]
            )

        if deltas:
            avg_delta = sum(deltas) / len(deltas)
            avg_intro_ts = datetime.fromtimestamp(sum(intro_times) / len(intro_times))
            write_csv_row(
                SUMMARY_CSV,
                [url, len(deltas), f"{avg_delta:.3f}", avg_intro_ts.isoformat(),
                 f"{min(deltas):.3f}", f"{max(deltas):.3f}"]
            )
            logging.info("AVG Δt=%.3f s | Introduce1 avg=%s", avg_delta, avg_intro_ts.isoformat())
        else:
            write_csv_row(SUMMARY_CSV, [url, 0, "", "", "", ""])
            logging.warning("No valid samples for %s", url)

        logging.info("Finished %s (%.1f min)", url, (datetime.utcnow() - start_time).total_seconds() / 60.0)

    logging.info("All done. Logs written to:\n  %s\n  %s", FULL_LOG_CSV, SUMMARY_CSV)


if __name__ == "__main__":
    main()

