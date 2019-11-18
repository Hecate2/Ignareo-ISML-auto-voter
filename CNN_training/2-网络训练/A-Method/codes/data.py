import os
import utils
import random
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from utils import log
from datetime import datetime
from numpy.random import choice


class Dataset(object):
    def __init__(self, FLAGS, LOGGER):
        self.input_size = (60, 60)  # image (input the GAN) size, must be times of 2^4
        self.class_num = 36

        self.FLAGS = FLAGS
        self.val_ratio = FLAGS.val_ratio
        self.batch_size = FLAGS.batch_size

        #%% input dirs
        self.data_dir = os.path.join('..', 'Data')
        self.train_dir = os.path.join('..', 'Data', 'DataTrain')
        # self.test_dir = os.path.join('..', 'Data', 'DataTest')

        #%% output dirs
        self.split_record_dir = os.path.join(LOGGER.log_dir, 'SplitRecord')
        utils.checkpath(self.split_record_dir)

        #%% record data list and split
        self._read_data_list()

        #%% implement batch fetcher
        self.train_batch_fetcher = TrainBatchFetcher(self.train_names, self.batch_size)

    def _read_data_list(self):
        self.all_file_names = utils.all_files_under(self.train_dir)
        # self.test_names = utils.all_files_under(self.test_dir)

        # split train files and validation files
        self.num_train, self.num_val, self.num_test = 0, 0, 0
        self.num_all = int(len(self.all_file_names))
        self.num_val = int(np.floor(self.val_ratio * self.num_all))
        self.num_train = self.num_all - self.num_val
        # self.num_test = len(self.test_names)
        self.train_names, self.val_names = utils.split_names(self.all_file_names, self.num_train)
        print("Num of training images:  {}".format(self.num_train))
        print("Num of validation images:{}".format(self.num_val))
        print("Num of test images:      {}".format(self.num_test))

        #%% record split
        timestr = datetime.now().strftime('%Y%m%d%H%M%S')
        self.SplitRecord_file = os.path.join(self.split_record_dir,
                                             "DataSplit{}.txt".format(timestr))
        utils.list2txt(self.SplitRecord_file, ['\nTrainFiles\n'] + self.train_names)
        utils.list2txt(self.SplitRecord_file, ['\nValidationFiles\n'] + self.val_names)

    def train_next_batch(self):
        batch_names = self.train_batch_fetcher.next()
        train_imgs, train_labels, showlabels = self.get_imgs(batch_names, self.input_size)

        return train_imgs, train_labels, showlabels

    def get_imgs(self, file_names, input_size):
        n_files = len(file_names)

        images = np.zeros((n_files, input_size[0], input_size[1], 1))
        labels = np.zeros((n_files, self.class_num), dtype=np.uint8)
        showlabels = []

        # load images tensor
        for i in range(n_files):
            filename = file_names[i]
            temp_img = (Image.open(filename)).convert('L')
            images[i, ...] = np.expand_dims(np.array(temp_img), axis=-1)

            label_str = filename[-5]
            showlabels.append(label_str)
            labels[i, ... ] = self.encode(label_str)

        images = images / 255.0

        return images, labels, showlabels

    def encode(self, labelstr):
        REFSTR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        labelstr = labelstr.upper()
        label = np.zeros((1, self.class_num), dtype=np.uint8)
        label[0, REFSTR.find(labelstr)] = 1
        
        return label


class TrainBatchFetcher(object):
    def __init__(self, train_names, batch_size):
        self.train_names = train_names
        self.n_train_names = len(self.train_names)
        self.batch_size = batch_size

    def next(self):
        indices = list(choice(self.n_train_names, self.batch_size))
        self.train_batch_names = []
        for i in indices:
            self.train_batch_names.append(self.train_names[i])

        return self.train_batch_names