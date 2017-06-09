# -*- coding: utf-8 -*-
from log import *
from utils import *
from redisclient import *

url_file_path = "<url file path>"
client = RedisClient()


def read_from_file():
    file_name = Utils.get_latest_file(url_file_path)
    logging.info("===>read urls from:%s" % file_name)
    with open(file_name) as f:
        for line in f:
            item = line.split('\t')
            author = item[0]
            title = item[1]
            digest = item[2]
            url = item[3].replace('\n', '').replace('\\', '')
            yield author, title, digest, url


def load():
    for author, title, digest, url in read_from_file():
        hashid = Utils.url_encode_md5(url)
        ret = client.set(hashid, url)
        if ret:
            logging.info("===>load %s to redis success" % url)
        else:
            logging.info("===>load %s to redis fail" % url)


if __name__ == '__main__':
    load()
