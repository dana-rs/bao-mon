#!/usr/bin/env python3

import subprocess
from datetime import datetime
import time
import socketio
import sys

# Configuration
SOLANA_CLI_PATH = "/home/sol/.local/share/solana/install/active_release/bin/solana"
SERVICE_NAME = "sol"
CHECK_INTERVAL = 0.05  # 50ms between each service status check
CENTRAL_SERVER_URL = "https://884a-113-130-126-115.ngrok-free.app"
CENTRAL_SERVER_KEY="my-secret-key"
RETRY_COUNT = 5  # Number of retry attempts for Socket.IO connection
RETRY_INTERVAL = 0.5  # Time in seconds between retries (500ms)

# Create a Socket.IO client
sio = socketio.Client()
connected = False  # Track Socket.IO connection
was_active = False  # Track if the service was ever active

@sio.event
def connect():
    global connected
    connected = True
    print(f"[{datetime.now().isoformat()}] Connected to the central server.")

@sio.event
def disconnect():
    global connected
    connected = False
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

def connect_with_retries():
    """Attempt to connect to the Socket.IO server with retries."""
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            print(f"[{datetime.now().isoformat()}] Attempting to connect to the central server (Attempt {attempt}/{RETRY_COUNT})...")
            sio.connect(CENTRAL_SERVER_URL, auth={"key": CENTRAL_SERVER_KEY})
            return True  # Successfully connected
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Connection attempt {attempt} failed: {e}")
            if attempt < RETRY_COUNT:
                retry_delay = RETRY_INTERVAL + (attempt - 1) * 0.1  # Slightly increase delay with each retry
                print(f"[{datetime.now().isoformat()}] Retrying in {retry_delay:.2f} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"[{datetime.now().isoformat()}] All connection attempts failed. Exiting.")
                sys.exit(1)  # Exit the script with an error code

def main():
    global was_active
    print(f"[{datetime.now().isoformat()}] Starting monitoring...")
    last_status = None  # Variable to store the last known status

    # Attempt to connect to the central server with retries
    connect_with_retries()

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

            if current_status == "active":
                was_active = True  # Mark that the service has been active

            # Send a Socket.IO event only if the service was active at least once and Socket.IO is connected
            if was_active and connected and current_status in ("deactivating", "inactive"):
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
