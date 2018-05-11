# coding: utf8

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from multiprocessing import Pool
import requests as rq
from config import *


cli = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT, connect=False)
db = cli[MONGODB_NAME]
collection = db[MONGODB_COLLECTION]


## 验证代理ip是否可用
def verify_proxy(proxy):
    proxies = {
        'http': 'http://' + proxy,
        'https': 'http://' + proxy
    }

    try:
        r = rq.get(url=PROXY_TEST_URI, headers=HEADERS, proxies=proxies, timeout=10)
        if r.status_code == 200:
            return True
        print('Status_code: ', r.status_code)
        return False
    except Exception:
        return False


def check_useful_mongodb(item):
    proxy = item['proxy']
    if verify_proxy(proxy):
        print('This proxy is available, keep it now!\t', proxy)
    else:
        print('This proxy is unavailable, remove now!\t', proxy)
        collection.remove({'proxy': proxy})


def run():
    try:
        cursor = collection.find()
        pool = Pool()
        pool.map(check_useful_mongodb, [item for item in cursor])
    except ServerSelectionTimeoutError:
        print('ServerSelectionTimeoutError: Connection refused!')


if __name__ == '__main__':
    run()
