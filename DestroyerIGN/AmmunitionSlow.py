#coding:utf-8
# 如果aiohttp连接超时，则会raise，但只是raise，不带错误信息

import aiohttp,asyncio
import re,functools
from AsyncIteratorWrapper import AsyncIteratorWrapper
import datetime
import random

#设置刷票服务器地址。会轮流向这些服务器post
serverList=[
    'http://localhost:55568/',
    'http://localhost:55569/',
    #'http://localhost:8891/',
    #'http://localhost:8892/',
    ]
random.shuffle(serverList)
serverList=tuple(serverList)#随机切换服务器的排列顺序，
#避免多个Ammunition经常向同一服务器post

#设置获取代理ip的地址，以及每多少秒获取一次。获取完成后开始计秒数
ipList=(
    #['https://www.baidu.com',3],#每3秒获取一次百度，并解析所有的'ip:端口'
    ('http://localhost:55556/',10),#测试用服务器
    #('http://localhost:55556/',5),#测试用服务器
    )
headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate, sdch", 
    "Accept-Language": "zh-CN,zh;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Ammunition Reloader for ISML battleships by Hecate2",
    #"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
  }

def server_generator():#每调用一次next(sGen)，产生一个serverList中的url
    length=len(serverList)
    i=0
    while 1:
        yield serverList[i]
        i+=1
        if(i>=length):
            i=0
            
sGen=server_generator()

async def get_ip(ip_url,delay=9):
    #输出列表：[响应状态码(200),响应文字,url,等待时间]
    try:
        async with session.get(ip_url,ssl=False) as res:
            text=await res.text()
            return (res.status,text,ip_url,delay)
    except Exception as e:
        #print(e)
        return (499,'连接失败',ip_url,delay)

async def post_ip(server_url,delay,data,ip_url):
    #输出列表：[响应状态码(200),响应文字,url,等待时间]
    try:
        async with session.post(server_url,data=data,ssl=False) as res:
            text=await res.text()   #预计返回空余线程数
            return (res.status,text,server_url,delay,ip_url,data)
    except Exception as e:
        #print(e)
        return (499,'连接失败',server_url,delay,ip_url,data)

async def sleeper(delay,ip_url):
    await asyncio.sleep(delay)
    return (ip_url,delay)

def ip_parser(future):
    #解析代理ip提供商的响应，并post到刷票服务器
    res=future.result()#result为[响应状态码,响应文字,url,等待时间]
    status,text,ip_url,delay=res[0],res[1],res[2],res[3]
    #print(res)
    if(status==200):
        matches=re.findall("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}",text)
        #print(matches)
        if len(matches)>0:
            delay=res[3]
            matches=("\r\n".join(matches)).encode(encoding='utf-8')#列表转为字符串，再转为bytes
            task=post_ip(next(sGen),delay,matches,ip_url)
            future=asyncio.ensure_future(task)
            future.add_done_callback(functools.partial(post_parser))
            return
        else:
            print('请求代理%s\n没有解析到代理ip!响应文字为\n%s'%(ip_url,text))
    else:
        print('请求代理%s出错!\n响应码为%d'%(ip_url,status))
    #出错时执行以下，重新获取ip
##    task=get_ip(ip_url,delay)
##    future=asyncio.ensure_future(task)
##    future.add_done_callback(functools.partial(ip_parser))
    #上面这个操作会疯狂重试，过于刺激。还是过几秒再重试吧
    task=sleeper(1,ip_url)
    future=asyncio.ensure_future(task)
    future.add_done_callback(functools.partial(restart))


def post_parser(future):
    #post刷票服务器之后，解析刷票服务器的响应
    res=future.result()
    status,text,server_url,delay,ip_url,data=res[0],res[1],res[2],res[3],res[4],res[5]
    if status==200:
        print(datetime.datetime.now().strftime('%H:%M:%S'),'向 %s POST成功'%(server_url))
        task=sleeper(delay,ip_url)
        future=asyncio.ensure_future(task)
        future.add_done_callback(functools.partial(restart))
    else:#post失败，向下一台服务器post
        print(datetime.datetime.now().strftime('%H:%M:%S'),'向 %s POST失败!!!!!'%(server_url))
        task=post_ip(next(sGen),delay,data,ip_url)
        future=asyncio.ensure_future(task)
        future.add_done_callback(functools.partial(post_parser))

def restart(future):
    res=future.result()
    ip_url,delay=res[0],res[1]
    task=get_ip(ip_url,delay)
    future=asyncio.ensure_future(task)
    future.add_done_callback(functools.partial(ip_parser))

if __name__=='__main__':
    worker_loop=asyncio.get_event_loop()
    timeoutConfig=aiohttp.ClientTimeout(total=1)
    session = aiohttp.ClientSession(headers=headers,loop=worker_loop,timeout=timeoutConfig)
    for ip_url in ipList:
        task=get_ip(ip_url[0],ip_url[1])
        future=asyncio.ensure_future(task)
        future.add_done_callback(functools.partial(ip_parser))
    worker_loop.run_forever()
