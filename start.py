import argparse
import hack

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output")
    parser.add_argument("-m", "--mode")
    parser.add_argument("-l", "--length", type=int)
    parser.add_argument("-s", "--size", type=int)
    
    args = parser.parse_args()
    
    print(f"Output: {args.output}")
    print(f"Mode: {args.mode}")
    print(f"Length: {args.length}")
    print(f"Size: {args.size}")

    # ဒီနေရာမှာ hack.so ထဲက logic ကို လှမ်းခေါ်ပါ
    # hack.process(args.mode, args.length)

if __name__ == "__main__":
    main()
