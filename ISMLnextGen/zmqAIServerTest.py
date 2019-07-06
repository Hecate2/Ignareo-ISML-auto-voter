from  multiprocessing import Process
import zmq
import numpy as np
from time import sleep
#import shutil
#import os
from random import random
from io import BytesIO
from PIL import Image
from base64 import b64decode
import utils
model = utils.loadmodel('Model.json', 'Weights.h5')
REFSTR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def server(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print ("Running server on port: ", port)
    # serves only 5 request and dies
    #for reqnum in range(5):
    #i=1
    while(1):
        # Wait for next request from client
        img = b64decode(socket.recv())
        img = Image.open(BytesIO(img))
        img = 255-np.array(img.convert('L') ) #转化为灰度图
        cnt,img = utils.splitimage(img)
        img = np.expand_dims(img, axis=-1)#到此result还是个图片
        img = model.predict(img)
        img = np.argmax(img, axis=-1)
        img = ''.join(REFSTR[ch] for ch in img)
        if(random()<0.8568):
            img = img.lower()
        #print ("Received request #%s: %s" % (i, img))
        socket.send( img.encode("ascii") )
        #i=i+1

if __name__ == "__main__":
    server_ports = range(5552,5554,1)
    for server_port in server_ports:
        Process(target=server, args=(server_port,)).start()
    server(port='5551')
