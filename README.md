# MegaDominator

Это самый добрый бот для Discord, который ТОЧНО не создан для буллинга людей.

# ПЕРВОЕ ВКЛЮЧЕНИЕ:
- Для того, чтобы бот запускался, нужно создать файл с названием config.py, в котором будет содержаться переменная API_TOKEN.
**(ПРИМЕР:  API_TOKEN = "ТОКЕН БОТА")**

# ИСПОЛЬЗОВАНИЕ БОТА:
- Для вывода списка команд используйте - $help
- Для корректной работы бота, нужно включить PRESENCE INTENT, SERVER MEMBERS INTENT, MESSAGE CONTENT INTENT в настройках Bot(https://discord.com/developers/applications).

# ИСПОЛЬЗОВАНИЕ МУЗЫКАЛЬНЫХ КОМАНД:
Музыкальные команды работают ТОЛЬКО при установленном FFmpeg.
Ссылки на скачивание: 
- For Windows: https://ffmpeg.org/download.html#build-windows 
- For macOS: https://ffmpeg.org/download.html#build-mac
- For Linux: https://ffmpeg.org/download.html#build-linux

Инструкция по установке:
- https://www.hostinger.com/tutorials/how-to-install-ffmpeg

Для Docker используйте:
- RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

**Бот воспринимает только MP3 файлы.**


