import os
import asyncio
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DigitalOceanAPI:
    """DigitalOcean API客户端"""
    
    def __init__(self):
        """初始化DigitalOcean API客户端"""
        self.base_url = 'https://api.digitalocean.com/v2'
        self.token = os.getenv('DIGITALOCEAN_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    async def fetch_regions(self) -> List[Dict[str, Any]]:
        """获取DigitalOcean可用区域列表"""
        try:
            # 使用asyncio在线程池中运行同步请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f'{self.base_url}/regions',
                    headers=self.headers,
                    timeout=30
                )
            )
            
            response.raise_for_status()
            data = response.json()
            
            regions = []
            for region in data.get('regions', []):
                if region.get('available', False):
                    regions.append({
                        'region_id': region['slug'],
                        'region_name': region['name'], 
                        'country_code': self._map_region_to_country(region['slug']),
                        'raw_data': region
                    })
            
            return regions
            
        except Exception as e:
            print(f"Error fetching DigitalOcean regions: {e}")
            return []
    
    def _map_region_to_country(self, region_slug: str) -> str:
        """将DigitalOcean区域slug映射到国家代码"""
        # DigitalOcean区域到国家的映射
        region_mapping = {
            'nyc1': 'US', 'nyc2': 'US', 'nyc3': 'US',
            'sfo1': 'US', 'sfo2': 'US', 'sfo3': 'US',
            'tor1': 'CA',
            'lon1': 'GB',
            'fra1': 'DE',
            'ams2': 'NL', 'ams3': 'NL',
            'sgp1': 'SG',
            'blr1': 'IN',
            'syd1': 'AU'
        }
        
        return region_mapping.get(region_slug, 'US')  # 默认美国
