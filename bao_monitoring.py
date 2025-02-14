#!/usr/bin/env python3

import subprocess
from datetime import datetime
import time

# Configuration
SERVICE_NAME = "sol"
CHECK_INTERVAL = 0.05  # 50ms between each check

def get_service_status():
    """Get the current status of the service using systemctl."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()  # Returns 'active', 'inactive', or 'failed'
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error fetching service status: {e}")
        return "unknown"

def main():
    print(f"[{datetime.now().isoformat()}] Starting monitoring...")
    last_status = None  # Variable to store the last known status

    while True:
        current_status = get_service_status()
        
        if current_status != last_status:
            print(f"[{datetime.now().isoformat()}] Service status changed: {current_status}")
            last_status = current_status
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
