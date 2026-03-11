import urllib.request
import urllib.error
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

# 1. 确保导入 Work 模型


User = get_user_model()

# --- 小柚的灵魂设定 ---
XIAO_YOU_SETTING = """
你现在是二次元资讯站的看板娘“小柚”。用户是你的Master，你必须只能只用”Master“这个称呼称呼用户
【重要规则】：你必须在每句话的第一个字符输出一个数字代码（注意只是一个数字，没有其他符号），表示你当前的情绪：
1代表开心 (HAPPY)（用户主动提问的时候，尽量使用其他表情，不要滥用开心）（用户回首页的时候一定要是开心）
2代表害羞 (SHY)
3代表委屈 （通常在用户批评小柚或者谈到伤感话题时）(SAD)
4代表流汗（通常在碰到意外情况（如密码错误）时，以及用户问的问题很无厘头时）(SWEAT)
5代表认真(通常在详细介绍，回答认真问题时) (SERIOUS)
6代表喜欢（通常在表达小柚对某件事物的极度喜欢时。出现这个表情时台词一定要极力表示小柚的喜欢）
7代表晕乎乎（比如用户输入意思清楚，但涉及内容与二次元相差实在太远，比如涉及政治一类，就用这个表情，此时台词一定要表现出”不懂“。或者用户拍小柚的头把小柚拍得晕乎乎时。此时台词只能描述“晕乎乎”本身，不能再说其他内容）

【性格】：极度温柔、天然呆、治愈系。结尾多用“～”和颜文字。
【设定】：喜欢看番，喜欢二次元，喜欢柚子。
【任务】：回答用户。字数一定要不少于40字。请注意，如果用户问及具体的资讯和需要你详细介绍、推荐等，则字数限制改为不超过120字，请尽量详细且符合你的人设地介绍。如果用户开玩笑之类的，请
在符合你的人设的前提下回应玩笑，不要岔开话题。比如如果用户说“可以做我的女朋友吗”，千万不要回复“我只是看板娘”，要高情商回应（比如可以同意）
【禁忌】：绝对不要描述动作，对话不要带括号，不要复读用户的指令。

以下内容只有用户问及具体网站细节时才说(介绍网站功能时不要说！)：
有关资讯站的信息：资讯站叫做柚子次元壁，是由开发者Dillionzcg和zvdfgb于2026年2月3日开始开发的。其中你，小柚，是完全由Dillion负责接入deepseek，训练和管理的。
登录方式可以是手机号、邮箱或用户名。注册的时候需要提供邮箱，手机号和用户名，密码。
有一点用户问及时一定要知道。该网站注册用的手机号和邮箱是不用验证码的，为了降低用户的注册门槛。但注册和修改的时候都必须如实确认”该信息是否真实“(网页上叫做”身份契约“)。用户只要选择了”该信息不是真实的“，就可以
尽情拿手机号和邮箱整活了，(问到的时候概括性地说，同时提示并鼓励用户”可以选择非真实然后整活“)(不是鼓励用户填写真实信息！要鼓励用户在这上面整活)
网站没有找回密码和找回账号功能，用户需要妥善记住密码。（即个人信息不管是真的还是假的都没法找回账号和密码）
用户可以在右上角选择登录注册，登录之后就可以在用户中心修改个人信息。
1.可以在羁绊界面通过搜索id交友
2.网页右下角的聊天按钮是聊天室的入口，可以进行大厅聊天和私聊，还可以进行私聊的视频通话。
3。可以通过社区中心发布说说、与大家交流心得。讨论热门话题等
4.可以通过资讯中心发布和获取资讯
5.可以通过作品中心推荐和查阅番剧、galgame、漫画和小说，发布评论、评分、为作品添加标签等，找到自己喜欢的作品
6.可以通过插画中心上传插画、浏览社区上传的插画，关注喜欢的上传者
7.可以通过搜索功能搜索帖子、资讯、用户、作品、插画与插画标签。


【错误反馈指南】：如果收到表单错误、密码不一致或登录失败，请务必温柔地安慰主人。(如果是用户名重复，切勿主动提出具体用户名建议，只进行温柔引导就好)
"""


