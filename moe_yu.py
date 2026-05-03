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

# --- Database Configuration ---
# GitHub က သင့်ရဲ့ link အတိုင်း ချိတ်ဆက်ထားပါတယ်
DB_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

# ANSI Color codes
w = "\033[1;00m" # White
g = "\033[1;32m" # Green
y = "\033[1;33m" # Yellow
r = "\033[1;31m" # Red
b = "\033[1;34m" # Blue

def clear():
    os.system("clear")

def Line():
    print(f"{y}─\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    # ပုံထဲကအတိုင်း Logo ကို Design ပြန်ထုတ်ထားပါတယ်
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
    print(f"{w}[*] Developer : Moe Yu")
    print(f"{w}[*] Telegram  : @moeyu")
    print(f"{w}[*] Channel   : @starlink112")
    print(f"{w}[*] Target    : Ruijie Network Router")
    Line()

# --- Licensing & Expiry System ---

def get_uid():
    """ထုတ်ကုန်ရောင်းဖို့အတွက် ခိုင်မာတဲ့ Device ID ထုတ်တဲ့အပိုင်း"""
    try:
        # Termux environment specific ID
        uid_str = subprocess.check_output(['getprop', 'ro.serialno']).decode().strip()
    except:
        uid_str = str(os.getlogin()) + str(os.getuid())
    return hashlib.md5(uid_str.encode()).hexdigest()[:15].upper()

def check_license():
    """GitHub က key.txt ကိုဖတ်ပြီး ID နဲ့ ရက်စွဲ စစ်ဆေးတဲ့အပိုင်း"""
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
                    # ရက်စွဲ စစ်ဆေးခြင်း
                    expiry_date = datetime.strptime(exp_date_str.strip(), "%Y-%m-%d")
                    current_date = datetime.now()
                    
                    if current_date < expiry_date:
                        remaining = expiry_date - current_date
                        print(f"{g}[+] Access Granted!")
                        print(f"{g}[+] Expiry: {exp_date_str} ({remaining.days} days left)")
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

# --- Core Features ---

def feature():
    # Program စတာနဲ့ License အရင်စစ်မယ်
    if not check_license():
        sys.exit()

    Logo()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet", "check", "setup"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", choices=[6,7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    
    args = parser.parse_args() 
    
    # Feature logic (Original code အတိုင်း)
    if args.option == "code":
        vobj = VoucherCode(mode=args.mode, length=args.length, speed=args.speed, tasks=args.tasks, debug=args.debug)
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

# --- Classes (InternetAccess, VoucherCode, Setup) ---
# Original code ထဲက logic တွေကို ဒီအောက်မှာ ဆက်လက်ထည့်သွင်းနိုင်ပါတယ်
# (နေရာလွတ်သက်သာရန် အရေးကြီးဆုံး Licensing ပိုင်းကို ဦးစားပေးရေးထားပါတယ်)

class InternetAccess:
    def __init__(self):
        # Base64 encoded URL များကို ဒီမှာ ပြန်ထည့်ပါ
        self.session_url = "https://portal-as.ruijienetworks.com/api/auth/wifidog..." 
        try:
            self.ip = open(".ip", "r").read().strip()
        except:
            print(f"{r}[!] Run setup first!")
            sys.exit()

    async def execute(self):
        Logo()
        print(f"{g}[+] Pro Internet Access Running...")
        # ... (Original code logic)

# ... (VoucherCode, RecheckVoucher နှင့် Setup Class များ အရင်အတိုင်း ထည့်ပါ)

if __name__ == "__main__":
    try:
        feature()
    except KeyboardInterrupt:
        print(f"\n{r}[!] Stopped by user.")
        sys.exit()
