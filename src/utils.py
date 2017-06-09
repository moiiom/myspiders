import re
import os
import time
import errno
import codecs
from scrapy.selector import Selector
from log import *
from settings import *

__all__ = ["Utils"]


class Utils:
    @staticmethod
    def get_page_urls(base_url, total):
        page_urls = []
        for i in range(total):
            page_urls.append(base_url + "?page=" + str(i + 1))
        return page_urls

    @staticmethod
    def remove_html_tag(html):
        dr = re.compile(r'<[^>]+>', re.S)
        removed_tag_text = dr.sub('', html)
        return removed_tag_text

    @staticmethod
    def formate_html(html):
        html = re.sub(' +', ' ', html)
        html = html.replace('\r', '').replace('\n', '').replace('\t', '')
        final_html = html.strip()
        return final_html

    @staticmethod
    def write_to_file(data_file_path, item):
        # assert isinstance(item, ZhihuItem)

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

    @staticmethod
    def request_get(session, url, headers):
        # assert isinstance(session, requests.session())
        res = session.get(url, headers=headers)
        if res.status_code == 200:
            time.sleep(REQUEST_DELY)
            body_html = Selector(text=res.content)
            return body_html
        else:
            logger.error("bad response status code:%s" % res.status_code)
            return None

    @staticmethod
    def url_encode_md5(url):
        import hashlib
        m = hashlib.md5()
        m.update(url)
        return m.hexdigest()

    @staticmethod
    def get_latest_file(base_dir):
        file_list = os.listdir(base_dir)
        file_list.sort(key=lambda fn: os.path.getmtime(base_dir + fn) if not os.path.isdir(base_dir + fn) else 0)
        file_list.reverse()
        if len(file_list) > 0:
            latest_file_name = base_dir + file_list[0]
            return latest_file_name
        else:
            return None
