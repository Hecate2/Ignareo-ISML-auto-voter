import time, datetime
import requests
from config import default_config, monitor_headers

from AdvancedHTMLParser import AdvancedHTMLParser
# import re
# pattern = re.compile(r'''<input.*name="(.*)".*value="(.*)".*>''')

from logger import default_logger
from utils import list_cycle_gen

class UnexpectedHTML(Exception):
    pass


parser = AdvancedHTMLParser()

class Monitor:
    def __init__(self, url_list=default_config.monitor_url_list,
                 target_product_set=default_config.target_product_set,
                 session_gen=list_cycle_gen(tuple([requests.Session() for _ in range(1)]))):
        self.url_gen = list_cycle_gen(tuple(url_list))
        self.session_gen = session_gen
        self.target_product_set = tuple(target_product_set)
        self.failure_count = 0
        self.init_time = time.time()

    def run_until_available(self, sleep_time=0.1):
        while 1:
            results = self.run_once()  # results == (session, ((product_id, {post_data}), ...) )
            if results[1]:
                return results
            else:
                time.sleep(sleep_time)

    def run_once(self):
        session = next(self.session_gen)
        r = session.get(next(self.url_gen), headers=monitor_headers, verify=False)
        if r.status_code == 200:
            post_data_list = self.parse(self.target_product_set, r.text)
            # default_logger.logger.debug(f'{post_data_list}')
            # default_logger.logger.debug(
            #     f'商品{self.target_product_set}\n是否有货: {[True if post_data else False for post_data in post_data_list]}')
            return session, tuple(filter(lambda x:x[1] is not None, zip(self.target_product_set, post_data_list)))
        else:
            current_time = time.time()
            session.cookies.clear()
            self.failure_count += 1
            default_logger.logger.warning(
                f"监控失败了一次，状态码{r.status_code}。从启动到现在{str(datetime.timedelta(seconds=current_time - self.init_time))}时间内已有{self.failure_count}次监控失败")
            return session, None
    
    def parse(self, product_id_list: tuple, htm: str):
        def extract_post_data(product_node):
            if not product_node:
                return None
            if "脱销" in product_node.innerHTML or "お問い合わせ" in product_node.innerHTML:
                return None
            elif "放入购物车" in product_node.innerHTML or "カートに入れる" in product_node.innerHTML:
                post_data = dict()  # 准备需要post的参数
                input_nodes = product_node.getElementsByClassName("cart").getElementsByTagName("input")
                for child in input_nodes:
                    post_data[child.attributesDict['name']] = child.attributesDict['value']
                return post_data
                '''
                post_data example:
                {
                    'utf8': '✓',
                    'authenticity_token': '/82r8pGW3JuhCWIS6rGdDFqlDATT58QS0XS6aW6/pfGtTtr6OhQPpRPYnTlRSMNTPxpi2/9KLT+U1YUGDmbQPg==',
                    'variant_id': '186358',
                    'quantity': '1'
                }
                !!!url encoded!!!
                '''
            else:
                raise UnexpectedHTML('网站可能改版了，请联系开发者')
        
        parser.parseStr(htm)
        product_nodes = [parser.getElementById(product_id) for product_id in product_id_list]
        # default_logger.logger.debug(f'商品{product_id_list}\n是否在网页上: {[True if node else False for node in product_nodes]}')
        post_data_list = tuple(map(lambda node: extract_post_data(node), product_nodes))
        return post_data_list
