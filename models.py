from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    """
    用户模型
    用于存储用户信息、权限状态和账号状态
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 角色: 'user' (普通), 'premium' (高级), 'admin' (管理员), 'superAdmin'
    role = db.Column(db.String(20), nullable=False, default='USER')
    
    # 账号是否激活 (用于封禁功能)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class SSTPrediction(db.Model):
    """
    SST 预测结果存储表
    用于存储模型生成的预测数据
    """
    __tablename__ = 'sst_predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False, index=True)  # 纬度
    longitude = db.Column(db.Float, nullable=False, index=True) # 经度
    date = db.Column(db.Date, nullable=False, index=True)       # 预测日期
    temperature = db.Column(db.Float, nullable=False)           # 预测温度
    
    # 数据来源: 'observed' (实测/历史), 'predicted' (模型预测)
    # 注意：虽然这个表主要存预测，但为了查询方便，也可以存实测做缓存
    source_type = db.Column(db.String(20), nullable=False, default='predicted')
    
    # 记录这条数据是什么时候生成的（用于判断预测是否过期）
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def __repr__(self):
        return f'<SSTPrediction {self.latitude},{self.longitude} on {self.date}>'