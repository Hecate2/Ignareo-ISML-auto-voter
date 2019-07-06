#coding:utf-8

import logging,traceback

from functools import wraps

log = logging.getLogger(__name__)

acceptStatus=(503,'其他接受的状态码')

class RetryExhaustedError(Exception):
    pass
    #def __init__(self, funcname,args,kwargs):
    #    print('Exception from {}: {} {}'.format(funcname,args,kwargs))
        
import aiohttp,asyncio
loop = asyncio.get_event_loop()

def retry(*exceptions, retries=3, cooldown=1, verbose=True):
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
            retries_count = 0

            while True:
                try:
                    result = await func(*args, **kwargs)
                except exceptions as err:   #exceoptions是从retry传入的
                    retries_count += 1
                    message = "Exception:{} during\n{} execution. " \
                              "{} of {} retries attempted"\
                              .format(err, func, retries_count, retries)

                    if retries_count >= retries:
                        #verbose and log.exception(message)
                        verbose and print(message)
                        
                        #raise RetryExhaustedError(
                        #    func.__qualname__, args, kwargs) from err
                        #raise RetryExhaustedError
                        return err
                    else:
                        #verbose and log.warning(message)
                        verbose and print(message)
                        await asyncio.sleep(cooldown)
                else:
                    return result
        return inner
    return wrap

# Example is taken from http://aiohttp.readthedocs.io/en/stable/#getting-started
async def fetch(session, url):
    async with session.get(url) as response:
        #return await response.text()
        text=await response.text()
        if (response.status<400 or response.status in acceptStatus):
            return text
        else:
            return response.raise_for_status()

# Client code, provided for reference
@retry(aiohttp.ClientError,asyncio.TimeoutError)
#@retry(aiohttp.WSServerHandshakeError,aiohttp.ContentTypeError)
async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://localhost:55556')
        print(html)

if __name__=='__main__':
    loop.run_until_complete(main())
