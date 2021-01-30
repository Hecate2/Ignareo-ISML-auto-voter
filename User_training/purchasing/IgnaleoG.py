# github.com/Hecate2/Ignareo

# fixed IgnaleoG config
import asyncio,gevent
from gevent import monkey
monkey.patch_all()

import tornado.ioloop
import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

portList=tuple([i for i in range(55568,55569)])
worker_loop=asyncio.get_event_loop()
# end fixed IgnaleoG config

import random
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from monitor import Monitor
from order import OrderOperator
from logger import default_logger
from utils import list_cycle_gen

from config import default_config, customer_info_list


def run_once(customer_info, session=requests.Session()):
    session_gen = list_cycle_gen([session])
    session, post_data_tuple = Monitor(default_config.monitor_url_list, default_config.target_product_set, session_gen).run_until_available()
    operator = OrderOperator(customer_info, session, post_data=random.choice(post_data_tuple)[1])
    operator.run()


def run_batch(customer_info_list):
    session_gen = list_cycle_gen([requests.Session() for _ in customer_info_list])
    session, post_data_tuple = Monitor(default_config.monitor_url_list, default_config.target_product_set, session_gen).run_until_available()
    operator = OrderOperator(customer_info_list[0], session, post_data=random.choice(post_data_tuple)[1])
    gevent.spawn(operator.run)
    for customer_info in customer_info_list[1:]:
        operator = OrderOperator(customer_info, next(session_gen), post_data=random.choice(post_data_tuple)[1])
        gevent.spawn(operator.run)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        pass

def run_proc(port):
    AsyncIOMainLoop().install()
    # app = tornado.web.Application([
    #     (r'/', MainHandler),
    # ])
    # app.listen(port)
    default_logger.logger.info('\n\nDestroyerIgnaleoG@localhost:%d\n' % (port))
    default_logger.logger.info(f'target url: {default_config.monitor_url_list}')
    default_logger.logger.info(f'target products: {default_config.target_product_set}')
    default_logger.logger.info(f'customer name: {[customer_info[0][1] for customer_info in customer_info_list]}')

    tasks = [gevent.spawn(run_once, customer_info) for customer_info in customer_info_list]  # 启用这项为快速监控
    
    #gevent.spawn(run_batch, customer_info_list)  # 启用这项为慢速监控
    
    worker_loop.run_forever()


if __name__ == '__main__':
    # async version
    from multiprocessing import Process
    length=len(portList)
    for port in range(length-1):
        p=Process(target=run_proc, args=(portList[port],))
        p.start()
    run_proc(portList[length-1])
    
    # sync version for test
    # run_once(customer_info_list[0])