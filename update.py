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
        
        url_req = 'https://raw.githubusercontent.com/Jijuleta/MegaDominator/master/requirements.txt'
        req = requests.get(url_req)
        if req.status_code == 200:
            with open('new_requirements.txt', 'wb') as f:
                f.write(req.content)
                f.close()
            os.replace('new_requirements.txt', 'requirements.txt')
            os.system('pip install -r requirements.txt')
            print(f'Зависимости успешно обновлены.')
        else:
            print('Не удалось обновить зависимости.')
    else:
        print('Не удалось обновить бота.')
    
update()
