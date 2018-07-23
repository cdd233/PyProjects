# coding: utf-8

''' ishadowx vpn script
1. 连续请求 5 次不成功，将自动终止本程序
2. 每次返回 12 条信息，将随机选取一条自动连接，不支持手动
3. 站点的 vpn 大概 6 小时会更新一次，失效后请重新运行
author blog：http://saltedfish.org
source link：https://github.com/demoToGrn/PyProjects/tree/master/ishadowx
'''

import requests as rq
from random import randint
from requests.exceptions import RequestException
from fake_useragent import UserAgent
from fake_useragent.errors import FakeUserAgentError
from lxml import etree
import os
import time

MAX_RETRY = 5
try:
    ua = UserAgent(verify_ssl=False)
except FakeUserAgentError:
    print('error：raising FakeUserAgentError...')


def spider(cnt=1):
    if cnt <= MAX_RETRY:
        print('Preparing to obtain vpn:  {} / {}'.format(cnt, MAX_RETRY))
    else:
        print('The number of connections has reached a maximum, Exit now!')
        exit()

    try:
        headers = {'User-Agent': ua.random}
        r = rq.get(url='http://ss.ishadowx.com/', headers=headers, timeout=10)

        if r.status_code == 200:
            selector = etree.HTML(r.text)

            ip = selector.xpath('//div/h4[1]/span[1]/text()')
            port = selector.xpath('//div/h4[2]/span[1]/text()')
            password = selector.xpath('//div/h4[3]/span[1]/text()')
            verity_way = selector.xpath('//div/h4[4]/text()')

            return [ip, port, password, verity_way]
        else:
            return spider(cnt + 1)
    except RequestException:
        time.sleep(2)
        return spider(cnt + 1)


def system_script(vpn):
    i = randint(0, len(vpn[0]) - 1)
    command = 'sslocal -b 127.0.0.1 -l 1080 -s {} -p {} -k {} -m {}'.format(vpn[0][i], vpn[1][i].strip(), vpn[2][i].strip(), vpn[3][i][7:])
    print(command)
    os.system(command)


if __name__ == '__main__':
    print(__doc__)
    result = spider()
    system_script(result)
