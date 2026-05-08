Import os
import requests
import sys

# ၁။ HWID ထုတ်ယူခြင်း (Termux အတွက်)
def get_hwid():
    return os.popen("getprop ro.serialno").read().strip()

# ၂။ GitHub က key.txt (ဝယ်သူစာရင်းဖိုင်) ရဲ့ Raw Link
DB_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/main/key.txt"

def check_access():
    hwid = get_hwid()
    print(f"Your HWID: {hwid}")
    
    try:
        response = requests.get(DB_URL)
        # key.txt ထဲမှာ ဒီ HWID ရှိမရှိ စစ်တာပါ
        if hwid in response.text:
            print("Access Granted! Loading Tool...")
            import hack  # hack.so ကို ခေါ်သုံးတာပါ ( .so ထည့်စရာမလို)
        else:
            print("Access Denied! Please buy a key and send your HWID.")
            sys.exit()
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    check_access()

ဘယ်မှာ ထည့်ရမှာလဲ