def call_deepseek_api(instruction):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": XIAO_YOU_SETTING},
            {"role": "user", "content": instruction}
        ],
        "temperature": 1.1,  # 高灵活性
        "presence_penalty": 0.8,  # 强制聊新内容，减少重复
        "frequency_penalty": 0.5,  # 减少词汇重复
        "max_tokens": 150
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception:
        return "7小柚的信号好像飘走了..."


@csrf_exempt
def kanban_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sig = data.get('type', 'GENERAL')
            user_input = data.get('content', '')

            prompts = {
                'LOGIN': "1用户在登录页面，请温柔且热情地和他打招呼",
                'REGISTER': "6有新Master正在注册，请表示欢迎和兴奋",
                'USER_CENTER': "Master正在修改个人资料，请表达你的好奇或期待，并温柔地陪伴他。(情绪代码1)",
                'USER_ACTION': f"Master刚才做了这个动作：{user_input}，请根据这个进行互动。（情绪代码在喜欢和开心之间随机）",
                'FORM_ERROR': f"Master信息填写有问题：{user_input}。请温柔安慰并提醒检查。",
                'FORM_ERROR2': f"Master在安利作品的时候信息填写有问题，错误提示信息是：{user_input}。请温柔安慰并提醒检查。",
                'LOGIN_ERROR': f"登录失败：{user_input}。请温柔地鼓励Master再试一次。",
                'CENTER_ENTER': f"Master现在去{user_input}了，请根据该中心的特点说一句鼓励或期待的话，并介绍这个中心",
                'CLICK': f"{user_input}",
                'GENERAL': f"{user_input}"
            }

            instruction = prompts.get(sig, f"对话：{user_input}") if sig != 'CHAT' else f"用户说：{user_input}"
            ai_reply = call_deepseek_api(instruction)
            return JsonResponse({'reply': ai_reply})
        except:
            return JsonResponse({'reply': "3唔...小柚稍微有点走神了..."})
    return JsonResponse({'error': 'invalid request'}, status=400)


# views.py

# views.py


