# coding=utf-8
# Created by deserts at 9/30/16
# 代理配置，解决并发时服务器禁止访问的问题

import re
import requests
import random
import threading
import time
import Queue


header = {'headers':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# 系统代理，用以访问gatherproxy
SYS_PROXY = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

url = 'http://gatherproxy.com/proxylist'
pre1 = re.compile(r'<tr.*?>(?:.|\n)*?</tr>')
pre2 = re.compile(r"(?<=\(\').+?(?=\'\))")


def gather_proxy(self, page_index=1, uptime=70, fast=True):
    """
    Get Elite Anomy proxy from gatherproxy.com
    """
    proxies = set()
    params = {"Type": "elite", "PageIdx": str(page_index), "Uptime": str(uptime)}
    try:
        r = requests.post(url + "/anonymity/t=Elite", params=params,
                          headers=header, proxies=SYS_PROXY, timeout=5)
    except:
        return gather_proxy(page_index, uptime, fast)
    for td in pre1.findall(r.text):
        if fast and 'center fast' not in td:
            continue
        try:
            tmp = pre2.findall(str(td))
            if (len(tmp) == 2):
                proxies.add(tmp[0] + ":" + str(int('0x' + tmp[1], 16)))
        except:
            pass
    return proxies


class ProxyPool(object):
    """
    A proxypool class to obtain proxy
    """
    def __init__(self, threads=1):
        self.uncheckedQueue = Queue.Queue()
        self.checkedQueue = Queue.Queue()
        self.numCheckThreads = int(threads * 0.9)
        self.numGatherThreads = int(threads * 0.1)
        self.workEvent = threading.Event()
        self.workEvent.set()
        self.start_threads()

    def start_threads(self):
        for i in range(self.numCheckThreads):
            checkThread = threading.Thread(target=self.check_ip, args=(self.uncheckedQueue, self.checkedQueue))
            checkThread.daemon = True
            checkThread.start()
        for i in range(self.numGatherThreads):
            gatherThread = threading.Thread(target=self.gather_ip, args=(self.uncheckedQueue, self.workEvent))
            gatherThread.daemon = True
            gatherThread.start()

    def gather_ip(self, queue, event):
        """
        ip producer
        :param queue:
        :return:
        """
        while True:
            event.wait()
            ipList = gather_proxy(random.randint(1, 20))
            for ip in ipList:
                queue.put(ip)

    def check_ip(self, taskQueue, resultQueue):
        """
        ip consumer
        :param taskQueue:
        :param resultQueue:
        :return:
        """
        while True:
            ip = taskQueue.get()
            proxies = {'http': 'http://' + ip, 'https': 'https://' + ip}
            try:
                r = requests.get('http://mooc.guokr.com/post/605193/',
                                 proxies=proxies, timeout=2)
                if (r.status_code == 200):
                    resultQueue.put(ip)
            except:
                pass
            taskQueue.task_done()

    def gen_proxy(self):
        while True:
            # print self.checkedQueue.qsize(), self.uncheckedQueue.qsize()
            if not self.workEvent.isSet() and self.checkedQueue.qsize() < 20:
                self.workEvent.set()
            if (self.workEvent.isSet() and self.checkedQueue.qsize() > 100) or self.uncheckedQueue.qsize() > 500:
                self.workEvent.clear()
            proxy = self.checkedQueue.get()
            yield {'http': 'http://' + proxy, 'https': 'https://' + proxy}


if __name__ == '__main__':
    p = ProxyPool(300)
    ps = p.gen_proxy()
    print time.localtime()
    for i in range(1000):
        print ps.next()
    print time.localtime()
