import discord
import datetime
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

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
@commands.has_permissions(administrator=True)
async def dmbomb(ctx, times: int, user_id: int, *, message: str):
    user = bot.get_user(user_id)
    if user is None:
        print(f"User with ID {user_id} not found.")
        return
    for i in range(times):
        try:
            await user.send(message)
        except discord.Forbidden:
            print(f"User {user.name} has blocked the bot.")
            # Log the error to the console or a log file
            print(f"ERROR: {user.name} has blocked the bot.")
            # Ban the user from the server
            await ctx.guild.ban(user, reason="User has blocked the bot.")

@bot.command()
@commands.has_permissions(administrator=True)
async def chbomb(ctx, times: int, user_id: int, channel: discord.TextChannel, *, message: str):
    user = bot.get_user(user_id)
    for i in range(times):
        try:
            await channel.send(f"Sending message {i+1} of {times} to {user.mention}: {message}")
            await user.send(message)
        except discord.errors.Forbidden:
            print(f"{user.mention} has blocked the bot and has been banned from the server.")
            await user.ban(reason="Blocked bot during chbomb command.")
            break
    print(f"Finished sending {times} messages to {user.mention}.")

@bot.command()
async def spmove(ctx, num_moves: int, user_id: int, channel: discord.VoiceChannel):
    user = ctx.guild.get_member(user_id)
    if user is None:
        print("User not found.")
        return
    original_channel = user.voice.channel
    for i in range(num_moves):
        await user.move_to(channel)
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=1))
        await user.move_to(original_channel)
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=1))
    print(f"Moved {user.name} back and forth between {channel.name} and {original_channel.name} {num_moves} times.")

@bot.command()
@commands.has_permissions(administrator=True)
async def chngrpc(ctx, *, rpc_name: str):
    activity = discord.Activity(name=rpc_name, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)
    print(f"Changed Rich Presence to: {rpc_name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit+1)
    print(f"{limit} messages have been purged by {ctx.author.mention}.", delete_after=5)

bot.run(API_TOKEN)