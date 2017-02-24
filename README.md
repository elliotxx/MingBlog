个人博客：[呓语 | 杨英明的个人博客](http://www.yangyingming.com)

欢迎访问！

##特性

* 采用markdownx编辑器，支持编辑页和预览页双排显示，支持图片拖曳上传 
* 支持markdown和html两种编写博文的方式
* 采用多说评论框
* 文章分类
* 文章标签
* 文章归档
* 广告滚动条

##部署项目

###下载项目

```
clone https://github.com/windcode/MingBlog.git
```

###修改 MingBlog/setting.py

* 1、关闭DEBUG功能
DEBUG=False
* 2、ALLOWED_HOSTS = [] 改为 ALLOWED_HOSTS = ['*']
允许所有IP访问
* 3、填写数据库信息
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog',
        'USER': 'youruser',
        'PASSWORD': 'yourpwd',
        'HOST': '127.0.0.1',    # 默认
        'PORT': '3306',         # 默认
    }
}
```
* 4、填写网站基本信息
```python
SITE_HOST = 'http://www.your-domain.com'
SITE_NAME = 'xxx的个人博客'
SITE_DESC = '这是我的博客，专注于技术分享，欢迎交流'
ZHIHU_PAGE = ''
PRO_RSS = ''
PRO_EMAIL = 'youremail'
```
