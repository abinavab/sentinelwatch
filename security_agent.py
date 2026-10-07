#!/usr/bin/env python3
"""SentinelWatch security agent (LAB USE ONLY).

Generates SYNTHETIC login events and sends them to YOUR OWN SentinelWatch API.
It does not attack anything and never contacts any system except API_URL.
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "").strip()
API_KEY = os.getenv("AGENT_API_KEY", "").strip()
DEVICE = os.getenv("DEVICE_NAME", "Kali-VM")
OS_NAME = os.getenv("OPERATING_SYSTEM", "Kali Linux")
SOURCE_IP = os.getenv("SOURCE_IP", "10.0.2.15")
USERNAME = os.getenv("USERNAME_TARGET", "admin")

MESSAGES = {
    "login_success": "Successful login (synthetic lab event)",
    "login_failed": "Failed login attempt (synthetic lab event)",
    "suspicious_login": "Suspicious login pattern (synthetic lab event)",
    "logout": "User logged out (synthetic lab event)",
}


def send_event(event_type: str, username: str = USERNAME) -> bool:
    event = {
        "username": username, "source_ip": SOURCE_IP, "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(), "device_name": DEVICE,
        "operating_system": OS_NAME, "message": MESSAGES.get(event_type, "Synthetic event"),
    }
    print(f"[+] Event generated: {event_type} from {SOURCE_IP}")
    print("[+] Sending event...")
    try:
        r = requests.post(API_URL, json=event, headers={"X-API-Key": API_KEY}, timeout=20)
    except requests.RequestException as exc:
        print(f"[-] Could not reach API: {exc}")
        return False
    print(f"[+] API response: {r.status_code}")
    if r.status_code == 201:
        print("[+] Event stored successfully")
        return True
    print(f"[-] Rejected: {r.text[:200]}")
    return False


def burst(count: int, delay: float) -> None:
    print(f"\n--- Sending {count} synthetic failed-login events ---")
    ok = 0
    for i in range(1, count + 1):
        print(f"\n({i}/{count})")
        ok += send_event("login_failed")
        time.sleep(delay)
    print(f"\n[+] Done: {ok}/{count} stored. Check the dashboard for an alert.")


def menu() -> None:
    while True:
        print("\n=== SentinelWatch Security Agent ===")
        print("1) Successful login\n2) Failed login\n3) Multiple failed logins (brute-force simulation)\n4) Suspicious login\n0) Exit")
        choice = input("Choose: ").strip()
        if choice == "1": send_event("login_success")
        elif choice == "2": send_event("login_failed")
        elif choice == "3":
            n = input("How many (default 6): ").strip()
            burst(int(n) if n.isdigit() and 1 <= int(n) <= 50 else 6, 0.5)
        elif choice == "4": send_event("suspicious_login")
        elif choice == "0": break
        else: print("Invalid choice.")


def main() -> None:
    if not API_URL or not API_KEY:
        sys.exit("Set API_URL and AGENT_API_KEY in agent/.env first (see .env.example).")
    p = argparse.ArgumentParser(description="SentinelWatch lab security agent")
    p.add_argument("--mode", choices=["success", "failed", "burst", "suspicious"], help="run once, no menu")
    p.add_argument("--count", type=int, default=6, help="events for burst mode (1-50)")
    a = p.parse_args()
    if not a.mode:
        return menu()
    if a.mode == "success": send_event("login_success")
    elif a.mode == "failed": send_event("login_failed")
    elif a.mode == "suspicious": send_event("suspicious_login")
    else: burst(max(1, min(a.count, 50)), 0.5)


if __name__ == "__main__":
    main()
