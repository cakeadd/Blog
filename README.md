# Blog

一个基于 Django REST Framework 和 Vue 3 的个人 Blog MVP 项目。

## 功能

- 用户注册、登录、JWT access/refresh token 认证
- 用户资料编辑、密码修改、账号停用、头像上传
- 文章的发布、编辑、删除、详情查看和 Markdown 内容展示
- 文章分类、标题搜索、分类筛选和分页
- 文章点赞与取消点赞
- 评论发布、查看和作者删除
- 用户主页、我的文章、我的点赞
- 独立管理员登录和管理页面
- 管理员对普通用户、文章、评论进行搜索、删除、恢复或停用
- 统一的中文提示和权限校验

## 技术栈

### 后端

- Python
- Django
- Django REST Framework
- SimpleJWT
- SQLite（本地开发）
- Pillow（头像校验和处理）

### 前端

- Vue 3
- Vue Router
- Vite
- Bootstrap 5
- marked + DOMPurify（Markdown 渲染和安全过滤）

## 项目结构

```text
Blog/
├── Blog/              # Django 项目配置
├── users/             # 用户、认证和头像
├── articles/          # 文章和分类
├── comments/          # 评论
├── likes/             # 点赞
├── administration/    # 管理员接口
├── frontend/          # Vue 前端
├── manage.py
├── requirements.txt
└── .env.example
```

## 本地运行

### 1. 获取项目并进入目录

```bash
git clone <your-repository-url>
cd Blog
```

### 2. 创建并启用 Python 虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 配置后端环境变量

复制 `.env.example` 为 `.env`，按需修改其中的配置。

当前项目使用 SQLite，不需要额外配置数据库服务。

### 4. 初始化数据库

```bash
python manage.py migrate
```

### 5. 启动后端

```bash
python manage.py runserver 127.0.0.1:8000
```

### 6. 安装前端依赖并启动前端

```bash
cd frontend
npm install
npm run dev
```

打开 <http://127.0.0.1:5173> 访问前端。

## 管理员初始化

首次访问管理员注册页面，使用用户名和密码创建唯一管理员账号。管理员入口为：

<http://127.0.0.1:5173/admin/login>

管理员仅负责管理普通用户、文章和评论，不具备普通用户的发文、评论和点赞功能。

## 测试与构建

后端测试：

```bash
python manage.py test
```

前端构建：

```bash
cd frontend
npm run build
```

## Git 提交说明

以下内容属于本地开发数据，不应提交到仓库：

- Python 虚拟环境
- SQLite 数据库
- 用户上传的头像文件
- 前端依赖和构建产物
- 本地环境变量文件
- 本地开发计划和进度文件

对应规则已写入 `.gitignore`。公开仓库中只提交源代码、迁移文件、依赖清单和 `.env.example`，不要提交真实密码、JWT 密钥或用户数据。

## 当前项目范围

本项目是本地开发和功能演示用的 MVP，暂不包含生产部署、域名、HTTPS、云数据库、对象存储和 CI/CD 配置。
