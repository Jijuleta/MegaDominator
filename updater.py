import urllib.request
import os

url = 'https://raw.githubusercontent.com/Jijuleta/MegaDominator/master/main.py'

try:
    urllib.request.urlretrieve(url, 'new_main.py')

    os.replace('new_main.py', 'main.py')

    os.remove('new_main.py')

    print('Update successful.')
except urllib.error.URLError as e:
    print(f'Error downloading file: {e}')
