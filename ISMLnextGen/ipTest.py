#coding:utf-8
#访问这个服务器会获得一些'ip:端口'字符串。仅用于测试
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
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

app=tornado.web.Application([
    (r'/',MainHandler),
])

if __name__ == '__main__':
    print('访问这个服务器:55556会获得一些“ip:端口”字符串。仅用于测试')
    app.listen(55556)
    tornado.ioloop.IOLoop.instance().start()
