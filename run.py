import hack
import sys

def main():
    try:
        # hack.so ထဲက feature function ကို လှမ်းခေါ်တာပါ
        hack.feature()
    except KeyboardInterrupt:
        print("\n[!] အသုံးပြုသူမှ ရပ်တန့်လိုက်ပါသည်။")
        sys.exit()
    except Exception as e:
        print(f"\n[!] Error ဖြစ်ပွားပါသည်: {e}")

if __name__ == "__main__":
    main()
