#coding:utf-8
#使用gevent使requests异步化
import asyncio,gevent
from gevent import monkey
monkey.patch_all()

import functools,os,time,gc,random,re
repattern=re.compile('voting_token" value="(.*?)"')
waiting_time_pattern = re.compile('''<input id="voting_form_submit" type="submit" value="(.*?)" disabled="">''')

portList=tuple([i for i in range(55568,55578)])#本服务器监听端口

#验证码服务器
captchaServers=[
    'http://localhost:8889',
    ]
random.shuffle(captchaServers)
class CaptchaServers:
    captchaServers=captchaServers
captchaServers=tuple(captchaServers)#随机切换服务器的排列顺序，
#避免多个Voter经常向同一服务器post

def captcha_server_generator():#每调用一次next(csGen)，产生一个captchaServers中的url
    length=len(captchaServers)
    i=0
    while 1:
        yield captchaServers[i]
        i+=1
        if(i>=length):
            i=0
            
csGen=captcha_server_generator()

from charaSelector import selector

#超时设置
request_timeout=80
captcha_timeout=80

#异步服务，且客户端不需要返回值
#实战中的功能：收取一批ip地址的post，然后对每次post开一个线程投票
import tornado.ioloop
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop
#from concurrent.futures import ThreadPoolExecutor
import requests,cfscrape

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from hashlib import md5,sha256

#f=open('./tmp.txt','a',encoding='utf-8')

from fake_useragent import UserAgent
uaGen = UserAgent(
    fallback="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0"
    )
acceptLanguage=(
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5,en-us;q=0.3',
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5',
##    'ar-sa;q=0.9,en;q=0.5',
##    'ru;q=0.8,en;q=0.7',
    'en-us;q=0.8,en;q=0.5',
    'en;q=0.8',
    )
indexLanguage=len(acceptLanguage) - 1
def genHeaders():#aiohttp会自动生成大部分header
    headers = {
        'User-Agent': uaGen.random,
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Referer': "https://www.internationalsaimoe.com/voting/",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': acceptLanguage[random.randint(0, indexLanguage)],
        #'cache-control': "no-cache",
        'Connection':'keep-alive',
        'X-Requested-With':'XMLHttpRequest',
        'Upgrade-Insecure-Requests':'1',
    }
    return headers
localsession=cfscrape.create_scraper(headers=genHeaders())

from io import BytesIO
from PIL import Image
import numpy as np
from skimage.filters import gaussian
from skimage.exposure import equalize_hist
from skimage.morphology import opening,label
from skimage.measure import regionprops
def judge(img): #判断能否识别验证码
    img = img[97:,:]
    img=gaussian(img, sigma=0.85)
    img=equalize_hist(img)
    img=(img > 0.7)*1.0
    img=opening(img,selem=np.array([[0,1,0],[1,1,1],[0,1,0]]))
    image_region=img*0
    img=label(img,connectivity=1)
    props = regionprops(img)
    cnt=0
    centerx=[]
    width=[]
    for i in range(np.max(img)):
        if props[i]['area'] > 290:
            image_region = image_region + (img==props[i]['label'])
            centerx.append(props[i]['centroid'][1])
            width.append(props[i]['image'].shape[1])
            cnt += 1
    # 八个连通域
    if cnt != 8:
        return False
    # 连通域之间距离；宽高比
    centerx.sort()
    if np.std(np.diff(np.array(centerx))) > 10 or np.min(np.array(width)) < 18:
        return False
    return True

class NoVotingToken(Exception):
    '''自定义异常类。没找到voting_token时raise NoVotingToken'''
    def __init__(self):#, length, atleast):
        pass
        #self.length = length
        #self.atleast = atleast

RequestExceptions=(
    requests.RequestException,
    requests.ConnectionError,
    requests.HTTPError,
    requests.Timeout,
    )

from retryapi import retry,RetryExhausted

#这个函数在class MainHandler里也有一份，可在线程池运行

#def localsession_get(url='https://coinone.co.kr/'):#珂以测试防火墙
def localsession_get(url="http://www.internationalsaimoe.com"):
    with localsession.get(url,timeout=request_timeout,verify=False,
                          #proxies={'http':'http://localhost:58888','https':'http://localhost:58888'}
                          ) as res:
        print('IgnaleoG:本地session请求%s，状态码为%d'%(url,res.status_code))
        #print(res.text)

