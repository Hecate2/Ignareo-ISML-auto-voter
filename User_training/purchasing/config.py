from urllib.parse import quote as urlencode
from logger import default_logger
import random
# random.seed(68)  # 设置固定的随机数种子，这样本文件随机产生的内容将永远不变。不同种子产生不同结果。
from fake_useragent import UserAgent
uaGen = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0')
ua = uaGen.random

monitor_url_list = (
    'https://www.fasola-shop.com/zh-CN/products?utf8=✓&q[terminal1_min_eq]=0&q[terminal2_min_eq]=0&q[terminal3_min_eq]=0&q[keywords_search]=&q[taxons_id_eq]=&q[brand_id_eq][]=&q[brand_id_eq][]=171&q[brand_id_eq][]=&q[master_prices_between]=&q[limited_eq]=0&q[anchor_taxons_id_eq]=',
)
target_product_set = (  # 要抢的商品的id。在浏览商品列表的页面按F12找variant_id
"product_319464",  # 注意逗号！
"product_319468",
"product_319470",
)

# monitor_url_list = (
#     'https://www.fasola-shop.com/products?utf8=%E2%9C%93&q%5Bterminal1_min_eq%5D=0&q%5Bterminal2_min_eq%5D=0&q%5Bterminal3_min_eq%5D=0&q%5Bkeywords_search%5D=&q%5Btaxons_id_eq%5D=2&q%5Bbrand_id_eq%5D%5B%5D=&q%5Bbrand_id_eq%5D%5B%5D=&q%5Bbrand_id_eq%5D%5B%5D=&q%5Bmaster_prices_between%5D=&q%5Blimited_eq%5D=0&q%5Banchor_taxons_id_eq%5D=31',
# )
# target_product_set = ("product_576860",)

customer_info_list = [  # 本来应该写dict，但航空公司代码字段居然要post三遍
    [# 每条内容结束有英文逗号！每条内容本身有英文引号！单引号双引号都可以，但不能单引号开始双引号结束
        ['order[bill_address_attributes][fullname]','Your Name'.replace(' ','+')],  # 名字；必须是英文
        ['order[email]',urlencode('YourMail@email.com')],
        ['order[email_confirmation]',urlencode('YourMail@email.com')],  # 确认电子邮件。和上面填一模一样的邮件地址
        ['order[life_locale]',"japan"],  # 现在居住国家。可填内容的列表见说明
        ['order[required_nationality]',"china"],
        ['order[bill_address_attributes][phone_country]','86'],  # 国际电话区号。注意不要忘了单引号
        ['order[bill_address_attributes][phone]','15125689889'],  # 电话号码
        # ['depart_term_available_on','2020/12/25'],  # 不要启用这项。应当从网页中自动获取
        # ['depart_term_disavailable_on','2021/01/22'],  # 不要启用这项。应当从网页中自动获取
        ['order[depart_on(1i)]','2021'],  # 出发年
        ['order[depart_on(2i)]','1'],  # 出发月
        ['order[depart_on(3i)]','21'],  # 出发日
        ['order[depart_day_of_the_week]','4'],  # 星期几出发。注意：星期日应填'0'。必须与日期匹配。
        # ['terminal','1'],  # 第几航站楼。其实不用填
        # 注意：假如是1号航站楼，则在下面第1个order[airline_ids][]右边填航空公司代码。其他位置的航空公司代码空着
        # 假如是2号航站楼，则在下面第2个order[airline_ids][]右边填航空公司代码。其他位置的航空公司代码空着
        ['order[airline_ids][]',''],  # 航空公司代码。详见说明
        ['order[airline_ids][]','64'],  # 航空公司代码。
        ['order[airline_ids][]',''],  # 航空公司代码。
        ['order[flight_number]','JL829'],  # 航班号
        ['order[destination_region_id]','4'], # 到达地区id。详见说明
        ['order[transit_city]',''],  # 中转城市，可不填
        ['order[destination_city]','DALIAN'],  # 到达城市
        ['order[note]',''],  # 备注，可不填
        # ['order[bill_address_attributes][id]','299161'],  # 不要启用这项。应当从网页中自动获取。这一项仅在人工填表出错重填时才会有
        ['order[use_billing]','1'],  # 如果看不懂html一般不要修改这项  # <input type="hidden" name="order[use_billing]" id="order_use_billing" value="1">
        ['order[gender]',random.choice(['','man','woman'])],  # 随机选择男性或女性或不填。也可在这里直接填'man'或'woman'
        ['order[age]',random.choice(['',random.choice(['under_twenty','twenty','thirty','fourty','fifty','over_sixty'])])],  # 随机选择不填或填某个年龄。也可以直接填确定内容
        ['order[purpose]',random.choice(['',random.choice(['home','souvenir','business','other_purpose'])])],  # 购买目的。可自己直接填
        ['checkout',''],  # 如果看不懂html一般不要修改这项
    ],  # !!!千万不要忘了这个右括号后面的英文逗号!!!
    [# 每条内容结束有英文逗号！每条内容本身有英文引号！单引号双引号都可以，但不能单引号开始双引号结束
        ['order[bill_address_attributes][fullname]','Your Name'.replace(' ','+')],  # 名字；必须是英文
        ['order[email]',urlencode('YourMail@email.com')],
        ['order[email_confirmation]',urlencode('YourMail@email.com')],  # 确认电子邮件。和上面填一模一样的邮件地址
        ['order[life_locale]',"japan"],  # 现在居住国家。可填内容的列表见说明
        ['order[required_nationality]',"china"],
        ['order[bill_address_attributes][phone_country]','86'],  # 国际电话区号。注意不要忘了单引号
        ['order[bill_address_attributes][phone]','15125689889'],  # 电话号码
        # ['depart_term_available_on','2020/12/25'],  # 不要启用这项。应当从网页中自动获取
        # ['depart_term_disavailable_on','2021/01/22'],  # 不要启用这项。应当从网页中自动获取
        ['order[depart_on(1i)]','2021'],  # 出发年
        ['order[depart_on(2i)]','1'],  # 出发月
        ['order[depart_on(3i)]','21'],  # 出发日
        ['order[depart_day_of_the_week]','4'],  # 星期几出发。注意：星期日应填'0'。必须与日期匹配。
        # ['terminal','1'],  # 第几航站楼。其实不用填
        # 注意：假如是1号航站楼，则在下面第1个order[airline_ids][]右边填航空公司代码。其他位置的航空公司代码空着
        # 假如是2号航站楼，则在下面第2个order[airline_ids][]右边填航空公司代码。其他位置的航空公司代码空着
        ['order[airline_ids][]',''],  # 航空公司代码。详见说明
        ['order[airline_ids][]','64'],  # 航空公司代码。
        ['order[airline_ids][]',''],  # 航空公司代码。
        ['order[flight_number]','JL829'],  # 航班号
        ['order[destination_region_id]','4'], # 到达地区id。详见说明
        ['order[transit_city]',''],  # 中转城市，可不填
        ['order[destination_city]','DALIAN'],  # 到达城市
        ['order[note]',''],  # 备注，可不填
        # ['order[bill_address_attributes][id]','299161'],  # 不要启用这项。应当从网页中自动获取。这一项仅在人工填表出错重填时才会有
        ['order[use_billing]','1'],  # 如果看不懂html一般不要修改这项  # <input type="hidden" name="order[use_billing]" id="order_use_billing" value="1">
        ['order[gender]',random.choice(['','man','woman'])],  # 随机选择男性或女性或不填。也可在这里直接填'man'或'woman'
        ['order[age]',random.choice(['',random.choice(['under_twenty','twenty','thirty','fourty','fifty','over_sixty'])])],  # 随机选择不填或填某个年龄。也可以直接填确定内容
        ['order[purpose]',random.choice(['',random.choice(['home','souvenir','business','other_purpose'])])],  # 购买目的。可自己直接填
        ['checkout',''],  # 如果看不懂html一般不要修改这项
    ],  # !!!千万不要忘了这个右括号后面的英文逗号!!!
]
for customer_info in customer_info_list:
    if customer_info[1][1] != customer_info[2][1]:
        default_logger.logger.error(f'邮件地址{customer_info[1][1]}与确认邮件地址{customer_info[2][1]}不一致。这份顾客信息将不被使用。建议尽快修改')
        customer_info_list.remove(customer_info)
    for field in customer_info:
        field = (urlencode(field[0]), field[1])
