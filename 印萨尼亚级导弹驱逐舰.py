#coding:utf-8

#目前还请把这个东西当成工具包而不是现成的自动机
#我写了一批函数工具。请你自己改代码

from time import sleep
from os import rename
#import os, io, sys, re
import webbrowser
import winreg
#import win32com.client
from win32gui import GetWindowDC
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import SRCCOPY
from ctypes import *
import cv2
from skimage import morphology
#以上引入winapi
from cfscrape import CloudflareScraper
from random import normalvariate
from scipy.fftpack import fft

import pymouse,pykeyboard
from pymouse import *
from pykeyboard import PyKeyboard
m = PyMouse() 
k = PyKeyboard()
#import pyscreenshot as ImageGrab
#shell = win32com.client.Dispatch("WScript.Shell")

#bbox = (668, 579, 668+563, 579+250) #截图范围。要求你的屏幕是1080p，浏览器缩放比例100%

#proxyGlobal=[
#    ]
#可以直接在这里输入一批代理。格式为：
#[
#'192.168.1.1:8080',
#'219.168.1.1:8080',
#]
#可以使用IP processing.py把大批代理转为此格式。

import json
import requests
from requests.exceptions import ConnectionError, HTTPError
from pyquery import PyQuery as pq

TEST_URL='https://www.internationalsaimoe.com'

base_headers={
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
    }

#以下是代理平台提供的提取代理的链接
proxyAPI='http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
#以下是打码平台提供的信息和函数
from traceback import print_exc
captchaPSWD='siC1kuRwvaodaeuE'
#服务提供的两个URL
YZM_URL = ["http://dt1.91yzm.com:8080/","http://dt2.91yzm.com:8080/"]

#封装提交和请求，第一个url请求失败，就试图请求第二个url
def Request(url):
    err = "#请求失败"
    for YZM_url in YZM_URL:
        try:
            r = requests.get(YZM_url + url)
            if r.status_code<300:
                return r.content
            err = "#请求失败," + str(r.status_code)
        except:
            print_exc()
    return err

def Post(url,data,pic):
    err = "#发送文件失败"
    for YZM_url in YZM_URL:
        try:
            r = requests.post(YZM_url + url,data=data,files = pic )
            if r.status_code<300:
                return r.content
            err = "#发送文件失败," + str(r.status_code)
        except:
            pass
    return err


#发送文件
#auth_code:密码串
#path:文件路径
#dati_type:类型
#timeout:超时时间
#extra_str:备注
#zz:作者
def SendFile(auth_code,path,dati_type,timeout,extra_str,zz=None):
    senddata = {}
    senddata["dati_type"] = dati_type
    senddata["acc_str"] = auth_code
    senddata["timeout"] = timeout
    senddata["extra_str"] = extra_str
    if zz:
        senddata["zz"] = zz

    return Post("uploadpic.php", senddata,{"pic":open(path,"rb")})



#得到答案
def GetAnswer(captchaID):
    return Request("query.php?sid=" + captchaID.decode())


#得到密码串余额
def QueryBalance(auth_code):
    return Request("query.php?action=qmoney&self_authcode=" + auth_code.decode())

#报告错误，当一个识别出错时，提交给服务器说识别出错
def ReportError(auth_code,captchaID):
    return Request("response.php?action=error&auth_code=" + auth_code.decode() +"&sid="+captchaID.decode())


#直接识别，返回答案
def Recoginze(auth_code,path,dati_type,timeout,extra_str,zz=None):

    captchaID = SendFile(auth_code,path,dati_type,timeout,extra_str,zz).decode()
    if captchaID[0]=='#':
        return captchaID
    sleep(2)
    while True:
        answer = GetAnswer(captchaID)
        if answer!="":
            break
        sleep(1)
    return answer
#以上是打码平台提供的函数

#爬虫用的普通get命令。如果你不知道它的安全隐患，则不要使用它
def get_page(url,options={}):
    headers=dict(base_headers, **options)
    #print('正在抓取', url)
    try:
        response=requests.get(url, headers=headers)
        #print('抓取成功',url,response.status_code)
        if response.status_code==200:
            return response.text
    except (ConnectionError, HTTPError):
        #print('抓取失败', url)
        return None

#可以爬取一些代理，但不保证爬到的ip质量
def get_xicidaili(page_count=20):   #page_count为获取代理的页数
    start_url='http://www.xicidaili.com/nn/{page}'
    urls=[start_url.format(page=page) for page in range(1,page_count+1)]
    for url in urls:
        print('Crawling', url)
        html=get_page(url)
        if html:
            doc=pq(html)
            results=doc('#ip_list tr').items()
            for result in results:
                ip=result.find('td:nth-child(2)').text()
                port=result.find('td:nth-child(3)').text()
                if ip and port:
                    yield ':'.join([ip,port])

