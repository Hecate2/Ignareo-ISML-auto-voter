# `AP` for `async playwright`
# IGN AP is for getting Cloudflare clearance before voting with httpx
# Alternatively it may just obtain the clearance and return the ua & clearance to other processes
from get_cf_clearance import (get_one_clearance, build_client_with_clearance,
    async_playwright, async_cf_retry, stealth_async)
from playwright.async_api import Route, Playwright

from charaSelector import selector
from judge_img import judge
import numpy as np
from io import BytesIO
from PIL import Image


from typing import Optional, Union, Dict
import time
from functools import wraps
from itertools import cycle
from abc import ABC
import os
import traceback
import re
import logging
import asyncio
from hashlib import md5
from urllib.parse import urlencode
import multiprocessing

import psutil
import httpx
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

save_path = './HTML'
portList = [i for i in range(55068, 55068 + multiprocessing.cpu_count())]
captcha_servers = [
    'http://localhost:8889',
]
cs_gen = cycle(captcha_servers)

total_memory = psutil.virtual_memory().total
total_memory_GB = int(total_memory / 1024 ** 3)
num_cpu = multiprocessing.cpu_count()
browser_pool_size = int((total_memory_GB - 3) / (multiprocessing.cpu_count() * 0.25))
browser_pool = asyncio.Semaphore(browser_pool_size)

local_client = httpx.AsyncClient()
worker_loop = asyncio.get_event_loop()
asyncio.set_event_loop(worker_loop)

playwright: Playwright = worker_loop.run_until_complete(async_playwright().start())

HttpxExceptions = (httpx.HTTPError, httpx.StreamError)
REQUEST_TIMEOUT, CAPTCHA_TIMEOUT = 80, 80
voting_token_pattern = re.compile('voting_token" value="(.*?)"')
waiting_time_pattern = re.compile('''<input id="voting_form_submit" type="submit" value="(.*?)" disabled=''')


class RetryExhausted(Exception):
    pass


class NoVotingToken(Exception):
    pass