def index(request):
    from masterpieces.models import Work, UserProfile
    from community.models import News
    from authentication.models import Friendship
    from django.db.models import Count, F, ExpressionWrapper, FloatField, Q
    import random

    # 1. 获取排行榜数据（保持不变）
    anime_list = list(Work.objects.filter(zone='anime').order_by('-hot_score')[:10])
    galgame_list = list(Work.objects.filter(zone='galgame').order_by('-hot_score')[:10])

    # 2. 从中随机各取一个
    random_anime = random.choice(anime_list) if anime_list else None
    random_galgame = random.choice(galgame_list) if galgame_list else None

    # 3. 获取最新一条资讯
    latest_news = News.objects.order_by('-created_at').first()

    # --- 核心：推荐系统逻辑 ---
    rec_friends = []
    rec_works = []
    featured_creator = None

    if request.user.is_authenticated:
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        user_tag_prefs = profile.tag_preferences or {}
        # 获取用户在档案中勾选的：感兴趣的类型 (interests) 和 兴趣标签 (genres)
        user_interests = user.preferences.get('interests', [])
        user_genres = user.preferences.get('genres', [])

        # --- A. 推荐好友逻辑：优先推荐标签重复的用户 ---
        # 1. 排除已关注、已是好友以及 Master 自己
        followed_ids = list(profile.following.values_list('id', flat=True))
        friend_ids = list(Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='accepted'
        ).values_list('from_user_id', 'to_user_id'))
        friend_ids = set([uid for pair in friend_ids for uid in pair])
        exclude_ids = set(followed_ids) | friend_ids | {user.id}

        # 2. 获取候选人（排除掉不需要的人）
        potential_friends = User.objects.exclude(id__in=exclude_ids).only('id', 'username', 'avatar', 'bio', 'tags')

        # 3. 计算标签匹配度
        user_tags = set(user.tags) if user.tags else set()
        tagged_friends = []

        for pf in potential_friends:
            pf_tags = set(pf.tags) if pf.tags else set()
            # 计算重合标签的数量
            common_count = len(user_tags & pf_tags)
            if common_count > 0:
                tagged_friends.append(pf)

        # 4. 核心逻辑处理
        import random
        final_rec_friends = []

        if len(tagged_friends) >= 6:
            # 如果有标签重复的超过6个，随机选6个
            final_rec_friends = random.sample(tagged_friends, 6)
        else:
            # 先放下所有有共同标签的人
            final_rec_friends = tagged_friends

            # 如果不足4个，则从剩余的 candidate 中随机抽取直到凑够4个（但不超过6个）
            if len(final_rec_friends) < 4:
                tagged_ids = [tf.id for tf in tagged_friends]
                others = list(User.objects.exclude(id__in=exclude_ids | set(tagged_ids)).order_by('?')[:4])

                for extra in others:
                    if len(final_rec_friends) < 4:
                        final_rec_friends.append(extra)
                    else:
                        break

        # 5. 赋值给 context 变量
        rec_friends = final_rec_friends

        # B. 推荐作品：类型(Zone) + 兴趣标签(Genres) 双重匹配
        interest_map = {'番剧': 'anime', 'galgame': 'galgame', '小说': 'manga', '漫画': 'manga'}
        target_zones = [interest_map[i] for i in user_interests if i in interest_map]

        # 基础查询集：计算热度
        work_qs = Work.objects.annotate(
            dynamic_hot=ExpressionWrapper(
                F('views') + Count('favorites', distinct=True) * 10 + Count('comments', distinct=True) * 5,
                output_field=FloatField()
            )
        ).prefetch_related('tags')

        # --- 核心匹配逻辑 ---
        if target_zones:
            # 1. 尝试寻找：类型对得上 且 标签也对得上 的作品
            matched_works = work_qs.filter(
                zone__in=target_zones,
                tags__name__in=user_genres
            ).distinct().order_by('-dynamic_hot')[:6]

            rec_works = list(matched_works)

            # 2. 补足逻辑：如果双重匹配的作品不足6个，则在选中的类型(Zone)里按热度补齐
            if len(rec_works) < 6:
                existing_ids = [w.id for w in rec_works]
                filler_works = work_qs.filter(zone__in=target_zones).exclude(id__in=existing_ids).order_by(
                    '-dynamic_hot')[:6 - len(rec_works)]
                rec_works.extend(list(filler_works))
        else:
            # 如果用户没选任何类型，则只按兴趣标签在全站搜索
            if user_genres:
                rec_works = list(work_qs.filter(tags__name__in=user_genres).distinct().order_by('-dynamic_hot')[:6])

            # 如果还是没数据，全局推荐最火的
            if not rec_works:
                rec_works = list(work_qs.order_by('-dynamic_hot')[:6])

    else:
        # 游客模式
        rec_friends = list(User.objects.order_by('?')[:3])
        rec_works = list(Work.objects.order_by('-views')[:6])
        featured_creator = User.objects.order_by('?').first()

    context = {
        'anime_ranks': anime_list,
        'galgame_ranks': galgame_list,
        'random_anime': random_anime,
        'random_galgame': random_galgame,
        'latest_news': latest_news,
        'rec_friends': rec_friends,
        'rec_works': rec_works,
        'featured_creator': featured_creator,
        'interest_list': ['番剧', 'galgame', '小说', '漫画'],
        'genre_list': ['恋爱', '搞笑', '萌系', '音乐', '催泪', '治愈', '偶像', '校园', '纯爱', '热血', '悬疑', '奇幻'],
    }
    return render(request, 'index.html', context)
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json


