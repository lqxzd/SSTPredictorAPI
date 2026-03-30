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