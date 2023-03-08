import discord
from discord.ext import commands
from config import API_TOKEN
# u have to create config.py and create API_TOKEN variable.

# Команды & фичи бота:
# dmbomb - используется для бомбинга лички.
# spmove - используется для многократного перемещения из оригинального канала в указанный.
# chbomb - используется для бомбинга в канале сервера
# chngrpc - используется для смены rpc бота.
# autoban - если указанный пользователь в dmbomb заблокировал бота, то происходит бан с последующим тегом этого человека в каком-то канале.

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, activity=discord.Game(name='Трахаю в задницу'))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def dmbomb(ctx, times: int, id: int, mess: str):
    for i in range(times):
        user = bot.get_user(id)
        await user.send(mess)

@bot.command()
async def spmove(ctx, times: int, id: int, dest: int):
    for i in range(times):
        print()

@bot.command()
async def joined(ctx, member: discord.Member):
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')

bot.run(API_TOKEN)