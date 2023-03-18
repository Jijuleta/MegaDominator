import requests
import os

def update():
    url = 'https://raw.githubusercontent.com/Jijuleta/MegaDominator/master/main.py'
    code = requests.get(url)
    if code.status_code == 200:
        with open('new_main.py', 'wb') as f:
            f.write(code.content)
            f.close()
        os.replace('new_main.py', 'main.py')
        print(f'Бот успешно обновлен.')
    else:
        print('Не удалось обновить бота.')
    
update()