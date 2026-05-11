import hack
import sys
import urllib3

# SSL Error မတက်အောင် ပိတ်ထားခြင်း
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    try:
        # ၁။ License အရင်စစ်မယ်
        if hack.check_license():
            # ၂။ အောင်မြင်ရင် Feature ကို run မယ်
            hack.feature()
    except KeyboardInterrupt:
        print("\n[!] User မှ ရပ်တန့်လိုက်ပါသည်။")
        sys.exit()
    except Exception as e:
        print(f"\n[!] Error: {e}")
