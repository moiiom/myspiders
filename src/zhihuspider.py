# -*- coding: utf-8 -*-
import re
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from log import *
from utils import *
from settings import *


class ZhihuItem:
    url = ""
    question_id = ""
    question_title = ""
    question_detail = ""
    answers = ""


def login():
    url = 'https://www.zhihu.com'
    loginURL = 'https://www.zhihu.com/login/email'
    data = {
        'email': user_config['email'],
        'password': user_config['password'],
        'rememberme': "true",
    }
    global s
    s = requests.session()
    global xsrf
    if os.path.exists('cookiefile'):
        with open('cookiefile') as f:
            cookie = json.load(f)
        s.cookies.update(cookie)

        # ------------------------------------
        # 建立一个zhihu.html文件,用于验证是否登陆成功
        # req1 = s.get(url, headers=headers)
        # soup = BeautifulSoup(req1.text, "html.parser")
        # xsrf = soup.find('input', {'name': '_xsrf', 'type': 'hidden'}).get('value')
        # with open('zhihu.html', 'w') as f:
        #     f.write(req1.content)
    else:
        req = s.get(url, headers=headers)
        print req

        soup = BeautifulSoup(req.text, "html.parser")
        xsrf = soup.find('input', {'name': '_xsrf', 'type': 'hidden'}).get('value')

        data['_xsrf'] = xsrf

        t = str(int(time.time() * 1000))
        captchaURL = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        print captchaURL

        with open('zhihucaptcha.gif', 'wb') as f:
            captchaREQ = s.get(captchaURL, headers=headers)
            f.write(captchaREQ.content)
        loginCaptcha = raw_input('input captcha:\n').strip()
        data['captcha'] = loginCaptcha
        print data
        loginREQ = s.post(loginURL, headers=headers, data=data)
        print('服务器端返回响应码：', loginREQ.status_code)
        print(loginREQ.json())
        if not loginREQ.json()['r']:
            print s.cookies.get_dict()
            with open('cookiefile', 'wb') as f:
                json.dump(s.cookies.get_dict(), f)
            print 'login success'
        else:
            print 'login fail'


def get_userInfo(userID):
    user_url = 'https://www.zhihu.com/people/' + userID
    response = s.get(user_url, headers=headers)
    # print response
    soup = BeautifulSoup(response.content, 'lxml')
    name = soup.find_all('span', {'class': 'name'})[1].string
    # print 'name: %s' % name
    ID = userID
    # print 'ID: %s' % ID
    location = soup.find('span', {'class': 'location item'})
    if location is None:
        location = 'None'
    else:
        location = location.string
    # print 'location: %s' % location
    business = soup.find('span', {'class': 'business item'})
    if business is None:
        business = 'None'
    else:
        business = business.string
    # print 'business: %s' % business
    gender = soup.find('input', {'checked': 'checked'})
    if gender is None:
        gender = 'None'
    else:
        gender = gender['class'][0]
    # print 'gender: %s' % gender
    employment = soup.find('span', {'class': 'employment item'})
    if employment is None:
        employment = 'None'
    else:
        employment = employment.string
    # print 'employment: %s' % employment
    position = soup.find('span', {'class': 'position item'})
    if position is None:
        position = 'None'
    else:
        position = position.string
    # print 'position: %s' % position
    education = soup.find('span', {'class': 'education item'})
    if education is None:
        education = 'None'
    else:
        education = education.string
    # print 'education: %s' % education
    major = soup.find('span', {'class': 'education-extra item'})
    if major is None:
        major = 'None'
    else:
        major = major.string
    # print 'major: %s' % major

    agree = int(soup.find('span', {'class': 'zm-profile-header-user-agree'}).strong.string)
    # print 'agree: %d' % agree
    thanks = int(soup.find('span', {'class': 'zm-profile-header-user-thanks'}).strong.string)
    # print 'thanks: %d' % thanks
    infolist = soup.find_all('a', {'class': 'item'})
    asks = int(infolist[1].span.string)
    # print 'asks: %d' % asks
    answers = int(infolist[2].span.string)
    # print 'answers: %d' % answers
    posts = int(infolist[3].span.string)
    # print 'posts: %d' % posts
    collections = int(infolist[4].span.string)
    # print 'collections: %d' % collections
    logs = int(infolist[5].span.string)
    # print 'logs: %d' % logs
    followees = int(infolist[len(infolist) - 2].strong.string)
    # print 'followees: %d' % followees
    followers = int(infolist[len(infolist) - 1].strong.string)
    # print 'followers: %d' % followers
    scantime = int(soup.find_all('span', {'class': 'zg-gray-normal'})[
                       len(soup.find_all('span', {'class': 'zg-gray-normal'})) - 1].strong.string)
    # print 'scantime: %d' % scantime

    info = (name, ID, location, business, gender, employment, position,
            education, major, agree, thanks, asks, answers, posts,
            collections, logs, followees, followers, scantime)
    return info


