#coding:utf-8
# 如果aiohttp连接超时，则会raise，但只是raise，不带错误信息

import random
#打码服务器列表:
captchaServers=[
    'http://localhost:8888',
    'http://localhost:8889',
    ]
random.shuffle(captchaServers)
class CaptchaServers:
    captchaServers=captchaServers
captchaServers=tuple(captchaServers)#随机切换服务器的排列顺序，
#避免多个Voter经常向同一服务器post

#接受的http status code
acceptStatus=(503)

import aiohttp,asyncio
#各种超时设置:
#initial_timeout=40
#如果花掉initial_timeout的时间依然没有进世萌的门，则放弃这次投票
#global_timeout=210
#进入世萌成功后，如果超过global_timeout依然没有完成整个流程，
#并且全局尝试次数global_retry用完，则放弃这次投票

#以上所有超时设置似乎都没啥意义

request_timeout=30 #单次http请求的默认超时。
#你可以随时暂时覆盖这一设置
captcha_timeout=60 #单次取验证码的默认超时
timeoutConfig=aiohttp.ClientTimeout(total=request_timeout)
captchaTimeoutConfig=aiohttp.ClientTimeout(total=captcha_timeout)

from charaSelector import selector

def captcha_server_generator():#每调用一次next(csGen)，产生一个captchaServers中的url
    length=len(captchaServers)
    i=0
    while 1:
        yield captchaServers[i]
        i+=1
        if(i>=length):
            i=0
            
csGen=captcha_server_generator()

from base64 import b64encode
from io import BytesIO
from PIL import Image
from fake_useragent import UserAgent
uaGen = UserAgent(
    fallback='Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'
    )
from functools import wraps
import functools

acceptLanguage=(
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5,en-us;q=0.3',
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5',
    'ar-sa;q=0.9,en;q=0.5',
    'ru;q=0.8,en;q=0.7',
    'en-us;q=0.8,en;q=0.5',
    'en;q=0.8',
    )
indexLanguage=len(acceptLanguage) - 1
def genHeaders():#aiohttp会自动生成大部分header
    headers = {
        'user-agent': uaGen.random,
        #'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        #'referer': "https://2019.internationalsaimoe.com/voting/",
        'accept-encoding': "gzip, deflate",
        'accept-language': acceptLanguage[random.randint(0, indexLanguage)],
        #'cache-control': "no-cache",
        'connection':'keep-alive',
        #'X-Requested-With':'XMLHttpRequest'
        #'Upgrade-Insecure-Requests':'1',
    }
    return headers

from aiocfscrape import CloudflareScraper

def printer(future):
    #一个回调函数，某些不想await的future可以回调到这里
    print(future.result())
def doNothing(future):
    #一个回调函数，某些不想await的future可以回调到这里
    #什么也不做
    pass

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
class RetryExhausted(Exception):
    '''自定义异常类。连续重试太多次'''
    def __init__(self):#, length, atleast):
        pass
        #self.length = length
        #self.atleast = atleast

from hashlib import md5,sha256
import time,re
repattern=re.compile('voting_token" value="(.*?)"')

