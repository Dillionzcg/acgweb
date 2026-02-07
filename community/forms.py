from django import forms
from .models import Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl bg-white/50 border border-gray-200 focus:ring-2 focus:ring-pink-300 focus:border-pink-300 outline-none transition-all',
                'placeholder': '请输入标题（最多50字）'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-xl bg-white/50 border border-gray-200 focus:ring-2 focus:ring-pink-300 focus:border-pink-300 outline-none transition-all'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-white/50 border border-gray-200 focus:ring-2 focus:ring-pink-300 focus:border-pink-300 outline-none transition-all h-64',
                'placeholder': '在此输入正文内容...'
            }),
        }
