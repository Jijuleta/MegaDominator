import discord
import datetime
import asyncio
import os
import json
import random
import math
import pytube
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

Version = "2.9.5"
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


'''@bot.command()
async def chngrpc(ctx, *, rpc_name: str):
    activity = discord.Activity(name=rpc_name, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=activity)
    print(f"Changed Rich Presence to: {rpc_name}")
    await ctx.send(f"Rich Presence был изменен на: {rpc_name}")'''

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
audio_files = [file for file in os.listdir('./media') if file.endswith(('.mp3'))]

async def change_rpc(s: str):
    act = discord.Activity(name=s, type=discord.ActivityType.watching, details="Watching", state="Discord")
    await bot.change_presence(activity=act)

song_dict = {}
for file_name in audio_files:
    title = os.path.splitext(file_name)[0]
    song_dict[title] = os.path.join(MUSIC_LIBRARY_PATH, file_name)

song_queue = deque()
SONGS_PER_PAGE = 10

async def show_list(ctx, page: int, list: list, header: str):
    num_pages = math.ceil(len(list) / SONGS_PER_PAGE)
    start_index = (page - 1) * SONGS_PER_PAGE
    end_index = start_index + SONGS_PER_PAGE

    embed = discord.Embed(title=header, color=0x00ff00)
    for i, song in enumerate(list[start_index:end_index], start=start_index):
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
                    for i, song in enumerate(list[start_index:end_index], start=start_index):
                        embed.add_field(name=f'{i+1}. {os.path.splitext(song)[0]}', value='\u200b', inline=False)

                    embed.set_footer(text=f'Страница {page}/{num_pages}. Для перехода на другую страницу используйте реакции ⬅️ и ➡️.')
                    await message.edit(embed=embed)

@bot.command()
async def list(ctx, page: int = 1):
    if not audio_files:
        await ctx.send("Нет доступных песен")
    else:
        await show_list(ctx, page, audio_files, 'Доступные песни:')


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
        await ctx.send(f"Проигрывается песня: {song_title}")
        audio_source = discord.FFmpegPCMAudio(song_path)
        voice_client.play(audio_source)
        await change_rpc(f'{song_title}')
        while voice_client.is_playing():
            await asyncio.sleep(1)

        if len(song_queue) > 0:
            next_song_path = song_queue.popleft()
            next_song_title = os.path.splitext(os.path.basename(next_song_path))[0]
            voice_client.play(discord.FFmpegPCMAudio(next_song_path), after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx, next_song_title), bot.loop))
            await change_rpc(f'{next_song_title}')
        else:
            await change_rpc(f'Version {Version}')
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
        await change_rpc(f'Version {Version}')
        await voice_client.disconnect()
    else:
        await ctx.send('Ничего не проигрывается.')

@bot.command()
#@commands.has_permissions(administrator=True)
async def songs_upload(ctx, *, file_name: str):
    artist_title = file_name.strip('"')

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


"""@songs_upload.error
async def songs_upload_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")"""

@bot.command()
#@commands.has_permissions(administrator=True)
async def download(ctx, url: str, name: str):
    try:
        video = pytube.YouTube(url)
        if video.length > 600:
            await ctx.send('Ошибка: видео слишком длинное.')
            return
        stream = video.streams.filter(only_audio=True).first()
        await ctx.send('Загрузка...')
        stream.download(output_path='./media', filename=name)
        file = f'./media/{name}'
        mp3_file = f'./media/{name}.mp3'
        if os.path.isfile(file):
            os.rename(file, mp3_file)
            song_dict[name] = mp3_file  
            await ctx.send(f'Файл {name} был загружен на сервер.')
        else:
            await ctx.send(f'Ошибка: файл {file} не был найден.')
    except Exception as e:
        print(f'Error: {e}')    