'''
fields not filled (with examples):
depart_term_available_on=2020/12/25
depart_term_disavailable_on=2021/01/22
'''

monitor_headers = {
'Host': 'www.fasola-shop.com',
'User-Agent': ua,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'If-None-Match': 'W/"41622b0865ef1f3708a4a0909654a5c8"',
'Cache-Control': 'max-age=0',
}

add_to_cart_headers = {
'Host': 'www.fasola-shop.com',
'User-Agent': ua,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate',
'Content-Type': 'application/x-www-form-urlencoded',
'Origin': 'https://www.fasola-shop.com',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
}

cart_checkout_headers = {
'Host': 'www.fasola-shop.com',
'User-Agent': ua,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate',
'Content-Type': 'application/x-www-form-urlencoded',
'Origin': 'https://www.fasola-shop.com',
'Connection': 'keep-alive',
'Referer': 'https://www.fasola-shop.com/cart',
'Upgrade-Insecure-Requests': '1',
}

submit_form_headers = {
'Host': 'www.fasola-shop.com',
'User-Agent': ua,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate',
'Referer': 'https://www.fasola-shop.com/checkout/update/address',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
}

final_confirm_headers = {
'Host': 'www.fasola-shop.com',
'User-Agent': ua,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Accept-Encoding': 'gzip, deflate',
'Content-Type': 'application/x-www-form-urlencoded',
'Origin': 'https://www.fasola-shop.com',
'Connection': 'keep-alive',
'Referer': 'https://www.fasola-shop.com/checkout/confirm',
'Upgrade-Insecure-Requests': '1',
}

class Config:
    def  __init__(self, monitor_url_list=monitor_url_list, target_product_set=target_product_set):
        self.monitor_url_list = monitor_url_list
        self.target_product_set = target_product_set

default_config = Config()
