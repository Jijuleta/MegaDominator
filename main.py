import discord
import asyncio
import os
import json
import random
import math
import difflib
from discord import FFmpegPCMAudio
from pytube import YouTube as YT
from discord.ext import commands
from collections import deque
from pytube import innertube

from moderationFuncs import show_settings, change_settings, purge
from trollFuncs import dmbomb, chbomb, spmove
from otherFuncs import send_message, defaultCommandsPerms

if not os.path.exists("commands.json"):
    print("commands.json is not found, creating new....")
    with open('commands.json', 'w') as json_file:
        json.dump(defaultCommandsPerms, json_file, indent=4)

if not os.path.exists("config.py"):
    APITokenFile = open("config.py", "x")
    APITokenFile.write('APIToken = ""\nlogsChannelID = 12345')
else:
    from config import APIToken, logsChannelID
    if logsChannelID == 12345:
        print("Enter logsChannelID in config.py file")


innertube._cache_dir = os.path.join(os.getcwd(), "cache")
innertube._token_file = os.path.join(innertube._cache_dir, 'tokens.json')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


Version = "3.2.2-TESTING"
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    sync = await bot.tree.sync()
    print(f'Synced {len(sync)} command')
    activity = discord.Activity(name=f'Version {Version}', type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)
    try:
        logsChannel = bot.get_channel(logsChannelID)
        await logsChannel.send(f'Бот был включён на версии {Version}')
    except AttributeError:
        print('Enter correct logsChannelID in config.py file')


async def adminCheck(commandName: str, interaction: discord.Interaction):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands[commandName] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        logsChannel = bot.get_channel(logsChannelID)
        await logsChannel.send(f'Пользователь {interaction.user.mention} попытался воспользоваться командой {commandName}, которая недоступна для него')
        return

@bot.tree.command(name="message", description="Позволяет писать от имени бота.")
async def send_message_func(interaction: discord.Interaction, channel:discord.TextChannel, message: str):
    await send_message(interaction, channel, message)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду message на канал <#{channel.id}>, написав "{message}"')

