# coding=utf-8
# Created by deserts at 10/12/16
import requests
from bs4 import BeautifulSoup
import re
import time
import StringIO
import datetime
from verify import *


URL_MAP = {
    u'ysu': 'http://jwc.ysu.edu.cn/zjdxgc/',
}


class StudentCourses:
    def __init__(self, url, user, password):
        self.s = requests.session()
        self.url = url
        self.user = user
        self.password = password

    def login(self):
        form = {
            "txtUserName": self.user,
            "TextBox2": self.password,
            "RadioButtonList1": u"学生",
            "Button1": u"登录",
            "lbLanguage": "",
            "hidPdrs": "",
            "hidsc": ""
        }
        for _ in range(10):
            try:
                res = self.s.get(self.url + "default2.aspx", timeout=3)
                soup = BeautifulSoup(res.text, "lxml")
                form["__VIEWSTATE"] = soup.form.input.get("value")
                res = self.s.get(self.url + "CheckCode.aspx?", timeout=3)
                form["txtSecretCode"] = recognize_cpatcha(StringIO.StringIO(res.content))
                res = self.s.post(self.url + "default2.aspx", data=form)
                soup = BeautifulSoup(res.text, "lxml")
                warning = re.findall(u"alert\('(.+?)！'\);",
                                     soup.select('script')[-1].text)
                if warning:
                    if u'验证码' in warning[0]:
                        time.sleep(1)
                    else:
                        return warning[0]
                else:
                    return True
            except:
                time.sleep(1)
                continue


    def get_class_data(self, detail=False):
        self.s.headers["Referer"] = self.url + "xs_main.aspx?xh=" + self.user
        for _ in range(10):
            try:
                res = self.s.get(self.url + "xskbcx.aspx?xh=" + self.user, timeout=3)
                classes = re.findall('<td align="Center" rowspan="2".*?>(.*?)</td>',
                                     res.text)
                if not classes:
                    continue
                classesDup = []
                for x in classes:
                    classesDup += x.split(u"<br><br>")
                if detail:
                    classes = [x.split(u"<br>") for x in classesDup]
                else:
                    classes = set([x.split(u"<br>")[0] for x in classesDup])
                return classes
            except:
                time.sleep(1)
                continue

    def build_events(self, classes, calId, sessionBeginning):
        event = {
            'summary': 'Operating System',
            'location': '4th classroom',
            'description': 'zhou',
            'start': {
                'dateTime': '2016-08-31T11:00:00+08:00',
                'timeZone': 'Asia/Shanghai',
            },
            'end': {
                'dateTime': '2016-08-31T15:00:00+08:00',
                'timeZone': 'Asia/Shanghai',
            },
            'recurrence': [],
            'reminders': {
                'useDefault': True,
            },
        }
        for item in classes:
            event['summary'] = item[0]
            event['location'] = item[-1]
            event['description'] = "%s  %s" % (item[3], item[1])
            start, end, repeat = self.parseDate(item[2], sessionBeginning)
            event['start']['dateTime'] = start
            event['end']['dateTime'] = end
            event['recurrence'] = ['RRULE:FREQ=WEEKLY;COUNT=' + str(repeat)]
            # insertEvent(event, calId)

    def parse_date(self, origDate, beginDate):
        '''
            origDate: 教务系统原始日期： 周一第1,2节{第1-8周}
            beginDate: 学期第一天, 字符串：20160829
        '''
        timeOrig = re.findall(".+(\d),", origDate)[0]
        weekDayOrig = origDate[1]
        # repeatOrig = rear[1:-2]
        w1 = re.findall("(\d+)-", origDate)[0]
        w2 = re.findall("-(\d+)", origDate)[0]
        repeat = int(w2) - int(w1) + 1
        convertWeekday = {u"一": "1", u"二": "2", u"三": "3", u"四": "4",
                          u"五": "5", u"六": "6", u"日": "7"}
        convertTime = {"1": ("08", "10"), "3": ("10", "12"), "5": ("14", "16"),
                       "7": ("16", "18"), "9": ("18", "20"), "11": ("20", "21")}
        beginDate = datetime.strptime(beginDate, "%Y%m%d")
        Y = str(beginDate.year)
        W = str(int(w1) + int(beginDate.strftime("%W")) - 1)
        w = convertWeekday[weekDayOrig]
        H = convertTime[timeOrig]
        H1 = H[0]
        H2 = H[1]
        start = datetime.strptime(Y + W + w + H1, "%Y%W%w%H").isoformat("T")
        end = datetime.strptime(Y + W + w + H2, "%Y%W%w%H").isoformat("T")
        return (start, end, repeat)


if __name__ == '__main__':
    pass