#测试代理是不是http协议
def test_proxy_http(proxy):
    proxies={
        'http':'http://'+proxy,
        #'https':'http://'+proxy
        }
    try:
        response=CloudflareScraper().get(TEST_URL,proxies=proxies,verify=False,timeout=10)
        if response.status_code==200:
            return True
        else:
            return False
    except Exception:
        return False

#测试代理是不是https协议
def test_proxy_https(proxy):
    proxies={
        #'http':'http://'+proxy,
        'https':'http://'+proxy
        }
    try:
        response=CloudflareScraper().get(TEST_URL,proxies=proxies,verify=False,timeout=10)
        if response.status_code==200:
            return True
        else:
            return False
    except Exception:
        return False

#截图。文件名为filename
def window_capture(filename):
    # 截取长宽为（w，h）从左上角（x，y）的图片
    #存为文件名filename
    #宽度w,高度h
    #左上角截图的坐标x,y
    w=563
    h=250
    x=668
    y=579
    hwnd = 0
    hwndDC = GetWindowDC(hwnd)
    mfcDC = CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = CreateBitmap()
    #MoniterDev = win32api.EnumDisplayMonitors(None,None)
    #w = MoniterDev[0][2][2]
    # #h = MoniterDev[0][2][3]
    # w = 516
    # h = 514
    saveBitMap.CreateCompatibleBitmap(mfcDC,w,h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0,0),(w,h),mfcDC,(x,y),SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC,filename)

#代理的注册表项路径
xpath = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
#设定代理,enable:是否开启,proxyIp:代理服务器ip及端口
#IgnoreIp:忽略代理的ip或网址
def enableProxy(proxyIP):
    #IgnoreIp = "172.*;192.*;"
    #print(" Setting proxy")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIP)
        #winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("ERROR: " + str(e.args))
    finally:
        None
    print(proxyIP)
    #print(" Proxy set!")
 
#关闭清空代理
def disableProxy():
    print("Disable proxy")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "")
        #winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "")
    except Exception as e:
        print("ERROR: " + str(e.args))
    finally:
        None
    print("Proxy Disabled!")

#可以拿到一大堆代理
def findProxy():
    disableProxy()
    proxys=[]
    for proxy in get_xicidaili():
        #print(proxy)
        #if proxy:
        if test_proxy_https(proxy):
            #proxy='\'https\':\'https://'+proxy+'\','
            proxys.append(proxy)
            #print(proxy)
        elif test_proxy_http(proxy):
            #proxy='\'http\':http://'+proxy+'\','
            proxys.append(proxy)
            #print(proxy)
        #with open('proxys_ip.txt','w+') as f:
            #f.write('\n'.join(proxys))

#测试代理是否可用
def testProxy():
    proxys=[]
    for proxy in proxys:
        if test_proxy_https(proxy):
            #proxy='\'https\':\'https://'+proxy+'\','
            proxys.append(proxy)
            #print(proxy)
        elif test_proxy_http(proxy):
            #proxy='\'http\':http://'+proxy+'\','
            proxys.append(proxy)
            #print(proxy)
    
#生成正态分布随机数
def normalDistribution(exp,var):
    #exp = 20 #正态分布的期望值
    #var = 10 #正态分布的方差
    x = normalvariate(exp, var) #正态分布的随机数取整
    while x<exp:
        x = normalvariate(exp, var) #正态分布的随机数取整
    return x

