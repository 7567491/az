import asyncio
from typing import Dict, List, Any
from .linode_api import LinodeAPI
from .digitalocean_api import DigitalOceanAPI
from .aliyun_api import AliyunAPI
from .tencent_api import TencentAPI


class CloudAPICollector:
    """云服务API数据收集器"""
    
    def __init__(self):
        """初始化收集器，创建各个云服务API实例"""
        self.providers = {
            'linode': LinodeAPI(),
            'digitalocean': DigitalOceanAPI(),
            'aliyun': AliyunAPI(),
            'tencent': TencentAPI()
        }
    
    async def collect_all_regions(self) -> Dict[str, List[Dict[str, Any]]]:
        """异步收集所有云服务商的区域数据"""
        results = {}
        
        # 创建异步任务
        tasks = []
        for provider_name, api_client in self.providers.items():
            task = asyncio.create_task(
                self._collect_provider_regions(provider_name, api_client)
            )
            tasks.append(task)
        
        # 等待所有任务完成
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, (provider_name, _) in enumerate(self.providers.items()):
            result = completed_results[i]
            if isinstance(result, Exception):
                print(f"Error collecting {provider_name} regions: {result}")
                results[provider_name] = []
            else:
                results[provider_name] = result
        
        return results
    
    async def _collect_provider_regions(self, provider_name: str, api_client) -> List[Dict[str, Any]]:
        """收集单个云服务商的区域数据"""
        try:
            regions = await api_client.fetch_regions()
            print(f"Successfully collected {len(regions)} regions from {provider_name}")
            return regions
        except Exception as e:
            print(f"Failed to collect regions from {provider_name}: {e}")
            return []
    
    def update_database(self, db_manager, regions_data: Dict[str, List[Dict[str, Any]]]):
        """将收集的数据更新到数据库"""
        for provider_name, regions in regions_data.items():
            try:
                # 获取或创建provider
                provider = db_manager.get_provider_by_name(provider_name)
                if not provider:
                    print(f"Provider {provider_name} not found in database")
                    continue
                
                # 更新区域数据（带去重）
                updated_count = 0
                for region_data in regions:
                    az = self._create_availability_zone(provider.id, region_data)
                    if az:
                        az_id = db_manager.create_availability_zone(az)
                        if az_id:
                            updated_count += 1
                
                print(f"Updated {updated_count} regions for {provider_name}")
                
                # 记录更新日志
                from database.models import UpdateLog
                log = UpdateLog(
                    provider_id=provider.id,
                    status='success',
                    message=f'Updated {len(regions)} regions'
                )
                db_manager.create_update_log(log)
                
            except Exception as e:
                print(f"Error updating database for {provider_name}: {e}")
                # 记录错误日志
                if provider:
                    from database.models import UpdateLog
                    log = UpdateLog(
                        provider_id=provider.id,
                        status='error',
                        message=str(e)
                    )
                    db_manager.create_update_log(log)
    
    def _clean_old_regions(self, db_manager, provider_id: int):
        """清理指定提供商的旧区域数据"""
        import sqlite3
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM availability_zones WHERE provider_id = ?
            ''', (provider_id,))
            conn.commit()
            print(f"Cleaned old regions for provider {provider_id}")
        except sqlite3.Error as e:
            print(f"Error cleaning old regions: {e}")
        finally:
            conn.close()
    
    def _create_availability_zone(self, provider_id: int, region_data: Dict[str, Any]):
        """根据区域数据创建AvailabilityZone对象"""
        try:
            from database.models import AvailabilityZone
            
            # 确定大洲
            continent = self._map_country_to_continent(region_data['country_code'])
            
            return AvailabilityZone(
                provider_id=provider_id,
                region_id=region_data['region_id'],
                region_name=region_data['region_name'],
                country_code=region_data['country_code'],
                continent=continent,
                status='available'
            )
        except KeyError as e:
            print(f"Missing required field in region data: {e}")
            return None
    
    def _map_country_to_continent(self, country_code: str) -> str:
        """将国家代码映射到大洲"""
        # 简化的映射表，实际项目中应该更完整
        continent_mapping = {
            # 美洲
            'US': 'americas', 'CA': 'americas', 'BR': 'americas', 'MX': 'americas',
            # 欧洲-非洲
            'GB': 'europe-africa', 'DE': 'europe-africa', 'FR': 'europe-africa',
            'NL': 'europe-africa', 'IT': 'europe-africa', 'ES': 'europe-africa',
            'PL': 'europe-africa', 'ZA': 'europe-africa',
            # 亚太
            'CN': 'apac', 'JP': 'apac', 'SG': 'apac', 'AU': 'apac', 'IN': 'apac',
            'KR': 'apac', 'HK': 'apac', 'TH': 'apac', 'ID': 'apac', 'MY': 'apac',
            'PH': 'apac', 'AE': 'apac'
        }
        
        return continent_mapping.get(country_code.upper(), 'apac')  # 默认为亚太
