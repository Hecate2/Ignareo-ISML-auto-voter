#coding:utf-8
#访问这个服务器会吃到非200的状态码。仅用于测试
import tornado.ioloop
import tornado.web
import random,time

class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        #time.sleep(5)
        self.write('''
                   <!DOCTYPE html><html>
                   <head><meta charset="utf-8" />
                   <title>html<br>标签换行符详细介绍</title></head>
                   <body bgcolor="burlywood">
                   <p>我是一个段落。
                   <br>我是一个段落。<br/>
                   我是一个段落。</p>

                   <p>
                   <br>192.168.1.1:99999\n<br/>
                   <br>192.168.1.1:91241\n<br/>
                   <br>192.168.1.1:91343\n<br/>
                   <br>192.168.1.1:94223\n<br/>
                   <br>192.168.1.1:97546\n<br/>
                   <br>192.168.1.1:92342\n<br/>
                   </p>
                   </body></html>
                   ''')
        #self.send_error(503) #这样浏览器直接报错
        #if(random.random()<0.5):
        #    self.set_status(503, 'OK')  #仅设置状态码
        self.set_status(503, 'Service Unavailable')
        #self.set_status(404, 'Not found')
        #self.set_status(302, 'Redirecting...')

app=tornado.web.Application([
    (r'/',MainHandler),
])

if __name__ == '__main__':
    print('访问这个服务器:55556会获得一些“ip:端口”字符串，并吃到非200的状态码。仅用于测试')
    app.listen(55556)
    tornado.ioloop.IOLoop.instance().start()
