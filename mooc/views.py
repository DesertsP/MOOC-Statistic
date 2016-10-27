# coding=utf-8
import datetime
import json
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Sum, Count, Avg, F, Q, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import *
from .student_courses.student_courses import StudentCourses, URL_MAP


def home(request):
    course_total = Course.objects.count()
    dpt_total = Department.objects.count()
    zh_total = Course.objects.filter(first_lang=2).count()
    school_count = School.objects.count()
    price = price_credit_count()
    high_grading_count = Course.objects.filter(grading__gte=7).count()
    grading_count = Course.objects.filter(grading__gt=0).count()
    high_grading_per = '%.2f%%' % (high_grading_count / float(grading_count) * 100)
    context = {
        'title': u'慕课数据统计分析-概览',
        'count_total': '%d,%d' % (course_total / 1000, course_total % 1000),
        'dp_count': dpt_total,
        'zh_total': '%d,%d' % (zh_total / 1000, zh_total % 1000),
        'school_count': school_count,
        'department_course_count': department_course_count(),
        'price_credit_count': price,
        'free_percent': '%.2f%%' % (100 * price[0][0] / float(course_total)),
        'increments': increments(),
        'grading_count': grading_course_count(),
        'high_grading_per': high_grading_per,
    }
    return render(request, 'home.html', context)


def department_course_count(condition=None):
    if condition is None:
        dpt_course_count = Department.objects.annotate(n_course=Count('course')).order_by('-n_course').values_list(
            'n_course', 'department_name')
    elif condition == 'follower':
        dpt_course_count = Department.objects.filter(course__followers_count__gte=10000).annotate(
            n_course=Count('course')).order_by('-n_course').values_list('n_course', 'department_name')
    elif condition == 'grading':
        dpt_course_count = Department.objects.filter(course__grading__gte=9).annotate(
            n_course=Count('course')).order_by('-n_course').values_list('n_course', 'department_name')
    else:
        return None
    merged = []
    cs_count = 0
    for n, d in dpt_course_count:
        if u'计算机' in d or u'开发' in d or u'数据' in d or u'网' in d or u'IT' in d or u'运维' in d:
            cs_count += n
        else:
            merged.append((n, d))
    merged.append((cs_count, u'计算机/软件相关专业'))
    merged.sort(reverse=True)
    return merged


def increments():
    monthly_count = []
    yy = 2012
    mm = 12
    while True:
        count = Course.objects.filter(date_created__lte=datetime.date(yy, mm, 1)).count()
        monthly_count.append(count)
        if yy >= 2016 and mm >= 11:
            break
        if mm == 12:
            mm = 6
            yy += 1
        else:
            mm += 6
    return monthly_count


def price_credit_count():
    free_count = Course.objects.filter(price=0).count()
    pay_count = Course.objects.count() - free_count
    price_count = [(free_count, u'免费'),
                   (pay_count, u'付费'),
                   ]
    return price_count


def language_course_count():
    lang_course_count = Course.objects.values('first_lang').annotate(num_course=Count('first_lang')).order_by(
        '-num_course').values_list('num_course', 'first_lang')
    lang_dict = {
        '0': u'未知',
        '2': u'中文',
        '22': u'乌克兰语',
        '9': u'俄语',
        '21': u'克罗地亚语',
        '18': u'印地语',
        '12': u'土耳其语',
        '13': u'希伯来语',
        '6': u'德语',
        '10': u'意大利语',
        '7': u'日语',
        '4': u'法语',
        '1': u'英语',
        '20': u'荷兰语',
        '11': u'葡萄牙语',
        '5': u'西班牙语',
        '15': u'阿拉伯语',
        '19': u'韩语',
        '17': u'马来语'
    }
    other_lang_count = sum([_[0] for _ in lang_course_count[6:]])
    lang_course_count = [(n, lang_dict[str(l)]) for n, l in lang_course_count[:6]]
    lang_course_count.append((other_lang_count, '其他'))
    for n, l in lang_course_count:
        print n, l


