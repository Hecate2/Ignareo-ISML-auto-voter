from typing import Optional, Union, Dict
import re
import logging
import time
from hashlib import md5
from urllib.parse import urlencode
from get_cf_clearance import (get_one_clearance, build_client_with_clearance,
    async_playwright, async_cf_retry, Error, Page, stealth_async)
from playwright.async_api import Route, Playwright
import asyncio
worker_loop = asyncio.get_event_loop()
asyncio.set_event_loop(worker_loop)

playwright: Playwright = worker_loop.run_until_complete(async_playwright().start())

class VoterPlaywright:
    def __init__(self, proxy: Union[str, Dict[str, str]],
                 browser_args=None, page_args: Optional[Dict] = None):
        self.browser_args = browser_args or ["--disable-web-security", "--disable-webgl"]
        self.page_args = page_args or {'viewport': {"width": 0, "height": 0}}
        self.proxy = {'server': proxy} if type(proxy) is str else proxy
        self.fingerprint = md5(('TiLakPanColNoRhChNeIt' + str(proxy)).encode()).hexdigest()
    
    async def enter_ISML(self):
        if self.proxy:
            browser = await playwright.chromium.launch(
                headless=False, proxy=self.proxy, args=self.browser_args)
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
        await page.route(re.compile(
            r"(https://www\.internationalsaimoe\.com/.*\.gif(\?.*|$))|(.*\.png(\?.*|$))|(.*\.jpg(\?.*|$))|(.*\.jpeg(\?.*|$))|(.*\.css(\?.*|$))"),
                         lambda route: route.abort())
        await page.goto('http://www.internationalsaimoe.com/voting')
        res = await async_cf_retry(page)
        if res:
            content = await page.content()
            self.html = content
            self.voting_token = None
            self.start_time = time.time()
            self.browser = browser
            self.context = context
            self.page = page
            logging.info(f'{self.proxy} entered ISML')
            await asyncio.sleep(100)
            return
        else:
            await browser.close()
            raise InterruptedError(f"{self.proxy} cf challenge fail")
    
    async def vote(self):
        await self.enter_ISML()

logging.basicConfig(datefmt='%H:%M:%S', format='%(asctime)s[%(levelname)s] %(message)s', level=logging.INFO)
worker_loop.run_until_complete(VoterPlaywright(None).vote())