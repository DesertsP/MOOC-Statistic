# coding=utf-8
# Created by deserts at 10/3/16
# 从百度百科获取慕课平台的信息
import requests
from bs4 import BeautifulSoup
import re
from proxy import SYS_PROXY, header

wiki_url = 'http://wapbaike.baidu.com/item/'
# google_url = 'https://www.google.com.sg/search'
key_words = [u'教育', u'课程', u'学习', u'课堂', u'培训', u'慕课']


def get_wiki(name):
    res = requests.get(wiki_url + name, headers = header)
    soup = BeautifulSoup(res.content, 'lxml')
    summarys = soup.select('.summary-content')
    if summarys:
        s = summarys[0].text
        for k in key_words:
            if k in s:
                s = s.strip()
                comments = re.findall(r'(\[\d+?\])', s)
                slist = [s.replace(c, '') for c in comments]
                if slist:
                    s = slist[-1]
                print s
                return s
    return '暂无该平台信息'