class VoterHttpx:
    def __init__(
            self, client: httpx.AsyncClient = None,
            proxy: Optional[Union[str, Dict[str, str]]] = None,
            ua: Optional[str] = None,
            cookies: Optional[Dict[str, str]] = None,
            local_client: httpx.AsyncClient = local_client,
            loop: asyncio.AbstractEventLoop = worker_loop,
    ):
        self.client = client or loop.run_until_complete(
            build_client_with_clearance(ua, cookies, proxies=proxy, test=False))
        if client:
            self.proxy = next(iter(client._mounts.values()))._pool._proxy_url
        elif type(proxy) is str:
            self.proxy = proxy
        elif type(proxy) is dict:
            self.proxy = next(iter(proxy.values()))
        self.local_client = local_client
        self.loop = loop
        self.fingerprint = md5(('TiLakPanColNoRhChNeIt' + self.proxy).encode()).hexdigest()
    
    @classmethod
    def from_client(cls, client: httpx.AsyncClient):
        return cls(client=client)
    
    def retry(self, *exceptions, retries=2, cooldown=0):
        def wrap(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                nonlocal retries
                while retries != 0:
                    try:
                        result = await func(*args, **kwargs)
                    except exceptions as err:
                        retries -= 1
                        logging.debug(f'{self.proxy} retrying: {retries} times left; {err}')
                        if cooldown > 0:
                            await asyncio.sleep(cooldown)
                    else:
                        return result
                raise RetryExhausted(err)
            return inner
        return wrap
    
    @retry(HttpxExceptions)
    async def _get(self, url, timeout=REQUEST_TIMEOUT):
        async with self.client.get(url, timeout=timeout) as response:
            if response.status_code < 400:
                if 'text' in response.headers['content-type']:
                    return response.text
                else:
                    return response.content
            else:
                return response.raise_for_status()
    
    @retry(HttpxExceptions)
    async def _post(self, url, data, timeout=REQUEST_TIMEOUT):
        async with self.client.post(
                url, data=data, timeout=timeout,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}) as response:
            if response.status_code < 400:
                return response.text
            else:
                if response.status_code > 500:
                    logging.error(f'{self.proxy} WARNING: POST may have been blocked by Cloudflare')
                    logging.error(f'{self.proxy} response: {response.status_code} {response.headers}')
                return response.raise_for_status()

    @retry(HttpxExceptions)
    async def _local_post(self, url, data, timeout=REQUEST_TIMEOUT):
        async with self.client.post(url, data=data, timeout=timeout) as response:
            if response.status_code < 400:
                return response.text
            else:
                return response.raise_for_status()

    async def enter_ISML(self):
        text = await self._get('http://www.internationalsaimoe.com/voting')
        voting_token = re.search(voting_token_pattern, text)
        if voting_token:
            self.html = text
            self.voting_token = voting_token.group(1)
            self.start_time = time.time()
            logging.info(f'{self.proxy} entered ISML')
        else:
            raise NoVotingToken(f'{self.proxy}')
    
    async def post_fingerprint(self):
        try:
            await self._post("https://www.internationalsaimoe.com/security", data={"secure": self.fingerprint})
        except httpx.HTTPStatusError as err:
            if err.response.status_code > 500:
                logging.error(f'{self.proxy} WARNING: fingerprint may have been blocked by Cloudflare')
        logging.info(f'{self.proxy} sent fingerprint')

    async def AI_decaptcha(self):
        tries = 0
        while 1:
            tries += 1
            raw_img = await self._get(
                f"https://www.internationalsaimoe.com/captcha/{self.voting_token}/{int(time.time() * 1000)}",
                timeout=CAPTCHA_TIMEOUT)
            img = Image.open(BytesIO(raw_img))
            img = 255 - np.array(img.convert('L'))  # 转化为灰度图
            if judge(img):
                del img
                logging.info(f'{self.proxy} can recognize the {tries}-th captcha')
                captcha = await self._local_post(next(cs_gen), raw_img)
                self.captcha = captcha
                return captcha
    
    async def submit(self) -> str:
        needed_sleep_time = int(re.search(waiting_time_pattern, self.html).group(1))
        sleep_time = needed_sleep_time - time.time() + self.start_time
        if sleep_time > 0:
            logging.info(f'{self.proxy} wait for {int(sleep_time)} seconds')
            await asyncio.sleep(sleep_time)
        post_data = selector(self.html, self.voting_token, self.captcha)
        result = await self._post("https://www.internationalsaimoe.com/voting/submit", data=post_data)
        logging.info(f'{self.proxy} {result}')
        return result
    
    async def save_html(self):
        text = await self._get('https://www.internationalsaimoe.com/voting')
        path = f'{os.path.join(save_path, self.proxy)}.html'
        try:
            f = open(path, 'w', encoding='utf-8')
            f.write(text)
            f.close()
            logging.info(f'{self.proxy} save html success')
        except Exception as err:
            logging.warning(f'{self.proxy} save html failed: {err}')
    
    async def vote(self):
        try:
            await self.enter_ISML()
        except NoVotingToken:
            logging.info(f'{self.proxy}: no voting token')
            await self.client.aclose()
            return
        except RetryExhausted:
            logging.info(f'{self.proxy} tried too many times before entering ISML')
            await self.client.aclose()
            return
        try:
            await self.post_fingerprint()
            await self.AI_decaptcha()
            result = await self.submit()
            while 'Invalid' in result:
                await self.AI_decaptcha()
                result = await self.submit()
            if 'refresh' in result:  # session expired
                logging.info(f'{self.proxy} session expired. Trying again')
                asyncio.create_task(self.vote())
                return
            if 'successful' in result:
                await self.save_html()
                logging.info(f'{self.proxy} html saved')
        except RetryExhausted as err:
            logging.info(f'{self.proxy} tried too many times failing with {err}')
        finally:
            await self.client.aclose()


