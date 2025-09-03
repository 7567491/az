import os
import asyncio
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LinodeAPI:
    """Linode API客户端"""
    
    def __init__(self):
        """初始化Linode API客户端"""
        self.base_url = 'https://api.linode.com/v4'
        self.token = os.getenv('LINODE_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    async def fetch_regions(self) -> List[Dict[str, Any]]:
        """获取Linode可用区域列表"""
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
            for region in data.get('data', []):
                if region.get('status') == 'ok' and 'Linodes' in region.get('capabilities', []):
                    regions.append({
                        'region_id': region['id'],
                        'region_name': region['label'],
                        'country_code': self._map_region_to_country(region['id']),
                        'raw_data': region
                    })
            
            return regions
            
        except Exception as e:
            print(f"Error fetching Linode regions: {e}")
            return []
    
    def _map_region_to_country(self, region_id: str) -> str:
        """将Linode区域ID映射到国家代码"""
        # Linode区域到国家的映射
        region_mapping = {
            'us-east': 'US', 'us-central': 'US', 'us-west': 'US',
            'us-southeast': 'US', 'us-lax': 'US', 'us-mia': 'US',
            'ca-central': 'CA', 
            'eu-west': 'GB', 'eu-central': 'DE', 'eu-south': 'IT',
            'ap-south': 'SG', 'ap-northeast': 'JP', 'ap-southeast': 'AU',
            'ap-west': 'IN'
        }
        
        return region_mapping.get(region_id, 'US')  # 默认美国
