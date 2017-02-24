#coding=utf8
from django import template
import markdown2
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.template.defaultfilters import stringfilter

register = template.Library()

# 定义一个将日记中的月份转换为大写的过滤器
@register.filter
def month_to_upper(key):
    return ['一','二','三','四','五','六','七','八','九','十','十一','十二'][key.month-1]

# @register.filter(is_safe=True)
# @stringfilter
# def custom_markdown(value):
#     return mark_safe(markdown2.markdown(force_text(value),
#         extensions=['markdown.extensions.codehilite'], safe_mode=True,\
#         enable_attributes=False))\

@register.filter(is_safe=True)
@stringfilter
def custom_markdown(value):
    return mark_safe(markdown2.markdown(force_text(value),
        extras=["codehilite","fenced-code-blocks","cuddled-lists","use-file-vars"]))

# # 注册过滤器
# register.filter('month_to_upper',month_to_upper)