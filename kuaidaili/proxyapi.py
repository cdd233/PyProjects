# coding: utf8

from flask import Flask
from pymongo import MongoClient
from random import randint
from config import *

app = Flask(__name__)


@app.route('/')
def index():
    return '<h2>Welcome To Proxy Api !</h2>'


@app.route('/api')
def proxy_api():
    try:
        cli = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT, connect=False)
        db = cli[MONGODB_NAME]
        col = db[MONGODB_COLLECTION]
        coursor = col.find()
        count = coursor.count()
        if count > 1:
            proxy = coursor.skip(randint(0, count - 1))
            return proxy.next()['proxy']
        elif count == 1:
            proxy = coursor.next()
            return proxy['proxy']
        else:
            return 'None', 400
    except Exception as e:
        print('Exception: ', e)
        return e, 400


if __name__ == '__main__':
    app.run()
