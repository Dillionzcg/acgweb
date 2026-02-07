from django import forms
from .models import Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 font-bold text-gray-700 placeholder-gray-400',
                'placeholder': '请输入精彩的标题...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-5 py-3 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 text-gray-700 cursor-pointer'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-5 py-4 rounded-xl bg-gray-50/80 border-2 border-transparent focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-100 outline-none transition-all duration-300 h-64 text-gray-700 placeholder-gray-400 leading-relaxed resize-none',
                'placeholder': '在这里分享你的观点、吐槽或情报...支持Markdown语法'
            }),
        }