Zhihu = 'http://www.zhihu.com'


def get_voters(ans_id):
    # 直接输入问题id(这个id在点击“等人赞同”时可以通过监听网络得到)，关注者保存在以问题id命名的.txt文件中
    login()
    file_name = str(ans_id) + '.txt'
    f = open(file_name, 'w')
    source_url = Zhihu + '/answer/' + str(ans_id) + '/voters_profile'
    source = s.get(source_url, headers=header_info)
    print source
    content = source.content
    print content  # json语句
    data = json.loads(content)  # 包含总赞数、一组点赞者的信息、指向下一组点赞者的资源等的数据
    # 打印总赞数
    txt1 = '总赞数'
    print txt1.decode('utf-8')
    total = data['paging']['total']  # 总赞数
    print data['paging']['total']  # 总赞数
    # 通过分析，每一组资源包含10个点赞者的信息（当然，最后一组可能少于10个），所以需要循环遍历
    nextsource_url = source_url  # 从第0组点赞者开始解析
    num = 0
    while nextsource_url != Zhihu:
        try:
            nextsource = s.get(nextsource_url, headers=header_info)
        except:
            time.sleep(2)
            nextsource = s.get(nextsource_url, headers=header_info)
        # 解析出点赞者的信息
        nextcontent = nextsource.content
        nextdata = json.loads(nextcontent)
        # 打印每个点赞者的信息
        # txt2 = '打印每个点赞者的信息'
        # print txt2.decode('utf-8')
        # 提取每个点赞者的基本信息
        for each in nextdata['payload']:
            num += 1
            print num
            try:
                soup = BeautifulSoup(each, 'lxml')
                tag = soup.a
                title = tag['title']  # 点赞者的用户名
                href = 'http://www.zhihu.com' + str(tag['href'])  # 点赞者的地址
                # 获取点赞者的数据
                list = soup.find_all('li')
                votes = list[0].string  # 点赞者获取的赞同
                tks = list[1].string  # 点赞者获取的感谢
                ques = list[2].string  # 点赞者提出的问题数量
                ans = list[3].string  # 点赞者回答的问题数量
                # 打印点赞者信息
                string = title + '  ' + href + '  ' + votes + tks + ques + ans
                f.write(string + '\n')
                print string
            except:
                txt3 = '有点赞者的信息缺失'
                f.write(txt3.decode('utf-8') + '\n')
                print txt3.decode('utf-8')
                continue
        # 解析出指向下一组点赞者的资源
        nextsource_url = Zhihu + nextdata['paging']['next']
    f.close()


def get_followees(username):
    # 直接输入用户名，关注者保存在以用户名命名的.txt文件中
    followers_url = 'http://www.zhihu.com/people/' + username + '/followees'
    file_name = username + '.txt'
    f = open(file_name, 'w')
    data = s.get(followers_url, headers=headers)
    print data  # 访问服务器成功，返回<responce 200>
    content = data.content  # 提取出html信息
    soup = BeautifulSoup(content, "lxml")  # 对html信息进行解析
    # 获取关注者数量
    totalsen = soup.select('span[class*="zm-profile-section-name"]')
    total = int(str(totalsen[0]).split(' ')[4])  # 总的关注者数量
    txt1 = '总的关注者人数：'
    print txt1.decode('utf-8')
    print total
    follist = soup.select('div[class*="zm-profile-card"]')  # 记录有关注者信息的list
    num = 0  # 用来在下面显示正在查询第多少个关注者
    for follower in follist:
        tag = follower.a
        title = tag['title']  # 用户名
        href = 'http://www.zhihu.com' + str(tag['href'])  # 用户地址
        # 获取用户数据
        num += 1
        print '%d   %f' % (num, num / float(total))
        # Alist = follower.find_all(has_attrs)
        Alist = follower.find_all('a', {'target': '_blank'})
        votes = Alist[0].string  # 点赞者获取的赞同
        tks = Alist[1].string  # 点赞者获取的感谢
        ques = Alist[2].string  # 点赞者提出的问题数量
        ans = Alist[3].string  # 点赞者回答的问题数量
        # 打印关注者信息
        string = title + '  ' + href + '  ' + votes + tks + ques + ans
        try:
            print string.decode('utf-8')
        except:
            print string.encode('gbk', 'ignore')
        f.write(string + '\n')

    # 循环次数
    n = total / 20 - 1 if total / 20.0 - total / 20 == 0 else total / 20
    for i in range(1, n + 1, 1):
        # if num%30 == 0:
        #   time.sleep(1)
        # if num%50 == 0:
        #   time.sleep(2)
        raw_hash_id = re.findall('hash_id(.*)', content)
        hash_id = raw_hash_id[0][14:46]
        _xsrf = xsrf
        offset = 20 * i
        params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
        payload = {"method": "next", "params": params, "_xsrf": _xsrf}
        click_url = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
        data = s.post(click_url, data=payload, headers=headers)
        # print data
        source = json.loads(data.content)
        for follower in source['msg']:
            soup1 = BeautifulSoup(follower, 'lxml')
            tag = soup1.a
            title = tag['title']  # 用户名
            href = 'http://www.zhihu.com' + str(tag['href'])  # 用户地址
            # 获取用户数据
            num += 1
            print '%d   %f' % (num, num / float(total))
            # Alist = soup1.find_all(has_attrs)
            Alist = soup1.find_all('a', {'target': '_blank'})
            votes = Alist[0].string  # 点赞者获取的赞同
            tks = Alist[1].string  # 点赞者获取的感谢
            ques = Alist[2].string  # 点赞者提出的问题数量
            ans = Alist[3].string  # 点赞者回答的问题数量
            # 打印关注者信息
            string = title + '  ' + href + '  ' + votes + tks + ques + ans
            try:
                print string.decode('utf-8')
            except:
                print string.encode('gbk', 'ignore')
            f.write(string + '\n')
    f.close()


