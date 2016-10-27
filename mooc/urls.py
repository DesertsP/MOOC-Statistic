"""mooc_analysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hot$', views.hot, name='hot'),
    url(r'^region$', views.region, name='region'),
    url(r'^$', views.home, name='home'),
    url(r'^grading$', views.grading, name='grading'),
    url(r'^recommend$', views.recommend, name='recommend'),
    url(r'^search$', views.search, name='search'),
    url(r'^about$', views.about, name='about'),
    url(r'^country$', views.get_coutry_course_count, name='country'),
    url(r'^geo$', views.get_school_geo, name='school_geo'),
    url(r'^recourses$', views.get_recommend_courses, name='recourses'),
]
