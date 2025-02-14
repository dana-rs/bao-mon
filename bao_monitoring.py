#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime
import time

# Configuration
SERVICE_NAME = "sol"
LAST_RESTART_FILE = "/home/bao/tmp/solana_last_restart.log"  # Updated path
CHECK_INTERVAL = 60  # Time in seconds between each check

# Ensure the directory exists
os.makedirs(os.path.dirname(LAST_RESTART_FILE), exist_ok=True)

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
    print(f"[{datetime.now().isoformat()}] Starting monitoring...")

    while True:
        current_restart = get_service_restart_time()
        if not current_restart:
            time.sleep(CHECK_INTERVAL)
            continue

        try:
            if os.path.exists(LAST_RESTART_FILE):
                with open(LAST_RESTART_FILE, "r") as file:
                    last_restart = file.read().strip()
                
                if current_restart != last_restart:
                    print(f"[{datetime.now().isoformat()}] Service has restarted.")
                    with open(LAST_RESTART_FILE, "w") as file:
                        file.write(current_restart)
                else:
                    print(f"[{datetime.now().isoformat()}] No restart detected.")
            else:
                print(f"[{datetime.now().isoformat()}] Initializing monitoring...")
                with open(LAST_RESTART_FILE, "w") as file:
                    file.write(current_restart)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error handling the file: {e}")

        # Wait before checking again
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
