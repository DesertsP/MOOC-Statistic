# coding=utf-8
# Created by Deserts Pan at 9/25/16
# 配置文件，包含数据库配置以及并发量控制

db_config_raw = {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "",
    "user": "",
    "password": ""
}

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "",
    "user": "",
    "password": ""
}

# multiprocessors & multithreads
threads = 100
proxyThreads = 10

timedelta = {
    'days': 0,
    'hours': 1,
}
