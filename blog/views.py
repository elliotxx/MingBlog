# coding=utf8
import logging
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger  # 分页类及异常类型
from django.db import connection  # 执行excute方法所需库
from models import *
from PIL import Image
import urllib2,json,os

logger = logging.getLogger('blog.views')


# Create your views here.
# 在setting里设置，每次加载页面自动运行
def global_setting(request):
    return {'SITE_HOST': settings.SITE_HOST,
            'SITE_NAME': settings.SITE_NAME,
            'SITE_DESC': settings.SITE_DESC,
            'INDEX_NAME':settings.INDEX_NAME,
            'ABOUT_NAME':settings.ABOUT_NAME,
            'BOARD_NAME':settings.BOARD_NAME,
            'SHORT_NAME':settings.SHORT_NAME,
            'MEDIA_URL': settings.MEDIA_URL,
            'THUMB_URL': settings.THUMB_URL,
            }


# 获取侧边栏数据
def get_sidebar():
    try:
        # 获取所有分类数据
        category_list = Category.objects.filter(level=1)
        for i,category in enumerate(category_list):
            # 提取该一级分类下的所有二级分类
            sub_category = Category.objects.filter(parentid=category.id)
            if len(sub_category)!=1 or sub_category[0].name != category.name:
                # 不是没有二级分类的一级分类
                setattr(category_list[i],'sub_category',sub_category)
                # 每个二级分类的文章数
                for j,sub in enumerate(sub_category):
                    article_num = Article.objects.filter(category=sub.id).count()
                    setattr(category_list[i].sub_category[j],'article_num',article_num)


        # 获取近期评论数据，默认获取5条评论
        # comment_list = Comment.objects.all()[:5]

        # 获取近期文章数据，默认获取5条评论
        sidebar_article_list = Article.objects.filter(isPublish=1)[:5]

        # 获取标签数据
        tag_list = Tag.objects.all()

        # 文章归档
        archive_list = Article.objects.distinct_date()
    except Exception as e:
        print e
        logger.error(e)
    return category_list, sidebar_article_list, tag_list, archive_list


# 获取当前分页数据
def get_Paginator(request, article_list):
    paginator = Paginator(article_list, settings.PER_PAGE)
    try:
        page = int(request.GET.get('page', 1))
        if page == 1:
            # 如果是第一页，提取置顶文章
            temp_list = []
            for article in article_list:
                if article.is_recommend == 1:
                    temp_list.append(article)

            article_list = paginator.page(page)

            # 将非置顶文章放到后面
            for article in article_list:
                if article.is_recommend == 0:
                    temp_list.append(article)

            article_list.object_list = temp_list
        else:
            article_list = paginator.page(page)

        # 转换作者名admin为‘呓语’
        for i, article in enumerate(article_list):
            if article.user.username == 'admin':
                article_list[i].user.username = u'呓语'

    except (EmptyPage, InvalidPage, PageNotAnInteger):
        # 出现错误，应该显示404页面
        article_list = paginator.page(1)
    return article_list

# 获取文章列表中每篇文章的评论数
# 性能优化点：每次都要请求多说服务器，需要耗费时间
# 获得评论数后，同时更新数据库
def get_article_comments(article):
    short_name = settings.SHORT_NAME    #  多说用户验证码
    timeout = 5         # 设置超时时间
    response = urllib2.urlopen('http://api.duoshuo.com/threads/listPosts.json?order=asc&thread_key=%s&short_name=%s&page=1&limit=999' % (article.id, short_name),timeout=timeout)
    article.comment_cnt = json.loads(response.read())['thread']['comments']
    article.save()
    return article


# 主页
def index(request):
    try:
        # 当前页面名称
        current_page = 'index'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 获取滑动条的广告数据
        ad_list = Ad.objects.all()


        # 准备左侧内容栏数据，近期所有文章
        # 获取最新文章数据（使用分页类）
        article_list = Article.objects.filter(isPublish=1)

        # 根据分页器获取当前页面数据
        article_list = get_Paginator(request, article_list)


    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'index.html', locals())


# 归档页面
def archive(request, year, month):
    try:
        # 当前页面名称
        current_page = 'archive'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 准备左侧内容栏数据，对应年月份的归档文章
        # 获取文章数据（使用分页类）
        article_list = Article.objects.filter(date_publish__icontains=year + '-' + month).filter(isPublish=1)

        # 根据分页器获取当前页面数据
        article_list = get_Paginator(request, article_list)

    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())


# 文章分类页面
def category(request, category_name):
    try:
        # 当前页面名称
        current_category = Category.objects.get(name=category_name)
        if current_category.level > 1:  # 是子分类
            current_page = Category.objects.get(id=current_category.parentid).name
        else:
            current_page = category_name

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 准备左侧内容栏数据
        # 获取文章数据（使用分页类）
        if current_category.level > 1:  # 是子分类
            # 获取分类名对应的id号
            category_id = Category.objects.get(name=category_name.encode('utf8')).id
            # 根据id号取出该分类下所有文章
            article_list = Article.objects.filter(category=category_id).filter(isPublish=1)
        else:   # 是一级分类
            # 取出所有父分类id是这个一级分类的子分类
            article_list = Article.objects.filter(category__parentid=current_category.id).filter(isPublish=1)


        # 根据分页器获取当前页面数据
        article_list = get_Paginator(request, article_list)


    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())

# 标签文章页面
def tag(request, tag_id):
    try:
        # 当前页面名称
        current_page = 'tag'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 准备左侧内容栏数据，对应的带此标签的所有文章
        # 获取文章数据（使用分页类）
        # 根据id号取出该标签下所有文章
        article_list = Tag.objects.get(id=tag_id).article_set.all().filter(isPublish=1)

        # 根据分页器获取当前页面数据
        article_list = get_Paginator(request, article_list)


    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())


# 文章显示页面
def article(request, article_id):
    try:
        # 当前页面名称
        current_page = 'article'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 准备左侧内容栏数据，对应年月份的归档文章
        # 获取文章数据（使用分页类）
        # 根据id号取出文章
        article = Article.objects.filter(id=article_id)[0]
        if article.isPublish==0:
            raise Exception,'该文章还没有发布，禁止访问！'
        if article.user.username == 'admin':
            article.user.username = u'呓语'

        # 获取每一篇文章的评论数
        # 每次点开一篇文章的时候更新具体的评论数
        article = get_article_comments(article)

        # 每次点开文章，更新点击次数
        article.click_count += 1
        article.save()

    except Exception as e:
        logger.error(e)
    return render(request, 'article.html', locals())


# 文章显示页面
def search(request):
    try:
        # 当前页面名称
        current_page = 'search'

        # 获取关键字
        key = request.GET.get('s',None).encode('utf8')

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 准备左侧内容栏数据，对应年月份的归档文章
        # 获取文章数据（使用分页类）
        # 根据id号取出文章
        article_list = Article.objects.filter(title__icontains=key).filter(isPublish=1)

        # 根据分页器获取当前页面数据
        article_list = get_Paginator(request, article_list)


    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())

# 留言板
def board(request):
    try:
        # 当前页面名称
        current_page = 'board'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

        # 加载留言板的短用户名
        SHORT_NAME_BOARD = settings.SHORT_NAME_BOARD

    except Exception as e:
        logger.error(e)
    return render(request, 'board.html', locals())

# 关于我
def about(request):
    try:
        # 当前页面名称
        current_page = 'about'

        # 获取侧边栏数据
        category_list, sidebar_article_list, tag_list, archive_list = get_sidebar()

    except Exception as e:
        logger.error(e)
    return render(request, 'about.html', locals())

