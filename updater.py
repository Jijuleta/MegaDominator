import requests
import os

url = 'https://raw.githubusercontent.com/Jijuleta/MegaDominator/master/main.py'

response = requests.get(url)

if response.status_code == 200:
    with open('new_main.py', 'wb') as f:
        f.write(response.content)

    os.replace('new_main.py', 'main.py')

    print('Обновление успешно завершено.')
else:
    print('Ошибка обновления.')





