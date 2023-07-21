import discord
import json
import asyncio
import datetime

async def dmbomb(interaction: discord.Interaction, times: int, user: discord.User, message: str):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["dmbomb"] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        return
    if times > 100:
        await interaction.response.send_message(content="Максимальное количество сообщений - 100.", ephemeral=True)
        return
    if user is None:
        print(f"User {user} not found.")
        return
    await interaction.response.send_message(content=f'Я уничтожаю {user} в личных сообщениях {times} раз.', ephemeral=True)
    for i in range(times):
        try:
            print(f'Dmbombing {user} with "{message}" message')
            await user.send(message)
        except discord.Forbidden:
            print(f"User {user.name} has blocked the bot.")
            await interaction.guild.ban(user, reason="User has blocked the bot.")

async def chbomb(interaction: discord.Interaction, times: int, user: discord.User):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["chbomb"] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        return
    if times > 100:
        await interaction.response.send_message(content="Максимальное количество сообщений - 100.", ephemeral=True)
        return
    if user is None:
        print(f"User {user} not found.")
        return
    await interaction.response.send_message(content=f'Я уничтожаю {user} в канале {times} раз.', ephemeral=True)

    channel = await interaction.guild.create_text_channel(name=f"chbomb-{user}")
    await channel.set_permissions(user, read_messages=True, send_messages=True)

    for i in range(times):
        print(f'Chbombing {user} {i+1}/{times} times')
        await channel.send(f"Дурашка на {user.mention}, тебя чпокнули {i+1}/{times} раз")
    await asyncio.sleep(180)
    await channel.delete()

async def spmove(interaction: discord.Interaction, num_moves: int, user: discord.User, channel: discord.VoiceChannel):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands["spmove"] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        return
    if num_moves > 100:
        await interaction.response.send_message(content="Максимальное количество перемещений - 100.", ephemeral=True)
        return
    if user is None:
        print("User not found.")
        return

    original_channel = user.voice.channel
    await interaction.response.send_message(content=f"Пользователь {user.name} будет перемещен между {channel.name} и {original_channel.name} {num_moves} раз.", ephemeral=True)

    for i in range(num_moves):
        await user.move_to(channel)
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=1))
        await user.move_to(original_channel)
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=1))
    
    print(f"Moved {user.name} back and forth between {channel.name} and {original_channel.name} {num_moves} times.")
