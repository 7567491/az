import os
import asyncio
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from .region_mapper import region_mapper, CloudProvider

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
                        'country_code': region_mapper.get_country_code(CloudProvider.LINODE, region['id']),
                        'raw_data': region
                    })
            
            return regions
            
        except Exception as e:
            print(f"Error fetching Linode regions: {e}")
            return []
