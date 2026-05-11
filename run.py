import hack
import sys

if __name__ == "__main__":
    # ၁။ License ကို အရင်ဆုံး စစ်ဆေးမယ်
    if hack.check_license():
        # ၂။ License မှန်မှသာ ကျန်တဲ့ Setup လုပ်ငန်းစဉ်တွေကို လုပ်မယ်
        print("\033[1;32m[+] Setting up the wifi info...")
        # သင့်ရဲ့ ကျန်တဲ့ feature code တွေကို ဒီအောက်မှာ ထည့်ပါ
        hack.feature()
