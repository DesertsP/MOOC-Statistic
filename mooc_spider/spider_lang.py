# coding=utf-8
# Created by deserts at 10/2/16
# 处理果壳慕课的语言ID

import requests
from bs4 import BeautifulSoup
from utilities import headers


def get_lang_name():
    url = 'http://mooc.guokr.com/course/'
    langIdList = [1, 2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22]
    langDict = {}
    for lang_id in langIdList:
        params = {'lang_id': lang_id, 'order': 'hot'}
        res = requests.get(url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        lang_tag = soup.select('li .active')
        lang = lang_tag[0].text.strip()
        langDict[str(lang_id)] = lang
    if len(langDict) == len(langIdList):
        return langDict
    else:
        print('get language name failed, try again!')
        return get_lang_name()


if __name__ == '__main__':
    print get_lang_name()