def fourierCheck(filename): #用傅里叶变换检查截到的图是不是验证码
    integral=1000.0
    img = cv2.imread(filename,0)    #直接读取为灰度图像
    ret,img = cv2.threshold(img,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img=1-img
    img.dtype='bool'
    sizeY=img.shape[0]
    for j in [0,round(sizeY*0.2),round(sizeY*0.4),round(sizeY*0.6),round(sizeY*0.8),sizeY-1]:
        F=fft(img[j])
        integral=min(sum(abs(F[round(len(F)*0.8):len(F)-1].real)),integral)
    if(integral>530):
        img=img[round(img.shape[0]*0.45):img.shape[0]]
        img=morphology.remove_small_objects(img, min_size=250, connectivity=1, in_place=False)
        img.dtype='uint8'
        img=img*255
        cv2.imwrite('processed '+filename,img)
        return True
    else:
        return False

j=2044
disableProxy()
#for proxy in get_xicidaili(1):
for j in range(2044,2500):
    #if(test_proxy_https(proxy) or test_proxy_http(proxy)):
        proxy=CloudflareScraper().get(proxyAPI,verify=False,timeout=10).content.decode()
        #print(proxy)
        enableProxy(proxy)
        #webbrowser.open('https://www.internationalsaimoe.com/voting')
        #sleep(1)
        #sleep(normalDistribution(2,10))   
        #等待几秒钟。秒数为均值2方差10的正态分布 
        #这并非普通的正态分布！如果抽数抽到的值小于均值，则强行再抽一次数
        #这样奇怪的分布可以扰乱服务器对我们访问频率的统计
        #win32api.ShellExecute(0, 'open', 'https://www.internationalsaimoe.com/voting', '','',3)
        webbrowser.open('https://www.internationalsaimoe.com/voting')
        #webbrowser.open('https://www.internationalsaimoe.com/nominations/autumn')
        #sleep(normalDistribution(2,16))
        sleep(2)
        #win32api.SetCursorPos([870,16]) #浏览器上方大约正中的位置。在此单击确保选中浏览器窗口
        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        #win32api.SetCursorPos([1910,1000])
        
        #从打开浏览器到这里为止平均已过去的时间应该不超过10秒
        
        #准备检查屏幕上的像素点颜色
        gdi32 = windll.gdi32
        user32 = windll.user32
        #获取句柄
        hdc = user32.GetDC(None)
        m.click(870, 16, 1, 1)
        #win32api.SetCursorPos([870,16]) #浏览器上方大约正中的位置。在此单击确保选中浏览器窗口
        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        for i in range(1,30):
            if(20>gdi32.GetPixel(hdc,844,629) or 20>gdi32.GetPixel(hdc,900,600) or 20>gdi32.GetPixel(hdc,1515,600)):
                #获取指定像素的颜色
                #如果这个点的颜色是黑色，或者说等于0，说明网页加载出来了
                #现在实际设定的是如果这个点的颜色小于20
                allowed=1   #允许执行后续步骤
                break
            else:
                sleep(1)
                #m.click(870, 16, 1, 1)
                allowed=100   #不许执行后续步骤
        #上面这个循环会检查某个像素点的颜色30次。
        #如果30秒后这个像素点还不是黑色，则我们认为这波加载网页失败。我们会关掉浏览器重来
        #到此为止如果加载网页成功了，则平均总消耗时间应该不超过50秒
        if(16000000<gdi32.GetPixel(hdc,460,448) and 16000000<gdi32.GetPixel(hdc,940,492) and 16000000<gdi32.GetPixel(hdc,940,442) and 16000000<gdi32.GetPixel(hdc,1035,494)):
            #An entry has already been submitted from this IP Address.
            #This entry will not be counted. 
            allowed=100
        if(allowed==1): #如果我们认为打开网页已经成功
            m.click(380, 600, 1, 1)
            #win32api.SetCursorPos([870,16]) #浏览器上方大约正中的位置。在此单击确保选中浏览器窗口
            #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            #sleep(0.2)
            k.press_keys([k.control_key,k.down_key])
            sleep(0.2)
            filename='{my_name}.png'\
                .format(my_name=j) 
            while(allowed<=10): #截图并检查是不是验证码。尝试10次
                window_capture(filename)
                if(fourierCheck(filename)):
                    #选择角色（用JavaScript完成）
                    #发送验证码到打码平台
                    disableProxy()
                    captchaID = SendFile(captchaPSWD,'processed '+filename,1013,60,"")
                    sleep(10)
                    #收验证码结果
                    for times in range(1,20):
                        captcha = GetAnswer(captchaID).decode()
                        #print(captcha)
                        if(captcha!="" and captcha.find('#')==-1):
                            #captcha=captcha.encode()
                            break
                        sleep(1)
                    #验证码图片重命名
                    newfilename='processed {my_name} '\
                        .format(my_name=j) 
                    try:
                        rename('processed '+filename,newfilename+captcha+'.png')
                    except Exception as e:
                        print(e)
                        print('processed '+filename)
                    enableProxy(proxy)
                    #用鼠标键盘填验证码 1023 895
                    m.click(945, 900, 1, 1)
                    k.type_string(captcha)
                    break
                    allowed=1  #事实上一般不会执行这一句
                else:
                    allowed+=1
                    m.click(1890,140,1,1)
                    k.press_keys([k.control_key,k.down_key])
                    sleep(1)
            #j=j+1
            #img = ImageGrab.grab(bbox)
            #img.save(filename)
            #img.show()
            #shell.SendKeys("%{F4}", 0)  #发送Alt+F4
        #if(allowed==1)语句的作用范围结束
        #以下关闭浏览器。如果打开网页后等了好久还没出来，则会直接关闭浏览器
        #win32api.SetCursorPos([1898,12])
        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        if (allowed<=10):
            sleep(75)
            m.click(1890,140,1,1)
            sleep(5)
            m.click(895, 963, 1, 1) #点击提交
            sleep(15)
        m.click(1898,12,1,1)
        #我们现在实际给予ISML网站的反应时间不少于44秒
        #最坏情况下，启动浏览器大约55~60秒后，如果还没截到验证码，会关闭浏览器重来
        j=j+1
        disableProxy()#关闭Windows自身的代理
        sleep(1)
disableProxy()#关闭Windows自身的代理
