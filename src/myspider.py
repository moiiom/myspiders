# -*- coding: utf-8 -*-
import re
import os
import time
import errno
import codecs
import random
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from settings import *
from log import *
from proxy import *

domain = "https://www.zhihu.com"


class ZhihuItem:
    url = ""
    question_id = ""
    question_title = ""
    question_detail = ""
    answers = ""


def topic_parse(url):
    topic_links = []
    try:
        body = driver_source(url)
        topics = body.xpath('//ul[@class="list topics"]/li/a/@href').extract()
        logging.info("topics:%s" % topics)
        # for cookie in driver.get_cookies():
        #     print "%s -> %s" % (cookie['name'], cookie['value'])

        if not topics or not isinstance(topics, list):
            sys.exit(0)
        for topic in topics:
            topic_links.append(domain + topic + "/top-answers")
    except Exception as ex:
        logging.info("except url:%s" % url)
        logging.error(ex.message)
        raise ex
    return topic_links


def top_answer_parse(url):
    try:
        body = driver_source(url)
        total_str = body.xpath('//div[@class="zm-invite-pager"]/span[6]/a/text()').extract()[0]
        total = int(total_str)
        page_links = get_page_urls(url, total)
        logging.info("page_links:%s" % page_links)
    except Exception as ex:
        logging.info("except url:%s" % url)
        logging.error(ex.message)
        raise ex
    return page_links


def top_answer_list_parse(url):
    links = []
    try:
        body = driver_source(url)
        question_links = body.xpath('//div[@id="zh-topic-top-page-list"]/div/link/@href').extract()
        assert question_links and isinstance(question_links, list)
        for link in question_links:
            links.append(domain + link)
    except Exception as ex:
        logging.info("except url:%s" % url)
        logging.error(ex.message)
        raise ex
    return links


def answer_parse(url):
    try:
        body = driver_source(url)
        question_title = body.xpath(
            '//div[@class="QuestionHeader-main"]/h1[@class="QuestionHeader-title"]/text()').extract_first()
        question_detail = body.xpath('//div[@class="QuestionHeader-detail"]//text()').extract()
        answer_contexts = body.xpath('//div[@class="RichContent-inner"]').extract()
    except Exception as ex:
        logging.info("except url:%s" % url)
        logging.error(ex.message)
        raise ex

    # print "url======>", url
    logging.info("url======>%s" % url)
    logging.info("title======>%s" % question_title)
    # print "title detail======>", ",".join(question_detail)
    # print "question_id======>", url.split("/")[-1]
    # print "answers======>", ",".join(answer_contexts)

    item = ZhihuItem()
    item.url = url
    item.question_id = url.split("/")[-1]
    item.question_title = remove_html_tag(question_title or "")
    item.question_detail = ",".join(question_detail) if isinstance(question_detail, list) else ""
    item.answers = ",".join(answer_contexts) if isinstance(answer_contexts, list) else ""
    write_to_file(item)


def get_page_urls(base_url, total):
    page_urls = []
    for i in range(total):
        page_urls.append(base_url + "?page=" + str(i + 1))
    return page_urls


def driver_source(url):
    driver.get(url)
    time.sleep(2)
    content = driver.page_source.encode('utf-8')
    time.sleep(2)
    body = Selector(text=content)
    return body


def remove_html_tag(content):
    dr = re.compile(r'<[^>]+>', re.S)
    removed_tag_text = dr.sub('', content)
    return removed_tag_text


def write_to_file(item):
    assert isinstance(item, ZhihuItem)

    filename = data_file_path.format(question_id=item.question_id)
    logging.info("write to file==>%s" % filename)
    content = item.url + "\t" + item.question_id + "\t" + item.question_title + "\t" + item.question_detail + "\t" + item.answers
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(content)


def login():
    # url = 'http://www.zhihu.com/#signin'
    login_url = "https://www.zhihu.com/login/email?email=email@email.cn&password=xxxxx&remember_me=true&_xsrf=b59c15988d71afdba3fbcc6990eb36a6&captcha=mmtx"
    driver.get(login_url)
    time.sleep(2)
    for cookie in driver.get_cookies():
        print "%s -> %s" % (cookie['name'], cookie['value'])

    js = 'document.querySelector(\'div[data-za-module="SignUpForm"]\').style.display="none";document.querySelector(\'div[data-za-module="SignInForm"]\').style.display="block";'
    driver.execute_script(js)
    # driver.find_element_by_name("account").send_keys(user_config["email"])
    driver.find_element_by_xpath('//div[@class="account input-wrapper"]/input').send_keys(user_config["email"])
    driver.find_element_by_xpath('//div[@class="verification input-wrapper"]/input').send_keys(user_config["password"])
    time.sleep(5)
    # driver.find_element_by_xpath('//div[@data-za-module="SignInForm"]/form/div[1]/button').click()
    driver.find_element_by_xpath('//div[@data-za-module="SignInForm"]//button[@class="sign-button submit"]').click()

    print "------------------"
    flag = 0
    for cookie in driver.get_cookies():
        print "%s -> %s" % (cookie['name'], cookie['value'])
        if cookie["name"] == "z_c0":
            flag += 1
    if flag > 0:
        print "login success!"
    else:
        print "login fail!"
        # cookies_list = driver.get_cookies()
        # driver.delete_all_cookies()
        # for cookie in cookies_list:
        #     driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry')})
        # driver.add_cookie({'name': 'z_c0', 'value': 'Mi4wQUFCQXZlWWxBQUFBRUlLaDBkcGNDeGNBQUFCaEFsVk5FOGxZV1FBSk9nb05ZLUNyWW43TGlnV0l6Qjd1SVk4WkZ3|1496398868|69f8baa7b13b3c29fbc3cefc9035b0ffd93f0edf'})


# def add_proxy():
#     proxy = driver.Proxy()
#     proxy.proxy_type = ProxyType.MANUAL
#     proxy.http_proxy = '1.9.171.51:800'
#     # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
#     proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
#     browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)

def start():
    # base_url = "https://www.zhihu.com/search?type=topic&q={topic}"
    # for topic in topic_list:
    #     start_url = base_url.format(topic=topic)
    #     print start_url
    start_url = "https://www.zhihu.com/search?type=topic&q=大数据"
    links = topic_parse(start_url)
    for i in links:
        i_links = top_answer_parse(i)
        for j in i_links:
            j_links = top_answer_list_parse(j)
            for k in j_links:
                answer_parse(k)


if __name__ == '__main__':
    # print "login into zhihu..."
    # login()

    proxy_list = fetch_all()
    assert len(proxy_list) > 0
    proxy_ip_port = random.choice(proxy_list)
    service_args = [
        '--proxy={0}'.format(proxy_ip_port),
        '--proxy-type=http',
    ]
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch, br',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
               'Connection': 'keep-alive',
               'Referer': 'http://www.baidu.com/'
               }
    desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
    for key, value in headers.iteritems():
        desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value
    desired_capabilities['phantomjs.page.customHeaders.User-Agent'] = random.choice(USER_AGENT_LIST)
    driver = webdriver.PhantomJS('/usr/bin/phantomjs', service_args=service_args,
                                 desired_capabilities=desired_capabilities)
    print "start src..."
    start()
