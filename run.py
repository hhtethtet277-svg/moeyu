import hack
import sys

if __name__ == "__main__":
    # ၁။ အရင်ဆုံး License စစ်မယ်
    if hack.check_license():
        # ၂။ License အောင်မြင်ရင် Main Feature ကို run မယ်
        # သင့် code ထဲက argparse က sys.argv ကို ဖတ်မှာဖြစ်လို့ 
        # command line က ပေးလိုက်တဲ့ -o internet စတာတွေ auto အလုပ်လုပ်ပါမယ်
        hack.feature()
