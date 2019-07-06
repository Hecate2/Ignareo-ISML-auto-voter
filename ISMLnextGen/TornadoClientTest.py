#!/usr/bin/env python3
import time,re,random
from datetime import timedelta

from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag

from tornado import gen, httpclient, ioloop, queues
from tornado.httpclient import HTTPRequest as request
from tornado.httpclient import AsyncHTTPClient
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

#base_url = "http://www.tornadoweb.org/en/stable/"
base_url = "http://www.baidu.com/"
#base_url = "https://www.internationalsaimoe.com/"
concurrency = 1000

from fake_useragent import UserAgent
useragent = UserAgent()
acceptLanguage=[
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5,en-us;q=0.3',
    'zh-cn,zh;q=0.8,zh-tw;q=0.7,zh-hk;q=0.5',
    'ar-sa;q=0.9,en;q=0.5',
    'ru;q=0.8,en;q=0.7',
    'en-us;q=0.8,en;q=0.5',
    'en;q=0.8',
    ]
ua = useragent.random

def genHeaders():
    headers = {
        'user-agent': useragent.random,
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'referer': "https://www.internationalsaimoe.com/voting/",
        'accept-encoding': "gzip, deflate",
        'accept-language': acceptLanguage[random.randint(0, len(acceptLanguage) - 1)],
        'cache-control': "no-cache",
        'connection':'keep-alive',
        'X-Requested-With':'XMLHttpRequest'
        #'Upgrade-Insecure-Requests':'1',
    }
    return headers


async def get_links_from_url(url):
    """Download the page at `url` and parse it for links.
    Returned links have had the fragment after `#` removed, and have been made
    absolute so, e.g. the URL 'gen.html#tornado.gen.coroutine' becomes
    'http://www.tornadoweb.org/en/stable/gen.html'.
    """
    req=request(url)#,headers=genHeaders())
    response = await AsyncHTTPClient().fetch(req,raise_error=False)
    if(response.code==200):
        html = response.body.decode(errors="ignore")
        print("fetched %s" % url)

    # 保存数据到文件
        try:
            filename=re.search(r'[^/]+(?!.*/)',url).group()
            with open('./tmp/'+filename, 'wb') as f:
                f.write(html.encode('utf8'))
        except Exception as e:
            print(e,url)
        return [urljoin(url, remove_fragment(new_url)) for new_url in get_links(html)]

    else:
        print("Code:",response.code,url)
        return []


def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url


def get_links(html):
    class URLSeeker(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.urls = []

        def handle_starttag(self, tag, attrs):
            href = dict(attrs).get("href")
            if href and tag == "a":
                self.urls.append(href)

    url_seeker = URLSeeker()
    url_seeker.feed(html)
    return url_seeker.urls


async def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()

    async def fetch_url(current_url):
        if current_url in fetching:
            return

        #print("fetching %s" % current_url)
        fetching.add(current_url)
        urls = await get_links_from_url(current_url)
        fetched.add(current_url)

        for new_url in urls:
            # Only follow links beneath the base URL
            if new_url.startswith(base_url):
                await q.put(new_url)
        #print("qsize",q.qsize(),urls)

    async def worker():
        async for url in q:
            if url is None:
                return
            try:
                await fetch_url(url)
            except Exception as e:
                print("Exception: %s %s" % (e, url))
            finally:
                q.task_done()

    await q.put(base_url)

    # Start workers, then wait for the work queue to be empty.
    workers = gen.multi([worker() for _ in range(concurrency)])
    await q.join(timeout=timedelta(seconds=300))
    #assert fetching == fetched
    if(fetching == fetched):
        print('(set)fetching == (set)fetched')
    else:
        print('(set)fetching != (set)fetched !!!!!!')
    print("Done in %d seconds, fetched %s URLs." % (time.time() - start, len(fetched)))

    # Signal all the workers to exit.
    for _ in range(concurrency):
        await q.put(None)
    await workers


if __name__ == "__main__":
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
