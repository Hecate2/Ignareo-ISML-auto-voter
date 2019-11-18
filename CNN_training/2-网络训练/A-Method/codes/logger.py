import os
import sys
import numpy as np
import shutil
import utils
import tensorflow as tf
from utils import log
from keras.utils import plot_model
from keras.callbacks import TensorBoard
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


class LOGGER(object):
    def __init__(self, FLAGS):
        self.FLAGS = FLAGS
        self.model_out_dir = "../Model"
        self.log_dir = "../Log"
        utils.checkpath(self.model_out_dir)
        utils.checkpath(self.log_dir)
        self.callback = TensorBoard(self.log_dir)
        shutil.copy('./bin/plotboard.py', self.log_dir)     
        shutil.copy('./bin/run.bat', self.log_dir)     

    def save_model(self, model, savename):
        jsonfile = os.path.join(self.model_out_dir, "{}.json".format(savename))
        with open(jsonfile, 'w') as f:
            f.write(model.to_json())

    def plot_model(self, model, savename, show_shapes=True):
        try:
            picname = os.path.join(self.model_out_dir, "{}.png".format(savename))
            plot_model(model, to_file=picname, show_shapes=show_shapes)
        except:
            pass

    def save_weights(self, model, savename):
        h5file = os.path.join(self.model_out_dir, "{}.h5".format(savename))
        model.save_weights(h5file)

    def load_pretrained_weights(self, model, weightsfile):
        f_weights = os.path.join('.', 'Pretrained', weightsfile)
        if (self.FLAGS.pretrained):
            if (os.path.exists(f_weights)):
                model.load_weights(f_weights)
                log('Loaded Pretrained-Model !')
            else:
                log('Cannot find Model weights !')
                sys.exit()
        else:
            log('Train Model without Pretrained')

    def write_tensorboard(self, names, logs, step):
        for names, value in zip(names, logs):
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.simple_value = value
            summary_value.tag = names
            self.callback.writer.add_summary(summary, step)
            self.callback.writer.flush()
