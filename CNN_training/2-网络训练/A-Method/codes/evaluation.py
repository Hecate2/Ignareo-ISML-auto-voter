import os
import sys
import utils
import random
import datetime
import argparse
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve


class Evaluation(object):
    def __init__(self, logger, dataset):
        self.logger = logger
        self.dataset = dataset
        self.batch_size = dataset.batch_size

    def EvaluateModel(self, model, epoch):
        val_names = self.dataset.val_names
        input_size = self.dataset.input_size
        x_batch, y_batch, _ = self.dataset.get_imgs(val_names, input_size)
        loss, acc = model.evaluate(x_batch, y_batch, batch_size=self.batch_size, verbose=0)
        self.logger.write_tensorboard(['valid_acc', 'valid_loss'], [acc, loss], epoch)
        return loss, acc

    def PredictFiles(self, model, filenames, batch_size, epoch):
        self.test_names = filenames
        test_images, test_labels, showlabels = self.dataset.get_imgs(filenames,
                                                                     self.dataset.input_size)

        # predict
        pre_result = model.predict(test_images, batch_size=self.batch_size)
        # decode result
        result = []
        for i in range(test_images.shape[0]):
            result.append(decode(pre_result[i, ...]))
        self.test_result = result
        self.test_labels = showlabels
        # acc
        self.Measure_Acc(epoch)

    def Measure_Acc(self, epoch):
        acc = 0
        for i in range(len(self.test_result)):
            result = self.test_result[i]
            label = self.test_labels[i]
            print('GT: {}\tPre: {}'.format(label, result))
            if (result == label):
                acc += 1
        print('*' * 30)
        print('Test Accuracy : {}\n'.format(acc / len(self.test_result)))

"""
evaluation utils
"""

def decode(result):
    result = np.reshape(result, (10, 4), order='F')
    index = np.argmax(result, axis=0)
    string = ''.join(str(ch) for ch in index)

    return string