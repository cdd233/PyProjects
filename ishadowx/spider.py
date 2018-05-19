# coding: utf8

import requests as rq
from random import randint
from requests.exceptions import RequestException
from lxml import etree
import os

MAX_RETRY = 10
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36',
}


def spider(cnt=0):
    if cnt >= MAX_RETRY:
        print('The number of connections has reached a maximum, Exit now!')
        exit()
    else:
        print('Preparing to obtain vpn:  {} / {}'.format(cnt + 1, MAX_RETRY))

    try:
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
        return spider(cnt + 1)


def system_script(vpn):
    i = randint(0, len(vpn[0])-1)
    command = 'sslocal -b 127.0.0.1 -l 1080 -s {} -p {} -k {} -m {}'.format(vpn[0][i], vpn[1][i].strip(), vpn[2][i].strip(), vpn[3][i][7:])
    print(command)
    os.system(command)


if __name__ == '__main__':
    result = spider()
    print('vpn_script is running !')
    system_script(result)
    exit()
