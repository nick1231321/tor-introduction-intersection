#!/usr/bin/env bash

# ====== CONFIG ======
TOR_BIN="/opt/tor-custom/bin/tor"
TORRC="/etc/tor-client/torrc"
SOCKS="127.0.0.1:9052"
ONION_URL="http://na6zq4cbd5d5vi4dhgokzea33vvnarq4yugv6qrqn4rod3b2cazunuid.onion"
SLEEP_SECONDS=30

# SSH CONFIG
TARGET_IP="ip"                 # <-- set target machine IP
REMOTE_USER="root"
SSH_KEY="/root/.ssh/id_ed25519"
REMOTE_SCRIPT="/exp/runner.sh"
REMOTE_LOG="/exp/runner.log"
# ====================

# Start packet processor in background
python3 /exp/packet_processer.py &
PACKET_PID=$!

echo "[*] packet_processer.py started with PID $PACKET_PID"

while true; do
    # If packet_processer exited, stop everything
    if ! kill -0 "$PACKET_PID" 2>/dev/null; then
        echo "[!] packet_processer.py exited, stopping loop"
        break
    fi

    echo "[*] Starting Tor client"
    sudo -u debian-tor "$TOR_BIN" -f "$TORRC" &

    # Give Tor time to bootstrap
    sleep 10

    echo "[*] Curling onion"
    curl --socks5-hostname "$SOCKS" "$ONION_URL"

    echo "[*] Killing Tor client (by torrc match)"
    pkill -f "$TORRC" 2>/dev/null || true

    echo "[*] Sleeping for $SLEEP_SECONDS seconds"
    sleep "$SLEEP_SECONDS"
done

echo "[*] Script finished cleanly"

# ====== SSH TO REMOTE & START RUNNER ======
if [[ -z "$TARGET_IP" ]]; then
    echo "[!] TARGET_IP not set, skipping SSH step"
    exit 1
fi

echo "[*] Connecting to $REMOTE_USER@$TARGET_IP and starting runner.sh"

ssh -i "$SSH_KEY" \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=accept-new \
    "$REMOTE_USER@$TARGET_IP" \
    "chmod +x '$REMOTE_SCRIPT' && nohup bash '$REMOTE_SCRIPT' > '$REMOTE_LOG' 2>&1 < /dev/null & echo '[REMOTE] runner.sh started'"