def grading_course_count(condition=None):
    grd_course_count = []
    lower_than_6 = 0
    for i in range(8, 20):
        if condition is None:
            n = Course.objects.filter(grading__gte=i / 2.0, grading__lt=(i + 1) / 2.0).count()
        elif condition == 'follower':
            n = Course.objects.filter(followers_count__gte=10000, grading__gte=i / 2.0,
                                      grading__lt=(i + 1) / 2.0).count()
        if n > 0 and i / 2.0 > 6:
            grd_course_count.append((n, i / 2.0))
        elif n > 0 and i / 2.0 > 0:
            lower_than_6 += 1
    if condition is None:
        grd_course_count.insert(0, (lower_than_6, '不高于6'))
    return grd_course_count


def hot(request):
    limit = 8
    courses = Course.objects.filter(followers_count__gte=10000).order_by('-followers_count', '-grading')
    count = courses.count()
    zh_count = courses.filter(first_lang=2).count()
    # dpt statistic
    dpt_course_count = department_course_count('follower')
    dpt_count = len(dpt_course_count)
    # grading count
    grd_count = grading_course_count('follower')
    avg_grading = Course.objects.filter(followers_count__gte=10000).aggregate(avg=Avg('grading'))['avg']
    # page nav
    paginator = Paginator(courses, limit)
    page = request.GET.get('page', 1)
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
    context = {
        'title': '慕课关注度排行',
        'courses': courses,
        'count': count,
        'zh_count': zh_count,
        'departments_ordered': dpt_course_count,
        'dp_count': dpt_count,
        'max_grade': max([c.grading for c in courses]),
        'grading_count': grd_count,
        'avg_grading': '%.2f' % avg_grading,
    }
    return render(request, 'hot.html', context)


def grading(request):
    limit = 8
    courses = Course.objects.filter(grading__gte=9).order_by('-grading', '-followers_count')
    count = courses.count()
    zh_count = courses.filter(first_lang=2).count()
    # followers count
    avg_followers_count = courses.aggregate(avg=Avg('followers_count'))['avg']
    # date created
    o_year_ago = courses.filter(date_created__lte='2016-12-31').count()
    one_year_ago = courses.filter(date_created__lte='2015-12-31').count()
    two_years_ago = courses.filter(date_created__lte='2014-12-31').count()
    three_years_ago = courses.filter(date_created__lte='2013-12-31').count()
    count_2016 = o_year_ago - one_year_ago
    count_2015 = one_year_ago - two_years_ago
    count_2014 = two_years_ago - three_years_ago
    count_2013 = three_years_ago
    count_years = ((count_2013, '2013年或更早'), (count_2014, '2014年'),
                   (count_2015, '2015年'), (count_2016, '2016年'))
    # tags
    tags = Tag.objects.filter(course__grading__gte=9).distinct()
    tag_counts = []
    for t in tags:
        n = CourseTag.objects.filter(tag=t, course__grading__gte=9).aggregate(Sum('count'))['count__sum']
        tag_counts.append((n, t))
    tag_counts = sorted(tag_counts, reverse=True)[:10]
    # page nav
    paginator = Paginator(courses, limit)
    page = request.GET.get('page', 1)
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)
    context = {
        'title': '评分最高的课程',
        'courses': courses,
        'count': count,
        'zh_count': zh_count,
        'avg_follow': '%0.f' % avg_followers_count,
        'two_years_ago': '%.0f' % (100 * float(two_years_ago) / count),
        'tag_counts': tag_counts,
        'count_years': count_years,
    }
    return render(request, 'grading.html', context)


def get_coutry_course_count(request):
    if request.method == 'GET' and 'json' in request.GET:
        foo = list(Course.objects.values('school__country').distinct().annotate(z=Count('school__country')).values(
            'school__country', 'z'))
        return HttpResponse(json.dumps(foo),
                            content_type="application/json")
    else:
        return HttpResponseRedirect('/region')


