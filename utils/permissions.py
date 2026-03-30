from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from config import Config

def require_permission(permission_code):
    """
    权限校验装饰器
    用法: @require_permission('user:manage')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. 验证 JWT Token 是否有效
            verify_jwt_in_request()
            
            # 2. 获取当前用户的 claims (包含 role)
            claims = get_jwt()
            current_role = claims.get("role")
            
            # 3. 获取该角色的权限列表
            user_permissions = Config.PERMISSIONS_MAP.get(current_role, [])
            
            # 4. 权限检查
            # 如果是超级管理员 (*) 或者 包含具体权限码，则通过
            if '*' in user_permissions or permission_code in user_permissions:
                # 将当前用户信息存入 g 对象，方便后续函数使用
                g.current_role = current_role
                return f(*args, **kwargs)
            else:
                return jsonify(msg="权限不足，无法访问该资源"), 403
                
        return decorated_function
    return decorator