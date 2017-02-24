#coding=utf8
from django.contrib import admin
from models import *
from markdownx.widgets import AdminMarkdownxWidget

# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    # 文章的admin管理类
    #fields = ('title','desc','content')

    # form = ArticleAdminForm
    # 在列表中显示那些列
    list_display = (
        'title','desc','click_count','is_recommend','date_publish','user','category','get_tags','isMarkdown','isPublish'
    )

    list_editable = (
        'is_recommend','isMarkdown','isPublish','category'
    )

    list_display_links = ('title','desc')

    # 发布文章界面
    fieldsets = (
        (None,{
            'fields':('title','content','desc')
        }),
        ('高级设置',{
            # 'classes':('collapse',),    # 折叠
            'classes':('wide',),          # 展开
            'fields':('user','is_recommend','category','tag','isPublish','isMarkdown')
        })
    )

    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }

    # 加入kindeditor富文本编辑器
    # 通过定义ModelAdmin的媒体文件来加入富文本编辑器
    class Media:
        css = {
            'all':('/static/css/code.css',),
        }

class CategoryAdmin(admin.ModelAdmin):
    # 分类的admin管理类
    list_display = ['id','name','level','parentid','index']

    list_editable = ['index','parentid']

    list_display_links = ['id','name']

class AdAdmin(admin.ModelAdmin):
    # 广告滑动条的admin管理类
    list_display = ['title','description','callback_url','date_publish','index']

    list_editable = ['index']

# 将Model注册到admin后台进行管理
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Links)
admin.site.register(Ad,AdAdmin)
