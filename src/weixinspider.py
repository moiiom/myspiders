# -*- coding: utf-8 -*-
import os
import errno
import codecs
import random
import requests
from log import *
from utils import *
from settings import *
from redisclient import *

url_file_path = "<root path>/weixin_url/"
data_file_path = "<root path>/weixin/{hashid}"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "mp.weixin.qq.com",
    "Upgrade-Insecure-Requests": 1,
    "User-Agent": random.choice(USER_AGENT_LIST)
}

session = requests.session()
conn = RedisClient()


class WeixinItem:
    id = ""
    author = ""
    title = ""
    digest = ""
    content = ""
    post_date = ""
    nick_name = ""
    url = ""


def read_from_file():
    file_name = Utils.get_latest_file(url_file_path)
    logging.info("read urls from:%s" % file_name)
    with open(file_name) as f:
        for line in f:
            item = line.split('\t')
            author = item[0]
            title = item[1]
            digest = item[2]
            url = item[3].replace('\n', '').replace('\\', '')
            yield author, title, digest, url


def get_start_urls():
    urls = []
    for author, title, digest, url in read_from_file():
        hashid = Utils.url_encode_md5(url)
        ifexists = conn.exists(hashid)
        if ifexists:
            logging.info("the url had crawled.%s" % hashid)
            continue

        urls.append({
            "id": hashid,
            "author": author.decode('utf-8'),
            "title": title.decode('utf-8'),
            "digest": digest.decode('utf-8'),
            "url": url.decode('utf-8')
        })
    return urls


def write_to_file(item):
    filename = data_file_path.format(hashid=item.id)
    content = item.id + "\t" + item.url + "\t" + item.title + "\t" + item.digest + "\t" + item.author + "\t" + item.nick_name + "\t" + item.post_date + "\t" + item.content
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(content)
    logging.info("write to file success:%s" % filename)


def page_crawl(profile):
    author = profile["author"]
    # title = urlObj["title"]
    digest = profile["digest"]
    url = profile["url"]
    try:
        body = Utils.request_get(session, url, headers)
        if body:
            title = body.xpath('//h2[@id="activity-name"]/text()').extract_first() or "null"
            post_date = body.xpath('//em[@id="post-date"]/text()').extract_first() or "null"
            nick_name = body.xpath('//a[@id="post-user"]/text()').extract_first() or "null"
            content = body.xpath('//div[@id="js_content"]').extract_first() or "null"

            item = WeixinItem()
            item.id = profile["id"]
            item.post_date = post_date
            item.nick_name = nick_name
            item.url = url
            item.author = author or "null"
            item.title = Utils.formate_html(title)
            item.digest = Utils.formate_html(digest)
            item.content = Utils.formate_html(content)
            write_to_file(item)
    except Exception as ex:
        logging.error("exception message:%s" % ex)
    finally:
        logging.info("crawl url:%s" % url)


def start():
    logging.info("start weixin spider...")
    urls = get_start_urls()
    for profile in urls:
        page_crawl(profile)
    logging.info("weixin spider finish.")


if __name__ == '__main__':
    start()
