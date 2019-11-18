import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import utils
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--filename', default='test.png', type=str)
FLAGS, _ = parser.parse_known_args()

time_start=time.time()
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

#%% load model
modelfile = os.path.join('.','Pretrained','Model.json')
weightsfile = os.path.join('.','Pretrained','Weights.h5')

REFSTR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


filename = FLAGS.filename
img_rgb = np.array(Image.open(filename))
img = 255-np.array((Image.open(filename)).convert('L') ) #转化为灰度图 
cnt,image = utils.splitimage(img)
if (cnt == 8):
    image = np.expand_dims(image, axis=-1)
    model = utils.loadmodel(modelfile, weightsfile)
    result = model.predict(image)
    result = np.argmax(result, axis=-1)
    result = ''.join(REFSTR[ch] for ch in result)
    label = (filename[-12:-4]).upper()
    print('识别结果：{}'.format(label))
else:
    print('取消识别！')
    
time_end=time.time()
print('Totally cost:{}s'.format(time_end-time_start))        
        