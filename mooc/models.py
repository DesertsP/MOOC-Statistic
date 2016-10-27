# coding=utf-8

from __future__ import unicode_literals

from django.db import models


class School(models.Model):
    school_name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=3)
    geo_lat = models.FloatField()
    geo_lng = models.FloatField()

    def __unicode__(self):
        return self.school_name

    class Meta:
        db_table = 'schools'


class Platform(models.Model):
    platform_name = models.CharField(max_length=255, unique=True)
    platform_site = models.URLField()
    platform_wiki = models.TextField()

    def __unicode__(self):
        return self.platform_name

    class Meta:
        db_table = 'platforms'


class Department(models.Model):
    department_name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.department_name

    class Meta:
        db_table = 'departments'


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.teacher_name

    class Meta:
        db_table = 'teachers'


class Tag(models.Model):
    tag_name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.tag_name

    class Meta:
        db_table = 'tags'


class Course(models.Model):
    LANGUAGE = ((2, u'中文'),
                (22, u'乌克兰语'),
                (9, u'俄语'),
                (21, u'克罗地亚语'),
                (18, u'印地语'),
                (12, u'土耳其语'),
                (13, u'希伯来语'),
                (6, u'德语'),
                (10, u'意大利语'),
                (7, u'日语'),
                (4, u'法语'),
                (1, u'英语'),
                (20, u'荷兰语'),
                (11, u'葡萄牙语'),
                (5, u'西班牙语'),
                (15, u'阿拉伯语'),
                (19, u'韩语'),
                (0, u'未知'),
                (17, u'马来语'),)
    DIFFICULTY = ((0, u'暂无'),
                 (1, u'简单'),
                 (2, u'一般'),
                 (3, u'困难'))
    TYPE = ((1, 'MOOC'), (2, '职业课程'))
    name = models.CharField(max_length=255, unique=True)
    chinese_name = models.CharField(max_length=255)
    grading = models.FloatField(default=0)
    price = models.FloatField(default=0)
    url = models.CharField(max_length=511)
    icon_url = models.CharField(max_length=511, default=None)
    type = models.PositiveSmallIntegerField(choices=TYPE)
    date_created = models.DateField()
    date_status = models.DateField()
    duration = models.PositiveSmallIntegerField()
    followers_count = models.BigIntegerField()
    introduction = models.TextField()
    difficulty = models.SmallIntegerField(choices=DIFFICULTY)
    first_lang = models.SmallIntegerField(choices=LANGUAGE)
    second_lang = models.SmallIntegerField(choices=LANGUAGE)
    school = models.ForeignKey(School)
    platform = models.ForeignKey(Platform)
    departments = models.ManyToManyField(Department, through='CourseDepartment')
    tags = models.ManyToManyField(Tag, through='CourseTag')
    teachers = models.ManyToManyField(Teacher, through='CourseTeacher')

    def __unicode__(self):
        return self.name

    def get_tag_num(self):
        tag_id_list = [(_.count, _.tag_id) for _ in CourseTag.objects.filter(course_id=self.pk)]
        return set([(Tag.objects.get(pk=_id), count) for count, _id in tag_id_list])

    def get_tag_top(self):
        tag_id_list = set([(_.count, _.tag_id) for _ in CourseTag.objects.filter(course_id=self.pk)])
        sorted_tags = sorted([(count, Tag.objects.get(pk=_id)) for count, _id in tag_id_list], reverse=True)
        if len(sorted_tags) >= 4:
            return sorted_tags[:4]
        else:
            return sorted_tags

    def get_departments(self):
        return set(self.departments.all())

    def get_department(self):
        if self.departments.all():
            return self.departments.all()[0]
        else:
            return None

    class Meta:
        db_table = 'courses'


class CourseTag(models.Model):
    course = models.ForeignKey(Course)
    tag = models.ForeignKey(Tag)
    count = models.IntegerField()

    class Meta:
        db_table = 'course_tag_relationships'


class CourseDepartment(models.Model):
    course = models.ForeignKey(Course)
    department = models.ForeignKey(Department)

    class Meta:
        db_table = 'course_department_relationships'


class CourseTeacher(models.Model):
    course = models.ForeignKey(Course)
    teacher= models.ForeignKey(Teacher)

    class Meta:
        db_table = 'course_teacher_relationships'
