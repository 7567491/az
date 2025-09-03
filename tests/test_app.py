import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from app import create_app
from database.models import DatabaseManager


class TestFlaskApp:
    def setup_method(self):
        """每个测试方法前执行"""
        # 创建临时数据库
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        
        # 创建测试应用
        self.app = create_app(test_config={
            'TESTING': True,
            'DATABASE': self.test_db.name
        })
        self.client = self.app.test_client()
        
        # 初始化测试数据
        with self.app.app_context():
            db_manager = DatabaseManager(self.test_db.name)
            db_manager.create_tables()
            self._create_test_data(db_manager)

    def teardown_method(self):
        """每个测试方法后执行"""
        os.unlink(self.test_db.name)
    
    def _create_test_data(self, db_manager):
        """创建测试数据"""
        from database.models import Provider, Country, AvailabilityZone
        
        # 创建providers
        providers_data = [
            Provider(name='linode', display_name='Linode', color='#3498db'),
            Provider(name='digitalocean', display_name='DigitalOcean', color='#ffb3d9'),
            Provider(name='aliyun', display_name='阿里云', color='#ff8c00'),
            Provider(name='tencent', display_name='腾讯云', color='#2ecc71')
        ]
        
        provider_ids = {}
        for provider in providers_data:
            provider_id = db_manager.create_provider(provider)
            provider_ids[provider.name] = provider_id
        
        # 创建countries
        countries_data = [
            Country(country_code='US', country_name='United States', continent='americas'),
            Country(country_code='GB', country_name='United Kingdom', continent='europe-africa'),
            Country(country_code='SG', country_name='Singapore', continent='apac'),
            Country(country_code='CN', country_name='China', continent='apac')
        ]
        
        for country in countries_data:
            db_manager.create_country(country)
        
        # 创建availability zones
        azs_data = [
            AvailabilityZone(provider_ids['linode'], 'us-east-1', 'US East', 'US', 'americas'),
            AvailabilityZone(provider_ids['linode'], 'eu-west-1', 'EU West', 'GB', 'europe-africa'),
            AvailabilityZone(provider_ids['digitalocean'], 'nyc1', 'New York 1', 'US', 'americas'),
            AvailabilityZone(provider_ids['aliyun'], 'cn-beijing', '华北2（北京）', 'CN', 'apac'),
            AvailabilityZone(provider_ids['tencent'], 'ap-beijing', '华北地区(北京)', 'CN', 'apac')
        ]
        
        for az in azs_data:
            db_manager.create_availability_zone(az)

    def test_index_route(self):
        """测试首页路由"""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'cloud-az-visualizer' in response.data.lower() or b'html' in response.data.lower()

    def test_api_regions_route(self):
        """测试获取区域数据API"""
        response = self.client.get('/api/regions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'regions' in data
        assert isinstance(data['regions'], list)
        assert len(data['regions']) > 0
        
        # 检查数据结构
        region = data['regions'][0]
        required_fields = ['region_id', 'region_name', 'provider', 'country_code', 'continent']
        for field in required_fields:
            assert field in region

    def test_api_countries_route(self):
        """测试获取国家数据API"""
        response = self.client.get('/api/countries')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'countries' in data
        assert isinstance(data['countries'], list)
        assert len(data['countries']) > 0
        
        # 检查数据结构
        country = data['countries'][0]
        required_fields = ['country_code', 'country_name', 'continent', 'providers']
        for field in required_fields:
            assert field in country

    def test_api_providers_route(self):
        """测试获取云服务商数据API"""
        response = self.client.get('/api/providers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'providers' in data
        assert isinstance(data['providers'], list)
        
        # 验证包含所有预期的云服务商
        provider_names = [p['name'] for p in data['providers']]
        expected_providers = ['linode', 'digitalocean', 'aliyun', 'tencent']
        for provider in expected_providers:
            assert provider in provider_names

    @patch('api.cloud_collector.CloudAPICollector')
    def test_api_refresh_route(self, mock_collector_class):
        """测试数据刷新API"""
        # Mock CloudAPICollector
        mock_collector = Mock()
        mock_collector.collect_all_regions = AsyncMock(return_value={
            'linode': [{'region_id': 'us-east', 'region_name': 'US East', 'country_code': 'US'}],
            'digitalocean': []
        })
        mock_collector.update_database = Mock()
        mock_collector_class.return_value = mock_collector
        
        response = self.client.post('/api/refresh')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is True
        assert 'message' in data
        assert 'updated_at' in data

    def test_api_refresh_route_failure(self):
        """测试数据刷新API失败情况"""
        with patch('api.cloud_collector.CloudAPICollector') as mock_collector_class:
            mock_collector = Mock()
            mock_collector.collect_all_regions = AsyncMock(side_effect=Exception("API Error"))
            mock_collector_class.return_value = mock_collector
            
            response = self.client.post('/api/refresh')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is False
            assert 'error' in data

    def test_api_stats_route(self):
        """测试统计数据API"""
        response = self.client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_regions' in data
        assert 'total_countries' in data
        assert 'total_providers' in data
        assert 'regions_by_provider' in data
        assert 'regions_by_continent' in data
        
        # 验证数据类型
        assert isinstance(data['total_regions'], int)
        assert isinstance(data['total_countries'], int)
        assert isinstance(data['total_providers'], int)
        assert isinstance(data['regions_by_provider'], dict)
        assert isinstance(data['regions_by_continent'], dict)

    def test_api_color_mapping_route(self):
        """测试颜色映射API"""
        response = self.client.get('/api/colors')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'color_mapping' in data
        
        color_mapping = data['color_mapping']
        expected_providers = ['linode', 'digitalocean', 'aliyun', 'tencent']
        for provider in expected_providers:
            assert provider in color_mapping
            # 验证颜色格式 (hex color)
            assert color_mapping[provider].startswith('#')
            assert len(color_mapping[provider]) == 7

    def test_cors_headers(self):
        """测试CORS头设置"""
        response = self.client.get('/api/regions')
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_error_handling_invalid_route(self):
        """测试无效路由的错误处理"""
        response = self.client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_api_regions_with_provider_filter(self):
        """测试带云服务商过滤的区域API"""
        response = self.client.get('/api/regions?providers=linode,digitalocean')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'regions' in data
        
        # 验证只返回指定的云服务商
        providers = set(region['provider'] for region in data['regions'])
        assert providers.issubset({'linode', 'digitalocean'})

    def test_api_countries_with_continent_filter(self):
        """测试带大洲过滤的国家API"""
        response = self.client.get('/api/countries?continent=americas')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'countries' in data
        
        # 验证只返回指定大洲的国家
        continents = set(country['continent'] for country in data['countries'])
        assert continents == {'americas'}
