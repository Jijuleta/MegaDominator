import discord
import datetime
import asyncio
import os
from discord.ext import commands
from discord.utils import get
from config import API_TOKEN
from typing import Union

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

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    activity = discord.Activity(name="абрусил саси хахаха", type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)

@bot.command()
#@commands.has_permissions(administrator=True)
async def dmbomb(ctx, times: int, user_id: int, *, message: str):
    if times > 100:
        await ctx.send("Максимальное количество перемещений - 100.")
        return
    user = bot.get_user(user_id)
    if user is None:
        print(f"User with ID {user_id} not found.")
        return
    for i in range(times):
        try:
            await user.send(message)
            print(f'Dmbombing {user} with "{message}" message')
        except discord.Forbidden:
            print(f"User {user.name} has blocked the bot.")
            await ctx.guild.ban(user, reason="User has blocked the bot.")
    
    await ctx.send(f'{user} был изнасилован в личных сообщениях {times} раз.')


"""@dmbomb.error
async def dmbomb_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")"""

@bot.command()
#@commands.has_permissions(administrator=True)
async def chbomb(ctx, times: int, user_id: int):
    if times > 100:
        await ctx.send("Максимальное количество перемещений - 100.")
        return
    user = bot.get_user(user_id)
    if user is None:
        print(f"User with ID {user_id} not found.")
        return

    channel = await ctx.guild.create_text_channel(name=f"chbomb-{user_id}")
    await channel.set_permissions(user, read_messages=True, send_messages=True)

    for i in range(times):
        print(f'Chbombing {user} {i+1}/{times} times')
        await channel.send(f"Придурок на {user.mention}, тебя чпокнули {i+1}/{times} раз")
    await ctx.send(f"{user} был чпокнут в канале {times} раз.")
    await asyncio.sleep(180)
    await channel.delete()


"""@chbomb.error
async def chbomb_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")"""



@bot.command()
async def spmove(ctx, num_moves: int, user_id: int, channel: discord.VoiceChannel):
    if num_moves > 100:
        await ctx.send("Максимальное количество перемещений - 100.")
        return
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
    await ctx.send(f"Пользователь {user.name} был перемещен между {channel.name} и {original_channel.name} {num_moves} раз.")


@bot.command()
async def chngrpc(ctx, *, rpc_name: str):
    activity = discord.Activity(name=rpc_name, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)
    print(f"Changed Rich Presence to: {rpc_name}")
    await ctx.send(f"Rich Presence был изменен на: {rpc_name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, limit: int):
    if limit > 100:
        await ctx.send("Максимальное количество перемещений - 100.")
        return
    deleted = await ctx.channel.purge(limit=limit+1)
    await ctx.send(f"{len(deleted) - 1} сообщений было успешно удалено!")
    
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")

@bot.command()
async def id(ctx, user: Union[discord.Member, int]):
    if isinstance(user, int):
        try:
            user = await bot.fetch_user(user)
        except discord.NotFound:
            return await ctx.send('Неверный ID пользователя.')
    elif isinstance(user, discord.Member):
        pass
    else:
        return await ctx.send('Неправильный ввод.')
    
    await ctx.send(f"ID пользователя {user.display_name} - {user.id}")

# MUSIC FEATURES
# $play - {s(single) or p(playlist)} {song or name of playlist}
# $stop - останавливает воспроизведение песни.
# $skip - пропускает песню.
# $list {l(list of all songs) or p(playlists)} - показывает список всех песен или всех плейлистов.
# $queue - показывает текущую очередь.
# $create_playlist {name of playlist} {songs}.




@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Команды бота", color=0x00ff00)
    embed.add_field(name="$dmbomb [times] [user_id] [message]", value="Отправить сообщение в личку определенное количество раз.", inline=False)
    embed.add_field(name="$chbomb [times] [user_id]", value="Создать временный канал, где человек будет тегнут определенное количество раз.", inline=False)
    embed.add_field(name="$spmove [num_moves] [user_id] [channel]", value="Супер-перемещение между оригинальным и указанным каналом.", inline=False)
    embed.add_field(name="$chngrpc [rpc_name]", value="Поменять Rich Presence бота.", inline=False)
    embed.add_field(name="$purge [limit]", value="Удалить определенное количество сообщений в канале.(требуются админ права)", inline=False)
    embed.add_field(name="$id [@user] or [user id]", value="При умоминании пользователя выводит его ID, если отправить ID пользователя, то бот отправит владельца ID.")
    embed.add_field(name=" ",value=" ", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name="Автор замечательного бота:", value="Прекрасный Витюша Мастифф!!!", inline=False)
    await ctx.send(embed=embed)

bot.run(API_TOKEN)