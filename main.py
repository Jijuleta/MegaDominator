import discord
import datetime
import asyncio
import os
import json
import re
import random
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from config import API_TOKEN
from typing import Union
from collections import deque

# u have to create config.py and create API_TOKEN variable.

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

Version = "2.8"
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    activity = discord.Activity(name=f'Version {Version}', type=discord.ActivityType.watching, details="Watching", state="Discord")
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
    
    await ctx.send(f'{user} был уничтожен в личных сообщениях {times} раз.')


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
        await channel.send(f"Дурашка на {user.mention}, тебя чпокнули {i+1}/{times} раз")
    await ctx.send(f"{user} был разбомблен в канале {times} раз.")
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

MUSIC_LIBRARY_PATH = './media/'
audio_files = [file for file in os.listdir('./media') if file.endswith(('.mp3', '.wav', '.ogg'))]

song_dict = {}
for file_name in audio_files:
    title = os.path.splitext(file_name)[0]
    song_dict[title] = os.path.join(MUSIC_LIBRARY_PATH, file_name)

song_queue = deque()

@bot.command()
async def list(ctx):
    song_list = '\n'.join([f'{i}. {os.path.splitext(song)[0]}' for i, song in enumerate(audio_files, start=1)])
    await ctx.send(f'Доступные песни:\n{song_list}')

@bot.command()
async def play(ctx, *, song_title: str):
    voice_client = ctx.voice_client

    if not voice_client:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

    song_path = song_dict.get(song_title)
    if not song_path:
        await ctx.send(f"Я не смог найти песню с таким названием: {song_title}.")
        return

    if voice_client.is_playing():
        song_queue.append(song_path)
        await ctx.send(f'{song_title} добавлена в очередь.')
    else:
        audio_source = discord.FFmpegPCMAudio(song_path)
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        if len(song_queue) > 0:
            next_song_path = song_queue.popleft()
            next_song_title = os.path.splitext(os.path.basename(next_song_path))[0]
            voice_client.play(discord.FFmpegPCMAudio(next_song_path), after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx, next_song_title), bot.loop))
        else:
            await voice_client.disconnect()

@bot.command()
async def queue(ctx):
    if len(song_queue) == 0:
        await ctx.send('Очередь пуста.')
    else:
        queue_list = '\n'.join([f'{i}. {os.path.splitext(os.path.basename(song))[0]}' for i, song in enumerate(song_queue, start=1)])
        await ctx.send(f'Очередь:\n{queue_list}')

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

# PLAYLISTS MODULE:

def load_playlists(playlist_name=None):
    if os.path.exists("playlists.json"):
        with open("playlists.json", "r") as f:
            playlists = json.load(f)
            if playlist_name:
                return playlists.get(playlist_name)
            else:
                return playlists
    else:
        playlists = {}
        with open("playlists.json", "w") as f:
            json.dump(playlists, f)
        return {}

def save_playlists(playlists):
    with open("playlists.json", "w") as f:
        json.dump(playlists, f)

@bot.command()
async def playlists(ctx):
    playlists = load_playlists()
    if not playlists:
        await ctx.send("Нету доступных плейлистов.")
    else:
        await ctx.send("Доступные плейлисты:\n" + "\n".join(playlists.keys()))

@bot.command()
async def create_playlist(ctx, name, *songs):
    playlists = load_playlists()
    if name in playlists:
        await ctx.send("Плейлист с этим именем уже существует.")
    else:
        playlists[name] = songs
        save_playlists(playlists)
        await ctx.send("Плейлист создан.")

@bot.command()
async def play_playlist(ctx, name):
    playlists = load_playlists()
    if name not in playlists:
        await ctx.send("Плейлиста с таким именем не существует.")
    else:
        await ctx.send("Проигрываю плейлист: " + name)
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        for song in playlists[name]:
            source = FFmpegPCMAudio(f"./media/{song}.mp3")
            voice_client.play(source)
            while voice_client.is_playing():
                await asyncio.sleep(1)
        await voice_client.disconnect()
        
@bot.command()
async def delete_playlist(ctx, name):
    playlists = load_playlists()
    if name in playlists:
        del playlists[name]
        save_playlists(playlists)
        await ctx.send("Плейлист удалён.")
    else:
        await ctx.send("Плейлиста с таким именем не существует.")
        
@bot.command()
async def shuffle_playlist(ctx, name):
    playlists = load_playlists()
    if name in playlists:
        cur_playlist = playlists[name]
        random.shuffle(cur_playlist)
        await ctx.send("Проигрываю перемешанный плейлист: " + name)
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        for song in cur_playlist:
            source = FFmpegPCMAudio(f"./media/{song}.mp3")
            voice_client.play(source)
            while voice_client.is_playing():
                await asyncio.sleep(1)
        await voice_client.disconnect()
    else:
        await ctx.send("Плейлиста с таким именем не существует.")

@bot.command()
async def playlist_songs(ctx, name):
    playlists = load_playlists()
    if name not in playlists:
        await ctx.send("Плейлиста с таким именем не существует.")
    else:
        await ctx.send(f"Список песен в плейлисте {name}:\n" + "\n".join(playlists[name]))

@bot.command()
async def songs_delete(ctx, name, *args):
    playlists = load_playlists()
    if name in playlists:
        deleted_songs = []
        for song in args:
            if song in playlists[name]:
                playlists[name].remove(song)
                deleted_songs.append(song)
        if deleted_songs:
            save_playlists(playlists)
            await ctx.send(f"Песни {', '.join(deleted_songs)} успешно удалены из плейлиста {name}.")
        else:
            await ctx.send(f"Ни одна из указанных песен не найдена в плейлисте {name}.")
    else:
        await ctx.send(f"Плейлист {name} не найден.")


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
    embed.add_field(name="ДЛЯ РАБОТЫ МУЗЫКИ НУЖНО УСТАНОВИТЬ FFmpeg.", value="", inline=False)
    embed.add_field(name="$list", value="Выводит список доступных песен.", inline=False)
    embed.add_field(name="$play [song title]", value="Воспроизводит выбранную песню.", inline=False)
    embed.add_field(name="$queue", value="Показывает очередь песен.", inline=False)
    embed.add_field(name="$stop", value="Останавливает музыку.", inline=False)
    embed.add_field(name="$playlists", value="Показывает доступные плейлисты", inline=False)
    embed.add_field(name='$create_playlist "playlist title" "full song title 1" "full song title 2"...', value="Создает новый плейлист.(**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**) (**NOTE 2: НАЗВАНИЕ ПЛЕЙЛИСТА ДОЛЖНО СОСТОЯТЬ ИЗ 1 слова.**)", inline=False)
    embed.add_field(name="$play_playlist [playlist title]", value="Воспроизводит плейлист.",inline=False)
    embed.add_field(name="$delete_playlist [playlist title]", value="Удаляет плейлист.",inline=False)
    embed.add_field(name="$shuffle_playlist [playlist title]", value="Воспроизводит перемешанный плейлист.",inline=False)
    embed.add_field(name="$playlist_songs [playlist title]", value="Выводит список песен в плейлисте.", inline=False)
    embed.add_field(name='$songs_delete "playlist title" "song" "song2"', value="Удаляет определенную песню из плейлиста. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name='$songs_add "playlist title" "song" "song2"', value="Добавляет определенную песню из плейлиста. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name="Автор замечательного бота:", value="**Jeyen**", inline=False)
    embed.add_field(name="VERSION:", value= f'{Version}', inline=False)
    await ctx.send(embed=embed)

bot.run(API_TOKEN)
