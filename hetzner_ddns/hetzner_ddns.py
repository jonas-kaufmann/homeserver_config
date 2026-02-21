#!/usr/bin/env python3
import datetime
import json
import os
import sys

import fritzbox
import hcloud
import hcloud.zones as zones

HETZNER_API_TOKEN = os.getenv("HETZNER_API_TOKEN")
MY_DOMAIN = os.getenv("MY_DOMAIN")
RECORD_NAMES = [
    r.strip() for r in (os.getenv("RECORD_NAMES") or "").split(",") if r.strip()
]

STATE_FILE = "state.json"

if not HETZNER_API_TOKEN or not MY_DOMAIN or not RECORD_NAMES:
    print(
        "Missing configuration (HETZNER_API_TOKEN, MY_DOMAIN, RECORD_NAMES)",
        file=sys.stderr,
    )
    sys.exit(1)

client = hcloud.Client(token=HETZNER_API_TOKEN)


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


def update_dns(domain: str, record_name: str, ip: str):
    try:
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = client.zones.set_rrset_records(
            rrset=zones.ZoneRRSet(
                zone=zones.Zone(name=domain),
                name=record_name,
                type="A",
            ),
            records=[zones.ZoneRecord(value=ip, comment=time_now)],
        )
        action.wait_until_finished()

        print(f"Updated record {record_name} -> {ip}")
        return True

    except Exception as e:
        print(
            f"Failed to update record {record_name}: {e}",
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
        return

    all_success = True
    for record_name in RECORD_NAMES:
        success = update_dns(MY_DOMAIN, record_name, ip)
        if not success:
            all_success = False

    if all_success:
        save_ip(ip)
    else:
        print("Not all updates succeeded, IP state not saved. Will retry.")


if __name__ == "__main__":
    main()
