# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install updates
RUN apt-get -y update
RUN apt-get -y upgrade

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY cipher.py /usr/local/lib/python3.10/site-packages/pytube/cipher.py

# Install ffmpeg
RUN apt-get install -y ffmpeg
RUN apt-get install -y nano

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]
