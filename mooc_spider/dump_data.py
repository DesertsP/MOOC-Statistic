# coding=utf-8
# Created by deserts at 10/2/16
# 转存储主要的数据
# 操作之前language表中需要填充数据以满足约束

from config import db_config_raw, db_config
from utilities import *
import json
import re


def dump_name(cur, table, name):
    """
    a general function to dump name into database.
    :param cur: db cursor
    :param table: table name: 'department', 'platform', 'school', 'tag'  or 'teacher'
            NOTICE: table name without 's'
    :param name: item's name
    :return: id in the table
    """
    script = 'INSERT IGNORE INTO {}s ({}_name) VALUES (%s)'
    script = script.format(table, table)
    cur.execute(script, (name,))
    script = 'SELECT id FROM {}s WHERE {}_name=%s'
    script = script.format(table, table)
    cur.execute(script, (name,))
    return cur.fetchone()[0]


def dump_relationship(cur, table, course_id, item_id, tag_count=None):
    """
    :param cur:  db cursor
    :param table: relationship table: 'department', 'tag', or 'teacher'
    :param course_id:
    :param item_id:
    :param tag_count: for tag_relationship table
    :return: None
    """
    script = 'INSERT IGNORE INTO course_{}_relationships (course_id, {}_id{}) VALUES (%s, %s{})'
    if tag_count is None:
        script = script.format(table, table, '', '')
        cur.execute(script, (course_id, item_id))
    else:
        script = script.format(table, table, ', count', ', %s')
        cur.execute(script, (course_id, item_id, tag_count))


def dump_course(cur,
                name,
                chinese_name,
                grading,
                price,
                url,
                icon_url,
                type,
                date_created,
                date_status,
                duration,
                followers_count,
                introduction,
                difficulty,
                school_id,
                platform_id,
                first_lang_id,
                second_lang_id):
    script = '''
    INSERT IGNORE INTO courses (name,chinese_name,grading,price,url,icon_url,type,
    date_created,date_status,duration,followers_count,introduction,difficulty,
    school_id,platform_id,first_lang,second_lang)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    params = (name, chinese_name, grading, price, url, icon_url, type,
              date_created, date_status, duration, followers_count,
              introduction, difficulty, school_id, platform_id,
              first_lang_id, second_lang_id)
    cur.execute(script, params)
    script = 'SELECT id FROM courses WHERE name=%s'
    cur.execute(script, (name,))
    try:
        return cur.fetchone()[0]
    except Exception, e:
        print name + ": error!"
        print e
        return None


def gen_raw():
    conn = connect_db(db_config_raw)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM COURSES_RAW;')
    num = cur.fetchone()[0]
    cur.execute('SELECT DATA, MORE, SORT FROM COURSES_RAW;')
    for i in range(num):
        yield cur.fetchone()
    conn.close()


def dump_row(cur, row_data):
    data, more, sort = row_data
    data = json.loads(data)
    more = json.loads(more)
    platform = data['platform']
    school = data['school']
    departments = data['depts']
    tags = more['comment_tags']
    teachers = more['teacher'].split(u'，')
    # insert
    school_id = dump_name(cur, 'school', school.strip())
    platform_id = dump_name(cur, 'platform', platform)
    department_id_list = [dump_name(cur, 'department', dept.strip()) for dept in departments]
    teacher_id_list = [dump_name(cur, 'teacher', tchr.strip()) for tchr in teachers]
    tag_id_count_list = [(dump_name(cur, 'tag', t[0].strip()), int(t[1].strip())) for t in tags]
    course_info = {
        'name': data['name'].strip(),
        'chinese_name': data['chinese_name'].strip(),
        'grading': data['grading'],
        'price': data['price'],
        'url': more['link'].strip(),
        'icon_url': data['icon_url'],
        'type': sort,
        'date_created': data['date_created'][:10],
        'date_status': convert_date(data['date_status']),
        'duration': data['duration'],
        'followers_count': data['stat']['followers_count'],
        'introduction': data['blackboard'],
        'difficulty': more['difficulty'],
        'school_id': school_id,
        'platform_id': platform_id,
        'first_lang_id': data['teaching_lang_id'],
        'second_lang_id': data['second_subtitle_lang_id']
    }
    course_id = dump_course(cur, **course_info)

    [dump_relationship(cur, 'department', course_id, d_id) for d_id in department_id_list]
    [dump_relationship(cur, 'teacher', course_id, t_id) for t_id in teacher_id_list]
    [dump_relationship(cur, 'tag', course_id, t[0], t[1]) for t in tag_id_count_list]


def convert_date(date):
    r = re.findall(u'(\d*).(\d*).(\d*).', date)
    if len(r[0][0]) > 0:
        return r[0][0] + '-' + r[0][1] + '-' + r[0][2]
    elif date == u'时间待定':
        return '0001-01-02'
    elif date == u'时间自主':
        return '0001-01-01'
    else:
        raise Exception("date format error: can't parse date!")


def dump_data():
    print('Dumping...')
    rows = gen_raw()
    conn = connect_db(db_config)
    cur = conn.cursor()
    for r in rows:
        dump_row(cur, r)
        conn.commit()
    cur.close()
    conn.close()
    print('Done!')


def run(initDB=False):
    if initDB:
        init_tables(db_config)
    dump_data()


if __name__ == '__main__':
    run()