import requests
import os
import logging

logging.basicConfig(filename='update.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = 'https://raw.githubusercontent.com/<username>/<repository>/<branch>/main.py'

try:
    response = requests.get(url)

    if response.status_code == 200:
        with open('new_main.py', 'wb') as f:
            f.write(response.content)

        os.replace('new_main.py', 'main.py')

        logging.info('Успешное обновление.')
    else:
        logging.error('Не удалось скачать обновление.')
        print('Обновление не удалось.')
except requests.exceptions.RequestException as e:
    logging.error(f'Ошибка запроса: {e}')
    print('Обновление не удалось..')
