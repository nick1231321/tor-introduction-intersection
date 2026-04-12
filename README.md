This repository contains a modified version of the Tor daemon that allows the operator of a hidden service to force the selection of specific relays for its introduction circuit. It also includes scripts for running an intersection attack against a self-operated hidden service for experimental and reproducibility purposes.

## Step 1: Force the hidden service to use specific relays in its introduction circuit

To reproduce the experiment, the hidden service operator must first control four Tor relays that are active on the live network.

1. Locate the relays in Tor Metrics:
   https://metrics.torproject.org/rs.html

2. For each relay, copy the following fields:
   - `Nickname`
   - `Fingerprint`

3. Open the file:
   `src/feature/hs/hs_experiment.h`

4. Paste the corresponding relay fingerprints and nicknames into the following fields:

   - `FORCED_INTRO_FP_HEX` and `FORCED_INTRO_NICK`  
     Use the fingerprint and nickname of the relay that will act as the introduction point.

   - `FORCED_MID_FP_HEX` and `FORCED_MID_NICK`  
     Use the fingerprint and nickname of the relay that will act as the first middle relay.

   - `FORCED_VANGUARD_FP_HEX` and `FORCED_VANGUARD_NICK`  
     Use the fingerprint and nickname of the relay that will act as the vanguard relay.

   - `FORCED_ENTRY_FP_HEX` and `FORCED_ENTRY_NICK`  
     Use the fingerprint and nickname of the relay that will act as the entry guard.

## Step 2: Build the modified Tor daemon

Build the modified Tor daemon before running the experiment. This binary is used both by the hidden service and by a colocated Tor client running on the monitored relay.

The colocated client serves two purposes:
1. It issues requests to the hidden service to trigger executions of the introduction protocol.
2. It sends control signals to the intersector plugin (`packet_logger_scripts/last_node/packet_processer.py`), enabling online construction of anonymity sets and computation of intersections during the experiment.
## Build

```
./autogen.sh
./configure
make
make install
```
## Step 3: Bring the hidden service online

After building the modified Tor daemon, create a hidden service that will be used as the target of the experiment.

### 3.1 Create a data directory for Tor

mkdir -p /path/to/tor-hs-data  
chmod 700 /path/to/tor-hs-data  

### 3.2 Create a directory for the hidden service

mkdir -p /path/to/hidden_service  
chmod 700 /path/to/hidden_service  

### 3.3 Configure torrc

Create a file named torrc with the following content:

DataDirectory /path/to/tor-hs-data  
SocksPort 0  
Log notice stdout  

HiddenServiceDir /path/to/hidden_service  
HiddenServiceVersion 3  
HiddenServicePort 80 127.0.0.1:8080  

### 3.4 Start a local service

python3 -m http.server 8080 --bind 127.0.0.1  

### 3.5 Launch the modified Tor daemon

/path/to/tor/src/app/tor -f /path/to/torrc  

### 3.6 Retrieve the onion address

cat /path/to/hidden_service/hostname  

### 3.7 Verify the hidden service

torsocks curl http://<your_onion_address>  

### 3.8 Keep the service running

Keep the hidden service online during the experiment so that repeated introduction requests can be issued.

## Step 4: Configure the intersector plugin and the automation scripts

Install `packet_logger_scripts/packet_processer.py` on each relay machine that may be monitored during the experiment.

For each relay, edit the plugin configuration as follows:

- In `EXCLUDED_IPS`, add the IP address of the previous relay in the introduction circuit.
- For the first monitored relay, that is, the introduction point, leave `EXCLUDED_IPS` empty.
- For example, when monitoring the entry guard, `EXCLUDED_IPS` should contain the IP address of the vanguard relay.

- Set `TARGET_IP` to the IP address of the next relay in the circuit. This is used to verify that the pseudonym of the true successor is always included in the constructed anonymity set.

  Specifically:
  - For the introduction point, set `TARGET_IP` to the Middle 1 relay IP.
  - For the Middle 1 relay, set `TARGET_IP` to the vanguard relay IP.
  - For the vanguard relay, set `TARGET_IP` to the entry guard IP.
  - For the entry guard, set `TARGET_IP` to the hidden service IP.

Additionally, install the automation script that coordinates trial execution and interaction with the intersector plugin.

- Install `packet_logger_scripts/first_nodes/runner.sh` on each of the first three relays in the circuit.
- Install `packet_logger_scripts/last_node/runner.sh` on the last monitored relay.

The difference between these two scripts is the following:
- On the first three relays, once the packet logger converges, the script connects over SSH to the next machine and starts its corresponding `runner.sh`.
- On the last relay, the script does not initiate any SSH connection after convergence.
- 
For each `runner.sh`, set the following variables correctly. On the script under `last_node`, no SSH configuration is required.

```bash
TOR_BIN="/opt/tor-custom/bin/tor"
TORRC="/etc/tor-client/torrc"
SOCKS="127.0.0.1:9052"
ONION_URL="http://youronion.onion"
SLEEP_SECONDS=30

# SSH CONFIG
TARGET_IP="ip"                 # set the successor relay machine IP
REMOTE_USER="root"
SSH_KEY="/root/.ssh/id_ed25519"
REMOTE_SCRIPT="/exp/runner.sh"
REMOTE_LOG="/exp/runner.log"

Make sure that the SSH key on each of the first relays can authenticate to the next relay in the circuit, so that runner.sh can start the experiment remotely after convergence.
### Step 5: Schedule experiment execution on the introduction point

To automate the experiment, configure a cron job on the introduction point relay that periodically invokes `runner.sh`.

### 5.1 Edit the crontab

```bash
crontab -e
```

### 5.2 Add a scheduled task

Add an entry to execute `runner.sh` at the desired times and frequency.

For example, to run the experiment every 30 minutes:

```bash
*/30 * * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

You can adjust the schedule as needed.

- Every hour:

```bash
0 * * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

- At specific times (e.g., 02:00, 10:00, 18:00):

```bash
0 2,10,18 * * * /exp/runner.sh >> /exp/runner.log 2>&1
```

### 5.3 Verify execution

Make sure that the script has execute permissions:

```bash
chmod +x /exp/runner.sh
```

Also verify that the paths are correct and logs are written to `/exp/runner.log`.


## Reproducing Figures and Tables

To reproduce the results presented in the paper, use the following scripts.

### Figures 2 and 3
Before running the script, ensure that the required Python dependencies are installed:

```
pip3 install matplotlib requests
```

Run:

```
python3 produce_graphs/generate_stats_and_graphs.py
```

This script processes data from Onionoo api and generates the statistics and plots used in Figures 2 and 3.

---

### Table 1

Run:

```
python3 produce_graphs/measure_introduce_time.py
```

Before running the script, modify the following variables:

- `TARGET_URLS`  
  Set this to the list of onion services you want to measure. The script will trigger the introduction protocol and measure the `INTRODUCE1`--`RENDEZVOUS2` latency.

- `CSV_PATH`  
  Path where results will be stored. Example:
  ```
  CSV_PATH = "/tmp/tor_hs_timing.csv"
  ```

- `PROXY_CMD`  
  Path to the Tor binary used to issue requests. Example:
  ```
  PROXY_CMD = ["./src/app/tor"]
  ```

Make sure the modified Tor daemon is built and accessible at the specified path before running the script.