def get_avatar(userId):
    url = 'https://www.zhihu.com/people/' + userId
    response = s.get(url, headers=headers)
    response = response.content
    soup = BeautifulSoup(response, 'lxml')
    name = soup.find_all('span', {'class': 'name'})[1].string
    # print name
    temp = soup.find('img', {'alt': name})
    avatar_url = temp['src'][0:-6] + temp['src'][-4:]
    filename = 'pics/' + userId + temp['src'][-4:]
    f = open(filename, 'wb')
    f.write(requests.get(avatar_url).content)
    f.close()


def get_answer(questionID):
    url = 'http://www.zhihu.com/question/' + str(questionID)
    data = s.get(url, headers=headers)
    soup = BeautifulSoup(data.content, 'lxml')
    # print str(soup).encode('gbk', 'ignore')
    title = soup.title.string.split('\n')[2]  # 问题题目
    path = title
    if not os.path.isdir(path):
        os.mkdir(path)
    description = soup.find('div', {'class': 'zm-editable-content'}).strings  # 问题描述，可能多行
    file_name = path + '/description.txt'
    fw = open(file_name, 'w')
    for each in description:
        each = each + '\n'
        fw.write(each)
        # description = soup.find('div', {'class': 'zm-editable-content'}).get_text() # 问题描述
        # 调用.string属性返回None（可能是因为有换行符在内的缘故）,调用get_text()方法得到了文本，但换行丢了
    answer_num = int(soup.find('h3', {'id': 'zh-question-answer-num'}).string.split(' ')[0])  # 答案数量
    num = 1
    index = soup.find_all('div', {'tabindex': '-1'})
    for i in range(len(index)):
        print ('Scrapying the ' + str(num) + 'th answer......').encode('gbk', 'ignore')
        # print ('正在抓取第' + str(num) + '个答案......').encode('gbk', 'ignore')
        try:
            a = index[i].find('a', {'class': 'author-link'})
            title = str(num) + '__' + a.string
            href = 'http://www.zhihu.com' + a['href']
        except:
            title = str(num) + '__匿名用户'
        answer_file_name = path + '/' + title + '__.txt'
        fr = open(answer_file_name, 'w')
        try:
            answer_content = index[i].find('div', {'class': 'zm-editable-content clearfix'}).strings
        except:
            answer_content = ['作者修改内容通过后，回答会重新显示。如果一周内未得到有效修改，回答会自动折叠。']
        for content in answer_content:
            fr.write(content + '\n')
        num += 1

    _xsrf = xsrf
    url_token = re.findall('url_token(.*)', data.content)[0][8:16]
    # 循环次数
    n = answer_num / 10 - 1 if answer_num / 10.0 - answer_num / 10 == 0 else answer_num / 10
    for i in range(1, n + 1, 1):
        # _xsrf = xsrf
        # url_token = re.findall('url_token(.*)', data.content)[0][8:16]
        offset = 10 * i
        params = json.dumps({"url_token": url_token, "pagesize": 10, "offset": offset})
        payload = {"method": "next", "params": params, "_xsrf": _xsrf}
        click_url = 'https://www.zhihu.com/node/QuestionAnswerListV2'
        data = s.post(click_url, data=payload, headers=headers)
        data = json.loads(data.content)
        for answer in data['msg']:
            print ('Scrapying the ' + str(num) + 'th answer......').encode('gbk', 'ignore')
            # print ('正在抓取第' + str(num) + '个答案......').encode('gbk', 'ignore')
            soup1 = BeautifulSoup(answer, 'lxml')
            try:
                a = soup1.find('a', {'class': 'author-link'})
                title = str(num) + '__' + a.string
                href = 'http://www.zhihu.com' + a['href']
            except:
                title = str(num) + '__匿名用户'
            answer_file_name = path + '/' + title + '__.txt'
            fr = open(answer_file_name, 'w')
            try:
                answer_content = soup1.find('div', {'class': 'zm-editable-content clearfix'}).strings
            except:
                answer_content = ['作者修改内容通过后，回答会重新显示。如果一周内未得到有效修改，回答会自动折叠。']
            for content in answer_content:
                fr.write(content + '\n')
            num += 1


