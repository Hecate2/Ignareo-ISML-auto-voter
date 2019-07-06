#coding:utf-8
#多线程计算，客户端能收到返回值

import time
import datetime
import os
import tornado.web
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        print('index')
class NonBlockingHandler(tornado.web.RequestHandler):
    #多线程
    executor = ThreadPoolExecutor(4)
    @gen.coroutine
    def get(self):
        try:
            start = time.time()
            # 并发执行
            result1, result2 = yield gen.with_timeout(datetime.timedelta(seconds=15), [self.doing(1), self.doing(2)], quiet_exceptions=tornado.gen.TimeoutError)
            # 
            self.write("NO Timeout {} {}".format(result1,result2))
            #print(result1, result2)
            #print(time.time() - start)
        except gen.TimeoutError:
            self.write("Timeout")
            #print("Timeout")
            #print(time.time() - start)
    # 使用tornado 线程池需要加上下面的装饰器到I/O函数
    @run_on_executor
    def doing(self, num):
        #time.sleep(3)
        while(num<1048576*20):
            num=num+1
        return 'Non-Blocking%d' % num
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    print('A server that returns results.')
    application.listen(8890)
    tornado.ioloop.IOLoop.instance().start()
