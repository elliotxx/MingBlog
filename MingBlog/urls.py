#coding=utf8
"""MingBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from blog.views import index,archive,category,tag,article,search,board,about
from django.conf import settings
from blog.upload import upload_image

urlpatterns = [
    # admin模块的路由
    url(r'^admin/', include(admin.site.urls),name='admin'),
    # 上传文件的路由配置
    url(r"^uploads/(?P<path>.*)$", \
        "django.views.static.serve", \
        {"document_root": settings.MEDIA_ROOT, }),
    # 用于映射富文本编辑器的图片上传
    url(r'^admin/upload/(?P<dir_name>[^/]+)$', upload_image, \
        name='upload_image'),
    # 主页的路由
    url(r'^$', index, name='index'),
    # 文章归档页面的路由
    url(r'^archive/(\d+)/(\d+)/$',archive,name='archive'),
    # 文章分类页面的路由
    url(r'^category/([^\s]+)/$',category,name='category'),
    # 文章标签页面的路由
    url(r'^tag/([^\s]+)/$',tag,name='tag'),
    # 文章页面的路由
    url(r'^article/([^\s]+)/$',article,name='article'),
    # 文章搜索页面
    url(r'^search/$',search,name='search'),
    # 留言板
    url(r'^board/$',board,name='board'),
    # 关于我
    url(r'^about/$',about,name='about'),
    # 加入markdownx编辑器路由
    url(r'^markdownx/', include('markdownx.urls')),

]
