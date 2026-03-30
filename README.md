### **SSTPredictorAPI**

海表温度（SST）预测系统的后端 API 服务。本项目基于 Flask 框架开发，负责处理前端请求、管理用户认证、提供历史 SST 数据查询接口以及调用机器学习模型进行预测。

#### **技术栈**

- **语言**: Python 3.9
- **Web 框架**: Flask
- **数据处理**: (例如: xarray, pandas, numpy)
- **机器学习**: (例如: scikit-learn, torch)

#### **项目结构**

```text
SSTPredictorAPI
├── app.py              # 应用程序入口，创建 Flask 实例并注册蓝图
├── config.py           # 项目配置文件，包含数据库 URI、密钥等
├── extensions.py       # 扩展插件初始化，如 db, migrate, login_manager 等
├── models.py           # 数据模型定义，如用户模型等
├── requirements.txt    # 项目依赖包列表
├── README.md           # 项目说明文档
├── data_store/         # 数据存储目录
│   └── sst_raw/        # 原始 SST 数据文件 (.nc)
├── routes/             # 路由蓝图目录
│   ├── __init__.py
│   ├── admin.py        # 管理相关路由
│   ├── auth.py         # 用户认证相关路由 (登录、注册)
│   └── public.py       # 公开数据查询和预测路由
├── services/           # 业务逻辑层
│   └── historical.py   # 处理历史数据查询的业务逻辑
└── utils/              # 工具函数和辅助类
    └── permissions.py  # 权限校验相关工具
```

#### **快速开始**

##### **1. 环境准备**

确保你的系统已安装 Python 3.9 或更高版本。

##### **2. 克隆项目**

```bash
git clone <你的项目仓库地址>
cd SSTPredictorAPI
```

##### **3. 创建虚拟环境并安装依赖**

推荐使用 `venv` 或 `conda` 来隔离项目环境。

```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

##### **4. 配置项目**

编辑 `config.py` 文件，根据你的环境（开发、测试、生产）设置相应的配置项。通常需要设置：

- `SECRET_KEY`: 用于会话加密的密钥。
- `DATABASE_URI`: 数据库连接地址（如果使用数据库）。
- 其他自定义配置。

##### **5. 运行应用**

在项目根目录下，运行以下命令启动开发服务器：

```bash
python app.py
```

应用默认将在 `http://127.0.0.1:3000` 上运行。

#### **API 接口**

以下是本项目提供的主要 API 接口概览：

| 模块 | 请求方法 | 路由 (完整路径)                   | 描述                   | 权限/备注                                           |
| ---- | -------- | --------------------------------- | ---------------------- | --------------------------------------------------- |
| 认证 | POST     | `/api/auth/register`              | 普通用户注册           | 无 (默认角色为 USER)                                |
| 认证 | POST     | `/api/auth/register_admin`        | 特权注册 (管理员/超管) | 需填写有效的 `license_key`                          |
| 认证 | POST     | `/api/auth/login`                 | 用户登录               | 无 (返回 JWT Token 及权限列表)                      |
| 管理 | GET      | `/api/admin/users`                | 获取用户列表           | 需 `user:manage` 权限 (普通管理员无法看到超管)      |
| 管理 | POST     | `/api/admin/upgrade-user`         | 升级普通用户权限       | 需 `user:upgrade` 权限 (仅限升级为 USER 或 PREMIUM) |
| 管理 | POST     | `/api/admin/promote-to-admin`     | 提拔为管理员/超管      | 需 `admin:promote` 权限 (仅限 SUPER_ADMIN 使用)     |
| 公共 | GET      | `/api/public/history/point`       | 查询单点单日历史温度   | 无 (需参数: lat, lon, date)                         |
| 公共 | GET      | `/api/public/history/point/range` | 查询单点日期范围温度   | 无 (需参数: lat, lon, start, end)                   |
| 公共 | GET      | `/api/public/history/region`      | 查询区域单日温度快照   | 无 (用于热力图，需经纬度范围及日期)                 |

> **注意**: 具体的请求参数和响应格式，请参考 API 文档或使用 Postman 等工具进行测试。