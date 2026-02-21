#!/usr/bin/env python3
import json
import os
import sys

import fritzbox
import requests

HETZNER_API_KEY = os.getenv("HETZNER_API_KEY")
ZONE_ID = os.getenv("ZONE_ID")

RECORD_IDS = [
    r.strip() for r in (os.getenv("RECORD_IDS") or "").split(",") if r.strip()
]
RECORD_NAMES = [
    r.strip() for r in (os.getenv("RECORD_NAMES") or "").split(",") if r.strip()
]

STATE_FILE = "state.json"
BASE_URL = "https://dns.hetzner.com/api/v1"

if not HETZNER_API_KEY or not ZONE_ID or not RECORD_IDS or not RECORD_NAMES:
    print(
        "Missing configuration (HETZNER_API_KEY, ZONE_ID, RECORD_IDS)", file=sys.stderr
    )
    sys.exit(1)


def get_saved_ip():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f).get("ip")
        except Exception:
            return None
    return None


def save_ip(ip):
    with open(STATE_FILE, "w") as f:
        json.dump({"ip": ip}, f)


def update_dns(record_id, record_name, ip):
    url = f"{BASE_URL}/records/{record_id}"
    headers = {"Auth-API-Token": HETZNER_API_KEY, "Content-Type": "application/json"}
    data = {"name": record_name, "value": ip, "type": "A", "zone_id": ZONE_ID}
    r = requests.put(url, headers=headers, json=data)
    if r.status_code == 200:
        print(f"Updated record {record_id} {record_name} -> {ip}")
        return True
    else:
        print(
            f"Failed to update record {record_id} {record_name}: {r.status_code} {r.text}",
            file=sys.stderr,
        )
        return False


def main():
    ip = fritzbox.get_external_ip()
    if not ip:
        print("Warning: External IP is empty. Leaving record untouched.")
        return

    old_ip = get_saved_ip()
    if ip == old_ip:
        return  # nothing to do

    all_success = True
    for record_id, record_name in zip(RECORD_IDS, RECORD_NAMES):
        success = update_dns(record_id, record_name, ip)
        if not success:
            all_success = False

    if all_success:
        save_ip(ip)
    else:
        print("Not all updates succeeded, IP state not saved. Will retry on next run.")


if __name__ == "__main__":
    main()
