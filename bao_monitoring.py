#!/usr/bin/env python3

import os
import subprocess
import socketio
from datetime import datetime

# Configuration
SERVICE_NAME = "solana"
LAST_RESTART_FILE = "/tmp/solana_last_restart.log"
CENTRAL_SERVER_URL = "http://your-central-server:3000"  # Replace with your actual server URL

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the central server.")

@sio.event
def disconnect():
    print("Disconnected from the central server.")

def get_service_restart_time():
    """Get the last restart time of the service using systemctl."""
    try:
        result = subprocess.run(
            ["systemctl", "show", SERVICE_NAME, "--property=ActiveEnterTimestamp"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.split("=")[-1].strip()
        else:
            print(f"Error fetching service status: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception while fetching service status: {e}")
        return None

def main():
    sio.connect(CENTRAL_SERVER_URL)  # Connect to the central server
    
    current_restart = get_service_restart_time()
    if not current_restart:
        return

    if os.path.exists(LAST_RESTART_FILE):
        with open(LAST_RESTART_FILE, "r") as file:
            last_restart = file.read().strip()
        
        if current_restart != last_restart:
            print("Service has restarted. Notifying the central server...")
            sio.emit("service_status", {
                "service": SERVICE_NAME,
                "status": "restarted",
                "timestamp": datetime.now().isoformat()
            })
            with open(LAST_RESTART_FILE, "w") as file:
                file.write(current_restart)
        else:
            print("No restart detected.")
    else:
        print("Initializing monitoring...")
        with open(LAST_RESTART_FILE, "w") as file:
            file.write(current_restart)

    sio.disconnect()  # Disconnect after sending the data

if __name__ == "__main__":
    main()