#worker_loop=tornado.ioloop.IOLoop.instance()
worker_loop=asyncio.get_event_loop()
class MainHandler(tornado.web.RequestHandler):
    id=0
    #executor = ThreadPoolExecutor(30)

    class VoterMT:
        def __init__(self,proxy,loop,localsession,id=0):
            self.proxy=proxy
            self.loop=loop
            self.session=cfscrape.create_scraper(headers=genHeaders())
            self.localsession=localsession
            #self.executor=executor
            self.id=id #用于标记这次投票是第几次
            #if proxy:
            self.fingerprint=md5(('ChNeWi'+proxy).encode()).hexdigest()
            #else:#仅用于测试！
            #    self.fingerprint=md5(('Hecate2'+str(time.time())).encode()).hexdigest()
            #    self.voting_token=sha256(('Hecate2'+str(time.time())).encode()).hexdigest()
            #self.localsession=localsession

        @retry(exceptions=RequestExceptions,tries=2,logger=None)
        def _get(self,url,timeout=request_timeout):
            with self.session.get(url,timeout=timeout,proxies={"http":self.proxy,"https":self.proxy},verify=False) as response:
                if (response.status_code<400):
                    if 'text' in response.headers['content-type']:
                        #f=open('./tmp.txt','a',encoding='utf-8')
                        #f.write(text)
                        #f.close()
                        return response.text
                    #if 'image' in response.content_type:
                    else:
                        #fb=open('./tmp.png','wb')
                        #fb.write(body)
                        #fb.close()
                        return response.content
                #if (response.status==503):
                    #pass
                    #处理cloudflare防火墙
                else:
                    #print(response.status_code)
                    return response.raise_for_status()

        #不使用代理，直接get
        #暂时不要对着世萌用这个。如果一开始没有墙，突然墙开起来了，可能会出问题
        #因为同一个本地session会发起几百几千个get，吃到不同的墙
        @retry(exceptions=RequestExceptions,tries=2,logger=None)
        def _localget(self,url,timeout=request_timeout):
            with self.session.get(url,timeout=timeout) as response:
                if (response.status_code<400):
                    if 'text' in response.headers['content-type']:
                        #f=open('./tmp.txt','a',encoding='utf-8')
                        #f.write(text)
                        #f.close()
                        return response.text
                    #if 'image' in response.content_type:
                    else:
                        #fb=open('./tmp.png','wb')
                        #fb.write(body)
                        #fb.close()
                        return response.content
                #if (response.status==503):
                    #pass
                    #处理cloudflare防火墙
                else:
                    return response.raise_for_status()
                
        @retry(exceptions=RequestExceptions,tries=2,logger=None)
        def _post(self,url,data,timeout=request_timeout):
            with self.session.post(url,data=data,timeout=timeout,proxies={"http":self.proxy,"https":self.proxy},headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},verify=False) as response:
                if (response.status_code<400):
                    return response.text
                else:
                    return response.raise_for_status()
        
        @retry(exceptions=RequestExceptions,tries=2,logger=None)
        def _localpost(self,url,data,timeout=request_timeout):
            with self.localsession.post(url,data=data,timeout=timeout,verify=False) as response:
                if (response.status_code<400):
                    return response.text
                else:
                    return response.raise_for_status()

        def EnterISML(self):
            text=self._get('http://www.internationalsaimoe.com/voting')
            voting_token = re.search(repattern, text)
            if voting_token:
                self.html=text
                self.voting_token=voting_token.group(1)
                self.startTime=time.time()
                print(self.id,self.proxy,'进入ISML成功')
            else:
                #print(self.id,self.proxy,'找不到voting_token')
                raise NoVotingToken

        #发指纹
        def PostFingerprint(self):#确保self.fingerprint在class初始化时已经生成！
            self._post("https://www.internationalsaimoe.com/security",data={"secure":self.fingerprint})
            print(self.id,self.proxy,'发指纹成功')
            return('%d %s 发指纹成功'%(self.id,self.proxy))

        def AIDeCaptcha(self):
            #识别验证码。包含多次下载验证码，预处理，以及交给服务器最终识别
            tries=0
            while 1:#while tries<重试上限:
            #目前验证码重试次数不设上限！
                tries+=1
                raw_img=self._get(
                    'https://www.internationalsaimoe.com/captcha/%s/%s' % (self.voting_token, int(time.time() * 1000)),
                    timeout=captcha_timeout)
                img=Image.open(BytesIO(raw_img))
                img = 255-np.array(img.convert('L') ) #转化为灰度图
                if(judge(img)):
                    del img
                    print(self.id,self.proxy,'第%d次获取验证码，能够识别'%(tries))
                    captcha=self._localpost(next(csGen),raw_img)
                    self.captcha=captcha
                    return captcha
        def DeCaptcha(self):
            #识别验证码。直接丢给网上验证码平台处理
            #captcha=await self._get()
            #self.captcha='识别结果'
            print('丢给打码平台的版本还未完成！')
            raise

        def Submit(self):#提交投票
            postdata=selector(self.html,self.voting_token,self.captcha)
            sleepTime=190-(time.time()-self.startTime)#消耗的时间减去90秒
            if(sleepTime>0):#还没到90秒
                print(self.id,self.proxy,"开始等待%d秒"%(sleepTime))
                gevent.sleep(sleepTime)#坐等到90秒
            #try:
            result=self._post("https://www.internationalsaimoe.com/voting/submit",data=postdata)
            #except Exception:
            #    result=self._localpost("https://www.internationalsaimoe.com/voting/submit",data=postdata)
            return result

        def SaveHTML(self):#存票根
            text=self._get('https://www.internationalsaimoe.com/voting')
            try:
                f=open('./HTML/%s.html'%(self.captcha),'w',encoding=('utf-8'))
                f.write(text)
                f.close()
                return('%d %s 存票根成功'%(self.id,self.proxy))
            except Exception as e:
                print(e)
                return('%d %s 存票根失败!'%(self.id,self.proxy))

        #@tornado.concurrent.run_on_executor
        def Vote(self):#跑完整个投票流程！由gevent.spawn()启动
            try:
                self.EnterISML()
            except NoVotingToken:
                self.session.close()
                #return('%d %s %s'%(self.id,self.proxy,'找不到voting_token'))
                print('%d %s %s'%(self.id,self.proxy,'找不到voting_token'))
                return
                #self.voting_token=sha256(('Hecate2'+str(time.time())).encode()).hexdigest()
            except RetryExhausted:
                self.session.close()
                print('%d %s %s'%(self.id,self.proxy,'连续重试次数超限，放弃治疗（未进入ISML)'))
                return
            try:
                #下面开始发指纹
                self.PostFingerprint()
                #下面开始识别验证码任务。
                self.AIDeCaptcha()
                #下面坐等到90秒然后submit
                result=self.Submit()
                print('%d %s %s'%(self.id,self.proxy,result))
                #下面应对验证码错误
                if('Invalid' in result):#验证码错误
                    self.AIDeCaptcha()
                    result=self.Submit()
                    print('%d %s %s'%(self.id,self.proxy,result))
                #下面存票根
                if('successful' in result):
                    result=self.SaveHTML()
                    self.PostFingerprint()
                    self.session.close()
                    print(result)
                    return
                #if('refresh' in result): #session expired
                #    print('%d %s %s'%(self.id,self.proxy,result))
                    #if(random.random()<0.6):
                    #    self.Vote() #再来一次！
                #if('An entry' in result): #这个ip被抢先投票
                self.session.close()
                print('%d %s %s'%(self.id,self.proxy,result)) #结束投票
                return
            except RetryExhausted:
                self.session.close()
                print('%d %s %s'%(self.id,self.proxy,'连续重试次数超限，放弃治疗（已进入ISML）'))
                return

    #@tornado.concurrent.run_on_executor
    def localsession_get(self,url="http://www.internationalsaimoe.com"):
        with localsession.get(url,timeout=request_timeout) as res:
            self.write('IgnaleoMT:本地session请求%s，状态码为%d'%(url,res.status_code))
            print('IgnaleoMT:本地session请求%s，状态码为%d'%(url,res.status_code))

    #@tornado.concurrent.run_on_executor
    def get(self, *args, **kwargs):
        gc.collect()
        #worker_loop.add_callback(functools.partial(self.localsession_get))
        gevent.spawn(self.localsession_get)
        for server in CaptchaServers.captchaServers:
            #worker_loop.add_callback(functools.partial(self.localsession_get, url=server))
            gevent.spawn(self.localsession_get,server)

    #@tornado.concurrent.run_on_executor
    def post(self):
        #gc.collect()
        proxies=self.request.body.decode(encoding='utf-8').split('\r\n')
        self.write('收到POST')
        print('Ignaleo: 收到POST')
        #print('收到POST\n',proxies)
        for proxy in proxies:
            self.id+=1
            #proxy='http://'+proxy#'localhost:58888'
            voter=self.VoterMT('http://'+proxy,worker_loop,localsession,id=self.id)
            #voter=VoterMT(None,worker_loop,localsession,id=self.id)
            #不使用代理，仅用于测试！
            #worker_loop.add_callback(functools.partial(voter.Vote))
            #print('gevent.spawn',self.id)
            gevent.spawn(voter.Vote)

def run_proc(port):
    AsyncIOMainLoop().install()
    app=tornado.web.Application([
        (r'/',MainHandler),
    ])
    app.listen(port)
    print('DestroyerIgnaleoG@localhost:%d'%(port))
    
    print('Ignaleo开始准备本地session')
    #本地session，可用于向验证码服务器post，或许还可以用来取验证码
    #worker_loop.add_callback(functools.partial(localsession_get))
    gevent.spawn(localsession_get)
    for server in CaptchaServers.captchaServers:
        #worker_loop.add_callback(functools.partial(localsession_get, url=server))
        gevent.spawn(localsession_get, server)
    #worker_loop.start()
    worker_loop.run_forever()

if __name__ == '__main__':
    from multiprocessing import Process
    length=len(portList)
    for port in range(length-1):
        p=Process(target=run_proc, args=(portList[port],))
        p.start()
    run_proc(portList[length-1])
