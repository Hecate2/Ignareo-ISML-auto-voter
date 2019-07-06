# coding: utf-8
from AsyncIteratorWrapper import AsyncIteratorWrapper
import asyncio

import aiohttp
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop


headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate, sdch", 
    "Accept-Language": "zh-CN,zh;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
  }
session = aiohttp.ClientSession(headers=headers)
f=open('./tmp.txt','a',encoding='utf-8')

async def producer():
    asyncio.run_coroutine_threadsafe(coro(),thread_loop)
    await asyncio.sleep(0)

async def coro():
    async with session.get("https://www.internationalsaimoe.com",ssl=False) as res:
        text = await res.text()
    return text

class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        async for i in AsyncIteratorWrapper(range(10)):
            await asyncio.run_coroutine_threadsafe(coro(), loop)
        #text = await asyncio.get_event_loop().create_task(coro())
        #self.write(text)
        self.finish('It works!')
    pass



if __name__ == "__main__":
    AsyncIOMainLoop().install()
    app = tornado.web.Application([(r"/", MainHandler)])
    app.listen(8888)
    loop=asyncio.get_event_loop()
    loop.run_forever()
    
