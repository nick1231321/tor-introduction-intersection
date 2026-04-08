#!/usr/bin/env bash

# ====== CONFIG ======
TOR_BIN="/opt/tor-custom/bin/tor"
TORRC="/etc/tor-client/torrc"
SOCKS="127.0.0.1:9052"
#Here input the URL of your onion server
ONION_URL="http://na6zq4cbd5d5vi4dhgokzea33vvnarq4yugv6qrqn4rod3b2cazunuid.onion"
SLEEP_SECONDS=30
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


