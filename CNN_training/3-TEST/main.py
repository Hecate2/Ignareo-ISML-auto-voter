import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage import filters
from skimage.morphology import disk,square
from skimage.measure import regionprops
import skimage.morphology as sm
import utils
import time

time_start=time.time()
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

#%%
inputdir = os.path.join('.', 'TestData')
outputdir = os.path.join('.', 'TestResults')
utils.checkpath(outputdir)
filenames = utils.all_files_under(inputdir)


#%% load model
modelfile = os.path.join('.','Pretrained','Model.json')
weightsfile = os.path.join('.','Pretrained','Weights.h5')
model = utils.loadmodel(modelfile, weightsfile)

all_num = len(filenames)
pre_num = 0
acc_num = 0
setFont = ImageFont.truetype('C:/windows/fonts/Arial.ttf', 60)
fillColor = "#000000"
REFSTR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

for itr in range(all_num):
    filename = filenames[itr]
    img_rgb = np.array(Image.open(filename))
    img = 255-np.array((Image.open(filename)).convert('L') ) #转化为灰度图 
    cnt,image = utils.splitimage(img)
    if (cnt == 8):
        pre_num += 1
        image = np.expand_dims(image, axis=-1)
        result = model.predict(image)
        result = np.argmax(result, axis=-1)
        result = ''.join(REFSTR[ch] for ch in result)
        label = (filename[-12:-4]).upper()
        # 比对预测结果
        if label == result: 
            acc_num += 1
            
        # 展示预测结果
##        labelimage = img_rgb*0 + 255 
##        labelimage = utils.array2image(labelimage)
##        draw = ImageDraw.Draw(labelimage)
##        for j in range(8):
##            draw.text((15+50*j, 50), result[j], font=setFont, fill=fillColor)
##        newimage = np.vstack((img_rgb,labelimage))
##        _,basename = os.path.split(filename)
##        utils.array2image(newimage).save(os.path.join('.','TestResults',basename))
print('预测率：',pre_num/all_num)       
print('预测数：',pre_num)
print('准确率：',acc_num/pre_num)
print('准确数：',acc_num)
time_end=time.time()
print('totally cost',time_end-time_start)        
        
