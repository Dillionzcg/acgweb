from django import forms
from .models import Topic, News

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'keywords', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 font-bold text-gray-700 placeholder-gray-400',
                'placeholder': '请输入精彩的标题...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 text-gray-700 placeholder-gray-400',
                'placeholder': '添加关键词，用空格或逗号分隔'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-5 py-4 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 h-64 text-gray-700 placeholder-gray-400 leading-relaxed resize-none',
                'placeholder': '在这里分享你的观点、吐槽 or 情报...支持 Markdown 语法'
            }),
        }

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'category', 'cover_image', 'summary', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-blue-300 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 font-bold text-gray-700 placeholder-gray-400',
                'placeholder': '请输入新闻标题...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-blue-300 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 text-gray-700'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-blue-300 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 text-gray-700'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-blue-300 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 h-24 text-gray-700 placeholder-gray-400 resize-none',
                'placeholder': '请输入新闻摘要...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-5 py-4 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-blue-300 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 h-96 text-gray-700 placeholder-gray-400 leading-relaxed resize-none',
                'placeholder': '请输入新闻正文内容...'
            }),
        }
