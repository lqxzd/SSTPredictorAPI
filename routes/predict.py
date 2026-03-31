from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from utils.permissions import require_permission
from services.predictor import predictor_service
from models import db, SSTPrediction # 引入模型用于保存

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/point', methods=['POST'])
@require_permission('point:predict')
def predict_point():
    """
    单点预测接口
    入参:
        lat: 纬度
        lon: 经度
        start_date: 开始日期 (YYYY-MM-DD)
        days: 预测天数 (最大90天)
    """
    data = request.get_json()
    
    # 1. 参数校验
    lat = data.get('lat')
    lon = data.get('lon')
    start_date_str = data.get('start_date')
    days = data.get('days', 1)
    
    if not all([lat, lon, start_date_str]):
        return jsonify(msg="缺少必要参数"), 400
        
    # 解析日期
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(msg="日期格式错误，应为 YYYY-MM-DD"), 400
        
    # 2. 业务规则校验
    # 限制预测时长不超过 3 个月 (90天)
    if days > 90:
        return jsonify(msg="单次预测时长不能超过 90 天"), 400
        
    # 限制预测时间不能太遥远 (例如不能超过 2025-12-31)
    max_date = datetime.strptime('2025-12-31', '%Y-%m-%d').date()
    if start_date > max_date:
        return jsonify(msg=f"预测开始时间不能晚于 {max_date}"), 400

    # 3. 调用预测服务
    # 这里的逻辑是：先查数据库有没有现成的预测，如果没有再调模型
    # 为了演示简单，这里直接调用模型计算
    result = predictor_service.predict_point(lat, lon, start_date, days)
    
    if "error" in result:
        return jsonify(msg=result["error"]), 400
        
    # 4. (可选) 保存到数据库
    # 如果需要持久化，取消下面注释
    # predictor_service.save_predictions(lat, lon, result['data'])
    
    return jsonify({
        "msg": "预测成功",
        "location": {"lat": lat, "lon": lon},
        "predictions": result['data']
    }), 200