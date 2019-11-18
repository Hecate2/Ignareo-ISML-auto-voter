import os
import sys
import pickle
import random
import datetime
import argparse
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image, ImageEnhance
from skimage import filters
from skimage import measure
from sklearn.metrics import auc
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve
from scipy.ndimage import rotate
"""
general utils
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', default=10, type=int)
    parser.add_argument('--gpu_index', default='1', type=str)
    parser.add_argument('--batch_size', default=256, type=int)
    parser.add_argument('--val_ratio', default=0.1, type=float)
    parser.add_argument('--learning_rate', default=2e-4, type=float)
    parser.add_argument('--eval_frequency', default=1, type=int)
    parser.add_argument('--pretrained', default=False, type=bool, help="whether load pretrained model")
    FLAGS, _ = parser.parse_known_args()

    log('Settings')
    for i in vars(FLAGS):
        if len(i) < 8:
            print(i + '\t\t------------  ' + str(vars(FLAGS)[i]))
        else:
            print(i + '\t------------  ' + str(vars(FLAGS)[i]))
    print()

    return FLAGS


def progressbar(progress, total, length=40):
    total = total - 1
    num = int(progress / total * length)
    sys.stdout.write('#' * num + '_' * (length - num))
    sys.stdout.write(':{:.2f}%'.format(progress / total * 100) + '\r')
    if progress == total:
        sys.stdout.write('\n\n')
    sys.stdout.flush()


def checkpath(path):
    try:
        os.makedirs(path)
        # print('creat ' + path)
    except OSError:
        pass


def log(text):
    """
    log status with time label
    """
    print()
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line1 = '=' * 10 + '  ' + nowTime + '  ' + '=' * 10
    length = len(line1)
    leftnum = int((length - 4 - len(text)) / 2)
    rightnum = length - 4 - len(text) - leftnum
    line2 = '*' * leftnum + ' ' * 2 + text + ' ' * 2 + '*' * rightnum
    print(line1)
    print(line2)
    print('=' * len(line1))


"""
utils for data class
"""


def all_files_under(path, extension=None, append_path=True, sort=True):
    if append_path:
        if extension is None:
            filenames = [os.path.join(path, fname) for fname in os.listdir(path)]
        else:
            filenames = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith(extension)]
    else:
        if extension is None:
            filenames = [os.path.basename(fname) for fname in os.listdir(path)]
        else:
            filenames = [os.path.basename(fname) for fname in os.listdir(path) if fname.endswith(extension)]

    if sort:
        filenames = sorted(filenames)

    return filenames


def read_txt(filename):
    """
    read txt content from the txtfile
    """
    names = []
    if (os.path.exists(filename)):
        f = open(filename)
        line = f.readline()
        while line:
            if (line[-1] == '\n'):
                names.append(line[:-1])
            else:
                names.append(line)
            line = f.readline()
        return names  # do not return last \n
    else:
        (_, txtname) = os.path.split(filename)
        log('cannot find {}'.format(txtname))


def split_names(filenames, num_train):
    random.seed(10)
    train_names = random.sample(filenames, num_train)
    val_names = []
    for x in filenames:
        if (x not in train_names):
            val_names.append(x)

    return train_names, val_names


def list2txt(filename, inputlist):
    fp = open(filename, 'a')
    for line in inputlist:
        fp.writelines(line + '\n')
    fp.close()
    return True


def image_shape(filename):
    img = Image.open(filename)
    img_arr = np.asarray(img)
    img_shape = img_arr.shape
    return img_shape


def imagefiles2arrs(filenames):
    img_shape = image_shape(filenames[0])
    if len(img_shape) == 3:
        images_arr = np.zeros((len(filenames), img_shape[0], img_shape[1], img_shape[2]), dtype=np.float32)
    elif len(img_shape) == 2:
        images_arr = np.zeros((len(filenames), img_shape[0], img_shape[1]), dtype=np.float32)

    for file_index in range(len(filenames)):
        img = Image.open(filenames[file_index])
        images_arr[file_index] = np.asarray(img).astype(np.float32)

    return images_arr


def random_perturbation(imgs):
    for i in range(imgs.shape[0]):
        im = Image.fromarray(imgs[i, ...].astype(np.uint8))
        en = ImageEnhance.Color(im)
        im = en.enhance(random.uniform(0.8, 1.2))
        imgs[i, ...] = np.asarray(im).astype(np.float32)
    return imgs


def pad_tensor(tensor, tensor_size):
    org_h, org_w = tensor.shape[1], tensor.shape[2]
    target_h, target_w = tensor_size[0], tensor_size[1]

    if len(tensor.shape) == 4:
        d = tensor.shape[3]
        padded = np.zeros((tensor.shape[0], target_h, target_w, d))
    elif len(tensor.shape) == 3:
        padded = np.zeros((tensor.shape[0], target_h, target_w))

    padded[:, (target_h - org_h) // 2:(target_h - org_h) // 2 + org_h, (target_w - org_w) // 2:(target_w - org_w) // 2 + org_w, ...] = tensor

    return padded


def pad_img(img, img_size):
    img_h, img_w = img.shape[0], img.shape[1]
    target_h, target_w = img_size[0], img_size[1]

    if len(img.shape) == 3:
        d = img.shape[2]
        padded = np.zeros((target_h, target_w, d))
    elif len(img.shape) == 2:
        padded = np.zeros((target_h, target_w))

    padded[(target_h - img_h) // 2:(target_h - img_h) // 2 + img_h, (target_w - img_w) // 2:(target_w - img_w) // 2 + img_w, ...] = img

    return padded


def crop_tensor(tensor, ori_shape):
    pred_shape = tensor.shape
    assert len(pred_shape) > 2

    if ori_shape == pred_shape:
        return tensor
    else:
        if len(tensor.shape) > 3:
            ori_h, ori_w = ori_shape[0], ori_shape[1]
            pred_h, pred_w = pred_shape[1], pred_shape[2]

            start_h, start_w = (pred_h - ori_h) // 2, (pred_w - ori_w) // 2
            end_h, end_w = start_h + ori_h, start_w + ori_w

            return tensor[:, start_h:end_h, start_w:end_w, :]
        else:
            ori_h, ori_w = ori_shape[0], ori_shape[1]
            pred_h, pred_w = pred_shape[1], pred_shape[2]

            start_h, start_w = (pred_h - ori_h) // 2, (pred_w - ori_w) // 2
            end_h, end_w = start_h + ori_h, start_w + ori_w

            return tensor[:, start_h:end_h, start_w:end_w]


def crop_img(imgs, ori_shape):
    pred_shape = imgs.shape
    assert len(pred_shape) > 1

    if ori_shape == pred_shape:
        return imgs
    else:
        if len(imgs.shape) > 2:
            ori_h, ori_w = ori_shape[0], ori_shape[1]
            pred_h, pred_w = pred_shape[0], pred_shape[1]
            start_h, start_w = (pred_h - ori_h) // 2, (pred_w - ori_w) // 2
            end_h, end_w = start_h + ori_h, start_w + ori_w

            return imgs[start_h:end_h, start_w:end_w, :]
        else:
            ori_h, ori_w = ori_shape[0], ori_shape[1]
            pred_h, pred_w = pred_shape[0], pred_shape[1]

            start_h, start_w = (pred_h - ori_h) // 2, (pred_w - ori_w) // 2
            end_h, end_w = start_h + ori_h, start_w + ori_w

            return imgs[start_h:end_h, start_w:end_w]


def array2image(arr):
    if (np.max(arr) <= 1):
        image = Image.fromarray((arr * 255).astype(np.uint8))
    else:
        image = Image.fromarray((arr).astype(np.uint8))

    return image


"""
utils for Models
"""


def make_trainable(net, val):
    net.trainable = val
    for l in net.layers:
        l.trainable = val


def discriminator_shape(n, d_out_shape):
    if len(d_out_shape) == 1:  # image gan
        return (n, d_out_shape[0])
    elif len(d_out_shape) == 3:  # pixel, patch gan
        return (n, d_out_shape[0], d_out_shape[1], d_out_shape[2])
    return None


"""
utils for evaluation
"""


class Scheduler:
    def __init__(self, n_itrs_per_epoch_d, n_itrs_per_epoch_g, schedules, init_lr):
        self.schedules = schedules
        self.init_dsteps = n_itrs_per_epoch_d
        self.init_gsteps = n_itrs_per_epoch_g
        self.init_lr = init_lr
        self.dsteps = self.init_dsteps
        self.gsteps = self.init_gsteps
        self.lr = self.init_lr

    def get_dsteps(self):
        return self.dsteps

    def get_gsteps(self):
        return self.gsteps

    def get_lr(self):
        return self.lr

    def update_steps(self, n_round):
        key = str(n_round)
        if key in self.schedules['lr_decay']:
            self.lr = self.init_lr * self.schedules['lr_decay'][key]
        if key in self.schedules['step_decay']:
            self.dsteps = max(int(self.init_dsteps * self.schedules['step_decay'][key]), 1)
            self.gsteps = max(int(self.init_gsteps * self.schedules['step_decay'][key]), 1)
