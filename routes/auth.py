from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token
from config import Config

auth_bp = Blueprint('auth', __name__)

# 1. 普通用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # 校验用户名
    if User.query.filter_by(username=username).first():
        return jsonify(msg="用户名已存在"), 400
    
    # 校验邮箱
    if User.query.filter_by(email=email).first():
        return jsonify(msg="邮箱已被注册"), 400

    # 创建用户 (只传 username 和 email)
    user = User(username=username, email=email)
    # 使用模型自带的方法设置密码
    user.set_password(password)
    
    # 默认角色是 'USER' (模型定义里已经有 default='USER' 了，这里可以不写)
    # user.role = 'USER' 

    db.session.add(user)
    db.session.commit()

    return jsonify(msg="注册成功，请登录"), 201



# 2. 特权注册 (使用许可证)
@auth_bp.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email') # 特权注册也需要邮箱
    password = data.get('password')
    license_key = data.get('license_key')
    
    if not license_key:
        return jsonify(msg="许可证不能为空"), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify(msg="用户名已存在"), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify(msg="邮箱已被注册"), 400
        
    # 校验许可证并分配角色
    target_role = None
    if license_key == Config.SUPER_ADMIN_LICENSE_KEY:
        target_role = 'SUPER_ADMIN'
    elif license_key == Config.ADMIN_LICENSE_KEY:
        target_role = 'ADMIN'
    else:
        return jsonify(msg="无效的许可证"), 400
        
    # 创建用户
    new_user = User(username=username, email=email, role=target_role)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(msg=f"注册成功，角色为 {target_role}"), 201



# 3. 登录 (返回权限列表)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()

    
    
    # 使用模型自带的方法验证密码
    if not user or not user.check_password(password):
        return jsonify(msg="用户名或密码错误"), 401
    
    user_identity = str(user.id)
        
    # 生成 JWT Token
    access_token = create_access_token(identity=user_identity, additional_claims={"role": user.role})
    
    # 计算用户的权限列表返回给前端
    permissions = Config.PERMISSIONS_MAP.get(user.role, [])
    user_routes = Config.ROUTE_MAP.get(user.role, [])
    
    return jsonify({
        "token": access_token,
        "user_info": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "routes": user_routes
        }
    }), 200