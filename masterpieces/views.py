import json
from django.shortcuts import render, redirect
from .models import Work, Tag
# views.py

# views.py

def works_center(request):
    all_works = Work.objects.prefetch_related('tags').all()

    def get_zone_data(zone_name):
        zone_works = all_works.filter(zone=zone_name)
        return {
            'list': zone_works.order_by('-created_at')[:6],  # 最新推荐
            'ranks': zone_works.order_by('-views')[:10],    # 排行榜
            'hot': zone_works.order_by('-views')[:6],       # 热门作品
        }

    anime = get_zone_data('anime')
    galgame = get_zone_data('galgame')
    manga = get_zone_data('manga')

    context = {
        # 番剧
        'anime_list': anime['list'],
        'anime_ranks': anime['ranks'],
        'anime_hot': anime['hot'],
        # Galgame
        'galgame_list': galgame['list'],
        'galgame_ranks': galgame['ranks'],
        'galgame_hot': galgame['hot'],
        # 漫画
        'manga_list': manga['list'],
        'manga_ranks': manga['ranks'],
        'manga_hot': manga['hot'],
    }
    return render(request, 'masterpieces/works_center.html', context)


def recommend_work(request):
    if request.method == 'POST':
        # 1. 获取基础数据
        title = request.POST.get('title')
        zone = request.POST.get('zone')
        cover = request.FILES.get('cover')

        # 2. 获取前端 JSON 格式的标签数据 (对应之前 JS 写入的 tags_data)
        tags_json = request.POST.get('tags_data')
        tags_list = json.loads(tags_json) if tags_json else []

        # 3. 创建作品实例
        # 注意：这里我们先不给 tags 赋值，因为它是 ManyToMany 关系
        work = Work.objects.create(
            title=title,
            zone=zone,
            cover=cover
        )

        # 4. 处理多对多标签关联
        for tag_name in tags_list:
            # get_or_create 自动处理：如果标签已存在则获取，不存在则创建
            tag_obj, created = Tag.objects.get_or_create(name=tag_name.strip())
            work.tags.add(tag_obj)

        # 5. 提交成功后跳转回作品中心
        return redirect('masterpieces:works_center')

    # GET 请求则正常显示页面
    return render(request, 'masterpieces/recommend_work.html')