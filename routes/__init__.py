# 导入蓝图
from .auth import auth_bp
from .admin import admin_bp
from .public import public_bp

def register_routes(app):
    """注册蓝图到应用"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(public_bp, url_prefix='/api/public')