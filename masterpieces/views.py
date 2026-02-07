from django.shortcuts import render
from .models import Work


def works_center(request):
    # 获取所有作品
    all_works = Work.objects.all()

    # 构造前端需要的数据格式
    context = {
        'anime_list': all_works.filter(zone='anime').order_by('-created_at')[:6],
        'anime_ranks': all_works.filter(zone='anime').order_by('-views')[:10],

        'galgame_list': all_works.filter(zone='galgame').order_by('-created_at')[:6],
        'galgame_ranks': all_works.filter(zone='galgame').order_by('-views')[:10],

        'manga_list': all_works.filter(zone='manga').order_by('-created_at')[:6],
        'manga_ranks': all_works.filter(zone='manga').order_by('-views')[:10],
    }
    return render(request, 'masterpieces/works_center.html', context)