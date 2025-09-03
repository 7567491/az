import pytest
import sqlite3
import os
import tempfile
from datetime import datetime
from database.models import DatabaseManager, Provider, Country, AvailabilityZone, UpdateLog


class TestDatabaseManager:
    def setup_method(self):
        """每个测试方法前执行，创建临时数据库"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.db_manager = DatabaseManager(self.test_db.name)
        self.db_manager.create_tables()

    def teardown_method(self):
        """每个测试方法后执行，清理临时数据库"""
        os.unlink(self.test_db.name)

    def test_create_tables(self):
        """测试数据库表创建"""
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        
        # 检查所有表是否已创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['providers', 'countries', 'availability_zones', 'update_logs']
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist"
        
        conn.close()

    def test_provider_operations(self):
        """测试Provider CRUD操作"""
        provider = Provider(
            name='linode',
            display_name='Linode',
            color='#3498db',
            api_endpoint='https://api.linode.com/v4/'
        )
        
        # 测试插入
        provider_id = self.db_manager.create_provider(provider)
        assert provider_id is not None
        
        # 测试查询
        retrieved_provider = self.db_manager.get_provider(provider_id)
        assert retrieved_provider is not None
        assert retrieved_provider.name == 'linode'
        assert retrieved_provider.display_name == 'Linode'
        assert retrieved_provider.color == '#3498db'
        
        # 测试按名称查询
        provider_by_name = self.db_manager.get_provider_by_name('linode')
        assert provider_by_name is not None
        assert provider_by_name.id == provider_id

    def test_country_operations(self):
        """测试Country CRUD操作"""
        country = Country(
            country_code='US',
            country_name='United States',
            continent='americas'
        )
        
        # 测试插入
        country_id = self.db_manager.create_country(country)
        assert country_id is not None
        
        # 测试查询
        retrieved_country = self.db_manager.get_country(country_id)
        assert retrieved_country is not None
        assert retrieved_country.country_code == 'US'
        assert retrieved_country.country_name == 'United States'
        assert retrieved_country.continent == 'americas'

    def test_availability_zone_operations(self):
        """测试AvailabilityZone CRUD操作"""
        # 先创建provider和country
        provider = Provider(name='linode', display_name='Linode', color='#3498db')
        provider_id = self.db_manager.create_provider(provider)
        
        country = Country(country_code='US', country_name='United States', continent='americas')
        country_id = self.db_manager.create_country(country)
        
        # 创建可用区域
        az = AvailabilityZone(
            provider_id=provider_id,
            region_id='us-east-1',
            region_name='US East (Newark)',
            country_code='US',
            continent='americas'
        )
        
        # 测试插入
        az_id = self.db_manager.create_availability_zone(az)
        assert az_id is not None
        
        # 测试查询
        retrieved_az = self.db_manager.get_availability_zone(az_id)
        assert retrieved_az is not None
        assert retrieved_az.region_id == 'us-east-1'
        assert retrieved_az.region_name == 'US East (Newark)'
        assert retrieved_az.country_code == 'US'

    def test_get_countries_by_provider(self):
        """测试按云服务商查询国家"""
        # 创建测试数据
        provider1 = Provider(name='linode', display_name='Linode', color='#3498db')
        provider1_id = self.db_manager.create_provider(provider1)
        
        provider2 = Provider(name='digitalocean', display_name='DigitalOcean', color='#ffb3d9')
        provider2_id = self.db_manager.create_provider(provider2)
        
        # 创建国家
        us_country = Country(country_code='US', country_name='United States', continent='americas')
        self.db_manager.create_country(us_country)
        
        sg_country = Country(country_code='SG', country_name='Singapore', continent='apac')
        self.db_manager.create_country(sg_country)
        
        # 为provider1创建两个区域
        az1 = AvailabilityZone(provider1_id, 'us-east-1', 'US East', 'US', 'americas')
        az2 = AvailabilityZone(provider1_id, 'ap-south-1', 'Singapore', 'SG', 'apac')
        self.db_manager.create_availability_zone(az1)
        self.db_manager.create_availability_zone(az2)
        
        # 为provider2创建一个区域
        az3 = AvailabilityZone(provider2_id, 'nyc1', 'New York 1', 'US', 'americas')
        self.db_manager.create_availability_zone(az3)
        
        # 测试查询结果
        linode_countries = self.db_manager.get_countries_by_provider('linode')
        assert len(linode_countries) == 2
        assert 'US' in linode_countries
        assert 'SG' in linode_countries
        
        do_countries = self.db_manager.get_countries_by_provider('digitalocean')
        assert len(do_countries) == 1
        assert 'US' in do_countries

    def test_update_log_operations(self):
        """测试UpdateLog操作"""
        # 先创建provider
        provider = Provider(name='linode', display_name='Linode', color='#3498db')
        provider_id = self.db_manager.create_provider(provider)
        
        # 创建更新日志
        update_log = UpdateLog(
            provider_id=provider_id,
            status='success',
            message='Data updated successfully'
        )
        
        log_id = self.db_manager.create_update_log(update_log)
        assert log_id is not None
        
        # 查询日志
        retrieved_log = self.db_manager.get_update_log(log_id)
        assert retrieved_log is not None
        assert retrieved_log.provider_id == provider_id
        assert retrieved_log.status == 'success'
        assert retrieved_log.message == 'Data updated successfully'
        assert retrieved_log.update_time is not None

    def test_get_all_countries_with_providers(self):
        """测试获取所有国家及其云服务商信息"""
        # 创建测试数据
        provider1 = Provider(name='linode', display_name='Linode', color='#3498db')
        provider1_id = self.db_manager.create_provider(provider1)
        
        provider2 = Provider(name='digitalocean', display_name='DigitalOcean', color='#ffb3d9')
        provider2_id = self.db_manager.create_provider(provider2)
        
        # 创建国家
        us_country = Country(country_code='US', country_name='United States', continent='americas')
        self.db_manager.create_country(us_country)
        
        # 两个provider都在美国有服务
        az1 = AvailabilityZone(provider1_id, 'us-east-1', 'US East', 'US', 'americas')
        az2 = AvailabilityZone(provider2_id, 'nyc1', 'New York 1', 'US', 'americas')
        self.db_manager.create_availability_zone(az1)
        self.db_manager.create_availability_zone(az2)
        
        # 测试查询
        countries_data = self.db_manager.get_all_countries_with_providers()
        assert len(countries_data) >= 1
        
        # 找到美国的数据
        us_data = next((c for c in countries_data if c['country_code'] == 'US'), None)
        assert us_data is not None
        assert 'linode' in us_data['providers']
        assert 'digitalocean' in us_data['providers']
