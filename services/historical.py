import os
import xarray as xr
import redis
from datetime import datetime
from flask import current_app
from extensions import redis_client
from config import Config
import numpy as np

class HistoricalDataService:
    """
    历史数据服务类
    适配按年存储的 NetCDF 文件结构 (sst.day.mean.YYYY.nc)
    """

    def __init__(self):

        # 1. 获取当前文件 (historical.py) 的绝对路径
        current_file_path = os.path.abspath(__file__)

        # 2. 获取项目根目录 (即 historical.py 的上一级目录)
        # 目录结构是: project_root/services/historical.py
        project_root = os.path.dirname(os.path.dirname(current_file_path))

        # 3. 拼接出 data_store/sst_raw 的绝对路径
        self.data_dir = os.path.join(project_root, 'data_store', 'sst_raw')

        # print(f"📂 数据目录已初始化为: {self.data_dir}")


    def _get_file_path(self, date_obj):
        """
        根据日期对象确定应该读取哪个文件
        逻辑：
        - 2002-2013年: 单独文件 sst.day.mean.YYYY.nc
        - 2014-2023年: 混合文件 sst.day.mean.2014.nc
        """
        year = date_obj.year
        
        # 默认假设文件名就是年份
        target_year = year
        
        # 特殊处理：如果年份在 2014-2023 之间，根据你的描述，它们都在名为 2014 的文件里
        # 注意：这里硬编码了逻辑，如果实际文件名不是 2014.nc，请修改这里
        if 2014 <= year <= 2023:
            target_year = 2014 
            
        filename = f"sst.day.mean.{target_year}.nc"
        return os.path.join(self.data_dir, filename)

    def get_point_history(self, lat, lon, date_str):
        """
        获取指定点、指定日期的历史海温数据
        
        参数:
            lat (float): 纬度
            lon (float): 经度
            date_str (str): 日期字符串，支持两种格式:
                             1. 'YYYYMMDD' (如 '20140520')
                             2. 'YYYY-MM-DD' (如 '2014-05-20')
        """
        # 1. 解析日期字符串为 datetime 对象
        try:
            if len(date_str) == 8:
                # 处理 YYYYMMDD
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                # 标准化缓存 Key 为 YYYY-MM-DD
                cache_date_str = date_obj.strftime('%Y-%m-%d')
            else:
                # 处理 YYYY-MM-DD
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                cache_date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"❌ 日期格式错误: {date_str}")
            return None

        # 2. 构建缓存 Key
        cache_key = f"hist:point:{lat}:{lon}:{cache_date_str}"
        
        # 3. 查缓存
        cached_data = redis_client.get(cache_key)
        if cached_data is not None:
            print(f"✅ 命中缓存: {cache_key}")
            return float(cached_data)

        # 4. 缓存未命中，读取文件
        try:
            # A. 确定文件路径
            file_path = self._get_file_path(date_obj)
            
            if not os.path.exists(file_path):
                print(f"⚠️ 文件不存在: {file_path}")
                return None

            # B. 打开 NetCDF 文件
            with xr.open_dataset(file_path) as ds:
                # C. 提取数据
                # 关键点：xarray 的 sel 方法非常强大
                # 如果文件里的时间维度是 datetime 类型，我们可以直接传字符串 '2014-05-20'
                # method='nearest' 确保即使日期有微小偏差也能找到最近的一天
                
                # 假设变量名为 'sst'，时间维度名为 'time'
                # 注意：这里我们直接用解析好的 date_obj 或者字符串去匹配 time 维度
                point_data = ds['sst'].sel(
                    time=date_obj, 
                    lat=lat, 
                    lon=lon, 
                    method='nearest'
                )
                
                temp_value = float(point_data.values)
                
                # 处理 NaN (无效值)
                if temp_value != temp_value: # NaN 的自我判断方法
                     return None

                # D. 写入缓存
                redis_client.setex(cache_key, Config.CACHE_DEFAULT_TIMEOUT, temp_value)
                print(f"💾 已存入缓存: {cache_key} -> {temp_value}")
                
                return temp_value

        except KeyError as e:
            print(f"❌ 数据集中缺少维度或变量: {e}")
            return None
        except Exception as e:
            print(f"❌ 读取文件出错: {e}")
            return None

    def get_point_range(self, lat, lon, start_date_str, end_date_str):
        """
        获取指定点、指定日期范围的历史数据
        支持跨年查询（例如从 2013年 到 2014年）
        """
        # 1. 解析日期
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            print(f"❌ 日期格式错误")
            return None

        all_data = []
        
        # 2. 确定需要读取哪些文件
        # 逻辑：
        # - 2002-2013: 每年一个文件 sst.day.mean.YYYY.nc
        # - 2014-2023: 所有数据都在 sst.day.mean.2014.nc
        
        # 获取起始年份和结束年份
        start_year = start_date.year
        end_year = end_date.year
        
        # 构建需要读取的文件列表
        # 这是一个简单的集合，防止重复读取（比如起止都在2014-2023区间）
        files_to_process = set()
        
        for y in range(start_year, end_year + 1):
            if 2014 <= y <= 2023:
                # 如果是 2014-2023 之间的年份，统一指向 2014 那个文件
                files_to_process.add(2014)
            else:
                # 其他年份，指向对应的年份文件
                files_to_process.add(y)
        
        # 3. 循环读取文件
        for target_year in sorted(files_to_process):
            file_path = os.path.join(self.data_dir, f"sst.day.mean.{target_year}.nc")
            
            if not os.path.exists(file_path):
                print(f"⚠️ 文件不存在: {file_path}")
                continue

            try:
                with xr.open_dataset(file_path) as ds:
                    # --- 核心逻辑：分步切片 ---
                    
                    # A. 先锁定空间位置 (经纬度)
                    # 注意：这里不能用 method='nearest' 配合时间切片，所以先选点
                    point_series = ds['sst'].sel(lat=lat, lon=lon, method='nearest')
                    
                    # B. 确定当前文件的时间切片范围
                    # 我们需要计算：查询范围 [start, end] 和 当前文件年份范围 的交集
                    
                    # 当前文件的年份边界
                    file_start = f"{target_year}-01-01"
                    file_end = f"{target_year}-12-31"
                    
                    # 实际查询的边界（取交集）
                    # 如果查询是从 2013-12-30 开始，而当前文件是 2014.nc
                    # 那么在这个文件里，我们应该从 2014-01-01 开始查
                    query_start_in_file = max(start_date_str, file_start)
                    query_end_in_file = min(end_date_str, file_end)
                    
                    # C. 使用 .loc 进行时间切片
                    # 只有当查询范围在当前文件范围内时才执行
                    if query_start_in_file <= query_end_in_file:
                        range_data = point_series.loc[query_start_in_file:query_end_in_file]
                        
                        # D. 解析数据
                        for t, val in zip(range_data['time'].values, range_data.values):
                            # 过滤 NaN
                            if not np.isnan(val):
                                date_str = str(t).split('T')[0] 
                                all_data.append({
                                    "date": date_str,
                                    "temperature": float(val)
                                })

            except Exception as e:
                print(f"❌ 读取文件 {file_path} 出错: {e}")
                import traceback
                traceback.print_exc()

        # 4. 返回结果
        if not all_data:
            return None
            
        # 按日期排序（防止跨年读取顺序错乱）
        all_data.sort(key=lambda x: x['date'])
        return all_data

    def get_region_snapshot(self, lat_min, lat_max, lon_min, lon_max, date_str):
        """
        [新增功能] 获取指定区域、指定日期的海温数据（热力图数据）
        """
        # 1. 解析日期
        try:
             if len(date_str) == 8:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
             else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None

        # 2. 定位文件
        file_path = self._get_file_path(date_obj)
        if not os.path.exists(file_path):
            return None

        try:
            with xr.open_dataset(file_path) as ds:
                # 切片获取区域数据
                # 注意：为了性能，这里不要返回所有网格点，xarray会自动处理切片
                region_data = ds['sst'].sel(
                    time=date_obj,
                    lat=slice(lat_min, lat_max),
                    lon=slice(lon_min, lon_max)
                )
                
                # 将 xarray 数据转换为字典列表，方便前端解析
                # 格式: [ {lat: ..., lon: ..., temp: ...}, ... ]
                result = []
                # 使用 to_dataframe 或者直接迭代
                df = region_data.to_dataframe().reset_index()
                # 过滤掉 NaN
                df = df.dropna()
                
                # 限制返回数量，防止前端卡死 (例如最多返回 1000 个点)
                if len(df) > 1000:
                    df = df.sample(n=1000)

                for _, row in df.iterrows():
                    result.append({
                        "lat": row['lat'],
                        "lon": row['lon'],
                        "temp": float(row['sst'])
                    })
                    
                return result

        except Exception as e:
            print(f"❌ 区域查询出错: {e}")
            return None

# 实例化
history_service = HistoricalDataService()