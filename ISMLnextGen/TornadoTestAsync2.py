# coding: utf-8
from AsyncIteratorWrapper import AsyncIteratorWrapper
import asyncio
import functools

import aiohttp
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

from threading import Thread

headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate, sdch", 
    "Accept-Language": "zh-CN,zh;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
  }
session = aiohttp.ClientSession(headers=headers)
f=open('./tmp.txt','a',encoding='utf-8')

def printer(future):
    print(future.result()[0])
    f.write(future.result()[1])
    print('done')

async def producer():
    future=asyncio.run_coroutine_threadsafe(coro(),worker_loop)
    future.add_done_callback(functools.partial(printer))
    await asyncio.sleep(0)

async def coro():
    async with session.get("https://www.internationalsaimoe.com",ssl=False) as res:
        text = await res.text()
        return [res.status,text]

class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        async for i in AsyncIteratorWrapper(range(1)):
            future=asyncio.run_coroutine_threadsafe(coro(),worker_loop)
            future.add_done_callback(functools.partial(printer))
            #await producer()
            #await asyncio.run_coroutine_threadsafe(coro(), loop)
        #text = await asyncio.get_event_loop().create_task(coro())
        #self.write(text)
        self.finish('It works!')
    def post(self):
        print(self.request.body)
        #data=self.get_argument('data')
        #print(data)
        self.write('收到POST')
        print('收到POST')

def start_loop(loop):
    #  运行事件循环， loop以参数的形式传递进来运行
    loop.run_forever()
    
if __name__ == "__main__":
    AsyncIOMainLoop().install()
    app = tornado.web.Application([(r"/", MainHandler)])
    app.listen(8888)
    print('TornadoTestAsync2@localhost:8888')
    producer_loop=asyncio.get_event_loop()
    tornadoThread=Thread(target=start_loop, args=(producer_loop,))    #生产者
    tornadoThread.start()   #启动生产者tornado

    worker_loop=asyncio.get_event_loop()
