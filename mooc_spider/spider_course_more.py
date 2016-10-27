# coding=utf-8
# Created by deserts at 9/25/16
# 初步获取课程的其他信息（教师、标签、etc.），爬取所有课程页面进行初步处理

import json
import requests
import urllib
from bs4 import BeautifulSoup
import re
import datetime
import threading
import multiprocessing
import Queue
from config import db_config_raw as db_config, timedelta, threads, proxyThreads
from utilities import *
from proxy import ProxyPool

courseHome = 'http://mooc.guokr.com/{}/{}'


def get_id_list(sort):
    conn = connect_db(db_config)
    cur = conn.cursor()
    script = '''SELECT DATA FROM COURSES_RAW
                WHERE (MORE IS NULL OR TIMESTAMPDIFF(HOUR,TIMESTAMP,CURRENT_TIMESTAMP()) > %s) AND SORT=%s'''
    hourDiff = timedelta['hours'] + 24 * timedelta['days']
    cur.execute(script, (hourDiff, sort))
    dataList = cur.fetchall()
    idList = [json.loads(data[0])['id'] for data in dataList]
    return idList


def crawl(courseID, sort, proxies=None):
    '''
    crawl the course info of the specific id.
    '''
    global courseHome
    url = courseHome.format(SORT_DICT[str(sort)], courseID)
    soup = None
    try:
        res = requests.get(url, headers=headers, proxies=proxies, timeout=4)
        soup = BeautifulSoup(res.text, 'lxml')
        # 难度
        tag_diffi = soup.select('.course-score-difficulty b')[0]
        difficulty = convert_diffi(tag_diffi.text)
        # 链接
        tag_link = soup.select('.course-go')[0]
        link = convert_link(tag_link["href"])
        # 讲师
        if sort == 1:
            tag_teacher = soup.select('.course-info li')[3]
        else:
            tag_teacher = soup.select('.course-info li')[1]
        teacher = tag_teacher.b.text
        # 评论标签&计数
        tag_comment_tags = soup.select('.comment-tag li')
        comment_tags = [(tag.span.text, tag.b.text) for tag in tag_comment_tags]
        # (tag_name, tag_count)
        result = {
            'id': courseID,
            'teacher': teacher,
            'comment_tags': comment_tags,
            'link': link,
            'difficulty': difficulty
        }
        dump_to_db(courseID, sort, json.dumps(result))
        msg = "id:" + str(courseID) + " teacher: " + teacher + " difficulty: " + str(difficulty)
    except IndexError:
        # 503|404|500 etc.
        code = soup.title.text[:3]
        msg = 'failed! course:{}, status code:{}.'
        msg = msg.format(courseID, code)
    except requests.exceptions.ConnectionError:
        msg = 'network / proxy error: ConnectionError'
    except requests.exceptions.ReadTimeout:
        msg = 'network / proxy error: ReadTimeout'
    except requests.exceptions.TooManyRedirects:
        msg = 'proxy error: TooManyRedirects'
    return msg


def convert_diffi(diffi):
    dictionary = {
        u'暂无': 0,
        u'简单': 1,
        u'一般': 2,
        u'困难': 3
    }
    return dictionary[diffi]


def convert_link(url):
    '''
    convert the guokr's url to the real url
    :param url: original url
    :return: real url
    '''
    links = re.findall('PARM1=(.*)', url)
    if links:
        link = links[0]
        link = urllib.unquote(link)
        return link
    return url


def dump_to_db(courseID, sort, data):
    conn = connect_db(db_config)
    cur = conn.cursor()
    script = '''UPDATE COURSES_RAW
                SET MORE=%s, TIMESTAMP=CURRENT_TIMESTAMP
                WHERE COURSE_ID=%s AND SORT=%s;'''
    cur.execute(script, (data, courseID, sort))
    conn.commit()
    cur.close()
    conn.close()


def del_row(courseID, sort):
    conn = connect_db(db_config)
    cur = conn.cursor()
    script = '''DELETE FROM COURSES_RAW WHERE COURSE_ID=%s AND SORT=%s;'''
    cur.execute(script, (courseID, sort))
    conn.commit()
    cur.close()
    conn.close()


class SpiderThread(threading.Thread):
    lock = multiprocessing.Lock()

    def __init__(self, taskQueue):
        super(SpiderThread, self).__init__()
        self.queue = taskQueue

    def run(self):
        while True:
            courseID, sort, proxy = self.queue.get()
            msg = crawl(courseID, sort, proxy)
            self.queue.task_done()
            self.lock.acquire()
            print(multiprocessing.current_process().name + ': ' + msg)
            self.lock.release()


def start_spider(sort, numThreads, numProxyThreads):
    pname = multiprocessing.current_process().name
    # task queue
    taskQueue = Queue.Queue()

    [SpiderThread(taskQueue).start() for _ in range(numThreads)]
    print('{}: {} threads created.'.format(pname, threads))

    # add tasks (producers)
    while True:
        idList = get_id_list(sort)
        num = len(idList)
        if num == 0:
            break
        print('{}: {} rows need to update.'.format(pname, num))
        genProxy = ProxyPool(numProxyThreads).gen_proxy()
        [taskQueue.put((i, sort, genProxy.next())) for i in idList]
        print('{}: {} tasks added!'.format(pname, num))
        # wait
        taskQueue.join()


def run():
    print(str(datetime.datetime.now())[:-7] + '  Start.' )
    global threads, proxyThreads
    p1 = multiprocessing.Process(target=start_spider, args=(1, threads, proxyThreads))
    p2 = multiprocessing.Process(target=start_spider, args=(2, threads, proxyThreads))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(str(datetime.datetime.now())[:-7] + '  Done!')


if __name__ == '__main__':
    run()