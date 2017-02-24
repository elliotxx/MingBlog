#coding=utf8
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from PIL import Image
import logging
import os,re
# from redactor.fields import RedactorField
# from wmd import models as wmd_models
from markdownx.models import MarkdownxField


# 用户模型
class User(AbstractUser):
    #nickname = models.CharField(max_length=30,default='访客',unique=True,verbose_name='用户昵称')
    avatar = models.ImageField(upload_to='avatar/%Y/%m',default='avatar/default.png',max_length=200,verbose_name='头像')
    qq = models.CharField(max_length=20,blank=True,null=True,verbose_name='QQ号码')
    mobile = models.CharField(max_length=11,blank=True,null=True,unique=True,verbose_name='手机号码')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering=['-id']

    def __unicode__(self):
        return self.username

# 标签
class Tag(models.Model):
    name = models.CharField(max_length=30,verbose_name='标签名称')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

# 分类
class Category(models.Model):
    name = models.CharField(max_length=30,verbose_name='分类名称')
    index = models.IntegerField(default=999,verbose_name='排序权重')
    level = models.IntegerField(default=1,verbose_name='分类等级') # 他是几级标签（1级标签最大，显示在主页导航里）
    parentid = models.IntegerField(default=0,blank=True,null=True,verbose_name='父分类id')


    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering=['index','id']

    def __unicode__(self):
        return self.name

# 自定义一个文章model的管理器
# 1.新加一个数据处理方式
# 2.改变原有的queryset
class ArticleManager(models.Manager):
    def distinct_date(self):
        distinct_date_list = []
        date_list = self.values('date_publish')
        for date in date_list:
            # date = date['date_publish'].strftime('%Y年%m月')
            date['year'] = date['date_publish'].strftime('%Y')
            date['month'] = date['date_publish'].strftime('%m')
            date['date_publish'] = date['date_publish'].strftime('%Y年%m月')
            if date not in distinct_date_list:
                distinct_date_list.append(date)
        return distinct_date_list

# 文章模型
class Article(models.Model):
    # 文章选择分类时只显示二级分类名

    title = models.CharField(max_length=255,verbose_name='文章标题')
    desc = MarkdownxField(default='',blank=True,null=True,verbose_name='文章描述')
    content = MarkdownxField(verbose_name='文章内容')
    # 文章显示时是否用markdown渲染
    isMarkdown = models.BooleanField(default=1,verbose_name='Markdown?')
    click_count = models.IntegerField(default=0,verbose_name='点击次数')
    is_recommend = models.BooleanField(default=False,verbose_name='是否推荐')
    date_publish = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    comment_cnt = models.IntegerField(default=0,verbose_name='评论数')
    isPublish = models.BooleanField(default=1,verbose_name='是否发布')

    user = models.ForeignKey(User,default=1,verbose_name='发布人')
    category = models.ForeignKey(Category,blank=True,null=True,verbose_name='分类',limit_choices_to={'level':2})
    tag = models.ManyToManyField(Tag,blank=True,null=True,verbose_name='标签')


    objects = ArticleManager()

    def get_tags(self):
        return ",".join([str(p) for p in self.tag.all()])
    get_tags.short_description  = '标签云'


    def save(self):
        # 保存之前先处理一下desc文章描述内容
        more = self.content.find(settings.MORE_TAG)
        if more==-1:   # 没找到more标签
            # 让它等于标题
            if self.desc=='':      # desc为空
                self.desc = self.title
        else:   # 找到more标签
            self.desc = self.content[:more]
            self.content = ''.join(self.content.split(settings.MORE_TAG))
        super(Article, self).save()

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-date_publish']


    def __unicode__(self):
        return self.title


# 友情链接
class Links(models.Model):
    title = models.CharField(max_length=50,verbose_name='标题')
    description = models.CharField(max_length=200,verbose_name='链接描述')
    callback_url = models.URLField(verbose_name='url地址')
    date_publish = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    index = models.IntegerField(default=999,verbose_name='排列顺序（从小到大）')

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name
        ordering = ['index','id']

    def __unicode__(self):
        return self.title

# 广告
class Ad(models.Model):
    title = models.CharField(max_length=50,verbose_name='广告标题')
    description = models.CharField(max_length=200,verbose_name='广告描述')
    image_url = models.ImageField(upload_to='ad/%Y/%m',verbose_name='图片路径')
    callback_url = models.URLField(null=True,blank=True,verbose_name='回调url')
    date_publish = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    index = models.IntegerField(default=999,verbose_name='排序顺序（从小到大）')

    class Meta:
        verbose_name = '广告'
        verbose_name_plural = verbose_name
        ordering=['index','id']

    # 上传文件的同时，创建该文件的缩略图
    def save(self):
        # 将上传的图片先保存一下，否则报错
        super(Ad, self).save()
        src_file = str(self.image_url.path.encode('gbk'))
        # 打开源文件
        image = Image.open(src_file)
        # 得到缩略图保存路径
        index = src_file.find('uploads') + len('uploads') + 1
        save_file = os.path.join(src_file[:index],'thumbs',src_file[index:])
        # 如果缩略图保存路径所在目录不存在，则创建目录
        if not os.path.exists(os.path.dirname(save_file)):
            os.makedirs(os.path.dirname(save_file))
        # 生成缩略图
        image.thumbnail((settings.THUMB_HEIGHT,settings.THUMB_WIDTH),Image.ANTIALIAS)
        # 保存缩略图
        image.save(save_file,settings.THUMB_FORMAT)


    def __unicode__(self):
        return self.title

