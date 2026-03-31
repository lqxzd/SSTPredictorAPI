from datetime import timedelta
from models import db, SSTPrediction
import numpy as np
# 假设你有一个模型文件，这里先模拟加载
# from my_model_lib import load_model 

class SSTPredictor:
    def __init__(self):
        # 配置参数
        self.LOOKBACK_DAYS = 30  # 模型需要过去30天的数据
        # self.model = load_model('path/to/model.h5') # 后期在这里加载你的真实模型
        print("🤖 预测器已初始化")

    def get_history_data(self, lat, lon, end_date, days):
        """
        从数据库获取历史数据
        返回: List[float] 温度列表
        """
        start_date = end_date - timedelta(days=days)
        
        # 查询数据库 (这里假设你还有一个存实测数据的表，比如 SSTObservation)
        # 为了演示，我先查询预测表里的 'observed' 数据，你需要根据实际情况修改查询源
        records = SSTPrediction.query.filter(
            SSTPrediction.latitude == lat,
            SSTPrediction.longitude == lon,
            SSTPrediction.date >= start_date,
            SSTPrediction.date < end_date, # 不包含 end_date 当天
            SSTPrediction.source_type == 'observed' 
        ).order_by(SSTPrediction.date).all()
        
        # 提取温度值
        temps = [r.temperature for r in records]
        # return temps

        # 暂时返回随机数数组
        return [18.5 + i*0.1 for i in range(days)]

    def model_inference(self, input_sequence):
        """
        [核心] 模型推理接口
        这里目前返回一个随机值模拟，后期替换为你的 model.predict()
        """
        # 模拟逻辑：在输入序列最后一个值的基础上加一点随机波动
        last_temp = input_sequence[-1]
        noise = np.random.normal(0, 0.1) 
        predicted_temp = last_temp + noise
        return float(predicted_temp)

    def predict_point(self, lat, lon, start_date, days_to_predict):
        """
        执行单点预测
        逻辑：滑动窗口递归预测
        """
        results = []
        
        # 1. 获取初始历史数据 (过去 30 天)
        # 注意：start_date 前一天作为历史的终点
        history_end = start_date
        history_data = self.get_history_data(lat, lon, history_end, self.LOOKBACK_DAYS)
        
        if len(history_data) < self.LOOKBACK_DAYS:
            return {"error": f"历史数据不足，需要至少 {self.LOOKBACK_DAYS} 天数据，当前仅有 {len(history_data)} 天"}

        # 将历史数据转为列表以便操作
        current_window = history_data.copy()

        # 2. 递归预测循环
        for i in range(days_to_predict):
            # A. 推理：使用当前窗口预测下一天
            next_day_temp = self.model_inference(current_window)
            
            # B. 记录结果
            current_date = start_date + timedelta(days=i)
            results.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "temperature": round(next_day_temp, 4)
            })
            
            # C. 更新窗口 (滑动)：把预测出的新值加入窗口，移除最旧的值
            current_window.append(next_day_temp)
            current_window.pop(0) # 保持窗口大小为 30

        return {"data": results}

    def save_predictions(self, lat, lon, predictions_data):
        """
        将预测结果存入数据库
        """
        for item in predictions_data:
            pred = SSTPrediction(
                latitude=lat,
                longitude=lon,
                date=item['date'],
                temperature=item['temperature'],
                source_type='predicted'
            )
            db.session.add(pred)
        
        try:
            db.session.commit()
            print(f"✅ 已保存 {len(predictions_data)} 条预测数据")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 保存失败: {e}")

# 全局单例
predictor_service = SSTPredictor()