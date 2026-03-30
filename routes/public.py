from flask import Blueprint, request, jsonify
from services.historical import history_service

public_bp = Blueprint('public', __name__)

# --- 单点单日查询接口 ---
@public_bp.route('/history/point', methods=['GET'])
def get_point_history():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    date_str = request.args.get('date', type=str) # 支持 YYYYMMDD 或 YYYY-MM-DD

    if not lat or not lon or not date_str:
        return jsonify(msg="缺少必要参数：lat, lon, date"), 400

    temperature = history_service.get_point_history(lat, lon, date_str)

    if temperature is None:
        return jsonify(msg="未找到该日期的数据或读取失败"), 404

    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "date": date_str,
        "temperature": temperature,
        "unit": "°C"
    })

# --- 单点日期范围查询接口 ---
@public_bp.route('/history/point/range', methods=['GET'])
def get_point_range():
    """
    查询某点在某段时间内的温度序列
    URL: /api/public/history/point/range?lat=20.5&lon=120.5&start=2014-01-01&end=2014-01-10
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    start_date = request.args.get('start', type=str)
    end_date = request.args.get('end', type=str)

    if not all([lat, lon, start_date, end_date]):
        return jsonify(msg="缺少参数"), 400

    # 调用服务层
    data_list = history_service.get_point_range(lat, lon, start_date, end_date)

    if not data_list:
        return jsonify(msg="查询范围内无数据"), 404

    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "count": len(data_list),
        "data": data_list
    })

# --- 区域单日快照查询接口 ---
@public_bp.route('/history/region', methods=['GET'])
def get_region_snapshot():
    """
    查询某区域某天的温度分布 (用于画热力图)
    URL: /api/public/history/region?lat_min=10&lat_max=20&lon_min=100&lon_max=110&date=2014-05-20
    """
    lat_min = request.args.get('lat_min', type=float)
    lat_max = request.args.get('lat_max', type=float)
    lon_min = request.args.get('lon_min', type=float)
    lon_max = request.args.get('lon_max', type=float)
    date_str = request.args.get('date', type=str)

    if not all([lat_min, lat_max, lon_min, lon_max, date_str]):
        return jsonify(msg="缺少参数"), 400

    # 调用服务层
    data_list = history_service.get_region_snapshot(lat_min, lat_max, lon_min, lon_max, date_str)

    if not data_list:
        return jsonify(msg="区域无数据"), 404

    return jsonify({
        "date": date_str,
        "count": len(data_list),
        "data": data_list # 包含大量 {lat, lon, temp} 对象
    })