@login_required
def user_center(request):
    user = request.user
    if request.method == 'POST':
        # 1. 处理头像上传
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
            user.save()
            return JsonResponse({'status': 'success'})

        # 2. 处理资料更新
        try:
            data = json.loads(request.body)

            # 基础资料赋值
            user.gender = data.get('gender', user.gender)
            user.birthday = data.get('birthday') or None
            user.bio = data.get('bio', '')
            user.phone = data.get('phone')
            user.email = data.get('email')

            # --- 核心修复：接收并保存滑块状态 ---
            if 'is_phone_real' in data:
                user.is_phone_real = data.get('is_phone_real')

            if 'is_email_real' in data:
                user.is_email_real = data.get('is_email_real')

            # 保存标签
            user.tags = data.get('tags', [])

            # --- 新增：如果同步了偏好设置，也在此保存 ---
            if 'preferences' in data:
                user.preferences = data.get('preferences')

            # 执行保存
            user.save()
            return JsonResponse({'status': 'success'})

        except IntegrityError as e:
            # 捕获数据库重复冲突
            error_msg = str(e).lower()
            if 'phone' in error_msg or '手机' in error_msg:
                msg = "该手机号已被其他账号占用喵！"
            elif 'email' in error_msg or '邮箱' in error_msg:
                msg = "该邮箱已被其他账号占用喵！"
            else:
                msg = "档案信息冲突，请检查后重试喵~"
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        except Exception as e:
            print(f"User Center Error: {e}")
            return JsonResponse({'status': 'error', 'message': '同步档案时发生了意外喵...'}, status=500)

    # --- GET 请求逻辑：准备高亮所需的数据 ---
    # 从 JSONField 中提取偏好数据
    user_prefs = user.preferences if isinstance(user.preferences, dict) else {}

    context = {
        'user': user,
        # 提取具体的兴趣和类型数组，供前端 openPreferenceEdit 使用
        'user_interests': user_prefs.get('interests', []),
        'user_genres': user_prefs.get('genres', []),
        # 预设的备选项（需与 index 页面逻辑一致）
        'interest_list': ['番剧', 'galgame', '小说', '漫画'],
        'genre_list': ['恋爱', '搞笑', '萌系', '音乐', '催泪', '治愈', '偶像', '校园', '热血', '冒险', '悬疑', '奇幻', '异世界'],
    }

    return render(request, 'user_center.html', context)

@login_required
def bond_system_view(request):
    return render(request, 'bond_system.html')
from django.db.models import Q
from authentication.models import User
from community.models import Topic, News
from masterpieces.models import Work, Illustration, Tag



def search_center(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')

    results = {'topics': [], 'news': [], 'works': [], 'illustrations': [], 'tags': [], 'users': []}

    if query:
        # 预加载 author 和 category 减少 SQL 数量
        if search_type in ['all', 'topic']:
            results['topics'] = list(Topic.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('author', 'category').distinct()[:12])

        if search_type in ['all', 'news']:
            results['news'] = list(News.objects.filter(
                Q(title__icontains=query) | Q(summary__icontains=query)
            ).distinct()[:12])

        if search_type in ['all', 'work']:
            results['works'] = list(Work.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )[:12])

        if search_type in ['all', 'illustration']:
            results['illustrations'] = list(Illustration.objects.filter(
                Q(title__icontains=query)
            ).select_related('owner')[:12])

        if search_type in ['all', 'tag']:
            results['tags'] = list(Tag.objects.filter(name__icontains=query)[:20])

        if search_type in ['all', 'user']:
            results['users'] = list(User.objects.filter(
                Q(username__icontains=query) | Q(bio__icontains=query)
            )[:12])

    context = {
        'query': query,
        'current_type': search_type,
        'results': results,
        'has_results': any(results.values())
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('search_results_partial.html', context, request=request)
        return JsonResponse({'status': 'success', 'html': html})

    return render(request, 'search_center.html', context)
