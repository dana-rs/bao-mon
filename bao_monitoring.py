#!/usr/bin/env python3

import subprocess
from datetime import datetime
import time
import socketio

# Configuration

SOLANA_CLI_PATH = "/home/sol/.local/share/solana/install/active_release/bin/solana"  # Replace with the actual Solana CLI path
rpcURL = "http://127.0.0.1:8899"  # Example RPC URL

SERVICE_NAME = "sol"
CHECK_INTERVAL = 0.05  # 50ms between each check
CENTRAL_SERVER_URL = "http://your-central-server:3000"  # Replace with your actual Socket.IO server URL

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print(f"[{datetime.now().isoformat()}] Connected to the central server.")

@sio.event
def disconnect():
    print(f"[{datetime.now().isoformat()}] Disconnected from the central server.")

def get_service_status():
    """Get the current status of the service using systemctl."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()  # Returns 'active', 'inactive', 'failed', 'deactivating', etc.
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error fetching service status: {e}")
        return "unknown"

def get_identity_pubkey():
    """Get the identity public key using Solana CLI."""
    try:
        result = subprocess.run(
            [SOLANA_CLI_PATH, "address"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error fetching identity pubkey: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception while fetching identity pubkey: {e}")
        return None


def main():
    print(f"[{datetime.now().isoformat()}] Starting monitoring...")
    last_status = None  # Variable to store the last known status

    # Connect to the central server
    try:
        sio.connect(CENTRAL_SERVER_URL)
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Failed to connect to the central server: {e}")
        return

    identity_pubkey = get_identity_pubkey()
    if identity_pubkey:
        print(f"Identity Pubkey: {identity_pubkey}")
    else:
        print("Failed to fetch identity pubkey.")

    while True:
        current_status = get_service_status()

        if current_status != last_status:
            print(f"[{datetime.now().isoformat()}] Service status changed: {current_status}")
            last_status = current_status

            # Send a Socket.IO event if the service is deactivating or inactive
            if current_status in ("deactivating", "inactive"):
                sio.emit("service_status", {
                    "service": SERVICE_NAME,
                    "status": current_status,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"[{datetime.now().isoformat()}] Socket.IO event sent for status: {current_status}")

        time.sleep(CHECK_INTERVAL)

    sio.disconnect()

if __name__ == "__main__":
    main()
