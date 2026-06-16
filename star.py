import os
import re
import socket
import json
import base64
import time
import sys
import uuid
from typing import Optional, Dict, Any
import requests
import urllib3

# Suppress insecure request warnings safely
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    """Utility class for terminal text color formatting."""
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    WHITE = "\033[1;00m"
    CYAN = "\033[1;36m"
    MAGENTA = "\033[1;35m"
    RESET = "\033[0m"


class WiFiBypassTool:
    # သင်တောင်းဆိုထားသော URL အသေ
    FIXED_URL = (
        "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=984a6b46cc8b&gw_sn=H1U0488004405&"
        "gw_address=192.168.61.1&gw_port=2060&ip=192.168.61.202&mac=0a:37:c4:3f:36:89&slot_num=37&"
        "nasip=192.168.1.222&ssid=Zin%20Myo%20Aung&ustate=0&mac_req=1&url=http%3A%2F%2Fhttpbin.org%2Fget&"
        "chap_id=%5C122&chap_challenge=%5C303%5C112%5C252%5C022%5C100%5C060%5C144%5C015%5C052%5C103%5C070%5C254%5C266%5C110%5C270%5C162"
    )
    
    AUTH_ENDPOINT = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    USER_AGENT = (
        "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
    )

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})
        self.session.verify = False  

    @staticmethod
    def clear_screen() -> None:
        os.system('clear' if os.name == 'posix' else 'cls')

    @staticmethod
    def animate_text(text: str, delay: float = 0.02) -> None:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def detect_mac_address() -> str:
        try:
            mac_num = hex(uuid.getnode())[2:].zfill(12)
            formatted_mac = ":".join(mac_num[i:i+2] for i in range(0, 12, 2))
            if len(formatted_mac) == 17:
                return formatted_mac
        except Exception:
            pass
        return "0a:37:c4:3f:36:89"

    @staticmethod
    def detect_gateway_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            ip_parts = local_ip.split('.')
            if ip_parts[0] in ["192", "10", "172"]:
                ip_parts[-1] = "1"
                return ".".join(ip_parts)
        except Exception:
            pass
        return "192.168.61.1"

    @staticmethod
    def animate_loading_bar(duration: float = 1.5, description: str = "Processing") -> None:
        frames = ["[ ■ □ □ □ ]", "[ ■ ■ □ □ ]", "[ ■ ■ ■ □ ]", "[ ■ ■ ■ ■ ]"]
        steps = len(frames)
        interval = duration / steps
        
        for frame in frames:
            sys.stdout.write(f"\r{Colors.MAGENTA}{description} {Colors.CYAN}{frame}")
            sys.stdout.flush()
            time.sleep(interval)
        sys.stdout.write(f"\r{Colors.MAGENTA}{description} {Colors.GREEN}[ Complete ]\n{Colors.WHITE}")
        sys.stdout.flush()

    def print_banner(self) -> None:
        c, r, y, g, m, w = Colors.CYAN, Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.MAGENTA, Colors.WHITE
        print(f"{c}╔" + "═" * 75 + f"╗")
        print(f"{c}║{r}   ██████╗ ███████╗ ██████╗ ██╗  ██╗     ██╗  ██╗   █████╗    {c}║")
        print(f"{c}║{r}   ██╔══██╗██╔════╝██╔═══██╗██║  ██║     ██║ ██╔╝  ██╔══██╗   {c}║")
        print(f"{c}║{y}   ██████╔╝███████╗██║   ██║███████║     █████╔╝   ███████║   {c}║")
        print(f"{c}║{y}   ██╔══██╗╚════██║██║   ██║██╔══██║     ██╔═██╗   ██╔══██║   {c}║")
        print(f"{c}║{g}   ██║  ██║███████║╚██████╔╝██║  ██║     ██║  ██╗  ██║  ██║   {c}║")
        print(f"{g}   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝  ╚═╝  ╚═╝  ╚═╝   {g}║")
        print(f"{c}╠" + "═" * 75 + f"╣")
        print(f"{c}║{m}                         ✦ RSHO KA WiFi Bypass ✦                          {c}║")
        print(f"{c}╚" + "═" * 75 + f"╝{w}")

    def _replace_mac(self, url: str, new_mac: str) -> str:
        return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

    def get_session_id(self, session_url: str, mac_address: str) -> Optional[str]:
        final_url = self._replace_mac(session_url, mac_address)
        headers = {'Referer': final_url}
        try:
            response = self.session.get(final_url, headers=headers, timeout=10)
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url)
            return match.group(1) if match else None
        except requests.RequestException as e:
            print(f"{Colors.RED}[-] Error Getting Session ID: {e}{Colors.WHITE}")
            return None

    def login_voucher(self, session_id: str, voucher: str) -> Optional[str]:
        payload = {
            "accessCode": voucher,
            "sessionId": session_id,
            "apiVersion": 1
        }
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://portal-as.ruijienetworks.com",
            "Referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={session_id}",
        }
        try:
            response = self.session.post(self.AUTH_ENDPOINT, json=payload, headers=headers, timeout=10)
            match = re.search(r'token=(.*?)&', response.text)
            return match.group(1) if match else None
        except requests.RequestException as e:
            print(f"{Colors.RED}[-] Voucher Login Error: {e}{Colors.WHITE}")
            return None

    def execute_bypass(self) -> None:
        self.clear_screen()
        self.print_banner()
        
        session_url = self.FIXED_URL
        mac_address = self.detect_mac_address()
        gateway_ip = self.detect_gateway_ip()
        
        print(f"{Colors.YELLOW}[!] အချက်အလက်များ ထည့်သွင်းပါ{Colors.WHITE}\n")
        
        voucher = input(f"{Colors.GREEN} ➢ Voucher Code ထည့်ပါ : {Colors.WHITE}").strip()

        if not voucher:
            print(f"{Colors.RED}[-] Voucher Code မရှိဘဲ ရှေ့ဆက်၍မရပါ။{Colors.WHITE}")
            return

        print()
        print(f"{Colors.CYAN}[+] Auto Detected MAC   : {Colors.WHITE}{mac_address}")
        print(f"{Colors.CYAN}[+] Auto Detected GW IP : {Colors.WHITE}{gateway_ip}\n")
        
        self.animate_loading_bar(duration=1.2, description="[⏳] Initializing Pipeline")
        
        session_id = self.get_session_id(session_url, mac_address)
        if not session_id:
            print(f"\n{Colors.RED}[-] Bypass Failed to get Session ID.{Colors.WHITE}")
            return
        print(f"{Colors.CYAN}[+] Inactive Session Id :{Colors.WHITE} {session_id}")
            
        active_session_id = self.login_voucher(session_id, voucher)
        if not active_session_id:
            print(f"\n{Colors.RED}[-] Bypass Failed to active voucher.{Colors.WHITE}")
            return
        print(f"{Colors.CYAN}[+] Active Session Id   :{Colors.WHITE} {active_session_id}")

        params = {
            'token': active_session_id,
            'phoneNumber': 'RSHO_KA_User',
        }
        
        try:
            final_req_url = f'http://{gateway_ip}:2060/wifidog/auth?'
            response = self.session.get(final_req_url, params=params, timeout=10)
            
            success_conditions = ["baidu.com", "success.html", "success"]
            if any(cond in response.url.lower() or cond in response.text.lower() for cond in success_conditions):
                self.animate_text(f"\n{Colors.GREEN}[ ✔ ] Internet Bypass Successful! Enjoy your connection.{Colors.WHITE}", delay=0.01)
            else:
                print(f"\n{Colors.RED}[ ✘ ] Internet Bypass Failed or Unknown Response Route.{Colors.WHITE}")
        except requests.RequestException as e:
            print(f"\n{Colors.RED}[ ✘ ] Auth Gateway connection error: {e}{Colors.WHITE}")


if __name__ == "__main__":
    try:
        tool = WiFiBypassTool()
        tool.execute_bypass()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!] Exiting...{Colors.WHITE}")
