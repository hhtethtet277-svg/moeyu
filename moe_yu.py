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
from concurrent.futures import ThreadPoolExecutor

# --- Database Configuration ---
DB_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

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
                        time.sleep(1)
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

# --- Class Dummy Structures (သင့်ရဲ့ Original Code Logic များ ဤနေရာတွင် ထည့်ပါ) ---

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode = mode
        self.length = length
        
    async def execute_digit(self):
        print(f"{g}[+] Hacking Voucher Codes (Digit Mode)...")
        # Bruteforce logic များကို ဤနေရာတွင် ဆက်ရေးပါ
        
    async def execute_ascii(self):
        print(f"{g}[+] Hacking Voucher Codes (ASCII Mode)...")

class InternetAccess:
    async def execute(self):
        print(f"{g}[+] Bypassing Internet Access...")

class RecheckVoucher:
    async def check(self):
        print(f"{g}[+] Checking Router Status...")

# --- Main Feature Controller ---

def main():
    # ၁။ အရင်ဆုံး လိုင်စင်စစ်မည်
    if not check_license():
        sys.exit()

    # ၂။ လိုင်စင်အောင်မြင်မှ Argument Parser ကို စတင်မည်
    parser = argparse.ArgumentParser(description="Moe Yu Pro Engine")
    parser.add_argument("-o", "--option", choices=["code", "internet", "check", "setup"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", choices=[6,7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    
    # Command line ကနေရိုက်လိုက်တဲ့ option တွေကို ဖတ်မယ်
    args = parser.parse_args() 

    # ၃။ ရွေးချယ်လိုက်တဲ့ Option အလိုက် Feature များကို Run မည်
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
        print(f"{y}[*] Setup Mode Started...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{r}[!] Stopped by user.")
        sys.exit()