"""@download.error
async def download_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У вас недостаточно прав, чтобы выполнить эту команду.")"""

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
    playlists = load_playlists()
    if not playlists:
        await ctx.send("Нет доступных плейлистов.")
    else:
        names = load_names()
        await show_list(ctx, page, names, 'Доступные плейлисты:')

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
async def play_playlist(ctx, name, loop=False):
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
                await change_rpc(f'{song}')
                while voice_client.is_playing():
                    await asyncio.sleep(1)
            if not loop:
                break
        await change_rpc(f'Version {Version}')
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
async def shuffle_playlist(ctx, name, loop=False):
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
                await change_rpc(f'{song}')
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
    playlists = load_playlists()
    if name in playlists:
        await show_list(ctx, page, playlists[name], f'Песни в плейлисте {name}:')
    else:
        await ctx.send(f"Плейлист {name} не найден.")

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
async def songs_add(ctx, name, *args):
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
    embed.add_field(name="$dmbomb [times] [user_id] [message]", value="Отправить сообщение в личку определенное количество раз.", inline=False)
    embed.add_field(name="$chbomb [times] [user_id]", value="Создать временный канал, где человек будет тегнут определенное количество раз.", inline=False)
    embed.add_field(name="$spmove [num_moves] [user_id] [channel]", value="Супер-перемещение между оригинальным и указанным каналом.", inline=False)
    embed.add_field(name="$purge [limit]", value="Удалить определенное количество сообщений в канале.(требуются админ права)", inline=False)
    embed.add_field(name="$id [@user] or [user id]", value="При умоминании пользователя выводит его ID, если отправить ID пользователя, то бот отправит владельца ID.")
    embed.add_field(name=" ",value=" ", inline=False)
    embed.add_field(name="ДЛЯ РАБОТЫ МУЗЫКИ НУЖНО УСТАНОВИТЬ FFmpeg.", value="", inline=False)
    embed.add_field(name="$list", value="Выводит список доступных песен.", inline=False)
    embed.add_field(name="$play [song title]", value="Воспроизводит выбранную песню.", inline=False)
    embed.add_field(name="$queue", value="Показывает очередь песен.", inline=False)
    embed.add_field(name="$stop", value="Останавливает музыку.", inline=False)
    embed.add_field(name='$songs_upload "song title without extension"', value='Позволяет загрузить MP3 файл в папку с музыкой.(**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**) (**NOTE 2: К сообщению нужно прикрепить файл**)',inline=False)
    embed.add_field(name='$download "YOUTUBE URL" "song title"', value="Позволяет загрузить песню с Youtube.",inline=False)
    embed.add_field(name="$playlists", value="Показывает доступные плейлисты", inline=False)
    embed.add_field(name='$create_playlist "playlist title" "full song title 1" "full song title 2"...', value="Создает новый плейлист.(**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**) (**NOTE 2: НАЗВАНИЕ ПЛЕЙЛИСТА ДОЛЖНО СОСТОЯТЬ ИЗ 1 слова.**)", inline=False)
    embed.add_field(name="$play_playlist [playlist title] [НЕОБЯЗАТЕЛЬНО: True (тогда плейлист будет играть снова)]", value="Воспроизводит плейлист.",inline=False)
    embed.add_field(name="$delete_playlist [playlist title]", value="Удаляет плейлист.",inline=False)
    embed.add_field(name="$shuffle_playlist [playlist title] [НЕОБЯЗАТЕЛЬНО: True (тогда плейлист будет играть снова)]", value="Воспроизводит перемешанный плейлист.",inline=False)
    embed.add_field(name="$songs_playlist [playlist title]", value="Выводит список песен в плейлисте.", inline=False)
    embed.add_field(name='$songs_delete "playlist title" "song" "song2"', value="Удаляет определенную песню из плейлиста. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name='$songs_add "playlist title" "song" "song2"', value="Добавляет определенную песню из плейлиста. (**NOTE: ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ КАВЫЧКИ, КАК В ПРИМЕРЕ**)", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name=" ", value= " ", inline=False)
    embed.add_field(name="Автор замечательного бота:", value="**Jeyen**", inline=False)
    embed.add_field(name="Соавтор:", value="**ABrusil**",inline=False)
    embed.add_field(name="VERSION:", value= f'{Version}', inline=False)
    await ctx.send(embed=embed)

bot.run(API_TOKEN)
