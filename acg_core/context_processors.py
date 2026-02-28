# 文件路径示例：base/context_processors.py

def acg_preferences_context(request):
    """
    定义全局可用的偏好设置列表
    """
    return {
        'interest_list': ['番剧', 'galgame', '小说', '漫画'],
        'genre_list': ['恋爱', '搞笑', '萌系', '音乐', '催泪', '治愈', '偶像', '校园', '纯爱', '热血', '悬疑', '奇幻']
    }