class VoterPlaywright:
    def __init__(self, proxy: str,
                 browser_args=None, page_args: Optional[Dict] = None):
        self.browser_args = browser_args or [
            # "https://peter.sh/experiments/chromium-command-line-switches/"
            "--enable-low-end-device-mode",
            "--no-sandbox",
            "--single-process",
            "--renderer-process-limit=1",
            "--disable-smooth-scrolling",
            "--disable-web-security",
            "--disable-webgl",
            "--disable-dev-shm-usage",
            "--disable-site-isolation-trials",
            "--disable-features=site-per-process",
        ]
        self.page_args = page_args or {'viewport': {"width": 0, "height": 0}}
        self.proxy = proxy
        self.fingerprint = md5(('TiLakPanColNoRhChNeIt' + str(proxy)).encode()).hexdigest()

    def retry(self, *exceptions, retries=2, cooldown=0):
        def wrap(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                nonlocal retries
                while retries != 0:
                    try:
                        result = await func(*args, **kwargs)
                    except exceptions as err:
                        retries -= 1
                        logging.debug(f'{self.proxy} retrying: {retries} times left; {err}')
                        if cooldown > 0:
                            await asyncio.sleep(cooldown)
                    else:
                        return result
                raise RetryExhausted(err)
            return inner
        return wrap

    async def enter_ISML(self):
        if self.proxy:
            proxy = {'server': self.proxy}
            browser = await playwright.chromium.launch(
                headless=False, proxy=proxy, args=self.browser_args)
        else:
            browser = await playwright.chromium.launch(
                headless=False, args=self.browser_args)
        context = await browser.new_context(**self.page_args)
        page = await context.new_page()
        await stealth_async(page)

        def modify_fingerprint(route: Route):
            asyncio.create_task(route.continue_(post_data=urlencode({"secure": self.fingerprint})))

        await page.route(lambda s: 'www.internationalsaimoe.com/security' in s, modify_fingerprint)
        await page.route(lambda s: 'www.internationalsaimoe.com/fonts' in s, lambda route: route.abort())
        await page.route(lambda s: 'cdnjs.cloudflare.com/ajax/libs/owl-carousel' in s, lambda route: route.abort())
        await page.route(re.compile(r"(https://www\.internationalsaimoe\.com/.*\.gif(\?.*|$))|(.*\.png(\?.*|$))|(.*\.jpg(\?.*|$))|(.*\.jpeg(\?.*|$))|(.*\.css(\?.*|$))"),
                         lambda route: route.abort())
        await page.goto('http://www.internationalsaimoe.com/voting')
        res = await async_cf_retry(page)
        if res:
            content = await page.content()
            voting_token = re.search(voting_token_pattern, content)
            if voting_token:
                self.html = content
                self.voting_token = voting_token.group(1)
                self.start_time = time.time()
                self.browser = browser
                self.context = context
                self.page = page
                cookies = await page.context.cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in cookies}
                ua = await page.evaluate('() => {return navigator.userAgent}')
                self.client = await build_client_with_clearance(ua, cookies, proxies={'all://': self.proxy}, test=False)
                logging.info(f'{self.proxy} entered ISML')
            else:
                raise NoVotingToken(f'{self.proxy}')
            return
        else:
            await browser.close()
            raise InterruptedError(f"{self.proxy} cf challenge fail")

    @retry(HttpxExceptions)
    async def _local_post(self, url, data, timeout=REQUEST_TIMEOUT):
        async with local_client.post(url, data=data, timeout=timeout) as response:
            if response.status_code < 400:
                return response.text
            else:
                return response.raise_for_status()

    @retry(HttpxExceptions)
    async def _get(self, url, timeout=REQUEST_TIMEOUT):
        async with self.client.get(url, timeout=timeout) as response:
            if response.status_code < 400:
                if 'text' in response.headers['content-type']:
                    return response.text
                else:
                    return response.content
            else:
                return response.raise_for_status()

    async def AI_decaptcha(self):
        tries = 0
        while 1:
            tries += 1
            raw_img = await self._get(
                f"https://www.internationalsaimoe.com/captcha/{self.voting_token}/{int(time.time() * 1000)}",
                timeout=CAPTCHA_TIMEOUT)
            img = Image.open(BytesIO(raw_img))
            img = 255 - np.array(img.convert('L'))  # 转化为灰度图
            if judge(img):
                del img
                logging.info(f'{self.proxy} can recognize the {tries}-th captcha')
                captcha = await self._local_post(next(cs_gen), raw_img)
                self.captcha = captcha
                return captcha

    async def submit(self):
        # TODO: select characters
        # TODO: fill captcha input
        # TODO: wait for the submit button and click
        # TODO: wait for and handle the response
        raise NotImplementedError
    
    async def vote(self):
        await browser_pool.__aenter__()
        try:
            await self.enter_ISML()
            await self.AI_decaptcha()
            await self.submit()
        except:
            pass
        finally:
            await browser_pool.__aexit__(None, None, None)
        

