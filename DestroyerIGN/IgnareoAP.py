# `AP` for `async playwright`
# IGN AP is for getting Cloudflare clearance before voting with httpx
# Alternatively it may just obtain the clearance and return the ua & clearance to other processes
from get_cf_clearance import get_one_clearance, build_client_with_clearance
from abc import ABC
import traceback
import re
import logging
import asyncio
import psutil
import multiprocessing
import httpx
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

portList = [i for i in range(55068, 55068 + multiprocessing.cpu_count())]
captcha_servers = [
    'http://localhost:8888',
    'http://localhost:8889',
]

total_memory = psutil.virtual_memory().total
total_memory_GB = int(total_memory/1024**3)
num_cpu = multiprocessing.cpu_count()
browser_pool_size = int((total_memory_GB - 3) / (multiprocessing.cpu_count() * 0.25))
browser_pool = asyncio.Semaphore(browser_pool_size)
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

local_client = httpx.AsyncClient()
worker_loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(worker_loop)


class CfHandler(tornado.web.RequestHandler, ABC):
    
    def write_error(self, status_code: int, **kwargs):
        self.write(traceback.format_exc().replace("\n", "<br/>\n"))
    
    async def get(self, protocol: str, proxy: str):
        if '://' not in proxy:
            proxy = f'{protocol}://{proxy}'
        if not re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", proxy):
            proxy = None
        async with browser_pool:
            ua, cookies = await get_one_clearance(proxy)
        self.write({'ua': ua, 'cookies': cookies})
        return ua, cookies
        
    async def post(self):
        proxies = self.request.body.decode(encoding='utf-8').split('\r\n')
        
        async def get_clearance_and_vote(proxy):
            ua, cookies = await self.get('http', proxy)
            client = await build_client_with_clearance(ua, cookies, test=False)
            # TODO: vote with the client

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
    logging.info(f'IgnareoAP: {num_cpu} CPUs with total memory {total_memory_GB} GB')
    logging.info(f'IgnareoAP: set browser_pool_size=={browser_pool_size} for each process')
    
    for captcha_server in captcha_servers:
        worker_loop.run_until_complete(local_client.get(captcha_server))
    logging.info('IgnaleoAP: captcha servers OK')
    
    from multiprocessing import Process
    
    length = len(portList)
    for port in range(length - 1):
        p = Process(target=run_proc, args=(portList[port],))
        p.start()
    run_proc(portList[length - 1])
