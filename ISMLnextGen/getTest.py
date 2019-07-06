import aiohttp,asyncio
from retryTest import retry
loop = asyncio.get_event_loop()
import random,time
from hashlib import sha256

def VotingToken(saltString=str(random.randint(0,31))):
    return sha256((saltString+'Hecate2'+str(time.time())).encode()).hexdigest()
def Timer():
    return int(time.time()*1000)
def captchaUrl():
    return 'https://www.internationalsaimoe.com/captcha/%s/%s' % (VotingToken(), Timer())

# Example is taken from http://aiohttp.readthedocs.io/en/stable/#getting-started
async def fetch(session, url):
    async with session.get(url) as response:
        #return await response.text()
        body=await response.read()
        print(response.content_type)    #'text/html' 'image/png'
        #print(body)
        if (response.status<400):
            if 'text' in response.content_type:
                text=body.decode(encoding='utf-8')
                #f=open('./tmp.txt','a',encoding='utf-8')
                #f.write(text)
                #f.close()
                return text
            if 'image' in response.content_type:
                #fb=open('./tmp.png','wb')
                #fb.write(body)
                #fb.close()
                return body
        if (response.status==503):
            pass
            #处理cloudflare防火墙
        else:
            return response.raise_for_status()

# Client code, provided for reference
@retry(aiohttp.ClientError,asyncio.TimeoutError)
#@retry(aiohttp.WSServerHandshakeError,aiohttp.ContentTypeError)
async def main():
    timeoutConfig=aiohttp.ClientTimeout(total=3)
    async with aiohttp.ClientSession(timeout=timeoutConfig) as session:
        #html = await fetch(session, 'https://www.internationalsaimoe.com')
        #html=await fetch(session,captchaUrl())
        html=await fetch(session, 'http://localhost:55556')
        #f.write(html)
        print('done')

if __name__=='__main__':
    loop.run_until_complete(main())
