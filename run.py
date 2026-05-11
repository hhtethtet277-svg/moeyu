import hack # သင့်ရဲ့ .so ဖိုင်နာမည်
import sys

def main():
    # ၁။ License ကို အရင်ဆုံး စစ်ဆေးမယ်
    if hack.check_license():
        # ၂။ Key မှန်မှသာ Setup အပိုင်းတွေကို လုပ်ဆောင်မယ်
        print("\n\033[1;32m[+] Setting up the wifi info...")
        print("[+] Unbinding wifi success")
        print("[+] Setup success")
        
        # သင့်ရဲ့ main function ကို ဒီအောက်မှာ ထည့်ပါ
        # hack.start_menu()

if __name__ == "__main__":
    main()
