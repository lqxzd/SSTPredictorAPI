from flask import Flask, jsonify
from config import Config
from extensions import db, jwt
from routes import register_routes

def create_app():
    """应用工厂模式"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    # 注册路由
    register_routes(app)

    # 全局异常处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(msg="资源未找到"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify(msg="服务器内部错误"), 500

    return app

if __name__ == '__main__':
    app = create_app()
    
    # 创建数据库表 (开发环境)
    with app.app_context():
        db.create_all()
        
    app.run(debug=True, host='127.0.0.1', port=3000)