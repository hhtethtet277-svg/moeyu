import sys
import os

# requests နဲ့ တခြား လိုအပ်တဲ့ libraries တွေ ရှိမရှိ စစ်ဆေးပြီး မရှိရင် error ပြပေးမယ့်အပိုင်း
try:
    import requests
    import Crypto
    import ping3
    import ntplib
    import aiohttp
except ImportError:
    print("\n[!] လိုအပ်သော Libraries များ မရှိသေးပါ။")
    print("[*] 'pip install requests pycryptodome ping3 ntplib aiohttp' ကို ရိုက်ပြီး အရင်သွင်းပါ။\n")
    sys.exit()

def banner():
    print("-" * 45)
    print("      MOE YU BYPASS PRO ENGINE v5.2")
    print(" GitHub: https://github.com/hhtethtet277-svg/my-database-")
    print("-" * 45)

if __name__ == "__main__":
    banner()
    
    try:
        # hack.so (သို့မဟုတ် hack.py) ကို import လုပ်လိုက်တာနဲ့ 
        # အထဲက logic တွေက တန်းပြီး အလုပ်လုပ်ပါလိမ့်မယ်။
        import hack
        
    except Exception as e:
        print(f"\n[!] Error တစ်ခု တက်သွားပါသည်: {e}")
