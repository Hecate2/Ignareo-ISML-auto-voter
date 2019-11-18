import os
import tensorflow as tf

from keras import backend as K
from keras import objectives
from keras.models import Model
from keras.layers import Conv2D, MaxPooling2D, Dense
from keras.layers import Input, Concatenate, Dropout
from keras.layers import Maximum, Lambda
from keras.layers.core import Activation, Flatten, Reshape
from keras.layers.normalization import BatchNormalization
from keras.utils import plot_model
from keras.optimizers import Adam

os.environ['KERAS_BACKEND'] = 'tensorflow'
K.set_image_dim_ordering('tf')


class CNNModels(object):
    def __init__(self, FLAGS, dataset):
        self.FLAGS = FLAGS
        self.img_ch = 1
        self.class_num = dataset.class_num
        self.img_size = dataset.input_size
        self.init_lr = FLAGS.learning_rate

    def Classifier(self, name='Classifier'):

        img_ch = self.img_ch  # image channels
        class_num = self.class_num  # output channel
        img_height, img_width = self.img_size[0], self.img_size[1]
        padding = 'same'  #'valid'

        inputs = Input((img_height, img_width, img_ch))

        conv1 = Conv2D(32, kernel_size=(3, 3), strides=(1, 1), padding=padding)(inputs)
        conv1 = BatchNormalization(scale=False, axis=3)(conv1)
        conv1 = Activation('relu')(conv1)
        conv1 = Conv2D(32, kernel_size=(3, 3), strides=(2, 2), padding=padding)(conv1)
        conv1 = BatchNormalization(scale=False, axis=3)(conv1)
        conv1 = Activation('relu')(conv1)

        conv2 = Conv2D(64, kernel_size=(3, 3), strides=(2, 2), padding=padding)(conv1)
        conv2 = BatchNormalization(scale=False, axis=3)(conv2)
        conv2 = Activation('relu')(conv2)

        flat = Flatten()(conv2)
        fc1 = Dense(512, activation='relu')(flat)
        fc1 = Dropout(0.2)(fc1)

        outputs = Dense(self.class_num, activation='sigmoid')(fc1)

        model = Model(inputs, outputs, name=name)

        def train_loss(y_true, y_pred):
            Loss = objectives.binary_crossentropy(K.flatten(y_true), K.flatten(y_pred))

            return Loss


        model.compile(optimizer=Adam(lr=self.init_lr), loss=train_loss, metrics=['accuracy'])

        return model
