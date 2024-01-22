import discord
import json

async def adminCheck(commandName: str, interaction: discord.Interaction):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands[commandName] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        return

async def send_message(interaction: discord.Interaction, channel:discord.TextChannel, message: str):
    await adminCheck("send_message", interaction)
    await interaction.response.send_message(content="Сообщение успешно отправлено.", ephemeral=True)
    await channel.send(message)


'''import discord

async def help(interaction: discord.Interaction, version: str):
    embed = discord.Embed(title="Команды бота", color=0x00ff00)
    embed.add_field(name="$settings", value="Позволяет настроить бота.",inline=False)
    embed.add_field(name="$dmbomb [times] [user_id] [message]", value="Отправить сообщение в личку определенное количество раз.", inline=False)
    embed.add_field(name="$chbomb [times] [user_id]", value="Создать временный канал, где человек будет тегнут определенное количество раз.", inline=False)
    embed.add_field(name="$spmove [num_moves] [user_id] [channel]", value="Супер-перемещение между оригинальным и указанным каналом.", inline=False)
    embed.add_field(name="$purge [limit]", value="Удалить определенное количество сообщений в канале.", inline=False)
    embed.add_field(name="$id [@user] or [user id]", value="При умоминании пользователя выводит его ID, если отправить ID пользователя, то бот отправит владельца ID.")
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
    embed.add_field(name="VERSION:", value=version, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)'''