def topic_parse(url):
    topic_links = []
    try:
        body = Utils.request_get(s, url, headers)
        if body:
            topics = body.xpath('//ul[@class="list topics"]/li/a/@href').extract()
            if not topics or not isinstance(topics, list):
                sys.exit(0)
            for topic in topics:
                topic_links.append(domain + topic + "/top-answers")
    except Exception as ex:
        logging.info("exception url:%s" % url)
        logging.error("exception message:%s" % ex.message)
    logging.info("topic list url:%s" % topic_links)
    return topic_links
    # print topic_links


def top_answer_parse(url):
    page_links = []
    try:
        body = Utils.request_get(s, url, headers)
        if body:
            total_str = body.xpath('//div[@class="zm-invite-pager"]/span[6]/a/text()').extract()[0]
            total = int(total_str)
            page_links = Utils.get_page_urls(url, total)
            logging.info("page_links:%s" % page_links)
    except Exception as ex:
        logging.info("exception url:%s" % url)
        logging.error("exception message:%s" % ex.message)
    logging.info("page url:%s" % page_links)
    return page_links


def top_answer_list_parse(url):
    links = []
    try:
        body = Utils.request_get(s, url, headers)
        if body:
            question_links = body.xpath('//div[@id="zh-topic-top-page-list"]/div/link/@href').extract()
            assert question_links and isinstance(question_links, list)
            for link in question_links:
                links.append(domain + link)
    except Exception as ex:
        logging.info("exception url:%s" % url)
        logging.error("exception message:%s" % ex.message)
    logging.info("question anwser url:%s" % links)
    return links


def answer_parse(url):
    try:
        body = Utils.request_get(s, url, headers)
        if body:
            question_title = body.xpath(
                '//div[@class="QuestionHeader-main"]/h1[@class="QuestionHeader-title"]/text()').extract_first()
            question_detail = body.xpath('//div[@class="QuestionHeader-detail"]//text()').extract()
            answer_contexts = body.xpath('//div[@class="RichContent-inner"]').extract()

            logging.info("url======>%s" % url)
            logging.info("title======>%s" % question_title)
            # print "title detail======>", ",".join(question_detail)
            # print "question_id======>", url.split("/")[-1]
            # print "answers======>", ",".join(answer_contexts)

            item = ZhihuItem()
            item.url = url
            item.question_id = url.split("/")[-1]
            item.question_title = Utils.remove_html_tag(question_title or "")
            item.question_detail = ",".join(question_detail) if isinstance(question_detail, list) else ""
            item.answers = ",".join(answer_contexts) if isinstance(answer_contexts, list) else ""
            Utils.write_to_file(data_file_path, item)
    except Exception as ex:
        logging.info("exception url:%s" % url)
        logging.error("exception message:%s" % ex.message)


def start():
    logger.info("start crawl from zhihu...")
    base_url = "https://www.zhihu.com/search?type=topic&q={topic}"
    for topic in topic_list:
        start_url = base_url.format(topic=topic)
        logger.info("topic url:%s" % start_url)
        links = topic_parse(start_url)
        for i in links:
            i_links = top_answer_parse(i)
            for j in i_links:
                j_links = top_answer_list_parse(j)
                for k in j_links:
                    answer_parse(k)
    logger.info("crawl from zhihu finish.")


if __name__ == '__main__':
    login()
    start()

    # start_url = "https://www.zhihu.com/search?type=topic&q=机器学习"
    # topic_parse(start_url)

    # start_url = "https://www.zhihu.com/topic/19559450/top-answers"
    # top_answer_parse(start_url)

    # start_url = "https://www.zhihu.com/topic/19559450/top-answers?page=1"
    # top_answer_list_parse(start_url)
    #
    # start_url = "https://www.zhihu.com/question/49985162/answer/152099091"
    # answer_parse(start_url)
