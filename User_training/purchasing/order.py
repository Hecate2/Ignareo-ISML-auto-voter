import random, uuid, time
from urllib.parse import quote as urlencode
import requests
from AdvancedHTMLParser import AdvancedHTMLParser
parser = AdvancedHTMLParser()

from retryapi import retry, RetryExhausted
from monitor import Monitor
from config import default_config, add_to_cart_headers, cart_checkout_headers, submit_form_headers, final_confirm_headers
from utils import list_cycle_gen

request_timeout = None
RequestExceptions=(
    requests.RequestException,
    requests.ConnectionError,
    requests.HTTPError,
    requests.Timeout,
    )

class OrderOperator:
    def __init__(self, customer_info=None, session=requests.Session(), monitor_url=default_config.monitor_url_list[0], post_data=None):
        self.customer_info = customer_info
        self.session = session
        self.monitor_url = monitor_url
        self.post_data = post_data

    @retry(exceptions=RequestExceptions, tries=-1, logger=None)
    def _get(self, url, timeout=request_timeout, headers=None):
        r = self.session.get(url, timeout=timeout, headers=headers, verify=False)
        if r.status_code < 400:
            return r
        else:
            r.raise_for_status()

    @retry(exceptions=RequestExceptions,tries=-1,logger=None)
    def _post(self, url, data=None, timeout=request_timeout, headers=None):
        r = self.session.post(url, data=data, timeout=timeout, headers=headers, verify=False)
        if r.status_code < 400:
            return r
        else:
            r.raise_for_status()
    
    def add_one_random_item_to_cart(self):
        if not self.post_data:
            self.post_data = random.choice(Monitor(self.monitor_url, session_gen=list_cycle_gen(tuple(self.session,))).run_until_available())[1]
        r = self._post('https://www.fasola-shop.com/orders/populate', data=self.post_data, headers=add_to_cart_headers)  # add to cart
        self.cart_response = r
        return r
        
    def cart_checkout(self):
        def parse_cart(htm: str):
            parser.parseStr(htm)
            input_nodes = parser.getElementsByClassName("edit_order").getElementsByTagName("input")
            post_data = dict()
            for child in input_nodes:
                post_data[child.attributesDict['name']] = child.attributesDict['value']
            post_data['checkout']=''
            return post_data
        r = self.cart_response
        cart_post_data = parse_cart(r.text)
        r = self._post('https://www.fasola-shop.com/cart', data=cart_post_data, headers=cart_checkout_headers)
        self.cart_checkout_response = r
        return r
    
    def submit_form(self):
        def parse_form(htm: str, customer_info):
            parser.parseStr(htm)
            all_nodes = parser.getElementsByClassName("form-horizontal").getElementsByTagName("input")
            general_filter = {'utf8', '_method', 'authenticity_token', 'order[state_lock_version]'}
            general_nodes = list(filter(lambda child: child.attributesDict['name'] in general_filter, all_nodes))
            general_nodes = [(urlencode(child.attributesDict['name']), urlencode(child.attributesDict['value'])) for child in general_nodes]
            customer_info = general_nodes + customer_info
            departure_nodes = parser.getElementsByClassName("col-sm-9 form-inline departure_validated_form").getElementsByTagName("input")
            departure_nodes = [(urlencode(child.attributesDict['name']), child.attributesDict['value'].replace('/','%2F')) for child in departure_nodes]
            customer_info = customer_info + departure_nodes
            try:
                bill_id_node = parser.getElementById("order_bill_address_attributes_id")
                bill_id_node = [(urlencode(bill_id_node.attributesDict['name']), bill_id_node.attributesDict['value'])]
                customer_info = customer_info + bill_id_node
            except:
                pass
            return customer_info
        r = self.cart_checkout_response
        customer_info = parse_form(r.text, self.customer_info)
        post_data = ''
        for field in customer_info:
            post_data += f'{field[0]}={field[1]}&'
        post_data = post_data[0:-1]
        r = self._post('https://www.fasola-shop.com/checkout/update/address', data=post_data, headers=submit_form_headers)
        self.submit_form_response = r
        return r
    
    def submit_final_confirm(self):
        def parse_final_confirm(htm: str):
            parser.parseStr(htm)
            input_nodes = parser.getElementsByClassName("form-horizontal").getElementsByTagName("input")
            post_data = dict()
            for child in input_nodes:
                if child.attributesDict['name'] is not None:
                    post_data[child.attributesDict['name']] = child.attributesDict['value']
            return post_data
        r = self.submit_form_response
        post_data = parse_final_confirm(r.text)
        r = self._post('https://www.fasola-shop.com/checkout/update/confirm', data=post_data, headers=final_confirm_headers)
        self.submit_final_confirm_response = r
        return r

    def save_results(self, path='./results/'):
        r = self.submit_form_response
        with open(f'{path}{uuid.uuid4()}.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
            
    def run(self):
        self.add_one_random_item_to_cart()
        self.cart_checkout()
        self.submit_form()
        # with open('form.html', 'w', encoding='utf-8') as f:
        #     f.write(self.submit_form_response.text)
        self.submit_final_confirm()
        # time.sleep(15+random.random()*10)
        self.save_results()