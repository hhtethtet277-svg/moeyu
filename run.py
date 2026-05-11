import hack
import os
import sys

# hhh.so ဖိုင်ရှိမရှိ စစ်ဆေးခြင်း
if not os.path.exists("hhh.so"):
    print("\033[1;31m[!] Error: hhh.so file not found. Please compile your script first.")
    sys.exit()

try:
    # hhh.so ထဲက feature ကို import လုပ်ခြင်း
    from hhh import feature
    
    if __name__ == "__main__":
        # hhh.so ထဲက main feature function ကို စတင် run ခြင်း
        feature()
except Exception as e:
    print(f"\033[1;31m[!] Run Error: {e}")
