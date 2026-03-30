from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import redis

# 初始化数据库对象
db = SQLAlchemy()

# 初始化 JWT 管理器
jwt = JWTManager()

# --- 新增 Redis 客户端初始化 ---
# decode_responses=True 表示自动将字节数据解码为字符串，方便调试和存储 JSON
redis_client = redis.Redis(decode_responses=True)