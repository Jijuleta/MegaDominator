import discord
import datetime
import asyncio
import os
import json
import random
import math
from pytube import YouTube as YT
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from config import API_TOKEN
from typing import Union
from collections import deque

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


Version = "3.0.0-R1"
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    activity = discord.Activity(name=f'Version {Version}', type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)

@bot.command()
@commands.has_permissions(administrator=True)
async def settings(ctx):
    with open("commands.json", "r") as f:
        commands = json.load(f)

    output_message = "Доступные команды:\n"
    emojis = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹"]
    reactions = []

    for i, (command, admin_only) in enumerate(commands.items(), start=1):
        output_message += f"{emojis[i-1]} {command} - {'доступна только для администраторов' if not admin_only else 'доступна для всех пользователей'}\n"
    output_message += "\nНажмите реакцию с буквой команды, чтобы переключить ее доступность."
    message = await ctx.send(output_message)

    for i in range(len(commands)):
        reaction = emojis[i]
        await message.add_reaction(reaction)
        reactions.append(reaction)

    def check(reaction, user):
        return (
            user.guild_permissions.administrator
            and reaction.message == message
            and str(reaction.emoji) in emojis
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", check=check, timeout=30)
        command_index = emojis.index(str(reaction.emoji))
        command_name = list(commands.keys())[command_index]
        commands[command_name] = not commands[command_name]

        with open("commands.json", "w") as f:
            json.dump(commands, f, indent=4)

        await message.edit(content="Доступность команды обновлена.")
    except asyncio.TimeoutError:
        for reaction in reactions:
            await message.clear_reaction(reaction)      

@settings.error
async def settings_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")

@bot.command()
async def dmbomb(ctx, times: int, user_id: int, *, message: str):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["dmbomb"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    if times > 100:
        await ctx.send("Максимальное количество сообщений - 100.")
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

@bot.command()
async def chbomb(ctx, times: int, user_id: int):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["chbomb"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    if times > 100:
        await ctx.send("Максимальное количество сообщений - 100.")
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


@bot.command()
async def spmove(ctx, num_moves: int, user_id: int, channel: discord.VoiceChannel):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["spmove"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
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
async def purge(ctx, limit: int):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["purge"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    if limit > 100:
        await ctx.send("Максимальное количество перемещений - 100.")
        return
    deleted = await ctx.channel.purge(limit=limit+1)
    await ctx.send(f"{len(deleted) - 1} сообщений было успешно удалено!")

@bot.command()
async def id(ctx, user: Union[discord.Member, int]):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["id"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("This command is not available for all users.")
        return
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

if not os.path.exists("./media"):
        os.mkdir("./media")

MUSIC_LIBRARY_PATH = './media/'
audio_files = [file for file in os.listdir('./media') if file.endswith(('.mp3'))]

async def change_rpc(s: str):
    act = discord.Activity(name=s, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=act)

song_dict = {}
for song_title in audio_files:
    title = os.path.splitext(song_title)[0]
    song_dict[title] = os.path.join(MUSIC_LIBRARY_PATH, song_title)

song_queue = deque()
SONGS_PER_PAGE = 15

async def show_list(ctx, page: int, s_list, header: str):
    num_pages = math.ceil(len(s_list) / SONGS_PER_PAGE)
    start_index = (page - 1) * SONGS_PER_PAGE
    end_index = start_index + SONGS_PER_PAGE

    embed = discord.Embed(title=header, color=0x00ff00)
    for i, song in enumerate(s_list[start_index:end_index], start=start_index):
        embed.add_field(name=f'{i+1}. {os.path.splitext(song)[0]}', value='\u200b', inline=False)

    embed.set_footer(text=f'Страница {page}/{num_pages}. Для перехода на другую страницу используйте реакции ⬅️ и ➡️.')
    message = await ctx.send(embed=embed)

    if num_pages > 1:
        await message.add_reaction('⬅️')
        await message.add_reaction('➡️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        current_page = page
        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
            else:
                if str(reaction.emoji) == '⬅️':
                    current_page = max(1, current_page - 1)
                elif str(reaction.emoji) == '➡️':
                    current_page = min(num_pages, current_page + 1)

                await message.remove_reaction(reaction, user)

                if current_page != page:
                    page = current_page
                    start_index = (page - 1) * SONGS_PER_PAGE
                    end_index = start_index + SONGS_PER_PAGE

                    embed.clear_fields()
                    for i, song in enumerate(s_list[start_index:end_index], start=start_index):
                        embed.add_field(name=f'{i+1}. {os.path.splitext(song)[0]}', value='\u200b', inline=False)

                    embed.set_footer(text=f'Страница {page}/{num_pages}. Для перехода на другую страницу используйте реакции ⬅️ и ➡️.')
                    await message.edit(embed=embed)

@bot.command()
async def songs(ctx, page: int = 1):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["songs"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    if not audio_files:
        await ctx.send("Нет доступных песен")
    else:
        await show_list(ctx, page, audio_files, 'Доступные песни:')

async def songs_play(ctx, voice_client):
    while len(song_queue) > 0:
        song_title = song_queue.popleft()
        song_path = song_dict.get(song_title)
        audio_source = discord.FFmpegPCMAudio(song_path)
        voice_client.play(audio_source)
        await change_rpc(song_title)
        while voice_client.is_playing():
            await asyncio.sleep(1)
    await change_rpc(f'Version {Version}')
    await voice_client.disconnect()

@bot.command()
async def play(ctx, *, song_title: str):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["play"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    voice_client = ctx.voice_client
    if not voice_client:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        
    song_path = song_dict.get(song_title)
    if song_path:
        song_queue.append(song_title)
        if not voice_client.is_playing():
            await ctx.send(f'Проигрывается песня: {song_title}')
            await songs_play(ctx, voice_client)
        else:
            await ctx.send(f'Песня {song_title} добавлена в очередь.')
    else:
        await ctx.send(f'Не удалось найти песню: {song_title}')
        
@bot.command()
async def skip(ctx):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["skip"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send(f'Песня пропущена.')
    else:
        await ctx.send('Ничего не проигрывается.')

@bot.command()
async def queue(ctx, page: int = 1):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["queue"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    if len(song_queue) == 0:
        await ctx.send('Очередь пуста.')
    else:
        queue = [*song_queue]
        await show_list(ctx, page, queue, 'Текущая очередь:')

@bot.command()
async def stop(ctx):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["stop"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    voice_client = ctx.voice_client
    if voice_client:
        if voice_client.is_playing():
            await ctx.send('Останавливаю воспроизведение музыки.')
            voice_client.stop()
        song_queue.clear()
        await change_rpc(f'Version {Version}')
        await voice_client.disconnect()
    else:
        await ctx.send('Ничего не проигрывается.')

@bot.command()
async def songs_upload(ctx, *, file_name: str):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["songs_upload"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    artist_title = file_name.strip('"')

    if len(file_name) > 100:
        await ctx.send('Ошибка: название файла слишком длинное.')
        return

    if not ctx.message.attachments:
        await ctx.send("Пожалуйста, прикрепите файл MP3 к вашему сообщению.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith(".mp3"):
        await ctx.send("Пожалуйста, прикрепите файл MP3 к вашему сообщению.")
        return

    if not os.path.exists("./media"):
        os.mkdir("./media")

    new_file_name = f"{artist_title}.mp3"
    file_path = f"./media/{new_file_name}"
    await attachment.save(file_path)

    song_dict[artist_title] = file_path
    await ctx.send(f"Файл был успешно сохранен как '{artist_title}'.")

@bot.command()
async def download(ctx, url: str, title: str = ""):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["download"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    global song_dict
    try:
        video=YT(url, use_oauth=True, allow_oauth_cache=True)
        filtered=video.streams.filter(only_audio=True)
        if video.length > 600 or video.length < 1:
            await ctx.send(f'Ошибка: файл длиннее 10 минут. Длительность файла - {video.length//60}/10 минут.')
            return
        await ctx.send('Загрузка...')
        out_file = filtered[0].download('./media/')
        if os.path.isfile(out_file):
            base, ext = os.path.splitext(out_file)
            if title == "":
                title = video.title
            new_file = f'./media/{title}.mp3'
            os.rename(out_file, new_file)
            song_dict[title] = new_file
            await ctx.send(f'Файл {title} был загружен на сервер.')
        else:
            await ctx.send(f'Ошибка: файл не был найден.')
    except Exception as e:
        print(f"Error: {e}")

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

def load_names():
    names_list = []
    if os.path.exists("playlists.json"):
        with open("playlists.json", "r") as f:
            playlists = json.load(f)
            for key in playlists.keys():
                names_list.append(key)
            return names_list
    else:
        playlists = {}
        with open("playlists.json", "w") as f:
            json.dump(playlists, f)
        return {}

def save_playlists(playlists):
    with open("playlists.json", "w") as f:
        json.dump(playlists, f)

@bot.command()
async def playlists(ctx, page: int = 1):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["playlists"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if not playlists:
        await ctx.send("Нет доступных плейлистов.")
    else:
        names = load_names()
        await show_list(ctx, page, names, 'Доступные плейлисты:')

@bot.command()
async def create_playlist(ctx, name, *songs):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["create_playlist"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name in playlists:
        await ctx.send("Плейлист с этим именем уже существует.")
    else:
        playlists[name] = songs
        save_playlists(playlists)
        await ctx.send("Плейлист создан.")

@bot.command()
async def play_playlist(ctx, name, loop=False):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["play_playlist"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name not in playlists:
        await ctx.send("Плейлиста с таким именем не существует.")
    else:
        await ctx.send("Проигрываю плейлист: " + name)
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        cur_playlist = playlists[name]
        while True:
            for song in cur_playlist:
                source = FFmpegPCMAudio(f"./media/{song}.mp3")
                voice_client.play(source)
                await change_rpc(song)
                while voice_client.is_playing():
                    await asyncio.sleep(1)
            if not loop:
                break
        await change_rpc(f'Version {Version}')
        await voice_client.disconnect()
        
@bot.command()
async def delete_playlist(ctx, name):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["delete_playlist"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name in playlists:
        del playlists[name]
        save_playlists(playlists)
        await ctx.send("Плейлист удалён.")
    else:
        await ctx.send("Плейлиста с таким именем не существует.")
        
@bot.command()
async def shuffle_playlist(ctx, name, loop=False):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["shuffle_playlist"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name in playlists:
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        cur_playlist = playlists[name]
        await ctx.send("Проигрываю перемешанный плейлист: " + name)
        while True:
            if loop:
                random.shuffle(cur_playlist)
            for song in cur_playlist:
                source = FFmpegPCMAudio(f"./media/{song}.mp3")
                voice_client.play(source)
                await change_rpc(song)
                while voice_client.is_playing():
                    await asyncio.sleep(1)
            if not loop:
                break
        await change_rpc(f'Version {Version}')
        await voice_client.disconnect()
    else:
        await ctx.send("Плейлиста с таким именем не существует.")

@bot.command()
async def songs_playlist(ctx, name, page: int = 1):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["songs_playlist"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name in playlists:
        await show_list(ctx, page, playlists[name], f'Песни в плейлисте {name}:')
    else:
        await ctx.send(f"Плейлист {name} не найден.")

@bot.command()
async def songs_delete(ctx, name, *args):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["songs_delete"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
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
async def songs_add(ctx, name, *args):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["songs_add"] and not ctx.author.guild_permissions.administrator:
        await ctx.send("Эта команда недоступна для всех пользователей.")
        return
    playlists = load_playlists()
    if name in playlists:
        added_songs = []
        for song in args:
            if song not in playlists[name]:
                playlists[name].append(song)
                added_songs.append(song)
        if added_songs:
            save_playlists(playlists)
            await ctx.send(f"Песни {', '.join(added_songs)} успешно добавлены в плейлист {name}.")
        else:
            await ctx.send(f"Плейлист {name} не был обновлён.")
    else:
        await ctx.send(f"Плейлист {name} не найден.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Команды бота", color=0x00ff00)
    embed.add_field(name="$settings", value="Позволяет настроить бота.",inline=False)
    embed.add_field(name="$dmbomb [times] [user_id] [message]", value="Отправить сообщение в личку определенное количество раз.", inline=False)
    embed.add_field(name="$chbomb [times] [user_id]", value="Создать временный канал, где человек будет тегнут определенное количество раз.", inline=False)
    embed.add_field(name="$spmove [num_moves] [user_id] [channel]", value="Супер-перемещение между оригинальным и указанным каналом.", inline=False)
    embed.add_field(name="$purge [limit]", value="Удалить определенное количество сообщений в канале.", inline=False)
    embed.add_field(name="$id [@user] or [user id]", value="При умоминании пользователя выводит его ID, если отправить ID пользователя, то бот отправит владельца ID.")
    embed.add_field(name="ДЛЯ РАБОТЫ МУЗЫКИ НУЖНО УСТАНОВИТЬ FFmpeg.", value="", inline=False)
    embed.add_field(name="$songs", value="Выводит список доступных песен.", inline=False)
    embed.add_field(name="$play [song title]", value="Воспроизводит выбранную песню.", inline=False)
    embed.add_field(name="$skip", value="Пропускает текущую песню.", inline=False)
    embed.add_field(name="$queue", value="Показывает очередь песен.", inline=False)
    embed.add_field(name="$stop", value="Останавливает музыку.", inline=False)
    embed.add_field(name='$songs_upload "song title without extension"', value='Позволяет загрузить MP3 файл в папку с музыкой.(**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**) (**NOTE 2: К сообщению нужно прикрепить файл**)',inline=False)
    embed.add_field(name='$download YOUTUBE URL [НЕОБЯЗАТЕЛЬНО: "song title" (обязательно ставить кавычки)]', value="Позволяет загрузить песню с Youtube.",inline=False)
    embed.add_field(name="$playlists", value="Показывает доступные плейлисты", inline=False)
    embed.add_field(name='$create_playlist "playlist title" "full song title 1" "full song title 2"...', value="Создает новый плейлист.(**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**) (**NOTE 2: НАЗВАНИЕ ПЛЕЙЛИСТА ДОЛЖНО СОСТОЯТЬ ИЗ 1 слова.**)", inline=False)
    embed.add_field(name="$play_playlist [playlist title] [НЕОБЯЗАТЕЛЬНО: True (тогда плейлист будет играть снова)]", value="Воспроизводит плейлист.",inline=False)
    embed.add_field(name="$delete_playlist [playlist title]", value="Удаляет плейлист.",inline=False)
    embed.add_field(name="$shuffle_playlist [playlist title] [НЕОБЯЗАТЕЛЬНО: True (тогда плейлист будет играть снова)]", value="Воспроизводит перемешанный плейлист.",inline=False)
    embed.add_field(name="$songs_playlist [playlist title]", value="Выводит список песен в плейлисте.", inline=False)
    embed.add_field(name='$songs_delete "playlist title" "song" "song2"', value="Удаляет определенную песню из плейлиста. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name='$songs_add "playlist title" "song" "song2"', value="Добавляет определенную песню в плейлист. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name="Автор замечательного бота:", value="**Jeyen**", inline=False)
    embed.add_field(name="VERSION:", value= f'{Version}', inline=False)
    await ctx.send(embed=embed)

bot.run(API_TOKEN)
