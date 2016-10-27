# coding=utf-8
# Created by deserts at 10/4/16
# 存储其他数据，包括课程语言，学校及平台的相关信息
# 其中dump_langs()需要在dump_data.py之前进行，
# dump_platform_info()以及dump_school_geo()在dump_data.py之后进行

from utilities import *
from config import db_config, db_config_raw
from spider_platform import get_wiki
import re
import json


def get_home_page(url):
    r = re.findall(r"\s*?(ht.*?//.*?/).*", url)
    if len(r) > 0:
        return r[0]
    else:
        return None


def dump_platform_info():
    conn = connect_db(db_config)
    cur = conn.cursor()
    cur.execute('SELECT id, platform_name from platforms')
    platforms = cur.fetchall()
    for platform_id, platform_name in platforms:
        cur.execute('SELECT url FROM courses WHERE platform_id=%s', (platform_id,))
        url = cur.fetchall()[0][0]
        site = get_home_page(url)
        wiki = get_wiki(platform_name)
        script = '''UPDATE platforms
                    SET platform_site=%s, platform_wiki=%s
                    WHERE id=%s'''
        cur.execute(script, (site, wiki, platform_id))
        conn.commit()
    cur.close()
    conn.close()


def dump_one_geo(school, country, lat, lng):
    conn = connect_db(db_config)
    cur = conn.cursor()
    cur.execute('''UPDATE schools
                   SET country=%s, geo_lat=%s, geo_lng=%s
                   WHERE school_name=%s''',
                (country, lat, lng, school))
    conn.commit()
    conn.close()



def get_geometry(data):
    data = json.loads(data)
    if data['status'] != 'ok' and data['status'] != 'OK':
        if data['status'] == 0:
            location = data['result']['location']
            country = data['result']['addressComponent']['country_code']
            if country == 0:
                country = 'CN'
            return (country, location)
    else:
        components = data['results'][0]['address_components']
        country =  [c['short_name'] for c in components if 'country' in c['types']][0]
        location = data['results'][0]['geometry']['location']
        return (country, location)


def dump_school_geo():
    conn = connect_db(db_config_raw)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM locations_raw''')
    for row in cur:
        _, school, geodata = row
        try:
            country, location = get_geometry(geodata)
            lat = location['lat']
            lng = location['lng']
            print country, location
            dump_one_geo(school, country, lat, lng)
        except TypeError:
            pass
    conn.close()


if __name__ == '__main__':
    dump_school_geo()
    dump_platform_info()