class Voter:
    #session=CloudflareScraper(headers=headers,timeout=timeoutConfig)
    #localsession=从外部输入一个不使用代理的CloudflareScraper session
    #proxy=从外部输入一个代理ip
    #global_retry=10
    #如果进世萌后时间超过global_timeout，
    #且累计连接失败次数超过global_retry
    #则放弃这次投票
    #这个策略似乎没啥意义。先不用

    def __init__(self,proxy,loop,localsession,id=0):
        self.proxy=proxy
        self.loop=loop
        self.session=CloudflareScraper(headers=genHeaders(),timeout=timeoutConfig,loop=loop)
        self.localsession=localsession
        self.id=id #用于标记这次投票是第几次
        #if proxy:
        self.fingerprint=md5((proxy+'Hecate2').encode()).hexdigest()
        #else:#仅用于测试！
        #    self.fingerprint=md5(('Hecate2'+str(time.time())).encode()).hexdigest()
        #    self.voting_token=sha256(('Hecate2'+str(time.time())).encode()).hexdigest()
        #self.localsession=localsession

    def retry(self,*exceptions, retries=5, cooldown=0):#, verbose=True):
        """Decorate an async function to execute it a few times before giving up.
        Hopes that problem is resolved by another side shortly.

        Args:
            exceptions (Tuple[Exception]) : The exceptions expected during function execution
            retries (int): Number of retries of function execution.
            cooldown (int): Seconds to wait before retry.
            verbose (bool): Specifies if we should log about not successful attempts.
        """

        def wrap(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                #子函数可以访问父函数的所有变量，因此这里可以访问class的self
                retries_count = 0

                while True:
                    try:
                        result = await func(*args, **kwargs)
                    except exceptions as err:   #exceptions是从retry传入的
                        #self.global_retry -= 1
                        retries_count += 1

                        if retries_count >= retries:
                            message='已连续错误%d次,放弃治疗'%(retries)
                            #print(self.id,self.proxy,message)
                            print(message)
                            #verbose and log.exception(message)
                            #verbose and print(message)
                            #raise RetryExhaustedError(
                            #    func.__qualname__, args, kwargs) from err
                            #raise RetryExhaustedError
                            #return err
                            #return '还没想好return什么东西'
                            raise RetryExhausted
                        else:
                            #message = "Exception:{} during\n{} execution. " \
                            #          "{} of {} retries attempted"\
                            #          .format(err, func, retries_count, retries)
                            message= '出现错误:{}. 正在重试{}/{}'\
                                     .format(err, retries_count, retries)
                            #print(self.id,self.proxy,message)
                            print(message)
                            #verbose and log.warning(message)
                            #verbose and print(message)
                            await asyncio.sleep(cooldown)
                    else:
                        return result
            return inner
        return wrap

    @retry(aiohttp.ClientError,asyncio.TimeoutError)
    async def _get(self, url, timeout=timeoutConfig):
        #自动判断get到的是文字还是图片,返回utf-8编码的文字或bytes类型图片
        async with self.session.get(url,proxy=self.proxy,timeout=timeout) as response:
            #return await response.text()
            body=await response.read()
            #print(response.content_type)    #'text/html' 'image/png'
            #print(body)
            if (response.status<400):
                if 'text' in response.content_type:
                    text=body.decode(encoding='utf-8')
                    #f=open('./tmp.txt','a',encoding='utf-8')
                    #f.write(text)
                    #f.close()
                    return text
                #if 'image' in response.content_type:
                else:
                    #fb=open('./tmp.png','wb')
                    #fb.write(body)
                    #fb.close()
                    return body
            #if (response.status==503):
                #pass
                #处理cloudflare防火墙
            else:
                response.raise_for_status()
                print('get连续失败太多次！')

    #不使用代理，直接get
    #暂时不要对着世萌用这个。如果一开始没有墙，突然墙开起来了，可能会出问题
    #因为同一个本地session会发起几百几千个get，吃到不同的墙
    @retry(aiohttp.ClientError,asyncio.TimeoutError)
    async def _localget(self, url, timeout=captchaTimeoutConfig):
        #用本机ip去get！
        #自动判断get到的是文字还是图片,返回utf-8编码的文字或bytes类型图片
        async with self.localsession.get(url,timeout=timeout) as response:
            #return await response.text()
            body=await response.read()
            #print(response.content_type)    #'text/html' 'image/png'
            #print(body)
            if (response.status<400):
                if 'text' in response.content_type:
                    text=body.decode(encoding='utf-8')
                    #f=open('./tmp.txt','a',encoding='utf-8')
                    #f.write(text)
                    #f.close()
                    return text
                #if 'image' in response.content_type:
                else:
                    #fb=open('./tmp.png','wb')
                    #fb.write(body)
                    #fb.close()
                    return body
            #if (response.status==503):
                #pass
                #处理cloudflare防火墙
            else:
                response.raise_for_status()
                print('localget连续失败太多次！')

    @retry(aiohttp.ClientError,asyncio.TimeoutError)
    async def _post(self,url,data,timeout=timeoutConfig):
        async with self.session.post(url,data=data,proxy=self.proxy,timeout=timeout) as response:
            text=await response.text()
            if (response.status<400):
                return text
            else:
                response.raise_for_status()
                print('post连续失败太多次！')

    #本机向验证码服务器post，不使用代理
    #只能用于验证码post!只允许返回text!对于二进制内容会出错！
    @retry(aiohttp.ClientError,asyncio.TimeoutError)
    async def _localpost(self,url,data,timeout=timeoutConfig):
        async with self.localsession.post(url,data=data,timeout=timeout,ssl=False) as response:
            text=await response.text()
            if (response.status<400 and text!='!'):
                return text
            else:
                response.raise_for_status()
                print('localpost连续失败太多次！验证码服务器可能有严重问题！')

    async def EnterISML(self):
        text=await self._get('https://2019.internationalsaimoe.com/voting')
        voting_token = re.search(repattern, text)
        if voting_token:
            self.html=text
            self.voting_token=voting_token.group(1)
            self.startTime=time.time()
            print(self.id,self.proxy,'进入ISML成功')
        else:
            print(self.id,self.proxy,'找不到voting_token')
            raise NoVotingToken

    #发指纹和打码可以并发执行
    async def PostFingerprint(self):#确保self.fingerprint在class初始化时已经生成！
        await self._post("https://2019.internationalsaimoe.com/security",data={'secure':self.fingerprint})
        print(self.id,self.proxy,'发指纹成功')
        return('%d %s 发指纹成功'%(self.id,self.proxy))

    async def AIDeCaptcha(self):
        #打码。包含多次下载验证码，预处理，以及交给服务器最终识别
        tries=0
        while 1:#while tries<重试上限:
        #目前验证码重试次数不设上限！
            tries+=1
            raw_img=await self._get(
                'https://2019.internationalsaimoe.com/captcha/%s/%s' % (self.voting_token, int(time.time() * 1000)),
                timeout=captchaTimeoutConfig)
            img=Image.open(BytesIO(raw_img))
            img = 255-np.array(img.convert('L') ) #转化为灰度图
            if(judge(img)):
                del img
                print(self.id,self.proxy,'第%d次获取验证码，能够识别'%(tries))
                captcha=await self._localpost(next(csGen),raw_img)
                self.captcha=captcha
                return captcha

    async def DeCaptcha(self):
        #打码。直接丢给打码平台处理
        #captcha=await self._get()
        #self.captcha='打码结果'
        print('丢给打码平台的版本还未完成！')
        await asyncio.sleep(0)
        raise
        
    async def Submit(self):#提交投票
        postdata=selector(self.html,self.voting_token,self.captcha)
        sleepTime=90-(time.time()-self.startTime)#消耗的时间减去90秒
        if(sleepTime>0):#还没到90秒
            print(self.id,self.proxy,'开始等待%d秒'%(sleepTime))
            await asyncio.sleep(sleepTime)#坐等到90秒
        print(self.id,self.proxy,'开始Submit')
        result=await self._post("https://2019.internationalsaimoe.com/voting/submit",data=postdata)
        return result

    async def SaveHTML(self):#存票根
        text=await self._get('https://2019.internationalsaimoe.com/voting')
        try:
            f=open('./HTML/%s.html'%(self.captcha),'w',encoding=('utf-8'))
            f.write(text)
            f.close()
            #print(self.id,self.proxy,'存票根成功')
            return('%d %s 存票根成功'%(self.id,self.proxy))
        except Exception:
            return('%d %s 由于硬盘原因，存票根失败，可能硬盘过载!!!!!'%(self.id,self.proxy))

    #@retry(aiohttp.ClientError,asyncio.TimeoutError,retries=2)
    async def Vote(self):#跑完整个投票流程！建议由Launch函数启动
        try:
            await self.EnterISML()
        except NoVotingToken:
            return('%d %s %s'%(self.id,self.proxy,'找不到voting_token'))
        except RetryExhausted:
            return('%d %s %s'%(self.id,self.proxy,'连续重试次数超限'))
        except (aiohttp.ClientError,asyncio.TimeoutError):
            return('%d %s %s'%(self.id,self.proxy,'代理可能失效，放弃治疗'))
        try:
##            #下面开始发指纹并且暂时不管它。识别验证码与发指纹并发执行
##            task=self.PostFingerprint()
##            future=asyncio.ensure_future(task,loop=self.loop)
##            #下面开始识别验证码任务。
##            await self.AIDeCaptcha()
##            #下面等发指纹任务完成（通常早就完成了）
##            await future
            await self.PostFingerprint()
            await self.AIDeCaptcha()
            #下面坐等到90秒然后submit
            result=await self.Submit()
            #下面应对验证码错误（重试1次）
            if('Invalid' in result):#验证码错误
                await self.AIDeCaptcha()
                await self.Submit()
            #下面存票根
            if('successful' in result):
                task=self.SaveHTML()
                future=asyncio.ensure_future(task,loop=self.loop)
                future.add_done_callback(functools.partial(printer))
                task=self.PostFingerprint()
                future=asyncio.ensure_future(task,loop=self.loop)
                future.add_done_callback(functools.partial(printer))
                return('%d %s %s'%(self.id,self.proxy,result))
            if('refresh' in result): #session expired等各种原因
                print('%d %s %s %s'%(self.id,self.proxy,result,'开始重试整个投票流程'))
                await self.Vote() #再来一次！
            #if('An entry' in result): #这个ip被抢先投票
            return('%d %s %s'%(self.id,self.proxy,result)) #结束投票
        except RetryExhausted:
            return('%d %s %s'%(self.id,self.proxy,'连续重试次数超限'))
        except (aiohttp.ClientError,asyncio.TimeoutError):
            return('%d %s %s'%(self.id,self.proxy,'代理可能失效，放弃治疗'))

    def Launch(self):
        vote=self.Vote()
        vote_future=asyncio.ensure_future(vote,loop=self.loop)
        vote_future.add_done_callback(functools.partial(printer))
##        res=await vote_future
##        if(res==300):
##            vote_future.add_done_callback(functools.partial(self.Launch))

if __name__=='__main__':
    voter=Voter('192.168.1.1:9999',asyncio.get_event_loop(),CloudflareScraper())
    print(voter)