def get_school_geo(request):
    if request.method == 'GET' and 'json' in request.GET:
        school_geo = School.objects.annotate(name=F('school_name'),
                                             lat=F('geo_lat'),
                                             lon=F('geo_lng')).values('name', 'lat', 'lon')
        school_geo = list(school_geo)
        return HttpResponse(json.dumps(school_geo),
                            content_type="application/json")
    else:
        return HttpResponseRedirect('/region')


def region(request):
    course_total = Course.objects.count()
    school_total = School.objects.count()
    lang_total = Course.objects.values('first_lang').distinct().count()
    country_total = School.objects.values('country').distinct().count()
    context = {
        'title': u'慕课地域分布',
        'course_total': '%d,%d' % (course_total / 1000, course_total % 1000),
        'school_total': school_total,
        'lang_total': lang_total,
        'country_total': country_total,
    }
    return render(request, 'region.html', context)


def platform(request):
    pass


def search(request):
    single_page_limit = 12
    if request.method == 'GET' and 'q' in request.GET and request.GET['q']:
        keyword = request.GET['q']
        courses = search_course(keyword)
        if not courses:
            courses = search_course(keyword, limit=None, more_result=True)
        if not courses:
            return render(request, 'search.html', {'title': u'找不到关于"%s的课程"' % keyword, 'error': True})
        count = courses.count()
        zh_count = courses.filter(first_lang=2).count()
        max_followers_count = courses.aggregate(m=Max('followers_count')).get('m')
        max_grading = courses.aggregate(m=Max('grading')).get('m')
        # page nav
        paginator = Paginator(courses, single_page_limit)
        page = request.GET.get('page', 1)
        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            courses = paginator.page(1)
        except EmptyPage:
            courses = paginator.page(paginator.num_pages)
        context = {
            'title': u'"%s"的搜索结果' % keyword,
            'keyword': keyword,
            'courses': courses,
            'count': count,
            'zh_count': zh_count,
            'max_follow': max_followers_count,
            'max_grading': max_grading,
            'error': False,
        }
        return render(request, 'search.html', context)
    else:
        return HttpResponseRedirect('/')


def search_course(keyword, limit=None, more_result=False):
    if len(keyword) < 2:
        return None
    if more_result:
        selected = Course.objects.filter(Q(chinese_name__icontains=keyword) | Q(
            name__icontains=keyword) | Q(departments__department_name__contains=keyword) | Q(
            introduction__icontains=keyword)).distinct().order_by('-grading','-followers_count')[:limit]
    else:
        selected = Course.objects.filter(Q(chinese_name__icontains=keyword) | Q(
            name__icontains=keyword)).distinct().order_by('-grading','-followers_count')[:limit]
    if len(selected) > 0:
        return selected
    else:
        return search_course(keyword[:-1], limit, more_result)


def get_recommend_courses(request):
    limit = 3
    context = {
        'success': False
    }
    s = StudentCourses(URL_MAP[request.GET['school']],
                       request.GET['user'],
                       request.GET['password'])
    info = s.login()
    if info is True:
        school_classes = s.get_class_data()
        if school_classes:
            course_list = []
            for c in school_classes:
                foo = search_course(c, limit)
                if foo:
                    course_list += foo
            context['success'] = True
            context['courses'] = course_list
        else:
            context['notice'] = u'获取课程失败，无法获取到你的课程表.'
    else:
        context['notice'] = u'获取课程失败，' + info
    return render(request, 'recommended_courses.html', context)


def recommend(request):
    context = {
        'title': '优质慕课专属推荐',
        'show_login': True,
    }
    if request.method == 'POST':
        context['show_login'] = False
        context['school'] = request.POST['school']
        context['user'] = request.POST['user']
        context['password'] = request.POST['password']
    return render(request, 'recommend.html', context)


def about(request):
    context = {
        'title': u'关于我们',
    }
    return render(request, 'about.html', context)
