FROM python:3.12

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install virtualenv \
    && virtualenv venv

RUN bash -c "source venv/bin/activate && pip install -r requirements.txt"

COPY . .

CMD ["bash", "-c", "source venv/bin/activate && python main.py"]
