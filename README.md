# 学科实验操作分析平台 (SEOA)

## 项目简介

学科实验操作分析平台（Subject Experiment Operation Analysis）是一个基于现代Web技术开发的实验教学辅助平台，旨在帮助学生和教师进行学科实验的评价和管理。

## 概览

代码量：约8000行

有效代码量：约7200行

核心业务：为用户提供学科实验的智能分析服务。用户可以上传实验视频，系统会利用先进的大语言模型对视频内容进行分析和评估，生成详细的实验分析报告

核心功能：视频上传与AI分析、用户认证（登录注册）、对话管理（创建新对话、查看历史对话）、班级管理、考试系统、通知系统、评价表模板管理。

## 技术栈

### 后端

- **框架**: FastAPI (Python 3.10+)
- **数据库**: MySQL
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Token)
- **AI接口**: 阿里大模型API (DashScope)

### 前端

- **框架**: Vue.js
- **HTTP客户端**: axios
- **桌面应用**: Electron
- **运行地址**: <http://localhost:5175/seoa/>

## 项目结构

```
SEOA/
├── Back_end/              # 后端服务目录
│   ├── main.py            # 主启动文件（带数据库和完整功能）
│   ├── models.py          # 数据库模型
│   ├── database.py        # 数据库配置和连接
│   ├── password_hash.py   # 密码哈希处理
│   ├── auth.py            # 认证相关功能
│   ├── classes.py         # 班级管理功能
│   ├── conversations.py   # 对话管理功能
│   ├── exams.py           # 考试系统功能
│   ├── experiment_matcher.py  # 实验匹配器
│   ├── import_evaluation_templates.py  # 导入评价模板
│   ├── notifications.py   # 通知系统功能
│   ├── similarity.py      # 相似度计算
│   ├── templates.py       # 评价表模板管理
│   ├── test_ai_prompt.py  # AI提示测试
│   ├── check_classes.py   # 班级查询工具
│   ├── 人教版.txt         # 人教版实验数据
│   ├── 人教版_格式化.txt   # 格式化的人教版实验数据
│   ├── alembic/           # 数据库迁移工具
│   ├── keyframes/         # 视频关键帧存储
│   ├── videos/            # 视频文件存储目录
│   ├── requirements.txt   # 依赖文件
├── Front_end/             # 前端应用目录
│   ├── public/            # 静态资源目录
│   ├── src/               # 源代码目录
│   │   ├── assets/        # 资源文件（图片资源）
│   │   ├── utils/         # 工具函数
│   │   ├── App.vue        # 根组件
│   │   ├── AppMain.vue    # 主应用组件（用户类型路由）
│   │   ├── LoginOrRegister.vue  # 登录注册组件
│   │   ├── StudentPage.vue      # 学生端主页面
│   │   ├── TeacherPage.vue      # 教师端主页面
│   │   └── main.js        # 入口文件
│   ├── electron/           # Electron 预加载脚本
│   ├── dist-electron/      # Electron 构建输出
│   ├── index.html         # HTML模板
│   ├── package.json       # 项目配置
│   ├── package-lock.json  # 依赖锁定文件
│   ├── vite.config.mjs    # Vite配置
│   └── jsconfig.json      # JS配置
├── .venv/                 # Python虚拟环境
└── README.md              # 项目总文档
```

## 快速开始

### 环境准备

1. 确保已安装 Python 3.10 或更高版本
2. 确保已安装 Node.js 14 或更高版本（用于前端）
3. 激活虚拟环境（如已创建）:
   ```bash
   .venv\Scripts\activate.bat  # Windows
   source .venv/bin/activate    # Linux/macOS
   ```

### 安装依赖

#### 后端依赖

安装命令：

```bash
cd Back_end
pip install -r requirements.txt
```

#### 前端依赖

前端依赖通过npm管理，进入Front_end目录后安装：

```bash
cd Front_end
npm install
```

### 启动服务

#### 后端启动

```bash
cd Back_end
python main.py
```

服务地址：<http://localhost:8001>

#### 前端启动

```bash
cd Front_end
npm run dev
```

服务地址：<http://localhost:5175/seoa/>

