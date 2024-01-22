# python3 -c "import pytube as _; print(_.__path__)"
# python3 -m pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz
import discord
import asyncio
import os
import json
import random
import math
from discord import FFmpegPCMAudio
from pytube import YouTube as YT
from discord.ext import commands
from discord.utils import get
from config import API_TOKEN
from typing import Union
from collections import deque

innertube._cache_dir = os.path.join(os.getcwd(), "cache")
innertube._token_file = os.path.join(innertube._cache_dir, 'tokens.json')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

Version = "2.7.9"
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    sync = await bot.tree.sync()
    print(f'Synced {len(sync)} command')
    activity = discord.Activity(name=f'Version {Version}', type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)

async def adminCheck(commandName: str, interaction: discord.Interaction):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands[commandName] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
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
audio_files = [file for file in os.listdir('./media') if file.endswith(('.mp3'))]

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
    if not audio_files:
        await interaction.send("Нет доступных песен")
    else:
        await show_list(interaction, page, audio_files, 'Доступные песни:')

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
    if len(song_queue) == 0:
        await interaction.response.send_message(content='Очередь пуста.',ephemeral=True)
    else:
        queue = [*song_queue]
        await show_list(interaction, page, queue, 'Текущая очередь:')

@bot.tree.command(name="stop", description="Останавливает музыку.")
async def stop(interaction: discord.Interaction):
    await adminCheck("stop", interaction)
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
    global song_dict
    try:
        video=YT(url, use_oauth=False, allow_oauth_cache=False)
        filtered=video.streams.filter(only_audio=True)
        if video.length > 600 or video.length < 1:
            await interaction.response.send_message(content=f'Ошибка: файл длиннее 10 минут. Длительность файла - {video.length//60}/10 минут.', ephemeral=True)
            return
        await interaction.response.send_message(content='Загрузка...', ephemeral=True)
        out_file = filtered[0].download('./media/')
        if os.path.isfile(out_file):
            base, ext = os.path.splitext(out_file)
            if title == "":
                title = video.title
            new_file = f'./media/{title}.mp3'
            os.rename(out_file, new_file)
            song_dict[title] = new_file
        else:
            await interaction.response.send_message(content='Ошибка: файл не был найден.', ephemeral=True)
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
    playlists = load_playlists()
    if not playlists:
        await interaction.response.send_message(content="Нет доступных плейлистов.", ephemeral=True)
    else:
        names = load_names()
        await show_list(interaction, page, names, 'Доступные плейлисты:')

@bot.tree.command(name="create_playlist", description="Создает новый плейлист.")
async def create_playlist(interaction: discord.Interaction, name: str):
    await adminCheck("create_playlist", interaction)
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
    playlists = load_playlists()
    if name in playlists:
        voice_channel = interaction.user.voice.channel
        voice_client = await voice_channel.connect()
        cur_playlist = playlists[name]
        await interaction.response.send_message(content="Проигрываю перемешанный плейлист: " + name, ephemeral=True)
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
        await interaction.response.send_message(content="Плейлиста с таким именем не существует.", ephemeral=True)

@bot.tree.command(name="songs_playlist", description="Выводит список песен в плейлисте.")
async def songs_playlist(interaction: discord.Interaction, name: str, page: int = 1):
    await adminCheck("songs_playlist", interaction)
    playlists = load_playlists()
    if name in playlists:
        await show_list(interaction, page, playlists[name], f'Песни в плейлисте {name}:')
    else:
        await interaction.response.send_message(content=f"Плейлист {name} не найден.", ephemeral=True)

@bot.tree.command(name="songs_delete", description="Удаляет определенную песню из плейлиста.")
async def songs_delete(interaction: discord.Interaction, name: str, song: str):
    await adminCheck("songs_delete", interaction)
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
    voice_channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice_client is None:
        voice_client = await voice_channel.connect()

    try:
        video = YT(url, use_oauth=False, allow_oauth_cache=False)
        filtered = video.streams.filter(only_audio=True)
        if video.length > 600 or video.length < 1:
            await interaction.response.send_message(content=f'Ошибка: файл длиннее 10 минут. Длительность файла - {video.length//60}/10 минут.', ephemeral=True)
            return

        await interaction.response.send_message(content='Проигрываю/Добавляю в очередь файл стрима.', ephemeral=True)

        out_file = filtered[0].download('./temp/')

        if os.path.isfile(out_file):
            base, ext = os.path.splitext(out_file)
            title = video.title

            song_dict[title] = out_file

            song_queue.append(title)
            if not voice_client.is_playing():

                audio_source = discord.FFmpegPCMAudio(out_file)
                voice_client.play(audio_source)

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
                        while voice_client.is_playing():
                            await asyncio.sleep(1)
                        os.remove(next_file)
                        del song_dict[next_song]

                await voice_client.disconnect()
                clean_temp_folder("./temp")
    except Exception as e:
        print(f"Error: {e}")

bot.run(APIToken)
