# 化学实验评价系统 (CEEA)

## 项目简介

化学实验评价系统（Chemical Experiment Evaluation Assistant）是一个基于现代Web技术开发的实验教学辅助平台，旨在帮助学生和教师进行化学实验的评价和管理。

## 概览

代码量：5308行

有效代码量：约3000行

核心业务：为用户提供化学实验的智能评估服务。用户可以上传实验视频，系统会利用先进的大语言模型对视频内容进行分析和评估，生成详细的实验分析报告

核心功能：视频上传与AI分析、用户认证（登录注册）、对话管理（创建新对话、查看历史对话）、班级管理、考试系统。

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
- **运行地址**: <http://localhost:5174/ceea/>

## 项目结构

```
CEEA/
├── Back_end/              # 后端服务目录
│   ├── main.py            # 主启动文件（带数据库和完整功能）
│   ├── models.py          # 数据库模型
│   ├── database.py        # 数据库配置和连接
│   ├── password_hash.py   # 密码哈希处理
│   ├── auth.py            # 认证相关功能
│   ├── experiment_matcher.py  # 实验匹配器
│   ├── experiments.json   # 实验评价表
│   ├── update_database.py # 数据库更新脚本
│   ├── videos/            # 视频文件存储目录
│   ├── requirements.txt   # 依赖文件
├── Front_end/             # 前端应用目录
│   ├── public/            # 静态资源目录
│   ├── src/               # 源代码目录
│   │   ├── assets/        # 资源文件
│   │   ├── utils/         # 工具函数
│   │   ├── App.vue        # 根组件
│   │   ├── LoginOrRegister.vue  # 登录注册组件
│   │   ├── Page.vue       # 主页面组件
│   │   └── main.js        # 入口文件
│   ├── index.html         # HTML模板
│   ├── package.json       # 项目配置
│   ├── package-lock.json  # 依赖锁定文件
│   ├── vite.config.js     # Vite配置
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

前端依赖通过npm管理，进入Front\_end目录后安装：

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

服务地址：<http://localhost:5175/ceea/>

## API 接口说明

### 所有接口均以 `/api/ceea/` 为前缀

### 用户认证接口

- **POST /api/ceea/login** - 用户登录
  - 请求体：JSON数据（username, password）
  - 响应：包含access\_token和token\_type
- **POST /api/ceea/register** - 用户注册
  - 请求体：JSON数据（user\_phone, password）
  - 响应：注册成功的用户信息
- **GET /api/ceea/users/me** - 获取当前用户信息
  - 请求头：Authorization: Bearer <token>
  - 响应：用户信息

### 对话管理接口

- **GET /api/ceea/conversations** - 获取用户的所有对话列表
  - 请求头：Authorization: Bearer <token>
  - 响应：用户的对话列表
- **POST /api/ceea/conversations** - 创建新对话
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（title）
  - 响应：创建的新对话信息
- **GET /api/ceea/conversations/{id}** - 获取指定对话的详情和消息
  - 请求头：Authorization: Bearer <token>
  - 响应：对话详情和消息列表

### 消息管理接口

- **POST /api/ceea/conversations/{id}/messages** - 发送文本消息
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（content）
  - 响应：用户消息和AI回复
- **POST /api/ceea/conversations/{id}/video** - 上传视频并分析
  - 请求头：Authorization: Bearer <token>
  - 请求体：FormData（video文件, experiment\_name实验名称）
  - 响应：视频消息和AI分析结果

### 班级管理接口

- **POST /api/ceea/classes** - 创建班级（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（class\_name, description）
  - 响应：创建的班级信息
- **GET /api/ceea/classes** - 获取教师的班级列表
  - 请求头：Authorization: Bearer <token>
  - 响应：班级列表
- **POST /api/ceea/classes/join** - 加入班级（学生）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（class\_code）
  - 响应：加入班级成功信息
- **GET /api/ceea/student/classes** - 获取学生的班级列表
  - 请求头：Authorization: Bearer <token>
  - 响应：班级列表
- **GET /api/ceea/classes/{class\_id}** - 获取班级详情
  - 请求头：Authorization: Bearer <token>
  - 响应：班级详情和成员列表
- **DELETE /api/ceea/classes/{class\_id}** - 解散班级（教师）
  - 请求头：Authorization: Bearer <token>
  - 响应：解散班级成功信息

### 考试系统接口

- **POST /api/ceea/exams** - 创建考试（教师）
  - 请求头：Authorization: Bearer <token>
  - 请求体：JSON数据（exam\_name, description, class\_id, start\_time, end\_time）
  - 响应：创建的考试信息
- **GET /api/ceea/exams** - 获取教师的考试列表
  - 请求头：Authorization: Bearer <token>
  - 响应：考试列表
- **GET /api/ceea/exams/{exam\_id}** - 获取考试详情
  - 请求头：Authorization: Bearer <token>
  - 响应：考试详情
- **DELETE /api/ceea/exams/{exam\_id}** - 删除考试
  - 请求头：Authorization: Bearer <token>
  - 响应：删除考试成功信息

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
   ```bash
   cd Back_end
   python update_database.py
   ```

***

