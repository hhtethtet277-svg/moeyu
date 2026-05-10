import sys
import os

# လိုအပ်တဲ့ libraries တွေရှိမရှိ အရင်စစ်မယ်
try:
    import requests
    import hack  # hack.so သို့မဟုတ် hack.py ကို လှမ်းခေါ်ခြင်း
except ImportError as e:
    print(f"\n[!] Error: {e}")
    print("[*] 'pip install requests pycryptodome ping3 ntplib aiohttp' ကို အရင်သွင်းပေးပါ။")
    sys.exit()

def banner():
    print("-" * 45)
    print("      MOE YU BYPASS PRO ENGINE v5.2")
    print(" GitHub: https://github.com/hhtethtet277-svg/my-database-")
    print("-" * 45)

if __name__ == "__main__":
    os.system('clear') # Screen ကို အရင်ရှင်းမယ်
    banner()
    
    # ၁။ User ဆီကနေ Username တောင်းမယ်
    username = input("\n[+] Enter Username to access: ").strip()
    
    if not username:
        print("[!] Username ထည့်ပေးဖို့ လိုအပ်ပါတယ်။")
        sys.exit()

    try:
        # ၂။ hack.py/hack.so ထဲက check_license function ကို လှမ်းခေါ်ပြီး စစ်မယ်
        if hack.check_license(username):
            print("\n[+] Loading Bypass Engine...")
            # ဒီနေရာမှာ key မှန်ရင် ဆက်လုပ်မယ့် logic တွေကို ခေါ်လို့ရပါပြီ
            # ဥပမာ - hack.main_logic()
            
    except AttributeError:
        print("\n[!] Error: hack.so ထဲမှာ check_license ဆိုတဲ့ function ကို ရှာမတွေ့ပါ။")
    except Exception as e:
        print(f"\n[!] Error တစ်ခု တက်သွားပါသည်: {e}")
