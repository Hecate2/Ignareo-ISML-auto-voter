#coding:utf-8
#异步服务，且客户端不需要返回值
#实战中的功能：收取一批ip地址的post，然后对每次post开一个线程
#一个线程内部完成数百个ip异步投票？
import tornado.ioloop
import tornado.web
from concurrent.futures import ThreadPoolExecutor
import functools,os,time
import requests

f=open('./tmp.txt','a',encoding='utf-8')

class FutureHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(1000)
    
    #@tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        #try:
            url = 'https://www.baidu.com'
            #tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self.ping, url))
            for i in range(200):
                tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self.req, url))
            self.finish('It works')
        #except Exception as e:
            #print(e)
 
    @tornado.concurrent.run_on_executor
    def ping(self, url):
        os.system("ping {}".format(url))
        #print('pinged')

    @tornado.concurrent.run_on_executor
    def req(self, url):
        s=requests.session()
        try:
            for i in range(10):
                r = s.get('https://www.internationalsaimoe.com')
                #r = requests.get(url)
                if r.status_code!=200:
                    print(r.status_code)
                #with open('./tmp.txt','a') as f:
                    #f.write('{}\r\n'.format(r.status_code))
                f.write(r.text)
                time.sleep(10)
        except Exception as e:
            print(e)
app=tornado.web.Application([
    (r'/future',FutureHandler),
])

if __name__ == '__main__':
    print('A server that doesn`t return results.')
    app.listen(8889)
    tornado.ioloop.IOLoop.instance().start()
