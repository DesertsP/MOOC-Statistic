# coding=utf-8
# Created by deserts at 10/4/16
# 调用谷歌和百度地图API获取学校的国别和经纬度
import requests
from proxy import SYS_PROXY
from utilities import *
from config import db_config_raw, db_config
import json

# 为尽可能多的获取学校地理信息，Google Maps API获取失败情况下尝试百度地图API
google_api = "http://maps.googleapis.com/maps/api/geocode/json"
baidu_api = 'http://api.map.baidu.com/geocoder/v2/'


def get_geo_data(address, recur_limit=False):
    res = requests.get(google_api,
                       params={'sensor':'false', 'address':address},
                       proxies=SYS_PROXY)
    data = res.content
    json_data = json.loads(data)
    # print json.dumps(json_data)
    if json_data['status'] != 'ok' and json_data['status'] != 'OK':
        # 对台湾的大学特殊处理
        if u'國立' in address or u'国立' in address:
            return get_geo_data(address[2:], recur_limit=True)
        else:
            if recur_limit:
                return None
            return get_geo_baidu(address)
    else:
        return data


def get_geo_baidu(address):
    res = requests.get(baidu_api,
                         params={'output':'json',
                                 'ak':'IyCwjML6XRnPG9RF8CKUIiDwUkQ7w3qf',
                                 'address':address
                                })
    try:
        json_data = json.loads(res.content)
        location = json_data['result']['location']
        res = requests.get(baidu_api,
                           params={'output':'json',
                           'ak':'IyCwjML6XRnPG9RF8CKUIiDwUkQ7w3qf',
                           'location': str(location['lat']) + ',' + str(location['lng'])})
        return res.content
    except:
        return None


def dump_one_geo_data(cur, address):
    cur.execute(''' INSERT IGNORE INTO locations_raw (address, geodata)
                    VALUES (%s, %s)''', (address, get_geo_data(address)))


def dump_all_geo_data(address_list):
    conn = connect_db(db_config_raw)
    cur = conn.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS locations_raw (
                        id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE ,
                        address TEXT,
                        geodata TEXT )''')
    for address in address_list:
        dump_one_geo_data(cur, address)
        print(address + ' done!')
        conn.commit()
    cur.close()
    conn.close()


def get_address_list():
    conn = connect_db(db_config)
    cur = conn.cursor()
    cur.execute('''SELECT school_name FROM schools''')
    fetch = cur.fetchall()
    return [s[0] for s in fetch]


def run():
    dump_all_geo_data(get_address_list())


if __name__ == '__main__':
    run()