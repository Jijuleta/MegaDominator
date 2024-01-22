import discord
import json

async def adminCheck(commandName: str, interaction: discord.Interaction):
    with open("commands.json", "rb") as f:
        commands = json.load(f)
    if not commands[commandName] and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="Эта команда недоступна для всех пользователей.", ephemeral=True)
        return

async def show_settings(interaction: discord.Interaction):
    await adminCheck("show_settings", interaction)  
    output_message = "Доступные команды:\n"
    emojis = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼"]
    with open("commands.json", "r") as f:
        commands = json.load(f)
    for i, (command, admin_only) in enumerate(commands.items(), start=1):
        output_message += f"{emojis[i-1]} {command} - {'доступна только для администраторов' if not admin_only else 'доступна для всех пользователей'}\n"
    await interaction.response.send_message(content=output_message, ephemeral=True)

async def change_settings(interaction: discord.Interaction, command_name: str, state: bool):
    await adminCheck("change_settings", interaction)
    with open("commands.json", "r") as f:
        commands = json.load(f)
    if command_name in commands:
        commands[command_name] = state
        with open("commands.json", "w") as f:
            json.dump(commands, f, indent=4)
        await interaction.response.send_message(content=f"Настройки команды '{command_name}' изменены на '{state}'.", ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Команда '{command_name}' не найдена.", ephemeral=True)

async def purge(interaction: discord.Interaction, messages: int, channel: discord.TextChannel):
    adminCheck("purge")
    if messages <= 0:
        await interaction.response.send_message(content="Количество сообщений для удаления не может быть 0 или отрицательным.", ephemeral=True)
        return
    if messages > 100:
        await interaction.response.send_message(content="Максимальное количество сообщений для удаления - 100.", ephemeral=True)
        return
    await interaction.response.send_message(f"Удаялю {messages} сообщений в {channel.mention}.")
    await channel.purge(limit=messages + 1)