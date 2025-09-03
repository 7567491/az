import os
import asyncio
import requests
import hashlib
import hmac
import json
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TencentAPI:
    """腾讯云API客户端"""
    
    def __init__(self):
        """初始化腾讯云API客户端"""
        self.secret_id = os.getenv('TENCENT_SECRET_ID')
        self.secret_key = os.getenv('TENCENT_SECRET_KEY')
        self.endpoint = 'https://cvm.tencentcloudapi.com/'
        self.service = 'cvm'
        self.version = '2017-03-12'
        self.action = 'DescribeRegions'
    
    async def fetch_regions(self) -> List[Dict[str, Any]]:
        """获取腾讯云可用区域列表"""
        try:
            # 生成请求头和签名
            headers = self._generate_headers()
            payload = '{}'
            
            # 使用asyncio在线程池中运行同步请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    self.endpoint,
                    headers=headers,
                    data=payload,
                    timeout=30
                )
            )
            
            response.raise_for_status()
            data = response.json()
            
            regions = []
            if 'Response' in data and 'RegionSet' in data['Response']:
                for region in data['Response']['RegionSet']:
                    if region.get('RegionState') == 'AVAILABLE':
                        regions.append({
                            'region_id': region['Region'],
                            'region_name': region['RegionName'],
                            'country_code': self._map_region_to_country(region['Region']),
                            'raw_data': region
                        })
            
            return regions
            
        except Exception as e:
            print(f"Error fetching Tencent regions: {e}")
            return []
    
    def _generate_headers(self) -> Dict[str, str]:
        """生成腾讯云API请求头和签名"""
        timestamp = int(time.time())
        date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
        
        # 步骤1：拼接规范请求串
        http_request_method = 'POST'
        canonical_uri = '/'
        canonical_querystring = ''
        canonical_headers = f'content-type:application/json; charset=utf-8\nhost:cvm.tencentcloudapi.com\nx-tc-action:{self.action.lower()}\nx-tc-timestamp:{timestamp}\nx-tc-version:{self.version}\n'
        signed_headers = 'content-type;host;x-tc-action;x-tc-timestamp;x-tc-version'
        payload = '{}'
        hashed_request_payload = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_request = f'{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}'

        # 步骤2：拼接待签名字符串
        algorithm = 'TC3-HMAC-SHA256'
        credential_scope = f'{date}/{self.service}/tc3_request'
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f'{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}'

        # 步骤3：计算签名
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        secret_date = sign(('TC3' + self.secret_key).encode('utf-8'), date)
        secret_service = sign(secret_date, self.service)
        secret_signing = sign(secret_service, 'tc3_request')
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # 步骤4：拼接Authorization
        authorization = f'{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

        return {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'cvm.tencentcloudapi.com',
            'X-TC-Action': self.action,
            'X-TC-Timestamp': str(timestamp),
            'X-TC-Version': self.version
        }
    
    def _map_region_to_country(self, region_id: str) -> str:
        """将腾讯云区域ID映射到国家代码"""
        # 腾讯云区域到国家的映射
        region_mapping = {
            'ap-beijing': 'CN', 'ap-chengdu': 'CN', 'ap-chongqing': 'CN',
            'ap-guangzhou': 'CN', 'ap-shanghai': 'CN', 'ap-nanjing': 'CN',
            'ap-hongkong': 'HK',
            
            'ap-singapore': 'SG', 'ap-bangkok': 'TH', 'ap-jakarta': 'ID',
            'ap-seoul': 'KR', 'ap-tokyo': 'JP',
            
            'na-siliconvalley': 'US', 'na-ashburn': 'US', 'na-toronto': 'CA',
            'sa-saopaulo': 'BR',
            
            'eu-frankfurt': 'DE', 'eu-moscow': 'RU'
        }
        
        return region_mapping.get(region_id, 'CN')  # 默认中国
