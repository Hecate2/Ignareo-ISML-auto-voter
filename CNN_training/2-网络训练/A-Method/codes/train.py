import os
import sys
import utils
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from utils import log
from data import Dataset
from logger import LOGGER
from evaluation import Evaluation
from model import CNNModels
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# %% arrange arguments
FLAGS = utils.parse_args()
# %% set logger
logger = LOGGER(FLAGS)
log('Create Logger Successfully')
# %% set dataset
dataset = Dataset(FLAGS, logger)
n_train_imgs = dataset.num_train
log('Get Data Successfully')
# %% set evaluator
evaluator = Evaluation(logger, dataset)
log('Create Evaluator Successfully')

###################################################################
######################## Create Model #############################
###################################################################
# hyper-parameters
os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu_index
epochs = FLAGS.epochs
eval_freq = FLAGS.eval_frequency
batch_size = FLAGS.batch_size
batch_steps = int(n_train_imgs // batch_size)

# create networks
Models = CNNModels(FLAGS, dataset)
model = Models.Classifier()

# log network
logger.callback.set_model(model)  # record in tensorboard
logger.save_model(model, "Model")
logger.load_pretrained_weights(model, 'Model_weights.h5')
logger.plot_model(model, 'Classifier')
log('Create Networks Successfully')


#%%
###################################################################
######################## Start training ###########################
###################################################################

for epoch in range(epochs+1):
    log("Epoch {}".format(epoch + 1))
    
    # train
    loss_sum, acc_sum = 0, 0
    for i in range(batch_steps):
        x_batch, y_batch, showlabels= dataset.train_next_batch()
        loss, acc = model.train_on_batch(x_batch, y_batch) 
        loss_sum = loss_sum + loss
        acc_sum = acc_sum + acc
        utils.progressbar(i , batch_steps)
    logger.write_tensorboard(['train_acc', 'train_loss'], [acc_sum / batch_steps, loss_sum / batch_steps], epoch)
    print('Training Acc :\t{:.4f}'.format(acc_sum / batch_steps))

    # valid
    if (epoch % eval_freq == 0):
        loss, acc = evaluator.EvaluateModel(model, epoch)
        print('Validate Loss:\t{:.4f}'.format(loss))
        print('Validate Acc :\t{:.4f}'.format(acc))
        logger.save_weights(model, "Round{}_Weights".format(epoch))