class CfHandler(tornado.web.RequestHandler, ABC):
    
    def write_error(self, status_code: int, **kwargs):
        self.write(traceback.format_exc().replace("\n", "<br/>\n"))
    
    async def get(self, protocol: str, proxy: str):
        if '://' not in proxy:
            proxy = f'{protocol}://{proxy}'
        if not re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", proxy):
            proxy = None
        async with browser_pool:
            ua, cookies = await get_one_clearance(proxy, playwright=playwright)
        self.write({'ua': ua, 'cookies': cookies})
        return ua, cookies
    
    async def post(self):
        proxies = self.request.body.decode(encoding='utf-8').split('\r\n')
        
        async def get_clearance_and_vote(proxy):
            ua, cookies = await self.get('http', proxy)
            client = await build_client_with_clearance(ua, cookies, proxies=proxy, test=False)
            await VoterHttpx(client).vote()
        
        for proxy in proxies:
            worker_loop.create_task(get_clearance_and_vote(proxy))
        
        self.write('POST received')


def run_proc(port):
    AsyncIOMainLoop().install()
    app = tornado.web.Application([
        (r"/cf/(?P<protocol>[^\/]+)/?(?P<proxy>[^\/]+)", CfHandler),
    ])
    app.listen(port)
    logging.info(f'DestroyerIgnaleoAP@localhost:{port}')
    worker_loop.run_forever()


logging.basicConfig(datefmt='%H:%M:%S', format='%(asctime)s[%(levelname)s] %(message)s', level=logging.INFO)
if __name__ == "__main__":
    if not os.path.exists(save_path):
        logging.info(f'IgnareoAP: creating path {save_path} to save HTML files')
        os.makedirs(save_path)
    
    logging.info(f'IgnareoAP: {num_cpu} CPUs with total memory {total_memory_GB} GB')
    logging.info(f'IgnareoAP: set browser_pool_size=={browser_pool_size} for each process')
    
    captcha_servers_OK = True
    for captcha_server in captcha_servers:
        try:
            worker_loop.run_until_complete(local_client.get(captcha_server))
        except Exception as e:
            captcha_servers_OK = False
            logging.warning(f'Failed to contact captcha server {captcha_server}')
    if captcha_servers_OK:
        logging.info('IgnaleoAP: captcha servers OK')
    else:
        logging.warning('IgnaleoAP: failed to contact some captcha servers')
    
    from multiprocessing import Process
    
    length = len(portList)
    for port in range(length - 1):
        p = Process(target=run_proc, args=(portList[port],))
        p.start()
    run_proc(portList[length - 1])
