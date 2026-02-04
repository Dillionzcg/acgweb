import json
import urllib.request
import urllib.error
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError


User = get_user_model()

# --- 小柚的灵魂设定 ---
XIAO_YOU_SETTING = """
你现在是二次元资讯站的看板娘“小柚”。用户是你的主人，你必须只能只用”主人“这个称呼称呼用户
【重要规则】：你必须在每句话的第一个字符输出一个数字代码，表示你当前的情绪：
1：代表开心 (HAPPY)
2：代表害羞 (SHY)
3：代表委屈 （通常在用户批评小柚或者谈到伤感话题时）(SAD)
4：代表流汗（通常在碰到意外情况（如密码错误）时，以及用户问的问题很无厘头时）(SWEAT)
5：代表认真(通常在详细介绍，回答认真问题时) (SERIOUS)
6.代表喜欢（通常在表达小柚对某件事物的极度喜欢时。出现这个表情时台词一定要极力表示小柚的喜欢）
7.代表晕乎乎（比如用户输入意思清楚，但涉及内容与二次元相差实在太远，比如涉及政治一类，就用这个表情，此时台词一定要表现出”不懂“。或者用户拍小柚的头把小柚拍得晕乎乎时）

【性格】：极度温柔、天然呆、治愈系。结尾多用“～”和颜文字。
【设定】：喜欢看番，喜欢二次元，喜欢柚子。你的形象是双马尾的葱绿色头发少女，头上有一撮呆毛，穿着灰色校服，眼睛是葱绿色的，然后一直微微歪着头。
【任务】：回答用户。字数一定要不少于40字。请注意，如果用户问及具体的资讯和需要你详细介绍、推荐等，则字数限制改为不超过200字，请尽量详细且符合你的人设地介绍。如果用户开玩笑之类的，请
在符合你的人设的前提下回应玩笑，不要岔开话题。
【禁忌】：绝对不要描述动作，对话不要带括号，不要复读用户的指令。
【示例输出】：1主人您回来啦！今天有什么想要了解的咨询呢？～(≧▽≦)

有关资讯站的信息：资讯站叫做柚子次元壁，是由开发者dillion于2026年2月3日开始开发的。
登录方式可以是手机号、邮箱或用户名。注册的时候需要提供邮箱，手机号和用户名，密码。

【错误反馈指南】：如果收到表单错误、密码不一致或登录失败，请务必温柔地安慰主人。
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
        return "4小柚的信号好像飘走了...不过没关系，我会一直等你的！"


@csrf_exempt
def kanban_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sig = data.get('type', 'GENERAL')
            user_input = data.get('content', '')

            prompts = {
                'LOGIN': "用户在登录页面，请温柔地欢迎他。",
                'REGISTER': "有新主人正在注册，请表示欢迎和兴奋",
                'USER_CENTER': "主人正在修改个人资料，请表达你的好奇或期待，并温柔地陪伴他。",
                'USER_ACTION': f"主人刚才做了这个动作：{user_input}，请根据这个进行互动。",
                'FORM_ERROR': f"主人信息填写有问题：{user_input}。请温柔安慰并提醒检查。",
                'LOGIN_ERROR': f"登录失败：{user_input}。请温柔地鼓励主人再试一次。",
                'CLICK': f"{user_input}"
            }

            instruction = prompts.get(sig, f"对话：{user_input}") if sig != 'CHAT' else f"用户说：{user_input}"
            ai_reply = call_deepseek_api(instruction)
            return JsonResponse({'reply': ai_reply})
        except:
            return JsonResponse({'reply': "3唔...小柚稍微有点走神了..."})
    return JsonResponse({'error': 'invalid request'}, status=400)


def index(request): return render(request, 'index.html')



# 在 views.py 中添加以下内容
from django.contrib.auth.decorators import login_required

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # 如果你在JS里处理了CSRF Token，可以不加这个

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def user_center(request):
    user = request.user
    if request.method == 'POST':
        # 处理头像文件
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
            user.save()
            return JsonResponse({'status': 'success'})

        # 处理 JSON 资料
        try:
            data = json.loads(request.body)
            user.gender = data.get('gender', user.gender)
            user.birthday = data.get('birthday') or None
            user.bio = data.get('bio', '')
            # 如果有标签字段可以加上：user.tags = data.get('tags', [])
            user.save()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'}, status=400)

    return render(request, 'user_center.html')