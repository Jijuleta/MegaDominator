import discord
import datetime
import asyncio
import os
import random
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from config import API_TOKEN
from collections import deque

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

MUSIC_LIBRARY_PATH = './media/'
audio_files = [f for f in os.listdir(MUSIC_LIBRARY_PATH) if f.endswith('.mp3') or f.endswith('.wav') or f.endswith('.mp4')]

song_queue = deque()

@bot.command()
async def list(ctx):
    song_list = '\n'.join([f'{i}. {song}' for i, song in enumerate(audio_files, start=1)])
    await ctx.send(f'Доступные песни:\n{song_list}')

@bot.command()
async def play(ctx, song_number: int):
    voice_client = ctx.voice_client

    if not voice_client:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

    song_path = os.path.join(MUSIC_LIBRARY_PATH, audio_files[song_number - 1])

    if voice_client.is_playing():
        song_queue.append(song_number)
        await ctx.send(f'Песня #{song_number} добавлена в очередь.')
    else:
        audio_source = discord.FFmpegPCMAudio(song_path)
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        if len(song_queue) > 0:
            random.shuffle(song_queue)
            next_song_number = song_queue.popleft()
            next_song_path = os.path.join(MUSIC_LIBRARY_PATH, audio_files[next_song_number - 1])
            next_audio_source = discord.FFmpegPCMAudio(next_song_path)
            voice_client.play(next_audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx, next_song_number), bot.loop))
        else:
            await voice_client.disconnect()

@bot.command()
async def queue(ctx):
    if len(song_queue) == 0:
        await ctx.send('Очередь пуста.')
    else:
        song_queue_list = '\n'.join([f'{i}. {audio_files[song_number - 1]}' for i, song_number in enumerate(song_queue, start=1)])
        await ctx.send(f'Очередь:\n{song_queue_list}')

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        if voice_client.is_playing():
            await ctx.send('Останавливаю воспроизведение музыки.')
            voice_client.stop()
        song_queue.clear()
        await voice_client.disconnect()
    else:
        await ctx.send('Ничего не проигрывается.')



@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Команды бота", color=0x00ff00)
    embed.add_field(name="$dmbomb [times] [user_id] [message]", value="Отправить сообщение в личку определенное количество раз.", inline=False)
    embed.add_field(name="$chbomb [times] [user_id]", value="Создать временный канал, где человек будет тегнут определенное количество раз.", inline=False)
    embed.add_field(name="$spmove [num_moves] [user_id] [channel]", value="Супер-перемещение между оригинальным и указанным каналом.", inline=False)
    embed.add_field(name="$chngrpc [rpc_name]", value="Поменять Rich Presence бота.", inline=False)
    embed.add_field(name="$purge [limit]", value="Удалить определенное количество сообщений в канале.(требуются админ права)", inline=False)
    embed.add_field(name="$list", value="Выводит список доступных песен.", inline=False)
    embed.add_field(name="$play [number of music]", value="Воспроизводит выбранную песню.", inline=False)
    embed.add_field(name="$queue", value="Показывает очередь песен.", inline=False)
    embed.add_field(name="$stop", value="Останавливает музыку.", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name="Автор замечательного бота:", value="Прекрасный Витюша Мастифф!!!", inline=False)
    await ctx.send(embed=embed)

bot.run(API_TOKEN)