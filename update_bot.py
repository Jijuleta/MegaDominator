import os
import sys

os.replace('new_main.py', 'main.py')

python = sys.executable
os.execl(python, python, *sys.argv)
