#import argparse
#import datetime
#import os
#import pickle
#import random
#import sys

import numpy as np
#import matplotlib.pyplot as plt
from PIL import Image#, ImageEnhance
#import skimage.morphology as sm
from skimage.morphology import opening,label
#from scipy.ndimage import rotate
from skimage.filters import gaussian
#from skimage.morphology import disk,square
from skimage.measure import regionprops
#import skimage
from skimage.exposure import equalize_hist
from cv2 import resize

from keras.models import model_from_json

def loadmodel(Modelfile, Weightsfile):
    with open(Modelfile, 'r') as f:
        model = model_from_json(f.read())
    model.load_weights(Weightsfile)
    
    return model

def judge(img): #仅判断能否识别
    img = img[97:,:]
    img=gaussian(img, sigma=0.85)
    img=equalize_hist(img)
    img=(img > 0.7)*1.0
    img=opening(img,selem=np.array([[0,1,0],[1,1,1],[0,1,0]]))
    image_region=img*0
    img=label(img,connectivity=1)
    props = regionprops(img)
    cnt=0
    centerx=[]
    width=[]
    for i in range(np.max(img)):
        if props[i]['area'] > 290:
            image_region = image_region + (img==props[i]['label'])
            centerx.append(props[i]['centroid'][1])
            width.append(props[i]['image'].shape[1])
            cnt += 1
    # 八个连通域
    if cnt != 8:
        return False
    # 连通域之间距离；宽高比
    centerx.sort()
    if np.std(np.diff(np.array(centerx))) > 10 or np.min(np.array(width)) < 18:
        return False
    return True

def splitimage(img):
    img = img[97:,:]
##    img_blur = filters.gaussian(img, sigma=0.85)
##    img_equal = skimage.exposure.equalize_hist(img_blur)
##    img_bin = (img_equal > 0.7)*1.0
##    #%% 开运算去噪
##    se = np.array([[0,1,0],
##                    [1,1,1],
##                    [0,1,0]])
##    #se2 = square(3)
##    img_open = sm.opening(img_bin,selem=se)
##    img_label = sm.label(img_open,connectivity=1)
    img=gaussian(img, sigma=0.85)
    img=equalize_hist(img)
    img=(img > 0.7)*1.0
    img=opening(img,selem=np.array([[0,1,0],[1,1,1],[0,1,0]]))
    image_region=img*0
    img=label(img,connectivity=1)
    
    #%% 连通域分割
##    th_area = 290
##    props = regionprops(img_label)
##    image_region = img_bin*0
##    cnt = 0
##    centerx = []
##    width = []
##    for i in range(np.max(img_label)):
##        if props[i]['area'] > th_area:
##            image_region = image_region + (img_label==props[i]['label'])
##            centerx.append(props[i]['centroid'][1])
##            [h,w] = props[i]['image'].shape
##            width.append(w)
##            cnt += 1
    props = regionprops(img)
    cnt=0
    centerx=[]
    width=[]
    for i in range(np.max(img)):
        if props[i]['area'] > 290:
            image_region = image_region + (img==props[i]['label'])
            centerx.append(props[i]['centroid'][1])
            width.append(props[i]['image'].shape[1])
            cnt += 1
    # 八个连通域
    if cnt != 8:
        return cnt, None
    # 连通域之间距离；宽高比
    centerx.sort()
    if np.std(np.diff(np.array(centerx))) > 10 or np.min(np.array(width)) < 18:
        return 0, None

    del img,centerx,width
            
    #%% 
##    region_label = sm.label(image_region,connectivity=1)
##    props = regionprops(region_label)
##    images = np.zeros([8,60,60])
##    xpos = np.zeros([8,])
##    for i in range(np.max(region_label)):
##        temp = props[i]['image']*1.0
##        boxwidth = np.max(temp.shape)+6
##        temp = pad_img(temp,(boxwidth,boxwidth))
##        images[i,...] = resize(temp, (60,60))
##        xpos[i] = props[i]['centroid'][1]
    region_label = label(image_region,connectivity=1)
    props = regionprops(region_label)
    images = np.zeros([8,60,60])
    xpos = np.zeros([8,])
    for i in range(np.max(region_label)):
        temp = props[i]['image']*1.0
        boxwidth = np.max(temp.shape)+6
        temp = pad_img(temp,(boxwidth,boxwidth))
        images[i,...] = resize(temp, (60,60))
        xpos[i] = props[i]['centroid'][1]

    #%% save result
##    xpos = xpos.transpose()
##    sortindex = np.argsort(xpos)
    sortindex = np.argsort(xpos.transpose())
    sortimages = images * 0
    for i in range(8):
        sortimages[i, ...] = images[sortindex[i], ...]
    
    #return cnt, sortimages
    return 8, sortimages


"""
general utils
"""
##def progressbar(progress, total, length=40):
##    progress = progress + 1
##    num = int(progress / total * length)
##    sys.stdout.write('#' * num + '_' * (length - num))
##    sys.stdout.write(':{:.2f}%'.format(progress / total * 100) + '\r')
##    if progress == total:
##        sys.stdout.write('\n\n')
##    sys.stdout.flush()


##def all_files_under(path, extension=None, append_path=True, sort=True):
##    if append_path:
##        if extension is None:
##            filenames = [os.path.join(path, fname) for fname in os.listdir(path)]
##        else:
##            filenames = [
##                os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith(extension)
##            ]
##    else:
##        if extension is None:
##            filenames = [os.path.basename(fname) for fname in os.listdir(path)]
##        else:
##            filenames = [
##                os.path.basename(fname) for fname in os.listdir(path) if fname.endswith(extension)
##            ]
##
##    if sort:
##        filenames = sorted(filenames)
##
##    return filenames


#%%
##def checkpath(path):
##    try:
##        os.makedirs(path)
##        print('creat ' + path)
##    except OSError:
##        pass


def pad_img(img, img_size):
    img_h, img_w = img.shape[0], img.shape[1]
    target_h, target_w = img_size[0], img_size[1]

    if len(img.shape) == 3:
        d = img.shape[2]
        padded = np.zeros((target_h, target_w, d))
    elif len(img.shape) == 2:
        padded = np.zeros((target_h, target_w))

    padded[(target_h - img_h) // 2:(target_h - img_h) // 2 +
        img_h, (target_w - img_w) // 2:(target_w - img_w) // 2 + img_w, ...] = img

    return padded


##def array2image(arr):
##    if (np.max(arr) <= 1):
##        image = Image.fromarray((arr * 255).astype(np.uint8))
##    else:
##        image = Image.fromarray((arr).astype(np.uint8))
##    return image

##def threshold_by_otus(img):
##    th = filters.threshold_otsu(img)
##    img = (img >= th)*1.0
##    return img
    
