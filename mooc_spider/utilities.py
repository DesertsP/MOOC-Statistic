# coding=utf-8
# Created by deserts at 9/30/16
# 公用部分
import mysql.connector

# course type
SORT_DICT = {
    '1': 'course',
    '2': 'career'
}

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Host': 'mooc.guokr.com',
    'Referer': 'http://mooc.guokr.com/course/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
}


# start database operations


def connect_db(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.InterfaceError:
        print("MySQL Server not start, run 'mysql.server start' first!")
        conn = None
    return conn


def init_raw_table(db_config):
    print("Database refreshed")
    conn = connect_db(db_config)
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS courses_raw''')
    cur.execute('''CREATE TABLE courses_raw (
                   id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
                   course_id INTEGER NOT NULL,
                   sort TINYINT NOT NULL,
                   timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   data LONGTEXT,
                   more TEXT);''')
    cur.close()
    conn.commit()
    conn.close()

def init_tables(db_config):
    conn = connect_db(db_config)
    cur = conn.cursor(buffered=True)
    scripts = '''
    DROP TABLE IF EXISTS courses;
    DROP TABLE IF EXISTS schools;
    DROP TABLE IF EXISTS teachers;
    DROP TABLE IF EXISTS departments;
    DROP TABLE IF EXISTS tags;
    DROP TABLE IF EXISTS platforms;
    DROP TABLE IF EXISTS course_department_relationships;
    DROP TABLE IF EXISTS course_tag_relationships;
    DROP TABLE IF EXISTS course_teacher_relationships;

    CREATE TABLE schools
    (
        id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
        school_name VARCHAR(255) NOT NULL,
        country VARCHAR(3) NOT NULL,
        geo_lat DOUBLE NOT NULL,
        geo_lng DOUBLE NOT NULL
    );

    CREATE TABLE platforms
    (
        id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
        platform_name VARCHAR(255) NOT NULL,
        platform_site VARCHAR(200) NOT NULL,
        platform_wiki LONGTEXT NOT NULL
    );

    CREATE TABLE courses(
    id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    chinese_name VARCHAR(255) NOT NULL,
    grading DOUBLE NOT NULL,
    price DOUBLE NOT NULL,
    url VARCHAR(511) NOT NULL,
    icon_url VARCHAR(511) NOT NULL,
    type SMALLINT(5) unsigned NOT NULL,
    date_created DATE NOT NULL,
    date_status DATE NOT NULL,
    duration SMALLINT(5) unsigned NOT NULL,
    followers_count BIGINT(20) NOT NULL,
    introduction LONGTEXT NOT NULL,
    difficulty SMALLINT(6) NOT NULL,
    first_lang SMALLINT(6) NOT NULL,
    second_lang SMALLINT(6) NOT NULL,
    platform_id INT(11) NOT NULL,
    school_id INT(11) NOT NULL,
    FOREIGN KEY (platform_id) REFERENCES platforms (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
    );

    CREATE TABLE IF NOT EXISTS  teachers(
        teacher_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
        teacher_name VARCHAR(255) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS  tags(
        tag_id  INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
        tag_name VARCHAR(255) NOT NULL UNIQUE
    );

    CREATE TABLE departments
    (
        id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
        department_name VARCHAR(255) NOT NULL
    );

    CREATE TABLE course_department_relationships
    (
        id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
        course_id INT(11) NOT NULL,
        department_id INT(11) NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (department_id) REFERENCES departments (id)
    );

    CREATE TABLE  IF NOT EXISTS  course_teacher_relationships(
        course_id INTEGER,
        teacher_id INTEGER,
        PRIMARY KEY (course_id, teacher_id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
    );

    CREATE TABLE course_tag_relationships
    (
        id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
        count INT(11) NOT NULL,
        course_id INT(11) NOT NULL,
        tag_id INT(11) NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (tag_id) REFERENCES tags (id)
    );'''
    # mysql connector for python 貌似没有执行多条语句的API
    [cur.execute(s) for s in scripts.split(';')]
    conn.commit()
    cur.close()
    conn.close()
    print("Database created.")

# end database operations
