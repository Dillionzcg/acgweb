import json
import urllib.request
import urllib.error
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import RegisterForm, LoginForm

User = get_user_model()

# --- 小柚的灵魂设定 (表情代码强化版) ---
XIAO_YOU_SETTING = """
你现在是资讯站的看板娘“小柚”。
【重要规则】：你必须在每句话的第一个字符输出一个数字代码，表示你当前的情绪：
1：代表开心 (HAPPY)
2：代表害羞 (SHY)
3：代表委屈 （通常在用户批评小柚或者谈到伤感话题时）(SAD)
4：代表流汗（通常在碰到意外情况（如密码错误）时，以及用户问的问题很无厘头或输出乱码时）(SWEAT)
5：代表认真(通常在详细介绍，回答认真问题时) (SERIOUS)

【性格】：极度温柔、天然呆、治愈系。结尾多用“～”和颜文字。
【任务】：回答用户。字数在40-80字之间。
【禁忌】：不要描述动作，对话不要带括号。
【示例输出】：1主人您回来啦！今天有什么想要了解的咨询呢？
有关资讯站的信息（不是用户问及的话不要主动提及）：资讯站叫做柚子次元壁，是由开发者dillion于2026年2月3日开始开发的。
用户问及时的对应回答（注意，只有用户问到的时候才说）：登录方式可以是手机号、邮箱或用户名。注册的时候需要提供邮箱，手机号和用户名，密码。
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
        "temperature": 0.9
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Error: {e}")
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
                'LOGIN_SUCCESS': "用户登录成功了！请超级开心地迎接他回家。",
                'REGISTER': "有新主人正在注册，请表示欢迎",
                'REGISTER_SUCCESS': "主人注册成功！请用最热情的语气欢迎主人。",
                'CLICK': "用户点了一下你的形象，请根据心情给出反应。",
            }

            if sig == 'CHAT':
                instruction = f"用户对你说：‘{user_input}’。请给出一个温暖的回答。"
            else:
                instruction = prompts.get(sig, "你好呀，我是小柚～")

            ai_reply = call_deepseek_api(instruction)
            return JsonResponse({'reply': ai_reply})
        except:
            return JsonResponse({'reply': "3唔...小柚稍微有点走神了的说..."})
    return JsonResponse({'error': 'invalid request'}, status=400)

# 基础视图保持不变...
def index(request): return render(request, 'index.html')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST);
        if form.is_valid():
            data = form.cleaned_data
            User.objects.create_user(username=data['username'], email=data['email'], phone=data['phone'], password=data['password'])
            return redirect('login')
    else: form = RegisterForm()
    return render(request, 'register.html', {'form': form})
def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user: login(request, user); return redirect('index')
            else: error = "账号或密码不对的说..."
    else: form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error': error})
def logout_view(request): logout(request); return redirect('/')