#### 桌面应用启动

```bash
cd Front_end
npm run electron:dev
```

## 用户角色

系统支持两种用户角色：

- **学生 (student)**：可以上传实验视频进行AI分析、加入班级、参加考试、查看通知
- **教师 (teacher)**：可以创建班级、管理学生、创建评价表模板、发布考试、查看通知

## API 接口说明

### 所有接口均以 `/api/seoa/` 为前缀

### 用户认证接口

- **POST /api/seoa/login** - 用户登录
  - 请求体：JSON数据（username, password）
  - 响应：包含access_token和token_type
- **POST /api/seoa/register** - 用户注册
  - 请求体：JSON数据（user_phone, password）
  - 响应：注册成功的用户信息
- **GET /api/seoa/users/me** - 获取当前用户信息
  - 请求头：Authorization: Bearer <token>
  - 响应：用户信息（user_id, user_phone, user_type, name）

### 对话管理接口

- **GET /api/seoa/conversations** - 获取用户的所有对话列表
  - 请求头：Authorization: Bearer <token>
  - 响应：用户的对话列表
- **POST /api/seoa/conversations** - 创建新对话
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（title）
  - 响应：创建的新对话信息
- **GET /api/seoa/conversations/{id}** - 获取指定对话的详情和消息
  - 请求头：Authorization: Bearer <token>
  - 响应：对话详情和消息列表

### 消息管理接口

- **POST /api/seoa/conversations/{id}/messages** - 发送文本消息
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（content）
  - 响应：用户消息和AI回复
- **POST /api/seoa/conversations/{id}/video** - 上传视频并分析
  - 请求头：Authorization: Bearer <token>
  - 请求体：FormData（video文件, experiment_name实验名称）
  - 响应：视频消息和AI分析结果

### 班级管理接口

- **POST /api/seoa/classes** - 创建班级（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（class_name, description）
  - 响应：创建的班级信息（包含自动生成的班级码）
- **GET /api/seoa/classes** - 获取教师的班级列表
  - 请求头：Authorization: Bearer <token>
  - 响应：班级列表
- **POST /api/seoa/classes/join** - 加入班级（学生）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（class_code）
  - 响应：加入班级成功信息
- **GET /api/seoa/student/classes** - 获取学生的班级列表
  - 请求头：Authorization: Bearer <token>
  - 响应：班级列表
- **GET /api/seoa/classes/{class_id}** - 获取班级详情
  - 请求头：Authorization: Bearer <token>
  - 响应：班级详情和成员列表
- **POST /api/seoa/classes/{class_id}/students** - 添加学生到班级（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（student_id）
  - 响应：添加学生成功信息
- **DELETE /api/seoa/classes/{class_id}/students/{student_id}** - 从班级移除学生（教师）
  - 请求头：Authorization: Bearer <token>
  - 响应：移除学生成功信息
- **DELETE /api/seoa/classes/{class_id}** - 解散班级（教师）
  - 请求头：Authorization: Bearer <token>
  - 响应：解散班级成功信息

### 考试系统接口

- **POST /api/seoa/exams** - 创建考试（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（exam_name, description, class_id, template_id, start_time, end_time）
  - 响应：创建的考试信息（会自动向班级学生发送通知）
- **GET /api/seoa/exams** - 获取教师的考试列表
  - 请求头：Authorization: Bearer <token>
  - 响应：考试列表
- **GET /api/seoa/student/exams** - 获取学生可参加的考试列表
  - 请求头：Authorization: Bearer <token>
  - 响应：考试列表
- **GET /api/seoa/exams/{exam_id}** - 获取考试详情
  - 请求头：Authorization: Bearer <token>
  - 响应：考试详情
- **PUT /api/seoa/exams/{exam_id}** - 更新考试信息（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（exam_name, description, class_id, template_id, start_time, end_time）
  - 响应：更新后的考试信息
- **DELETE /api/seoa/exams/{exam_id}** - 删除考试
  - 请求头：Authorization: Bearer <token>
  - 响应：删除考试成功信息

### 评价表模板接口

- **GET /api/seoa/templates** - 获取评价表模板列表（教师）
  - 请求头：Authorization: Bearer <token>
  - 响应：模板列表
