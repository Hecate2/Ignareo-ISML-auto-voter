import os
import sys

import webbrowser


url='http://localhost:6006/'
webbrowser.open(url, new=0, autoraise=True)

os.system('tensorboard --logdir=./')

