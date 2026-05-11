import hack # hhh.py ကို hack လို့ နာမည်ပေးထားရင်
import sys

def main():
    # ၁။ License ကို အရင်ဆုံး စစ်ဆေးမယ်
    if hack.check_license():
        # ၂။ License မှန်မှသာ ကျန်တဲ့ Setup အပိုင်းတွေကို လုပ်ဆောင်မယ်
        print("\n\033[1;32m[+] Setting up the wifi info...")
        print("[+] Unbinding wifi success")
        print("[+] Trying to get info")
        print("[+] Setup success")
        
        # သင့်ရဲ့ main feature ကို ဒီမှာ ခေါ်သုံးပါ
        # hack.feature() 

if __name__ == "__main__":
    main()
