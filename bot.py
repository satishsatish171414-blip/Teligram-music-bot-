import pyrogram.errors
pyrogram.errors.GroupcallForbidden =    getattr(pyrogram.errors, "GroupCallForbidden", Exception)

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL
from config import BOT_TOKEN, API_ID, API_HASH, SESSION_NAME

bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
call_py = PyTgCalls(user)

queues = {}

YTDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch1",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "opus"}],
}

def get_audio(query):
    os.makedirs("downloads", exist_ok=True)
    with YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        return info.get("title", "Unknown"), ydl.prepare_filename(info).rsplit(".", 1)[0] + ".opus"

async def play_next(chat_id):
    q = queues.get(chat_id, [])
    if not q:
        return
    title, path = q[0]
    await call_py.play(chat_id, MediaStream(path))

@bot.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text("🎵 Music Bot ready!\n\n/play <song>\n/skip\n/stop\n/queue")

@bot.on_message(filters.command("play") & filters.group)
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("Usage: /play <song name or YouTube URL>")
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔎 Searching/downloading...")
    try:
        title, path = await asyncio.to_thread(get_audio, query)
        chat_id = m.chat.id
        queues.setdefault(chat_id, []).append((title, path))
        if len(queues[chat_id]) == 1:
            await call_py.join_group_call(chat_id, MediaStream(path))
        await status.edit_text(f"🎵 Added: **{title}**")
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")

@bot.on_message(filters.command("queue") & filters.group)
async def queue(_, m: Message):
    q = queues.get(m.chat.id, [])
    if not q:
        return await m.reply_text("📭 Queue empty.")
    await m.reply_text("📜 Queue:\n" + "\n".join(f"{i+1}. {x[0]}" for i, x in enumerate(q)))

@bot.on_message(filters.command("skip") & filters.group)
async def skip(_, m: Message):
    chat_id = m.chat.id
    q = queues.get(chat_id, [])
    if not q:
        return await m.reply_text("📭 Nothing is playing.")
    q.pop(0)
    if q:
        await call_py.change_stream(chat_id, MediaStream(q[0][1]))
        await m.reply_text(f"⏭️ Playing: **{q[0][0]}**")
    else:
        await call_py.leave_group_call(chat_id)
        await m.reply_text("⏹️ Queue finished.")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, m: Message):
    chat_id = m.chat.id
    queues.pop(chat_id, None)
    try:
        await call_py.leave_group_call(chat_id)
    except Exception:
        pass
    await m.reply_text("⏹️ Stopped.")

async def main():
    await user.start()
    await bot.start()
    await call_py.start()
    print("Music bot is running.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
