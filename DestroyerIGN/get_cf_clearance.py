import logging
import re
import asyncio
from playwright.async_api import async_playwright, Error, Page
from cf_clearance import stealth_async
import httpx

# local_client = httpx.AsyncClient(verify=False)
url = 'https://www.internationalsaimoe.com/'


async def async_cf_retry(page: Page, tries=10) -> bool:
    # use tries=-1 for infinite retries
    # excerpted from `from cf_clearance import async_retry`
    success = False
    while tries != 0:
        try:
            title = await page.title()
        except Error:
            tries -= 1
            await asyncio.sleep(1)
        else:
            logging.debug(f'title: {title}')
            if title == 'Please Wait... | Cloudflare':
                await page.close()
                raise NotImplementedError('Encountered recaptcha. Check whether your proxy is an elite proxy.')
            elif title == 'Just a moment...':
                tries -= 1
                await asyncio.sleep(5)
            elif "www." in title:
                await page.reload()
                tries -= 1
                await asyncio.sleep(5)
            else:
                success = True
                break
    return success


async def get_one_clearance(proxy, logs=False):
    # proxy = {"server": "socks5://localhost:7890"}
    if type(proxy) is str:
        proxy = {'server': proxy}
    async with async_playwright() as p:
        if proxy:
            browser = await p.chromium.launch(
                headless=False, proxy=proxy,
                args=["--window-position=1000,800", "--disable-web-security", "--disable-webgl"])
        else:
            browser = await p.chromium.launch(
                headless=False,
                args=["--window-position=1000,800", "--disable-web-security", "--disable-webgl"])
        page = await browser.new_page(viewport={"width": 0, "height": 0})
        await stealth_async(page)
        
        await page.route(lambda s: 'www.internationalsaimoe.com/security' in s, lambda route: route.abort())
        await page.route(lambda s: 'www.internationalsaimoe.com/js' in s, lambda route: route.abort())
        await page.route(lambda s: 'cdnjs.cloudflare.com/ajax/libs/owl-carousel' in s, lambda route: route.abort())
        await page.route(lambda s: '/cloudflare-static/' in s, lambda route: route.abort())
        await page.route(lambda s: 'www.youtube-nocookie.com' in s, lambda route: route.abort())
        await page.route(re.compile(r"(.*\.png(\?.*|$))|(.*\.jpg(\?.*|$))|(.*\.jpeg(\?.*|$))|(.*\.css(\?.*|$))"),
                         lambda route: route.abort())
        
        if logs:
            def log_response(intercepted_response):
                logging.debug(f"{proxy} response: {intercepted_response.url}")
            page.on("response", log_response)
        
        await page.goto(url)
        res = await async_cf_retry(page)
        if res:
            cookies = await page.context.cookies()
            cookies_for_httpx = {cookie['name']: cookie['value'] for cookie in cookies}
            ua = await page.evaluate('() => {return navigator.userAgent}')
            # print(ua)
        else:
            await page.close()
            raise InterruptedError("cf challenge fail")
        await page.close()
        return ua, cookies_for_httpx


async def build_client_with_clearance(
        ua, cookies_for_httpx, client: httpx.AsyncClient = None, proxies=None, test=False):
    # proxies = {"all://": "socks5://localhost:7890"}
    if type(proxies) is str:
        proxies = {'all://': proxies}
    client = client or httpx.AsyncClient(proxies=proxies, verify=False)
    # use cf_clearance, must be same IP and UA
    client.headers.update({"user-agent": ua})
    client.cookies.update(cookies_for_httpx)
    if test:  # not necessary in actual combat
        res = await client.get(url)
        if '<title>Please Wait... | Cloudflare</title>' not in res.text:
            print("cf challenge success")
        else:
            raise InterruptedError("cf challenge failed")
        await client.aclose()
    return client


async def get_client_with_clearance(proxy: str = None):
    ua, cookies_for_httpx = await get_one_clearance(proxy, logs=False)
    client = await build_client_with_clearance(ua, cookies_for_httpx, test=False)
    return client


if __name__ == '__main__':
    url = 'https://nowsecure.nl/'
    logging.basicConfig(datefmt='%H:%M:%S', format='%(asctime)s[%(levelname)s] %(message)s', level=logging.DEBUG)
    async def get_client_with_clearance(proxy: str = None):
        ua, cookies_for_httpx = await get_one_clearance(proxy, logs=True)
        client = await build_client_with_clearance(ua, cookies_for_httpx, test=True)
        return client
    print(asyncio.get_event_loop().run_until_complete(get_client_with_clearance(
        # proxy='http://localhost:8888'
        # use proxifier on windows as an elite proxy
    )))
