#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime
import time  # Import time for delay

# Configuration
SERVICE_NAME = "sol"
LAST_RESTART_FILE = "/home/bao-monitor/solana_last_restart.log"  # Adjusted for bao-monitor user
CHECK_INTERVAL = 1  # Time in seconds between each check (e.g., 60 seconds)

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

        print(f"[{datetime.now().isoformat()}] checking if sol has restarted......")

        current_restart = get_service_restart_time()
        if not current_restart:
            time.sleep(CHECK_INTERVAL)
            continue

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

        # Wait for the specified interval before checking again
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
