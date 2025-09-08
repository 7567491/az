#!/usr/bin/env python3
"""
通用区域映射器 - 消除代码重复
基于TDD重构，为所有云服务商提供统一的区域映射逻辑
"""
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class CloudProvider(Enum):
    """云服务提供商枚举"""
    LINODE = "linode"
    DIGITALOCEAN = "digitalocean"
    ALIYUN = "aliyun"
    TENCENT = "tencent"


@dataclass
class RegionInfo:
    """区域信息数据类"""
    region_id: str
    country_code: str
    display_name: str = ""
    continent: Optional[str] = None


class UnifiedRegionMapper:
    """统一区域映射器 - 消除各云服务商的重复映射逻辑"""
    
    def __init__(self):
        """初始化映射器，加载所有云服务商的区域映射"""
        self._region_mappings = self._initialize_mappings()
    
    def _initialize_mappings(self) -> Dict[CloudProvider, Dict[str, RegionInfo]]:
        """初始化所有云服务商的区域映射"""
        return {
            CloudProvider.LINODE: self._get_linode_mappings(),
            CloudProvider.DIGITALOCEAN: self._get_digitalocean_mappings(), 
            CloudProvider.ALIYUN: self._get_aliyun_mappings(),
            CloudProvider.TENCENT: self._get_tencent_mappings(),
        }
    
    def _get_linode_mappings(self) -> Dict[str, RegionInfo]:
        """获取Linode区域映射 - 基于TDD完善的映射"""
        return {
            # 美国区域
            'us-east': RegionInfo('us-east', 'US', 'Newark, NJ'),
            'us-central': RegionInfo('us-central', 'US', 'Dallas, TX'),
            'us-west': RegionInfo('us-west', 'US', 'Fremont, CA'),
            'us-southeast': RegionInfo('us-southeast', 'US', 'Atlanta, GA'),
            'us-ord': RegionInfo('us-ord', 'US', 'Chicago, IL'),
            'us-lax': RegionInfo('us-lax', 'US', 'Los Angeles, CA'),
            'us-mia': RegionInfo('us-mia', 'US', 'Miami, FL'),
            'us-sea': RegionInfo('us-sea', 'US', 'Seattle, WA'),
            'us-iad': RegionInfo('us-iad', 'US', 'Washington, DC'),
            
            # 加拿大区域
            'ca-central': RegionInfo('ca-central', 'CA', 'Toronto, CA'),
            
            # 欧洲区域
            'eu-west': RegionInfo('eu-west', 'GB', 'London, UK'),
            'eu-central': RegionInfo('eu-central', 'DE', 'Frankfurt, DE'),
            'de-fra-2': RegionInfo('de-fra-2', 'DE', 'Frankfurt 2, DE'),
            'fr-par': RegionInfo('fr-par', 'FR', 'Paris, FR'),
            'it-mil': RegionInfo('it-mil', 'IT', 'Milan, IT'),
            'nl-ams': RegionInfo('nl-ams', 'NL', 'Amsterdam, NL'),
            'se-sto': RegionInfo('se-sto', 'SE', 'Stockholm, SE'),
            'gb-lon': RegionInfo('gb-lon', 'GB', 'London 2, UK'),
            'es-mad': RegionInfo('es-mad', 'ES', 'Madrid, ES'),
            
            # 亚太区域
            'ap-south': RegionInfo('ap-south', 'SG', 'Singapore, SG'),
            'ap-northeast': RegionInfo('ap-northeast', 'JP', 'Tokyo 2, JP'),
            'ap-southeast': RegionInfo('ap-southeast', 'AU', 'Sydney, AU'),
            'ap-west': RegionInfo('ap-west', 'IN', 'Mumbai, IN'),
            'au-mel': RegionInfo('au-mel', 'AU', 'Melbourne, AU'),
            'sg-sin-2': RegionInfo('sg-sin-2', 'SG', 'Singapore 2, SG'),
            'jp-osa': RegionInfo('jp-osa', 'JP', 'Osaka, JP'),
            'jp-tyo-3': RegionInfo('jp-tyo-3', 'JP', 'Tokyo 3, JP'),
            'in-bom-2': RegionInfo('in-bom-2', 'IN', 'Mumbai 2, IN'),
            'in-maa': RegionInfo('in-maa', 'IN', 'Chennai, IN'),
            'id-cgk': RegionInfo('id-cgk', 'ID', 'Jakarta, ID'),
            
            # 南美区域
            'br-gru': RegionInfo('br-gru', 'BR', 'São Paulo, BR'),
        }
    
    def _get_digitalocean_mappings(self) -> Dict[str, RegionInfo]:
        """获取DigitalOcean区域映射"""
        return {
            'nyc1': RegionInfo('nyc1', 'US', 'New York 1'),
            'nyc2': RegionInfo('nyc2', 'US', 'New York 2'),
            'nyc3': RegionInfo('nyc3', 'US', 'New York 3'),
            'sfo1': RegionInfo('sfo1', 'US', 'San Francisco 1'),
            'sfo2': RegionInfo('sfo2', 'US', 'San Francisco 2'),
            'sfo3': RegionInfo('sfo3', 'US', 'San Francisco 3'),
            'tor1': RegionInfo('tor1', 'CA', 'Toronto 1'),
            'lon1': RegionInfo('lon1', 'GB', 'London 1'),
            'fra1': RegionInfo('fra1', 'DE', 'Frankfurt 1'),
            'ams2': RegionInfo('ams2', 'NL', 'Amsterdam 2'),
            'ams3': RegionInfo('ams3', 'NL', 'Amsterdam 3'),
            'sgp1': RegionInfo('sgp1', 'SG', 'Singapore 1'),
            'blr1': RegionInfo('blr1', 'IN', 'Bangalore 1'),
            'syd1': RegionInfo('syd1', 'AU', 'Sydney 1'),
        }
    
    def _get_aliyun_mappings(self) -> Dict[str, RegionInfo]:
        """获取阿里云区域映射"""
        return {
            # 中国大陆
            'cn-beijing': RegionInfo('cn-beijing', 'CN', '华北2（北京）'),
            'cn-zhangjiakou': RegionInfo('cn-zhangjiakou', 'CN', '华北3（张家口）'),
            'cn-huhehaote': RegionInfo('cn-huhehaote', 'CN', '华北5（呼和浩特）'),
            'cn-wulanchabu': RegionInfo('cn-wulanchabu', 'CN', '华北6（乌兰察布）'),
            'cn-hangzhou': RegionInfo('cn-hangzhou', 'CN', '华东1（杭州）'),
            'cn-shanghai': RegionInfo('cn-shanghai', 'CN', '华东2（上海）'),
            'cn-nanjing': RegionInfo('cn-nanjing', 'CN', '华东5（南京）'),
            'cn-shenzhen': RegionInfo('cn-shenzhen', 'CN', '华南1（深圳）'),
            'cn-heyuan': RegionInfo('cn-heyuan', 'CN', '华南2（河源）'),
            'cn-guangzhou': RegionInfo('cn-guangzhou', 'CN', '华南3（广州）'),
            'cn-fuzhou': RegionInfo('cn-fuzhou', 'CN', '华东6（福州）'),
            'cn-wuhan-lr': RegionInfo('cn-wuhan-lr', 'CN', '华中1（武汉）'),
            'cn-chengdu': RegionInfo('cn-chengdu', 'CN', '西南1（成都）'),
            'cn-qingdao': RegionInfo('cn-qingdao', 'CN', '华北1（青岛）'),
            
            # 香港
            'cn-hongkong': RegionInfo('cn-hongkong', 'HK', '中国香港'),
            
            # 海外
            'ap-northeast-1': RegionInfo('ap-northeast-1', 'JP', '日本（东京）'),
            'ap-northeast-2': RegionInfo('ap-northeast-2', 'KR', '韩国（首尔）'),
            'ap-southeast-1': RegionInfo('ap-southeast-1', 'SG', '新加坡'),
            'ap-southeast-3': RegionInfo('ap-southeast-3', 'MY', '马来西亚（吉隆坡）'),
            'ap-southeast-5': RegionInfo('ap-southeast-5', 'ID', '印尼（雅加达）'),
            'ap-southeast-6': RegionInfo('ap-southeast-6', 'PH', '菲律宾（马尼拉）'),
            'ap-southeast-7': RegionInfo('ap-southeast-7', 'TH', '泰国（曼谷）'),
            'us-east-1': RegionInfo('us-east-1', 'US', '美国（弗吉尼亚）'),
            'us-west-1': RegionInfo('us-west-1', 'US', '美国（硅谷）'),
            'na-south-1': RegionInfo('na-south-1', 'MX', '墨西哥'),
            'eu-west-1': RegionInfo('eu-west-1', 'GB', '英国（伦敦）'),
            'eu-central-1': RegionInfo('eu-central-1', 'DE', '德国（法兰克福）'),
            'me-east-1': RegionInfo('me-east-1', 'AE', '阿联酋（迪拜）'),
        }
    
    def _get_tencent_mappings(self) -> Dict[str, RegionInfo]:
        """获取腾讯云区域映射"""
        return {
            # 中国大陆
            'ap-beijing': RegionInfo('ap-beijing', 'CN', '华北地区(北京)'),
            'ap-chengdu': RegionInfo('ap-chengdu', 'CN', '西南地区(成都)'),
            'ap-chongqing': RegionInfo('ap-chongqing', 'CN', '西南地区(重庆)'),
            'ap-guangzhou': RegionInfo('ap-guangzhou', 'CN', '华南地区(广州)'),
            'ap-shanghai': RegionInfo('ap-shanghai', 'CN', '华东地区(上海)'),
            'ap-nanjing': RegionInfo('ap-nanjing', 'CN', '华东地区(南京)'),
            
            # 港澳台
            'ap-hongkong': RegionInfo('ap-hongkong', 'HK', '港澳台地区(中国香港)'),
            
            # 海外
            'ap-singapore': RegionInfo('ap-singapore', 'SG', '亚太地区(新加坡)'),
            'ap-bangkok': RegionInfo('ap-bangkok', 'TH', '亚太地区(曼谷)'),
            'ap-jakarta': RegionInfo('ap-jakarta', 'ID', '亚太地区(雅加达)'),
            'ap-seoul': RegionInfo('ap-seoul', 'KR', '亚太地区(首尔)'),
            'ap-tokyo': RegionInfo('ap-tokyo', 'JP', '亚太地区(东京)'),
            'na-siliconvalley': RegionInfo('na-siliconvalley', 'US', '美国西部(硅谷)'),
            'na-ashburn': RegionInfo('na-ashburn', 'US', '美国东部(弗吉尼亚)'),
            'na-toronto': RegionInfo('na-toronto', 'CA', '北美地区(多伦多)'),
            'sa-saopaulo': RegionInfo('sa-saopaulo', 'BR', '南美地区(圣保罗)'),
            'eu-frankfurt': RegionInfo('eu-frankfurt', 'DE', '欧洲地区(法兰克福)'),
            'eu-moscow': RegionInfo('eu-moscow', 'RU', '欧洲地区(莫斯科)'),
        }
    
    def get_country_code(self, provider: CloudProvider, region_id: str) -> str:
        """获取指定云服务商和区域的国家代码"""
        provider_mappings = self._region_mappings.get(provider, {})
        region_info = provider_mappings.get(region_id)
        
        if region_info:
            return region_info.country_code
        
        # 返回合理的默认值
        if provider in [CloudProvider.ALIYUN, CloudProvider.TENCENT]:
            return 'CN'  # 中国云服务商默认中国
        else:
            return 'US'  # 国际云服务商默认美国
    
    def get_region_info(self, provider: CloudProvider, region_id: str) -> Optional[RegionInfo]:
        """获取指定云服务商和区域的完整信息"""
        provider_mappings = self._region_mappings.get(provider, {})
        return provider_mappings.get(region_id)
    
    def get_all_regions(self, provider: CloudProvider) -> Dict[str, RegionInfo]:
        """获取指定云服务商的所有区域映射"""
        return self._region_mappings.get(provider, {})
    
    def validate_mapping(self, provider: CloudProvider, region_id: str) -> bool:
        """验证指定区域是否有映射定义"""
        provider_mappings = self._region_mappings.get(provider, {})
        return region_id in provider_mappings


# 全局单例实例
region_mapper = UnifiedRegionMapper()