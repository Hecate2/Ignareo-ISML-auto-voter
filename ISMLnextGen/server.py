import tornado.ioloop
import tornado.web
import json
from mainHandler import mainHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #import time
        #time.sleep(10)
        #self.write("Hello, world")
        self.write("ready")
        print(self.request.headers)
        #print("requested")
    def post(self):
        #self.write(self.request.headers)
        mainHandler.get_ip(self.request.body,ipNum=self.request.headers.get('ipNum'))


application = tornado.web.Application([
    (r"/main", MainHandler),
])

if __name__ == "__main__":
    print("刷票服务器启动")
    application.listen(8999)
    tornado.ioloop.IOLoop.instance().start()