@bot.tree.command(name="showsettings", description="Показывает текущие настройки бота.")
async def show_settings_func(interaction: discord.Interaction):
    await show_settings(interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь "{interaction.user.mention}" использовал команду show_settings')

@bot.tree.command(name="changesettings", description="Позволяет изменить настройки бота.")
async def change_settings_func(interaction: discord.Interaction, command_name: str, state: bool):
    await change_settings(interaction, command_name, state)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь "{interaction.user.mention}" использовал команду change_settings')
    
@bot.tree.command(name="dmbomb", description="Отправить сообщение в личку определенное количество раз.")
async def dmbomb_func(interaction: discord.Interaction, times: int, user: discord.User, message: str):
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду dmbomb на {user.mention} {times} раз, написав "{message}"')
    await dmbomb(interaction, times, user, message)

@bot.tree.command(name="chbomb", description="Создать временный канал, где человек будет тегнут определенное количество раз.")
async def chbomb_func(interaction: discord.Interaction, times: int, user: discord.User):
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду chbomb на {user.mention} {times} раз')
    await chbomb(interaction, times, user)

@bot.tree.command(name="spmove", description="Супер-перемещение между оригинальным и указанным каналом.")
async def spmove_func(interaction: discord.Interaction, num_moves: int, user: discord.User, channel: discord.VoiceChannel):
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду spmove на {user.mention} {num_moves} раз в канал {channel.mention}')
    await spmove(interaction, num_moves, user, channel)

@bot.tree.command(name="purge",description="Удалить определенное количество сообщений в канале.")
async def purge_func(interaction: discord.Interaction, messages: int, channel: discord.TextChannel):
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду purge, удалив {messages} сообщений в канале {channel.mention}')
    await purge(interaction, messages, channel)


# MUSIC FEATURES

if not os.path.exists("./media"):
        os.mkdir("./media")

if not os.path.exists("./temp"):
        os.mkdir("./temp")

def clean_temp_folder(folder_path):
    try:
        files = os.listdir(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        
        print("Folder cleanup completed.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

clean_temp_folder("./temp")

MUSIC_LIBRARY_PATH = './media/'
audio_files = [file for file in os.listdir('./media') if file.lower().endswith('.mp3' or 'mp4')]

async def change_rpc(activityname: str):
    act = discord.Activity(name=activityname, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=act)

song_dict = {}
for song_title in audio_files:
    title = os.path.splitext(song_title)[0]
    song_dict[title] = os.path.join(MUSIC_LIBRARY_PATH, song_title)

song_queue = deque()
SONGS_PER_PAGE = 15

async def show_list(interaction: discord.Interaction, page: int, s_list, header: str):
    num_pages = math.ceil(len(s_list) / SONGS_PER_PAGE)
    if page < 1 or page > num_pages:
        await interaction.response.send_message(f"Неправильный номер страницы. Доступные страницы: 1 to {num_pages}", ephemeral=True)
        return

    start_index = (page - 1) * SONGS_PER_PAGE
    end_index = start_index + SONGS_PER_PAGE

    embed = discord.Embed(title=header, color=0x00ff00)
    for i, song in enumerate(s_list[start_index:end_index], start=start_index):
        embed.add_field(name=f'{i+1}. {os.path.splitext(song)[0]}', value='\u200b', inline=False)

    embed.set_footer(text=f'Страница {page}/{num_pages}.')
    message = await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="songs", description="Выводит список доступных песен.")
async def songs(interaction: discord.Interaction, page: int = 1):
    await adminCheck("songs", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду songs')
    if not audio_files:
        await interaction.send("Нет доступных песен")
    else:
        await show_list(interaction, page, audio_files, 'Доступные песни:')

@bot.tree.command(name="search", description="Позволяет искать песню по названию")
async def search(interaction: discord.Interaction, song_name: str):
    await adminCheck("search", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду search, пытаясь найти песню {song_name}')
    audio_files = [file for file in os.listdir('./media') if file.endswith(('.mp3' or '.mp4'))]
    if audio_files == []:
        await interaction.response.send_message(f"Песни не были обнаружены", ephemeral=True)
    else:
        await interaction.response.send_message(f"Работаю над поиском песни...", ephemeral=True)
        matches = difflib.get_close_matches(song_name, audio_files)
        await interaction.edit_original_response(content=f'Совпадения с введённой песней: {matches}')

async def songs_play(voice_client):
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

@bot.tree.command(name="play", description="Воспроизводит выбранную песню.")
async def play(interaction: discord.Interaction, song_title: str):
    await adminCheck("play", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду play, включив песню "{song_title}"')
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client:
        voice_channel = interaction.user.voice.channel
        voice_client = await voice_channel.connect()
        
    song_path = song_dict.get(song_title)
    if song_path:
        song_queue.append(song_title)
        if not voice_client.is_playing():
            await interaction.response.send_message(content=f'Проигрывается песня: {song_title}', ephemeral=True)
            await songs_play(voice_client)
        else:
            await interaction.response.send_message(content=f'Песня {song_title} добавлена в очередь.', ephemeral=True)
    else:
        await interaction.response.send_message(content=f'Не удалось найти песню: {song_title}', ephemeral=True)
        
@bot.tree.command(name="skip", description="Пропускает текущую песню.")
async def skip(interaction: discord.Interaction):
    await adminCheck("skip", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду skip')
    voice_channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message(content=f'Песня пропущена.', ephemeral=True)
    else:
        await interaction.response.send_message(content='Ничего не проигрывается.', ephemeral=True)


@bot.tree.command(name="queue", description="Показывает очередь песен.")
async def queue(interaction: discord.Interaction, page: int = 1):
    await adminCheck("queue", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду queue')
    if len(song_queue) == 0:
        await interaction.response.send_message(content='Очередь пуста.',ephemeral=True)
    else:
        queue = [*song_queue]
        await show_list(interaction, page, queue, 'Текущая очередь:')

@bot.tree.command(name="stop", description="Останавливает музыку.")
async def stop(interaction: discord.Interaction):
    await adminCheck("stop", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду stop')
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client:
        if voice_client.is_playing():
            await interaction.response.send_message(content='Останавливаю воспроизведение музыки.', ephemeral=True)
            voice_client.stop()
        song_queue.clear()
        await change_rpc(f'Version {Version}')
        await voice_client.disconnect()
    else:
        await interaction.response.send_message(content='Ничего не проигрывается.', ephemeral=True)

@bot.tree.command(name="songsupload", description="Для отправки используйте устаревший формат $songs_upload")
async def songsupload(interaction:discord.Interaction):
    await interaction.response.send_message(content='Для отправки используйте устаревший формат $songs_upload', ephemeral=True)

@bot.command()
async def songs_upload(ctx, *, file_name: str):
    await adminCheck("songs_upload")
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {ctx.user.mention} использовал команду songs_upload, назвав песню "{file_name}"')
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

@songs_upload.error
async def songs_upload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, прикрепите файл MP3 к вашему сообщению.")


@bot.tree.command(name="download", description="Позволяет загрузить песню с Youtube.")
async def download(interaction: discord.Interaction, url: str, title: str = ""):
    await adminCheck("download", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду download с URL {url} и названием "{title}"')
    await interaction.response.send_message(content='Загрузка...', ephemeral=True)
    global song_dict
    try:
        video=YT(url, use_oauth=False, allow_oauth_cache=False)
        filtered=video.streams.filter(only_audio=True)
        if video.length > 600 or video.length < 1:
            await interaction.edit_original_response(content=f'Ошибка: файл длиннее 10 минут. Длительность файла - {video.length//60}/10 минут.')
            return
        out_file = filtered[0].download('./media/')
        if os.path.isfile(out_file):
            base, ext = os.path.splitext(out_file)
            if title == "":
                title = video.title
            new_file = f'./media/{title}.mp3'
            os.rename(out_file, new_file)
            song_dict[title] = new_file
            await interaction.edit_original_response(content='Файл был успешно загружен.')
        else:
            await interaction.edit_original_response(content='Ошибка: файл не был найден.')
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

@bot.tree.command(name="playlists", description="Показывает доступные плейлисты.")
async def playlists(interaction: discord.Interaction, page: int = 1):
    await adminCheck("playlists", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду playlists')
    playlists = load_playlists()
    if not playlists:
        await interaction.response.send_message(content="Нет доступных плейлистов.", ephemeral=True)
    else:
        names = load_names()
        await show_list(interaction, page, names, 'Доступные плейлисты:')

@bot.tree.command(name="create_playlist", description="Создает новый плейлист.")
async def create_playlist(interaction: discord.Interaction, name: str):
    await adminCheck("create_playlist", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду create_playlist с названием "{name}"')
    playlists = load_playlists()
    if name in playlists:
        await interaction.response.send_message(content="Плейлист с этим именем уже существует.", ephemeral=True)
    else:
        playlists[name] = []
        save_playlists(playlists)
        await interaction.response.send_message(content="Плейлист создан.", ephemeral=True)


@bot.tree.command(name="play_playlist", description="Воспроизводит плейлист.")
async def play_playlist(interaction: discord.Interaction, name: str, loop: bool = False):
    await adminCheck("play_playlist", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду play_playlist, включив плейлист "{name}"')
    playlists = load_playlists()
    if name not in playlists:
        await interaction.response.send_message(content="Плейлиста с таким именем не существует.", ephemeral=True)
    else:
        await interaction.response.send_message(content="Проигрываю плейлист: " + name, ephemeral=True)
        voice_channel = interaction.user.voice.channel
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

@bot.tree.command(name="delete_playlist", description="Удаляет плейлист.")
async def delete_playlist(interaction: discord.Interaction, name: str):
    await adminCheck("delete_playlist", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду delete_playlist, удалив плейлист "{name}"')
    playlists = load_playlists()
    if name in playlists:
        del playlists[name]
        save_playlists(playlists)
        await interaction.response.send_message(content="Плейлист удалён.", ephemeral=True)
    else:
        await interaction.response.send_message(content="Плейлиста с таким именем не существует.", ephemeral=True)
       
@bot.tree.command(name="shuffle_playlist", description="Воспроизводит перемешанный плейлист.")
async def shuffle_playlist(interaction: discord.Interaction, name: str, loop: bool = False):
    await adminCheck("shuffle_playlist", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду shuffle_playlist, включив плейлист "{name}"')
    playlists = load_playlists()
    if name in playlists:
        voice_channel = interaction.user.voice.channel
        voice_client = await voice_channel.connect()
        cur_playlist = playlists[name]
        await interaction.response.send_message(content="Проигрываю перемешанный плейлист: " + name, ephemeral=True)
        while True:
            random.shuffle(cur_playlist)
            if loop or True:
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
        await interaction.response.send_message(content="Плейлиста с таким именем не существует.", ephemeral=True)

@bot.tree.command(name="songs_playlist", description="Выводит список песен в плейлисте.")
async def songs_playlist(interaction: discord.Interaction, name: str, page: int = 1):
    await adminCheck("songs_playlist", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду songs_playlist')
    playlists = load_playlists()
    if name in playlists:
        await show_list(interaction, page, playlists[name], f'Песни в плейлисте {name}:')
    else:
        await interaction.response.send_message(content=f"Плейлист {name} не найден.", ephemeral=True)

@bot.tree.command(name="songs_delete", description="Удаляет определенную песню из плейлиста.")
async def songs_delete(interaction: discord.Interaction, name: str, song: str):
    await adminCheck("songs_delete", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду songs_delete, удалив песню "{song}" из плейлиста "{name}"')
    playlists = load_playlists()
    if name in playlists:
        if song in playlists[name]:
            playlists[name].remove(song)
            save_playlists(playlists)
            await interaction.response.send_message(content=f"Песня {song} успешно удалена из плейлиста {name}.", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Песня {song} не найдена в плейлисте {name}.", ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Плейлист {name} не найден.", ephemeral=True)

@bot.tree.command(name="songs_add", description="Добавляет определенную песню в плейлист.")
async def songs_add(interaction: discord.Interaction, name: str, song: str):
    await adminCheck("songs_add", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду songs_add, добавив песню "{song}" в плейлист "{name}"')
    playlists = load_playlists()
    if name in playlists:
        if song not in playlists[name]:
            playlists[name].append(song)
            save_playlists(playlists)
            await interaction.response.send_message(content=f"Песня {song} успешно добавлена в плейлист {name}.", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Песня {song} уже существует в плейлисте {name}.", ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Плейлист {name} не найден.", ephemeral=True)

@bot.tree.command(name="stream", description="Временно скачивает и проигрывает песню с Youtube. (Поддеживает очередь)")
async def stream(interaction: discord.Interaction, url: str):
    await adminCheck("stream", interaction)
    logsChannel = bot.get_channel(logsChannelID)
    await logsChannel.send(f'Пользователь {interaction.user.mention} использовал команду stream, проиграв песню с URL {url}')
    voice_channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice_client is None:
        voice_client = await voice_channel.connect()

    await interaction.response.send_message(content='Работаю над воспроизведением...', ephemeral=True)

    try:
        video = YT(url, use_oauth=False, allow_oauth_cache=False)
        filtered = video.streams.filter(only_audio=True)
        if video.length > 600 or video.length < 1:
            await interaction.edit_original_response(content=f'Ошибка: файл длиннее 10 минут. Длительность файла - {video.length//60}/10 минут.')
            return

        await interaction.edit_original_response(content='Проигрываю/Добавляю в очередь файл стрима.')

        out_file = filtered[0].download('./temp/')

        if os.path.isfile(out_file):
            base, ext = os.path.splitext(out_file)
            title = video.title

            song_dict[title] = out_file

            song_queue.append(title)
            if not voice_client.is_playing():

                audio_source = discord.FFmpegPCMAudio(out_file)
                voice_client.play(audio_source)
                await change_rpc(title)

                while voice_client.is_playing():
                    await asyncio.sleep(1)

                os.remove(out_file)
                del song_dict[title]

                while len(song_queue) > 0:
                    next_song = song_queue.popleft()
                    next_file = song_dict.get(next_song)
                    if next_file:
                        audio_source = discord.FFmpegPCMAudio(next_file)
                        voice_client.play(audio_source)
                        await change_rpc(next_song)
                        while voice_client.is_playing():
                            await asyncio.sleep(1)
                        os.remove(next_file)
                        del song_dict[next_song]

                await voice_client.disconnect()
                await change_rpc(f'Version {Version}')
                clean_temp_folder("./temp")
    except Exception as e:
        print(f"Error: {e}")

try:
    bot.run(APIToken)
except NameError:
    print("Enter APIToken in config.py")
