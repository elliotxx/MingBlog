from django import forms
# from wmd.widgets import MarkDownInput
from markdownx.fields import MarkdownxFormField

# content = forms.CharField(widget=AdminMarkDownInput())

class MyForm(forms.Form):
    content = MarkdownxFormField()