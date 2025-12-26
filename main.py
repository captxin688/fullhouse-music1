import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os # 1. เพิ่ม import os
from dotenv import load_dotenv # 2. เพิ่ม import dotenv
from keep_alive import keep_alive
# 3. โหลดค่าจากไฟล์ .env เข้ามาในระบบ
load_dotenv()

# ตั้งค่า Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ตัวแปรเก็บคิวเพลง
music_queue = [] 

# ปรับ FFmpeg ให้ Buffer เยอะขึ้น กันกระตุก
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

# ปรับ yt_dlp ให้เบาเครื่องที่สุด
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': False,       # 1. เปลี่ยนเป็น False เพื่อให้เราเห็น Error จริงๆ ใน Log
    'no_warnings': False, # 2. เปลี่ยนเป็น False จะได้เห็นคำเตือน
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt',
    # 3. เพิ่มส่วนนี้เข้าไป (สำคัญ)
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
}

@bot.event
async def on_ready():
    print(f'✅ ล็อกอินในชื่อ {bot.user} พร้อมทำงาน!')

# ฟังก์ชันเล่นเพลง
def play_next(ctx):
    if len(music_queue) > 0:
        song_url, title = music_queue.pop(0)
        vc = ctx.voice_client
        
        try:
            source = discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
            source = discord.PCMVolumeTransformer(source, volume=0.1)
            
            vc.play(source, after=lambda e: play_next(ctx))
            
            asyncio.run_coroutine_threadsafe(ctx.send(f"▶️ กำลังเล่น: **{title}**"), bot.loop)
        except Exception as e:
            print(f"Error playing song: {e}")
            play_next(ctx) 
    else:
        if ctx.voice_client and ctx.voice_client.is_connected():
            asyncio.run_coroutine_threadsafe(ctx.send("✅ หมดคิวเพลงแล้วครับ"), bot.loop)

@bot.command(name='fullhouse') 
async def play(ctx, *, search: str): 
    if not ctx.author.voice:
        await ctx.send("❌ กรุณาเข้าห้อง Voice ก่อนสั่งเพลงครับ")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    msg = await ctx.send(f"🔎 กำลังค้นหา: **{search}**...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(search, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]

            song_url = data['url']
            title = data.get('title', 'Unknown Title')

            music_queue.append((song_url, title))
            
            await msg.delete()

            if not ctx.voice_client.is_playing():
                play_next(ctx)
            else:
                await ctx.send(f"📝 เพิ่มเข้าคิวแล้ว ({len(music_queue)}): **{title}**")

    except Exception as e:
        await msg.edit(content=f"⚠️ เกิดข้อผิดพลาด: หาเพลงไม่เจอหรือลิงก์ผิด")
        print(e)

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop() 
        await ctx.send("⏭️ ข้ามเพลงเรียบร้อย!")
    else:
        await ctx.send("❌ ไม่มีการเล่นเพลงอยู่")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        music_queue.clear()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("👋 บายครับ!")
    else:
        await ctx.send("❌ บอทไม่ได้อยู่ในห้อง")

@bot.command(name='queue')
async def show_queue(ctx):
    if len(music_queue) == 0:
        await ctx.send("📭 คิวว่างเปล่า")
    else:
        queue_list = "\n".join([f"{i+1}. {title}" for i, (url, title) in enumerate(music_queue[:10])])
        if len(music_queue) > 10:
            queue_list += f"\n... และอีก {len(music_queue)-10} เพลง"
        await ctx.send(f"🎵 **คิวเพลงรอเล่น:**\n{queue_list}")

# 4. เปลี่ยนจากการใส่ Token ตรงๆ เป็นการดึงจาก os.getenv
# ตรวจสอบว่ามี Token หรือไม่เพื่อป้องกัน Error
keep_alive()

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ ไม่พบ Token! กรุณาตรวจสอบไฟล์ .env")