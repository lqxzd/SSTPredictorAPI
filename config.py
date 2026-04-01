import os

class Config:
    """应用配置类"""
    
    # 密钥：用于加密 Session 和 JWT，生产环境请使用环境变量
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'

    # 数据库配置 (MySQL)
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    # 请根据实际情况修改下方字符串
    DB_USER = 'root'
    DB_PASSWORD = 'zerodata'
    DB_HOST = '127.0.0.1'
    DB_PORT = '3306'
    DB_NAME = 'sst_db'

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    
    # 关闭每次请求结束后的修改追踪，节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # --- 新增 Redis 配置 ---
    # Redis 数据库配置
    # 假设 Redis 运行在本地默认端口 6379
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0  # 使用 Redis 的第 0 号数据库
    
    # 缓存过期时间（秒），这里设置为 1 小时
    # 这样可以保证数据不会永久占用内存，同时又能利用缓存加速重复查询
    CACHE_DEFAULT_TIMEOUT = 3600



    # --- RBAC 权限配置 ---
    # 定义每个角色拥有的权限列表
    PERMISSIONS_MAP = {
        'SUPER_ADMIN': ['*'],  # 通配符，拥有所有权限
        'ADMIN': [
            'point:predict', 
            'area:predict', 
            'user:manage', 
            'user:upgrade'
        ],
        'PREMIUM': [
            'point:predict', 
            'area:predict'
        ],
        'USER': [
            'point:predict'
        ]
    }

    # --- 许可证配置 ---
    # 用于特权注册
    ADMIN_LICENSE_KEY = "admin_pass_123"
    SUPER_ADMIN_LICENSE_KEY = "super_admin_pass_456"



    # --- 前端路由/菜单配置 ---
    # 定义每个角色可见的路由和菜单结构
    # 这里的结构可以直接对应前端 Vue Router 或 ElementUI Menu 的结构
    ROUTE_MAP = {
        'SUPER_ADMIN': [
            {'path': '/dashboard', 'name': '仪表盘', 'icon': 'DataAnalysis'},
            {'path': '/predict/point', 'name': '单点预测', 'icon': 'MapLocation'},
            {'path': '/predict/area', 'name': '区域预测', 'icon': 'Odometer'},
            {'path': '/system/users', 'name': '用户管理', 'icon': 'User'},
            {'path': '/system/logs', 'name': '系统日志', 'icon': 'Document'}
        ],
        'ADMIN': [
            {'path': '/dashboard', 'name': '仪表盘', 'icon': 'DataAnalysis'},
            {'path': '/predict/point', 'name': '单点预测', 'icon': 'MapLocation'},
            {'path': '/predict/area', 'name': '区域预测', 'icon': 'Odometer'},
            {'path': '/system/users', 'name': '用户管理', 'icon': 'User'}
            # 注意：管理员看不到系统日志
        ],
        'PREMIUM': [
            {'path': '/dashboard', 'name': '仪表盘', 'icon': 'DataAnalysis'},
            {'path': '/predict/point', 'name': '单点预测', 'icon': 'MapLocation'},
            {'path': '/predict/area', 'name': '区域预测', 'icon': 'Odometer'}
        ],
        'USER': [
            {'path': '/dashboard', 'name': '仪表盘', 'icon': 'DataAnalysis'},
            {'path': '/predict/point', 'name': '单点预测', 'icon': 'MapLocation'}
            # 普通用户只能看点预测，看不到区域预测
        ]
    }