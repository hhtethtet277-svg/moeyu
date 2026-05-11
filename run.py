import os
import sys

# hack.so ကို import လုပ်မယ်
try:
    import hack
except ImportError:
    print("\033[1;31m[!] Error: hack.so file not found.")
    sys.exit()

if __name__ == "__main__":
    try:
        # hack.so ထဲက feature() ကို လှမ်းခေါ်တာနဲ့ 
        # license အရင်စစ်ပြီး feature logic တွေ ဆက်သွားပါလိမ့်မယ်
        hack.feature()
    except KeyboardInterrupt:
        print("\n\033[1;33m[*] Stopped.")
    except Exception as e:
        print(f"\n\033[1;31m[!] Error: {e}")
