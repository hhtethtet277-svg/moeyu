import os
import re
import sys
import zlib
import json
import time
import ping3
import ntplib
import base64
import random
import string
import urllib
import marshal
import aiohttp
import asyncio
import hashlib
import argparse
import requests
import subprocess
from datetime import datetime, timedelta
from urllib.parse import quote
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Random import get_random_bytes
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
DB_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"
SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

# ANSI Colors
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

# --- Common Functions ---
def clear():
    os.system("clear")

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    logo = f"""{g} ___  ___  ________  _______           ___  ___  ___  ___ 
|  \/  |/  __  \|  ___||           |  \/  | |\  \ |  \ 
| \  / ||  |  | || |__  |           | \  / || \  \ |  \ 
| |\/| ||  |  | ||  __| |           | |\/| || \  \ |  \ 
| |  | ||  `--' || |___ |           | |  | || \  `--' / 
|_|  |_| \______/|_____||           |_|  |_| \_______/  {w}v22.0

{r} __  __  ____  _____  __  __ _   _ 
|  \/  |/ __ \|  ___||  \/  | | | |
| \  / | |  | | |__  | \  / | |_| |
| |\/| | |  | |  __| | |\/| |\   / 
| |  | | |__| | |___ | |  | | | |  
|_|  |_|\____/|_____||_|  |_| |_|  {g}
                                   
              Created by Moe Yu\033[1;00m"""
    print(logo)
    Line()
    print(f"{w}[*] This tool is created by Moe Yu")
    print(f"{w}[*] Creator telegram account @moeyu")
    print(f"{w}[*] Reseller telegram channel @starlink112")
    print(f"{w}[*] This tool is only for Ruijie Network Router")
    Line()

# --- Licensing System ---
def get_uid():
    try:
        uid_str = subprocess.check_output(['getprop', 'ro.serialno']).decode().strip()
    except:
        uid_str = str(os.getlogin()) + str(os.getuid())
    return hashlib.md5(uid_str.encode()).hexdigest()[:15].upper()

def check_license():
    user_id = get_uid()
    Logo()
    print(f"{w}[*] Checking Pro License... {y}Please wait")
    try:
        response = requests.get(DB_URL, timeout=10)
        if response.status_code != 200:
            print(f"{r}[!] Database Connection Error!")
            return False
            
        auth_data = response.text.splitlines()
        for entry in auth_data:
            if "," in entry:
                db_id, exp_date_str = entry.split(",")
                if db_id.strip() == user_id:
                    expiry_date = datetime.strptime(exp_date_str.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry_date:
                        print(f"{g}[+] Access Granted!")
                        print(f"{g}[+] Expiry: {exp_date_str}")
                        time.sleep(2)
                        return True
                    else:
                        print(f"{r}[!] License Expired on {exp_date_str}!")
                        return False
                        
        print(f"{r}[!] Unregistered Device ID!")
        print(f"{y}[*] Your ID: {user_id}")
        print(f"{w}[*] Send this ID to @moeyu to buy license.")
        return False
    except Exception as e:
        print(f"{r}[!] Check Error: {e}")
        return False

# --- Core Features Function ---
def feature():
    # ၁။ အရင်ဆုံး လိုင်စင်စစ်မည်
    if not check_license():
        sys.exit(0)

    # ၂။ လိုင်စင်အောင်မြင်မှ Argument စစ်မည်
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", help="features option", choices=["code", "internet", "check", "setup"], required=True)
    parser.add_argument("-m", "--mode", help="type of voucher code", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", help="length of voucher code(default 6)", choices=[6,7], type=int, default=6)
    parser.add_argument("-s", "--speed", help="voucher code bruteforce speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", help="number of tasks for parallel works", type=int, default=100)
    parser.add_argument("-d", "--debug", help="to show debug message", action="store_true")
    
    args = parser.parse_args() 
    
    # ၃။ Option အလိုက် Feature များ ခေါ်ယူမည်
    if args.option == "code":
        vobj = VoucherCode(is_free_user=True, mode=args.mode, length=args.length, speed=args.speed, tasks=args.tasks, debug=args.debug)
        if args.mode == "digit":
            asyncio.run(vobj.execute_digit())
        else:
            asyncio.run(vobj.execute_ascii())
            
    elif args.option == "internet":
        iobj = InternetAccess()
        asyncio.run(iobj.execute())
        
    elif args.option == "check":
        robj = RecheckVoucher()
        asyncio.run(robj.check())
        
    elif args.option == "setup":
        Setup().set()

# --- Helpers ---
async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
            return session_id
    except:
        return previous_session_id

# --- Classes ---
class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try:
            self.ip = open(".ip", "r").read().strip()
        except:
            print(f"{r}[!] Ip not found, run setup first")
            sys.exit()

    async def execute(self):
        Logo()
        print(f"{g}[+] Internet Access Bypass process running...")
        # (Internet bypass logic continues here...)

class VoucherCode:
    def __init__(self, is_free_user, mode, length, speed, tasks, debug):
        self.mode, self.length, self.speed, self.tasks, self.debug = mode, length, speed, tasks, debug
        self.file = f"failed_{self.mode}_{self.length}.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except:
            print(f"{r}[!] Session url not found, run setup first")
            sys.exit()

    async def execute_digit(self):
        Logo()
        print(f"{g}[+] Digit Brute-force starting...")
        # (Digit brute logic continues here...)

    async def execute_ascii(self):
        Logo()
        print(f"{g}[+] ASCII Brute-force starting...")
        # (ASCII brute logic continues here...)

async def login_voucher(session, session_id, voucher, file=None, check=False, debug=False):
    global SUCCESS
    # (Voucher login logic continues here...)

# --- (Other classes: RecheckVoucher, Setup stay same) ---
class RecheckVoucher:
    async def check(self):
        # (Recheck logic)
        pass

class Setup:
    def set(self):
        # (Setup logic)
        pass

if __name__ == "__main__":
    try:
        feature()
    except KeyboardInterrupt:
        print(f"\n{r}[!] Stopped by user.")
        sys.exit(0)