- **POST /api/seoa/templates** - 创建评价表模板（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（template_name, description）
  - 响应：创建的模板信息
- **GET /api/seoa/templates/{template_id}** - 获取评价表模板详情
  - 请求头：Authorization: Bearer <token>
  - 响应：模板详情（包含步骤和评分点）
- **POST /api/seoa/templates/{template_id}/steps** - 添加模板步骤
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（step_name, step_order）
  - 响应：创建的步骤信息
- **POST /api/seoa/templates/steps/{step_id}/score-points** - 添加步骤评分点
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（point_name, point_order, score, scoring_criteria, deduction_description）
  - 响应：创建的评分点信息
- **DELETE /api/seoa/templates/{template_id}** - 删除评价表模板
  - 请求头：Authorization: Bearer <token>
  - 响应：删除模板成功信息

### 通知系统接口

- **GET /api/seoa/notifications** - 获取通知列表（支持分页）
  - 请求头：Authorization: Bearer <token>
  - 查询参数：page（页码，默认1），page_size（每页数量，默认20）
  - 响应：分页的通知列表
- **GET /api/seoa/notifications/unread-count** - 获取未读通知数量
  - 请求头：Authorization: Bearer <token>
  - 响应：{ "unread_count": 数量 }
- **PUT /api/seoa/notifications/{notification_id}/read** - 标记单条通知为已读
  - 请求头：Authorization: Bearer <token>
  - 响应：{ "message": "success", "notification_id": id }
- **PUT /api/seoa/notifications/read-all** - 全部标记为已读
  - 请求头：Authorization: Bearer <token>
  - 响应：{ "message": "success", "marked_count": 数量 }

## 开发说明

### 数据库配置

系统使用MySQL数据库，配置参数如下：

1. **配置文件**: `Back_end/database.py`
2. **默认配置**:
   ```python
   DB_USER = "root"           # MySQL用户名
   DB_PASSWORD = "lzx200606"   # MySQL密码
   DB_HOST = "localhost"     # MySQL主机地址
   DB_PORT = 3306            # MySQL端口
   DB_NAME = "ceea"          # 数据库名称
   ```
3. **修改配置**:
   - 打开`Back_end/database.py`文件
   - 修改对应的数据库连接参数
   - 确保MySQL服务已启动，并且`ceea`数据库已创建
4. **创建数据库**:
   ```sql
   CREATE DATABASE ceea CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
5. **更新数据库结构**:
   - 使用数据库迁移工具（推荐）:
     ```bash
     cd Back_end
     alembic upgrade head
     ```
   - 或使用旧的更新脚本:
     ```bash
     cd Back_end
     python update_database.py
     ```

### 数据库模型说明

系统包含以下主要数据表：

- **users** - 用户表（包含学生和教师）
- **conversations** - 对话表
- **messages** - 消息表
- **classes** - 班级表
- **class_members** - 班级成员表
- **evaluation_templates** - 评价表模板表
- **template_steps** - 模板步骤表
- **template_score_points** - 模板评分点表
- **exams** - 考试表
- **notifications** - 通知表
- **experiment_evaluations** - 实验评价表

### 前端页面说明

- **LoginOrRegister.vue** - 登录/注册页面
- **AppMain.vue** - 主应用组件，根据用户类型路由到学生或教师页面
- **StudentPage.vue** - 学生端主页面
  - 视频上传与AI分析
  - 消息中心（通知查看）
  - 考试系统（参加考试）
  - 课程管理（加入课程）
  - 个人中心
- **TeacherPage.vue** - 教师端主页面
  - 视频上传与AI分析（支持批量）
  - 消息中心（通知查看）
  - 考试系统（发布管理考试）
  - 班级管理（创建班级、管理学生）
  - 评价表模板管理（创建管理模板）
  - 个人中心

### 桌面应用

项目支持打包为Electron桌面应用：

```bash
cd Front_end
npm run electron:build  # 构建桌面应用
```

构建后的应用将输出到 `dist-electron` 目录。

### 默认登录账号

- **手机号**: 13800138000
- **密码**: test123
