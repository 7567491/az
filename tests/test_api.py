import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from api.cloud_collector import CloudAPICollector
from api.linode_api import LinodeAPI
from api.digitalocean_api import DigitalOceanAPI
from api.aliyun_api import AliyunAPI
from api.tencent_api import TencentAPI
from database.models import DatabaseManager, Provider, AvailabilityZone


class TestCloudAPICollector:
    def setup_method(self):
        """每个测试方法前执行"""
        self.collector = CloudAPICollector()
        
    def test_init(self):
        """测试CloudAPICollector初始化"""
        assert hasattr(self.collector, 'providers')
        assert 'linode' in self.collector.providers
        assert 'digitalocean' in self.collector.providers
        assert 'aliyun' in self.collector.providers
        assert 'tencent' in self.collector.providers
        
    @pytest.mark.asyncio
    async def test_collect_all_regions(self):
        """测试收集所有区域数据"""
        # Mock各个API的响应
        mock_linode_data = [
            {'id': 'us-east', 'label': 'Newark, NJ', 'country': 'US'},
            {'id': 'eu-west', 'label': 'London, UK', 'country': 'GB'}
        ]
        mock_do_data = [
            {'slug': 'nyc1', 'name': 'New York 1', 'country': 'US'},
            {'slug': 'fra1', 'name': 'Frankfurt 1', 'country': 'DE'}
        ]
        
        with patch.object(self.collector.providers['linode'], 'fetch_regions', 
                         return_value=mock_linode_data) as mock_linode, \
             patch.object(self.collector.providers['digitalocean'], 'fetch_regions',
                         return_value=mock_do_data) as mock_do, \
             patch.object(self.collector.providers['aliyun'], 'fetch_regions',
                         return_value=[]) as mock_aliyun, \
             patch.object(self.collector.providers['tencent'], 'fetch_regions',
                         return_value=[]) as mock_tencent:
            
            results = await self.collector.collect_all_regions()
            
            assert 'linode' in results
            assert 'digitalocean' in results
            assert len(results['linode']) == 2
            assert len(results['digitalocean']) == 2
            
            mock_linode.assert_called_once()
            mock_do.assert_called_once()
            mock_aliyun.assert_called_once()
            mock_tencent.assert_called_once()


class TestLinodeAPI:
    def setup_method(self):
        """每个测试方法前执行"""
        self.api = LinodeAPI()
    
    def test_init(self):
        """测试LinodeAPI初始化"""
        assert hasattr(self.api, 'base_url')
        assert hasattr(self.api, 'headers')
        assert 'Authorization' in self.api.headers
        
    @pytest.mark.asyncio
    async def test_fetch_regions_success(self):
        """测试成功获取Linode区域"""
        mock_response_data = {
            "data": [
                {
                    "id": "us-east",
                    "label": "Newark, NJ",
                    "country": "us",
                    "capabilities": ["Linodes"],
                    "status": "ok"
                },
                {
                    "id": "eu-west",
                    "label": "London, UK", 
                    "country": "gb",
                    "capabilities": ["Linodes"],
                    "status": "ok"
                }
            ]
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            regions = await self.api.fetch_regions()
            
            assert len(regions) == 2
            assert regions[0]['region_id'] == 'us-east'
            assert regions[0]['region_name'] == 'Newark, NJ'
            assert regions[0]['country_code'] == 'US'
            assert regions[1]['region_id'] == 'eu-west'
            assert regions[1]['country_code'] == 'GB'
            
    @pytest.mark.asyncio 
    async def test_fetch_regions_failure(self):
        """测试Linode API请求失败"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            regions = await self.api.fetch_regions()
            assert regions == []


class TestDigitalOceanAPI:
    def setup_method(self):
        """每个测试方法前执行"""
        self.api = DigitalOceanAPI()
    
    def test_init(self):
        """测试DigitalOceanAPI初始化"""
        assert hasattr(self.api, 'base_url')
        assert hasattr(self.api, 'headers')
        assert 'Authorization' in self.api.headers
        
    @pytest.mark.asyncio
    async def test_fetch_regions_success(self):
        """测试成功获取DigitalOcean区域"""
        mock_response_data = {
            "regions": [
                {
                    "name": "New York 1",
                    "slug": "nyc1",
                    "features": ["virtio", "storage"],
                    "available": True
                },
                {
                    "name": "Frankfurt 1",
                    "slug": "fra1", 
                    "features": ["virtio", "storage"],
                    "available": True
                }
            ]
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            regions = await self.api.fetch_regions()
            
            assert len(regions) == 2
            assert regions[0]['region_id'] == 'nyc1'
            assert regions[0]['region_name'] == 'New York 1'
            assert regions[0]['country_code'] == 'US'  # 从映射表获取
            assert regions[1]['region_id'] == 'fra1'
            assert regions[1]['country_code'] == 'DE'  # 从映射表获取


class TestAliyunAPI:
    def setup_method(self):
        """每个测试方法前执行"""
        self.api = AliyunAPI()
    
    def test_init(self):
        """测试AliyunAPI初始化"""
        assert hasattr(self.api, 'access_key_id')
        assert hasattr(self.api, 'access_key_secret')
        
    @pytest.mark.asyncio
    async def test_fetch_regions_success(self):
        """测试成功获取阿里云区域"""
        mock_response_data = {
            "Regions": {
                "Region": [
                    {
                        "RegionId": "cn-beijing",
                        "LocalName": "华北2（北京）"
                    },
                    {
                        "RegionId": "us-east-1", 
                        "LocalName": "美国（弗吉尼亚）"
                    }
                ]
            }
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None  
            mock_get.return_value = mock_response
            
            regions = await self.api.fetch_regions()
            
            assert len(regions) == 2
            assert regions[0]['region_id'] == 'cn-beijing'
            assert regions[0]['region_name'] == '华北2（北京）'
            assert regions[0]['country_code'] == 'CN'
            assert regions[1]['region_id'] == 'us-east-1'
            assert regions[1]['country_code'] == 'US'


class TestTencentAPI:
    def setup_method(self):
        """每个测试方法前执行"""
        self.api = TencentAPI()
    
    def test_init(self):
        """测试TencentAPI初始化"""
        assert hasattr(self.api, 'secret_id')
        assert hasattr(self.api, 'secret_key')
        
    @pytest.mark.asyncio
    async def test_fetch_regions_success(self):
        """测试成功获取腾讯云区域"""
        mock_response_data = {
            "Response": {
                "RegionSet": [
                    {
                        "Region": "ap-beijing",
                        "RegionName": "华北地区(北京)",
                        "RegionState": "AVAILABLE"
                    },
                    {
                        "Region": "na-siliconvalley",
                        "RegionName": "美国西部(硅谷)",
                        "RegionState": "AVAILABLE" 
                    }
                ]
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            regions = await self.api.fetch_regions()
            
            assert len(regions) == 2
            assert regions[0]['region_id'] == 'ap-beijing'
            assert regions[0]['region_name'] == '华北地区(北京)'
            assert regions[0]['country_code'] == 'CN'
            assert regions[1]['region_id'] == 'na-siliconvalley'
            assert regions[1]['country_code'] == 'US'
