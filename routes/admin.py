from flask import Blueprint, request, jsonify, g
from models import db, User
from utils.permissions import require_permission


admin_bp = Blueprint('admin', __name__)

# 1. 获取用户列表
@admin_bp.route('/users', methods=['GET'])
@require_permission('user:manage')
def get_users():
    current_role = g.current_role
    
    query = User.query
    
    # 如果是普通管理员，过滤掉超级管理员
    if current_role == 'ADMIN':
        query = query.filter(User.role != 'SUPER_ADMIN')
        
    users = query.all()
    
    return jsonify([
        {"id": u.id, "username": u.username, "role": u.role} 
        for u in users
    ]), 200

# 2. 升级用户权限
# --- 接口 1: 普通用户权限升级 (管理员 & 超管可用) ---
@admin_bp.route('/upgrade-user', methods=['POST'])
@require_permission('user:upgrade')
def upgrade_user():
    data = request.get_json()
    target_user_id = data.get('target_user_id')
    target_role = data.get('target_role')
    
    # 只能操作普通用户和高级用户
    if target_role not in ['USER', 'PREMIUM']:
        return jsonify(msg="该接口仅限管理普通用户和高级用户"), 400
        
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify(msg="用户不存在"), 404
        
    target_user.role = target_role
    db.session.commit()
    
    return jsonify(msg=f"用户权限已更新为 {target_role}"), 200

# --- 接口 2: 升级为管理员/超管 (仅超管可用) ---
@admin_bp.route('/promote-to-admin', methods=['POST'])
@require_permission('admin:promote')  # 只有 SUPER_ADMIN 有这个权限
def promote_to_admin():
    data = request.get_json()
    target_user_id = data.get('target_user_id')
    target_role = data.get('target_role')
    
    # 只能提拔为管理员或超管
    if target_role not in ['ADMIN', 'SUPER_ADMIN']:
        return jsonify(msg="该接口仅限提拔管理员或超级管理员"), 400
        
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify(msg="用户不存在"), 404
        
    target_user.role = target_role
    db.session.commit()
    
    return jsonify(msg=f"恭喜！用户 {target_user.username} 已晋升为 {target_role}"), 200