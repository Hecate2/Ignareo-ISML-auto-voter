import tornado.ioloop
import tornado.web
import numpy as np
#import shutil
#import os
from random import random
from io import BytesIO
from PIL import Image
from base64 import b64decode
import utils
model = utils.loadmodel('Model.json', 'Weights.h5')
REFSTR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class UploadFileHandler(tornado.web.RequestHandler):
##    def get(self):
##        #允许浏览器直接访问，手动上传图片并识别。此功能仅用于测试和娱乐
##        self.write('''
##<html>
##  <head><title>Upload File</title></head>
##  <body>
##    <form action='file' enctype="multipart/form-data" method='post'>
##    <input type='file' name='file'/><br/>
##    <input type='submit' value='submit'/>
##    </form>
##  </body>
##</html>
##''')
    def get(self):
        self.write('delayed')
    def post(self):
        try:
            #upload_path=os.path.join(os.path.dirname(__file__),'files')  #文件的暂存路径
            #file_metas=self.request.files['file']    #提取表单中‘name’为‘file’的文件元数据
            #print(file_metas)
            #print(self)
            #img0 = b64decode(self.get_argument('file'))
            #img = Image.open(BytesIO(img0))
            img = b64decode(self.get_argument('file'))
            img = Image.open(BytesIO(img))
            img = 255-np.array(img.convert('L') ) #转化为灰度图
            cnt,img = utils.splitimage(img)
            img = np.expand_dims(img, axis=-1)#到此result还是个图片
            img = model.predict(img)
            img = np.argmax(img, axis=-1)
            img = ''.join(REFSTR[ch] for ch in img)
##        for meta in file_metas:
##            filename=meta['filename']
##            filepath=os.path.join(upload_path,filename)
##            with open(filepath,'wb') as up:      #有些文件需要已二进制的形式存储，实际中可以更改
##                up.write(meta['body'])
            if(random()<0.8568):
                img = img.lower()
            self.write(img)
            #print(img)
            try:
                with open('%s.txt'%('未执行投票'+img),'wb') as imgSave:
                    #imgSave.write(img0)
                    pass
            except Exception:
                print ('存验证码出错 可能硬盘过载!')
        except Exception as e:
            self.write('!')
            print(e)

app=tornado.web.Application([
    (r'/file',UploadFileHandler),
])

if __name__ == '__main__':
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
