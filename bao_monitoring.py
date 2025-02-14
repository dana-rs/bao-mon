#!/usr/bin/env python3

import subprocess
from datetime import datetime
import time

# Configuration
SERVICE_NAME = "sol"
CHECK_INTERVAL = 0.05  # Time in seconds (50ms) between each check

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
    last_restart = None  # Variable to store the last known restart time

    while True:
        current_restart = get_service_restart_time()
        if not current_restart:
            time.sleep(CHECK_INTERVAL)
            continue

        if current_restart != last_restart:
            print(f"[{datetime.now().isoformat()}] Service has restarted.")
            last_restart = current_restart
        else:
            print(f"[{datetime.now().isoformat()}] No restart detected.")

        # Wait for the next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
