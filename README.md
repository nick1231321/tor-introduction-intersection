This repository contains a modified version of the Tor daemon that allows the operator of a hidden service to force the selection of specific relays for its introduction circuit. It also includes scripts for running an intersection attack against a self-operated hidden service for experimental and reproducibility purposes.

---

## Step 1: Force the hidden service to use specific relays in its introduction circuit

To reproduce the experiment, the hidden service operator must first control four Tor relays that are active on the live network.

1. Locate the relays in Tor Metrics:  
   https://metrics.torproject.org/rs.html

2. For each relay, copy the following fields:
   - `Nickname`
   - `Fingerprint`

3. Open the file:
   ```
   src/feature/hs/hs_experiment.h
   ```

4. Paste the corresponding relay fingerprints and nicknames into the following fields:

   - `FORCED_INTRO_FP_HEX` and `FORCED_INTRO_NICK`  
     Introduction point relay

   - `FORCED_MID_FP_HEX` and `FORCED_MID_NICK`  
     First middle relay

   - `FORCED_VANGUARD_FP_HEX` and `FORCED_VANGUARD_NICK`  
     Vanguard relay

   - `FORCED_ENTRY_FP_HEX` and `FORCED_ENTRY_NICK`  
     Entry guard relay

---

## Step 2: Build the modified Tor daemon

Before building, install the required dependencies.

### macOS
```bash
brew install automake autoconf libtool pkg-config libevent openssl@3
```

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install -y git build-essential automake libevent-dev libssl-dev zlib1g-dev
```

Build the modified Tor daemon before running the experiment. This binary is used both by the hidden service and by a colocated Tor client running on the monitored relay.

The colocated client:
1. Issues requests to trigger the introduction protocol.
2. Sends control signals to the intersector plugin (`packet_logger_scripts/packet_processer.py`) to construct anonymity sets and compute intersections.

### Build
```bash
./autogen.sh
./configure --disable-asciidoc  # do not build manpages
make
make install
```

---

## Step 3: Bring the hidden service online

### 3.1 Create Tor data directory
```bash
mkdir -p /path/to/tor-hs-data
chmod 700 /path/to/tor-hs-data
```

### 3.2 Create hidden service directory
```bash
mkdir -p /path/to/hidden_service
chmod 700 /path/to/hidden_service
```

### 3.3 Configure `torrc`
```ini
DataDirectory /path/to/tor-hs-data
SocksPort 0
Log notice stdout

HiddenServiceDir /path/to/hidden_service
HiddenServiceVersion 3
HiddenServicePort 80 127.0.0.1:8080
```

### 3.4 Start local web service
```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

### 3.5 Launch Tor
```bash
/path/to/tor/src/app/tor -f /path/to/torrc
```

### 3.6 Retrieve onion address
```bash
cat /path/to/hidden_service/hostname
```

### 3.7 Verify service
```bash
torsocks curl http://<your_onion_address>
```

---

## Step 4: Configure the intersector plugin and automation scripts

Install:
```
packet_logger_scripts/packet_processer.py
```

### Plugin configuration (per relay)

- `EXCLUDED_IPS`: previous relay IP
- Leave empty for the introduction point

- `TARGET_IP`: next relay IP

Mapping:
- Introduction point → Middle1
- Middle1 → Vanguard
- Vanguard → Entry
- Entry → Hidden service

### Automation scripts

Install:
- `packet_logger_scripts/first_nodes/runner.sh` (first 3 relays)
- `packet_logger_scripts/last_node/runner.sh` (last relay)

Behavior:
- First 3 relays: SSH to next node after convergence
- Last relay: no SSH

### runner.sh configuration
```bash
TOR_BIN="/opt/tor-custom/bin/tor"
TORRC="/etc/tor-client/torrc"
SOCKS="127.0.0.1:9052"
ONION_URL="http://youronion.onion"
SLEEP_SECONDS=30

# SSH CONFIG
TARGET_IP="ip"
REMOTE_USER="root"
SSH_KEY="/root/.ssh/id_ed25519"
REMOTE_SCRIPT="/exp/runner.sh"
REMOTE_LOG="/exp/runner.log"
```

Ensure SSH access between consecutive relays.

---

## Step 5: Schedule experiment execution

### Edit crontab
```bash
crontab -e
```

### Example schedules

Every 30 minutes:
```bash
*/30 * * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

Every hour:
```bash
0 * * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

Specific times:
```bash
0 2,10,18 * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

### Make script executable
```bash
chmod +x /exp/runner.sh
```

---

## Reproducing Figures and Tables

### Install Python dependencies
```bash
pip3 install matplotlib requests
```

---

### Figures 2 and 3
```bash
python3 produce_graphs/generate_stats_and_graphs.py
```

---

### Table 1

Ensure no Tor process is running before executing the script.

```bash
python3 produce_graphs/measure_introduce_time.py
```

Modify:

- `TARGET_URLS` → list of onion services
- `CSV_PATH`
  ```python
  CSV_PATH = "/tmp/tor_hs_timing.csv"
  ```
- `PROXY_CMD`
  ```python
  PROXY_CMD = ["./src/app/tor"]
  ```

Ensure the modified Tor binary is built and accessible.
