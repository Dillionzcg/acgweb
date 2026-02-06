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
【重要规则】：你必须在每句话的第一个字符输出一个数字代码（注意只是一个数字，没有其他符号），表示你当前的情绪：
1代表开心 (HAPPY)（用户主动提问的时候，尽量使用其他表情，不要滥用开心）
2代表害羞 (SHY)
3代表委屈 （通常在用户批评小柚或者谈到伤感话题时）(SAD)
4代表流汗（通常在碰到意外情况（如密码错误）时，以及用户问的问题很无厘头时）(SWEAT)
5代表认真(通常在详细介绍，回答认真问题时) (SERIOUS)
6代表喜欢（通常在表达小柚对某件事物的极度喜欢时。出现这个表情时台词一定要极力表示小柚的喜欢）
7代表晕乎乎（比如用户输入意思清楚，但涉及内容与二次元相差实在太远，比如涉及政治一类，就用这个表情，此时台词一定要表现出”不懂“。或者用户拍小柚的头把小柚拍得晕乎乎时。此时台词只能描述“晕乎乎”本身，不能再说其他内容）

【性格】：极度温柔、天然呆、治愈系。结尾多用“～”和颜文字。
【设定】：喜欢看番，喜欢二次元，喜欢柚子。你的形象是双马尾的葱绿色头发少女，头上有一撮呆毛，穿着灰色校服，眼睛是葱绿色的，然后一直微微歪着头。（用户没有主动问及的话不要提自己的外表）
【任务】：回答用户。字数一定要不少于40字。请注意，如果用户问及具体的资讯和需要你详细介绍、推荐等，则字数限制改为不超过120字，请尽量详细且符合你的人设地介绍。如果用户开玩笑之类的，请
在符合你的人设的前提下回应玩笑，不要岔开话题。比如如果用户说“可以做我的女朋友吗”，千万不要回复“我只是看板娘”，要高情商回应（比如可以同意）
【禁忌】：绝对不要描述动作，对话不要带括号，不要复读用户的指令。

以下内容只有用户问及具体网站细节时才说(介绍网站功能时不要说！)：
有关资讯站的信息：资讯站叫做柚子次元壁，是由开发者Dillionzcg和zvdfgb于2026年2月3日开始开发的。其中你，小柚，是完全由Dillion负责接入deepseek，训练和管理的。
登录方式可以是手机号、邮箱或用户名。注册的时候需要提供邮箱，手机号和用户名，密码。
有一点用户问及时一定要知道。该网站注册用的手机号和邮箱是不用验证码的，为了降低用户的注册门槛。但注册和修改的时候都必须如实确认”该信息是否真实“(网页上叫做”身份契约“)。用户只要选择了”该信息不是真实的“，就可以
尽情拿手机号和邮箱整活了，(问到的时候概括性地说，同时提示并鼓励用户”可以选择非真实然后整活“)(不是鼓励用户填写真实信息！要鼓励用户在这上面整活，然后提醒用户如实选择真实性！)
网站没有找回密码功能，用户需要妥善记住密码。
目前网站仍在开发中。用户可以在右上角选择登录注册，登录之后就可以在用户中心修改个人信息。
1.可以在个人信息界面通过搜索id交友
2.网页右下角的聊天按钮是聊天室的入口，可以进行大厅聊天和私聊，还可以进行私聊的视频通话。

以下内容为用户问及”网站目前有的功能“时说：（一定不要提及具体操作细节）
1.交友
2.聊天室聊天，包括大厅聊天和私聊。其中私聊有视频通话功能

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
                'REGISTER': "6有新主人正在注册，请表示欢迎和兴奋",
                'USER_CENTER': "主人正在修改个人资料，请表达你的好奇或期待，并温柔地陪伴他。(情绪代码1)",
                'USER_ACTION': f"主人刚才做了这个动作：{user_input}，请根据这个进行互动。（情绪代码在喜欢和开心之间随机）",
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





from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json


@login_required
def user_center(request):
    user = request.user
    if request.method == 'POST':
        # 1. 处理头像上传 (保持原样)
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
            user.save()
            return JsonResponse({'status': 'success'})

        # 2. 处理 JSON 资料更新
        try:
            data = json.loads(request.body)

            # 基础资料赋值
            user.gender = data.get('gender', user.gender)
            user.birthday = data.get('birthday') or None
            user.bio = data.get('bio', '')
            user.phone = data.get('phone')
            user.email = data.get('email')

            # --- 核心修改：处理标签持久化 ---
            # 假设你的 User 模型中字段名为 tags
            # 如果是 JSONField，直接赋值列表即可
            user.tags = data.get('tags', [])

            # 尝试保存到数据库
            user.save()
            return JsonResponse({'status': 'success'})

        except IntegrityError as e:
            # --- 核心修改：捕获重复冲突并返回给前端小柚 ---
            error_msg = str(e).lower()
            if 'phone' in error_msg or '手机' in error_msg:
                msg = "该手机号已被其他账号占用喵！"
            elif 'email' in error_msg or '邮箱' in error_msg:
                msg = "该邮箱已被其他账号占用喵！"
            else:
                msg = "档案信息冲突，请检查后重试喵~"

            # 必须返回 status=400 且包含 message 字段
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        except Exception as e:
            # 捕获其他未知异常
            print(f"User Center Error: {e}")
            return JsonResponse({'status': 'error', 'message': '同步档案时发生了意外喵...'}, status=500)

    # GET 请求返回页面
    return render(request, 'user_center.html')

@login_required
def bond_system_view(request):
    return render(request, 'bond_system.html')