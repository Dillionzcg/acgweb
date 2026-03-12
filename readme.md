# 🍊 柚子次元壁 — ACG Web

> 一个面向 ACG（动画、漫画、游戏）爱好者的综合社区平台，集社交、内容分享、实时聊天和 AI 看板娘于一体。

---

## 📖 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [环境变量](#-环境变量)
- [使用说明](#-使用说明)
- [贡献指南](#-贡献指南)
- [开发者](#-开发者)

---

## 📝 项目简介

**柚子次元壁**是一个基于 Django 构建的 ACG 社区 Web 应用，为动漫爱好者、漫画读者、Galgame 玩家和插画创作者提供一个交流与分享的平台。平台拥有丰富的社区功能，并集成了 AI 看板娘"小柚"为用户提供智能互动体验。

---

## ✨ 功能特性

### 🔐 用户系统
- 支持用户名 / 邮箱 / 手机号多方式登录
- 用户注册与个人资料管理（头像、简介、标签、偏好等）

### 🎬 作品中心
- 浏览和管理番剧、Galgame、小说/漫画等多种作品类型
- 作品标签系统与评分评论
- 收藏夹功能
- 插画中心：上传、浏览和互动原创或转载插画

### 💬 社区中心
- 话题讨论区：发帖、浏览、置顶、点赞
- 资讯区：发布和阅读 ACG 相关新闻，支持嵌套评论

### 🗨️ 实时聊天
- 基于 WebSocket 的实时通信
- 大厅公共聊天与私信聊天
- 消息持久化存储

### 🤝 羁绊系统
- 好友搜索与添加
- 多种关系类型：普通、闺蜜/兄弟、恋人、家人

### 🔍 全局搜索
- 搜索帖子、资讯、用户、作品、插画和标签

### 🤖 AI 看板娘 —「小柚」
- 由 DeepSeek API 驱动的 AI 助手
- 可爱治愈的动漫角色人设
- 在登录、注册、用户中心等页面提供智能引导与互动

### 📊 个性化推荐
- 基于用户浏览和收藏行为的标签偏好系统
- 个性化内容推荐

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Django 5.2 |
| 实时通信 | Django Channels + Daphne (ASGI) |
| 数据库 | SQLite3（开发环境） |
| 前端 | Django Templates + HTML/CSS/JavaScript |
| AI 集成 | DeepSeek API |
| 图标 | FontAwesome |

---

## 📁 项目结构

```
acgweb/
├── DjangoProject/       # Django 项目配置（settings、urls、asgi、wsgi）
├── acg_core/            # 核心应用（首页、用户中心、搜索、羁绊系统）
├── authentication/      # 用户认证（登录、注册、自定义用户模型）
├── masterpieces/        # 作品中心（番剧、Galgame、插画）
├── community/           # 社区中心（话题、资讯）
├── chat/                # 实时聊天（WebSocket）
├── media/               # 用户上传文件（头像、插画、封面等）
├── static/              # 静态资源（CSS、JS、图片）
├── templates/           # 公共模板
├── manage.py            # Django 管理脚本
└── readme.md            # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Dillionzcg/acgweb.git
cd acgweb

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. 安装依赖
pip install django==5.2
pip install channels daphne
pip install python-dotenv
pip install pillow

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key

# 5. 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 6. 创建管理员账户（可选）
python manage.py createsuperuser

# 7. 启动开发服务器
daphne -b 0.0.0.0 -p 8000 DjangoProject.asgi:application
```

启动后访问 http://localhost:8000 即可进入平台。

---

## 🔑 环境变量

在项目根目录创建 `.env` 文件并配置以下变量：

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于 AI 看板娘功能 | 是 |

---

## 📌 使用说明

| 路由 | 说明 |
|------|------|
| `/` | 首页 |
| `/auth/login/` | 登录页 |
| `/auth/register/` | 注册页 |
| `/works/` | 作品中心 |
| `/community/` | 社区中心 |
| `/chat/` | 聊天室 |
| `/admin/` | 后台管理（需管理员权限） |

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 提交 Pull Request

---

## 👨‍💻 开发者

- [Dillionzcg](https://github.com/Dillionzcg)
- [zvdfgb](https://github.com/zvdfgb)
