import os
import asyncio
import requests
import hashlib
import hmac
import base64
import time
from datetime import datetime
import urllib.parse
from typing import List, Dict, Any
from dotenv import load_dotenv
from .region_mapper import region_mapper, CloudProvider

# 加载环境变量
load_dotenv()


class AliyunAPI:
    """阿里云API客户端"""
    
    def __init__(self):
        """初始化阿里云API客户端"""
        self.access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        self.endpoint = 'https://ecs.cn-hangzhou.aliyuncs.com/'
    
    async def fetch_regions(self) -> List[Dict[str, Any]]:
        """获取阿里云可用区域列表"""
        try:
            # 构建API请求
            params = {
                'AccessKeyId': self.access_key_id,
                'Action': 'DescribeRegions',
                'Format': 'JSON',
                'SignatureMethod': 'HMAC-SHA1',
                'SignatureNonce': str(int(time.time() * 1000000)),
                'SignatureVersion': '1.0',
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'Version': '2014-05-26'
            }
            
            # 生成签名
            signature = self._generate_signature(params)
            params['Signature'] = signature
            
            # 构建完整URL
            query_string = '&'.join([f'{k}={urllib.parse.quote(str(v), safe="")}' for k, v in params.items()])
            url = f'{self.endpoint}?{query_string}'
            
            # 使用asyncio在线程池中运行同步请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, timeout=30)
            )
            
            response.raise_for_status()
            data = response.json()
            
            regions = []
            if 'Regions' in data and 'Region' in data['Regions']:
                for region in data['Regions']['Region']:
                    regions.append({
                        'region_id': region['RegionId'],
                        'region_name': region['LocalName'],
                        'country_code': region_mapper.get_country_code(CloudProvider.ALIYUN, region['RegionId']),
                        'raw_data': region
                    })
            
            return regions
            
        except Exception as e:
            print(f"Error fetching Aliyun regions: {e}")
            return []
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成阿里云API签名"""
        # 参数排序
        sorted_params = sorted(params.items())
        query_string = '&'.join([f'{k}={urllib.parse.quote(str(v), safe="")}' for k, v in sorted_params])
        
        # 构建待签名字符串
        string_to_sign = f'GET&{urllib.parse.quote("/", safe="")}&{urllib.parse.quote(query_string, safe="")}'
        
        # 计算签名
        signature = base64.b64encode(
            hmac.new(
                (self.access_key_secret + '&').encode(),
                string_to_sign.encode(),
                hashlib.sha1
            ).digest()
        ).decode()
        
        return signature
    
