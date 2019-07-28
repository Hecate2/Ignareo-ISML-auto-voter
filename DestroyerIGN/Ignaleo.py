# coding: utf-8
portList=(55568,55569)#本服务器监听端口
# 如果aiohttp连接超时，则会raise，但只是raise，不带错误信息

import gc#内存垃圾清理控制
#gc.disable()#关闭自动清理

from Voter import Voter
from AsyncIteratorWrapper import AsyncIteratorWrapper
import functools,re

import aiohttp,asyncio
worker_loop=asyncio.get_event_loop()

from aiocfscrape import CloudflareScraper
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

from threading import Thread

from fake_useragent import UserAgent
uaGen = UserAgent(
    fallback="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0"
    )
headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate, sdch", 
    "Accept-Language": "zh-CN,zh;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": uaGen.random,
  }

##def printer(future):
##    print(future.result())
from Voter import printer,doNothing,CaptchaServers

request_timeout=30 #单次http请求的默认超时。
#你可以随时暂时覆盖这一设置
captcha_timeout=60 #单次取验证码的默认超时
timeoutConfig=aiohttp.ClientTimeout(total=request_timeout)
captchaTimeoutConfig=aiohttp.ClientTimeout(total=captcha_timeout)

localsession = CloudflareScraper(headers=headers,loop=worker_loop,timeout=timeoutConfig)
async def localsession_get(url="https://2019.internationalsaimoe.com"):
    async with localsession.get(url,ssl=False) as res:
        text = await res.text()
        return('Ignaleo:本地session请求%s，状态码为%d'%(url,res.status))
        #return res.status

#f=open('./tmp.txt','a',encoding='utf-8')

class MainHandler(tornado.web.RequestHandler):
    id=1
    
    def get(self):
        gc.collect()
        task=localsession_get()
        future=asyncio.ensure_future(task,loop=worker_loop)
        future.add_done_callback(functools.partial(printer))
        for server in CaptchaServers.captchaServers:
            task=localsession_get(url=server)
            future=asyncio.ensure_future(task,loop=worker_loop)
            future.add_done_callback(functools.partial(printer))
        self.write('Ignaleo:使用本地session访问世萌主页和所有验证码服务器各一次')
    def post(self):
        #gc.collect()#垃圾清理
        #print(self.request.body)
        #data=self.get_argument('data')
        #print(data)
        #await asyncio.sleep(1.5)
        proxies=self.request.body.decode(encoding='utf-8').split('\r\n')
        self.write('收到POST')
        #print('收到POST\n',proxies)
        print('Ignaleo: 收到POST')
        for proxy in proxies:
            voter=Voter('http://'+proxy,worker_loop,localsession,id=self.id)
            #voter=Voter(None,worker_loop,localsession,id=self.id)
            #不使用代理，仅用于测试！
            voter.Launch()
            self.id+=1

##def start_loop(loop):
##    #  运行事件循环， loop以参数的形式传递进来运行
##    loop.run_forever()

def run_proc(port):
    AsyncIOMainLoop().install()
    app=tornado.web.Application([
        (r'/',MainHandler),
    ])
    app.listen(port)
    print('DestroyerIgnaleo@localhost:%d'%(port))
    
    print('Ignaleo开始准备本地session')
    #本地session，可用于向验证码服务器post，或许还可以用来取验证码
    task=localsession_get()
    future=asyncio.ensure_future(task,loop=worker_loop)
    future.add_done_callback(functools.partial(printer))
    for server in CaptchaServers.captchaServers:
        task=localsession_get(server)
        future=asyncio.ensure_future(task,loop=worker_loop)
        future.add_done_callback(functools.partial(printer))
    worker_loop.run_forever()

if __name__ == "__main__":
    from multiprocessing import Process
    length=len(portList)
    for port in range(length-1):
        p=Process(target=run_proc, args=(portList[port],))
        p.start()
    run_proc(portList[length-1])
##    port=55568
##    app.listen(port)
##    #producer_loop=asyncio.get_event_loop()
##    #tornadoThread=Thread(target=start_loop, args=(producer_loop,))    #生产者
##    #tornadoThread.start()   #启动生产者tornado
##    worker_loop.run_forever()
