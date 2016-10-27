# coding=utf-8
# Created by Deserts Pan at 9/25/16
# 初步获取课程列表以及基本信息
import datetime
import json
from urllib import urlencode

import requests
from config import db_config_raw as db_config, timedelta
from utilities import *

API = 'http://mooc.guokr.com/apis/academy/{}_list.json?'
timedelta = datetime.timedelta(days=timedelta['days'], hours=timedelta['hours'])
step = 3000


class CourseListSpider():
    def __init__(self, sort=1):
        """
        :param sort: 1 or 2 ('course' or 'career')
        """
        self.apiUrl = API.format(SORT_DICT[str(sort)])
        self.sort = sort
        self.total = self.get_course_total()
        self.expireTime = timedelta
        self.conn = connect_db(db_config)
        self.cur = self.conn.cursor()

    def start(self):
        self.get_all_courses(step)

    def get_course_total(self):
        """
        Get the total number of courses.
        :return: the number or None if there's something wrong.
        """
        paras = {"order": "grading",
                 "retrieve_type": "by_params",
                 "limit": 1,
                 "offset": 0
                 }
        url = self.apiUrl + urlencode(paras)
        try:
            strData = requests.get(url).text
        except:
            raise Exception("Check your network state!")
        jsonData = json.loads(strData)
        if jsonData['ok']:
            total = int(jsonData['total'])
            return total
        else:
            return 0

    def get_course_list(self, offset, limit=3000):
        """
        get course data from url.
        :param offset: the start number.
        :param limit: the limit number, 1~5000
        :return: a str data of the courses in json format
        """
        assert type(offset) is int and type(limit) is int
        assert offset >= 0  and limit in range(1, 5000)
        paras = {"order": "grading",
                 "retrieve_type": "by_params",
                 "limit": limit,
                 "offset": offset
                 }
        url = self.apiUrl + urlencode(paras)
        data = requests.get(url).text
        jsonData = json.loads(data)
        if jsonData['ok']:
            courses = jsonData['result']['courses']
            return courses
        else:
            return None

    def get_all_courses(self, step=3000):
        for offset in xrange(0, self.total, step):
            courses = self.get_course_list(offset, step)
            print(str(len(courses)) + ' crawled.')
            for course in courses:
                courseStr = json.dumps(course)
                courseID = course['id']
                self.dump_to_db(courseID, courseStr)
            print('all data stored into database.')

    @staticmethod
    def is_expired(timestamp):
        """
        check if datas in database is expired
        """
        return datetime.datetime.now() - timestamp > timedelta

    def dump_to_db(self, courseID, data):
        script = '''SELECT ID, TIMESTAMP
                    FROM COURSES_RAW
                    WHERE COURSE_ID=%s AND SORT=%s'''
        self.cur.execute(script, (str(courseID), str(self.sort)))
        fetched = self.cur.fetchone()
        if fetched is not None:
            ID = fetched[0]
            timestamp = fetched[1]
            if self.is_expired(timestamp):
                script = '''UPDATE COURSES_RAW
                            SET DATA=%s, TIMESTAMP=CURRENT_TIMESTAMP
                            WHERE ID=%s;'''
                self.cur.execute(script, (data, str(ID)))
        else:
            script = '''INSERT INTO COURSES_RAW (COURSE_ID,SORT,DATA) VALUES (%s,%s,%s);'''
            self.cur.execute(script, (courseID, self.sort, data))
        self.conn.commit()

    def count(self):
        self.cur.execute('''SELECT COUNT(*) FROM COURSES_RAW''')
        return self.cur.fetchone()[0]


def run(refresh=False):
    if refresh:
        init_raw_table(db_config)
    s1 = CourseListSpider(1)
    s2 = CourseListSpider(2)
    total = s1.total + s2.total
    s1.start()
    s2.start()
    in_db = s1.count()
    print("total: " + str(total) + ", " + str(in_db) + " has stored.")
