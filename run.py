import os
import requests

# GitHub က Raw URL ကို ထည့်ပါ
raw_url = "https://raw.githubusercontent.com/hhtethtet277-svg/moeyu/refs/heads/main/hack.cpython-313-aarch64-linux-android.so"

def loader():
    if not os.path.exists("hack.so"):
        print("[+] Module မရှိသေးသဖြင့် GitHub မှ Download ဆွဲနေသည်...")
        r = requests.get(raw_url, verify=False)
        with open("hack.so", "wb") as f:
            f.write(r.content)
    
    try:
        from hack import feature
        feature()
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    loader()
