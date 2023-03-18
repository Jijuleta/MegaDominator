import os
import sys

os.replace('new_main.py', 'main.py')

os.execv(sys.executable, ['python'] + sys.argv)
