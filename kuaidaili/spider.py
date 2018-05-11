# coding: utf-8

from pyquery import PyQuery as pq
import requests as rq
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from multiprocessing import Pool
from config import *
import check
import logging

logging.basicConfig(filename='spider.log', filemode='w', format='%(asctime)s %(filename)s %(levelname)s %(message)s', level=logging.DEBUG)

class Kuaidaili(object):
    ## 返回整个网页的数据
    def get_html(self, page_cnt='', a=0):
        if a >= MAX_CONN_CNT:
            print('ConnectError: max connect count !')
            return None
        result = rq.get(url=KUAIDAILI_URI + page_cnt, headers=HEADERS)
        if result.status_code == 200:
            return result.text
        else:
            a += 1
            print('{} \trequest error: {}, try to connect: {}'.format(result.url, result.status_code, a))
            return get_html(page_cnt, a)

    ## 提取出网页所有代理ip
    def parse_ip(self, html):
        doc = pq(html)
        items = doc('#freelist table tbody tr').items()

        for item in items:
            proxy = item('td').eq(0).text() + ':' + item('td').eq(1).text()
            yield proxy

    ## 获取网站代理ip总页数
    def parse_page_cnt(self, html):
        doc = pq(html)
        items = doc('#listnav ul li a').items()
        page_cnt = None

        for x in items:
            page_cnt = x.text()
        print('page_count: ', page_cnt)
        return page_cnt

    ## 验证代理ip是否可用
    def verify_proxy(self, proxy):
        proxies = {
            'http': 'http://' + proxy,
            'https': 'http://' + proxy
        }

        try:
            r = rq.get(url=PROXY_TEST_URI, headers=HEADERS, proxies=proxies, timeout=10)
            if r.status_code == 200:
                print('Successed to connect ! ------------------------------------------', proxy)
                return True
            print('Status_code: {}\t{}'.format(r.status_code, proxy))
            return False
        except Exception:
            print('Unexcepted connect error ! May be connect time out !\t', proxy)
            return False

    ## 保存可用的代理ip到MongoDB
    def save_to_mongodb(self, proxy):
        cli = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT, connect=False)
        db = cli[MONGODB_NAME]
        collection = db[MONGODB_COLLECTION]
        if collection.update({'proxy': proxy}, {'$set': {'proxy': proxy}}, True):
            print('存入MongoDB成功....', proxy)
            return True
        else:
            print('存入MongoDB失败....', proxy)
            return False

    def run(self, page_cnt):
        html = self.get_html(str(page_cnt))
        if html is not None:
            proxies = self.parse_ip(html)

            for proxy in proxies:
                if proxy is not None:
                    if self.verify_proxy(proxy):
                        try:
                            self.save_to_mongodb(proxy)
                        except ServerSelectionTimeoutError:
                            print('ServerSelectionTimeoutError: Connection refused!')


if __name__ == '__main__':
    logging.debug('---------------------------------------------------------Go!')
    check.run()
    
    app = Kuaidaili()
    html = app.get_html()
    page_cnt = app.parse_page_cnt(html)
    
    pool = Pool()
    pool.map(app.run, [i for i in range(1, int(page_cnt) + 1)])


