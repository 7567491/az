#!/usr/bin/env python3
"""
TDD测试: Linode区域映射功能测试
使用测试驱动开发方法修正区域映射问题
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.linode_api import LinodeAPI
from api.region_mapper import region_mapper, CloudProvider


class TestLinodeRegionMapping(unittest.TestCase):
    """Linode区域映射测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.linode_api = LinodeAPI()
    
    def test_us_regions_mapping(self):
        """测试美国区域映射"""
        us_regions = [
            'us-east',      # Newark, NJ
            'us-central',   # Dallas, TX
            'us-west',      # Fremont, CA
            'us-southeast', # Atlanta, GA
            'us-ord',       # Chicago, IL
            'us-lax',       # Los Angeles, CA
            'us-mia',       # Miami, FL
            'us-sea',       # Seattle, WA
            'us-iad',       # Washington, DC
        ]
        
        for region_id in us_regions:
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, 'US', 
                    f"Region {region_id} should map to US, got {result}")
    
    def test_canada_regions_mapping(self):
        """测试加拿大区域映射"""
        canada_regions = ['ca-central']  # Toronto, CA
        
        for region_id in canada_regions:
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, 'CA', 
                    f"Region {region_id} should map to CA, got {result}")
    
    def test_europe_regions_mapping(self):
        """测试欧洲区域映射 - 这些是当前失败的测试"""
        europe_regions = {
            'eu-west': 'GB',        # London, UK
            'eu-central': 'DE',     # Frankfurt, DE
            'de-fra-2': 'DE',       # Frankfurt 2, DE ❌ 当前映射为US
            'fr-par': 'FR',         # Paris, FR ❌ 当前映射为US
            'it-mil': 'IT',         # Milan, IT ❌ 当前映射为US
            'nl-ams': 'NL',         # Amsterdam, NL ❌ 当前映射为US
            'se-sto': 'SE',         # Stockholm, SE ❌ 当前映射为US
            'gb-lon': 'GB',         # London 2, UK ❌ 当前映射为US
            'es-mad': 'ES',         # Madrid, ES ❌ 当前映射为US
        }
        
        for region_id, expected_country in europe_regions.items():
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, expected_country, 
                    f"Region {region_id} should map to {expected_country}, got {result}")
    
    def test_apac_regions_mapping(self):
        """测试亚太区域映射"""
        apac_regions = {
            'ap-south': 'SG',         # Singapore, SG
            'ap-northeast': 'JP',     # Tokyo 2, JP
            'ap-southeast': 'AU',     # Sydney, AU
            'ap-west': 'IN',          # Mumbai, IN
            'au-mel': 'AU',           # Melbourne, AU ❌ 当前映射为US
            'sg-sin-2': 'SG',         # Singapore 2, SG ❌ 当前映射为US
            'jp-osa': 'JP',           # Osaka, JP ❌ 当前映射为US
            'jp-tyo-3': 'JP',         # Tokyo 3, JP ❌ 当前映射为US
            'in-bom-2': 'IN',         # Mumbai 2, IN ❌ 当前映射为US
            'in-maa': 'IN',           # Chennai, IN ❌ 当前映射为US
            'id-cgk': 'ID',           # Jakarta, ID ❌ 当前映射为US
        }
        
        for region_id, expected_country in apac_regions.items():
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, expected_country, 
                    f"Region {region_id} should map to {expected_country}, got {result}")
    
    def test_south_america_regions_mapping(self):
        """测试南美区域映射"""
        south_america_regions = {
            'br-gru': 'BR',  # São Paulo, BR ❌ 当前映射为US
        }
        
        for region_id, expected_country in south_america_regions.items():
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, expected_country, 
                    f"Region {region_id} should map to {expected_country}, got {result}")
    
    def test_unknown_region_default(self):
        """测试未知区域的默认值处理"""
        # 对于真正未知的区域，应该有合理的默认值
        unknown_regions = ['unknown-region', 'test-region']
        
        for region_id in unknown_regions:
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                # 默认值应该是US（当前行为），但我们可能想要改变这个逻辑
                self.assertEqual(result, 'US', 
                    f"Unknown region {region_id} should default to US, got {result}")
    
    def test_all_current_regions_have_mapping(self):
        """测试所有当前Linode区域都有映射定义"""
        # 根据我们的分析，这些是所有当前的Linode区域
        all_current_regions = [
            # 美国
            'us-east', 'us-central', 'us-west', 'us-southeast', 'us-ord',
            'us-lax', 'us-mia', 'us-sea', 'us-iad',
            # 加拿大
            'ca-central',
            # 欧洲
            'eu-west', 'eu-central', 'de-fra-2', 'fr-par', 'it-mil',
            'nl-ams', 'se-sto', 'gb-lon', 'es-mad',
            # 亚太
            'ap-south', 'ap-northeast', 'ap-southeast', 'ap-west',
            'au-mel', 'sg-sin-2', 'jp-osa', 'jp-tyo-3', 'in-bom-2', 'in-maa', 'id-cgk',
            # 南美
            'br-gru',
        ]
        
        # 检查每个区域都不应该使用默认的US值（除非它真的应该是US）
        us_regions = {'us-east', 'us-central', 'us-west', 'us-southeast', 'us-ord',
                      'us-lax', 'us-mia', 'us-sea', 'us-iad'}
        
        for region_id in all_current_regions:
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                
                # 如果不是US区域，就不应该返回US
                if region_id not in us_regions:
                    self.assertNotEqual(result, 'US',
                        f"Non-US region {region_id} should not default to US")
                
                # 检查结果不为空
                self.assertIsNotNone(result, f"Region {region_id} should have a country mapping")
                self.assertNotEqual(result, '', f"Region {region_id} should not have empty country mapping")
    
    def test_region_name_consistency(self):
        """测试区域命名的一致性"""
        # 测试区域ID的格式是否符合预期
        test_cases = [
            ('us-east', 'US'),      # 格式: country-location
            ('eu-west', 'GB'),      # 格式: continent-direction
            ('ap-south', 'SG'),     # 格式: continent-direction
            ('de-fra-2', 'DE'),     # 格式: country-city-number
            ('jp-tyo-3', 'JP'),     # 格式: country-city-number
        ]
        
        for region_id, expected_country in test_cases:
            with self.subTest(region=region_id):
                result = region_mapper.get_country_code(CloudProvider.LINODE, region_id)
                self.assertEqual(result, expected_country,
                    f"Region {region_id} mapping inconsistent with naming pattern")


class TestLinodeRegionMappingIntegration(unittest.TestCase):
    """Linode区域映射集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.linode_api = LinodeAPI()
    
    def test_mapping_covers_database_regions(self):
        """测试映射表覆盖数据库中的所有区域"""
        # 这个测试需要数据库连接，暂时跳过
        # 在实际环境中，我们会检查数据库中的所有Linode区域是否都有正确的映射
        pass


if __name__ == '__main__':
    # 运行测试
    print("🧪 TDD Step 1: 运行Linode区域映射测试 (期望失败)")
    print("=" * 60)
    
    # 设置测试运行器，显示详细信息
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLinodeRegionMapping)
    result = runner.run(suite)
    
    # 输出测试结果统计
    print("\n" + "=" * 60)
    print(f"📊 测试结果统计:")
    print(f"   总测试数: {result.testsRun}")
    print(f"   失败数: {len(result.failures)}")
    print(f"   错误数: {len(result.errors)}")
    print(f"   成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ 失败的测试 ({len(result.failures)} 个):")
        for test, traceback in result.failures:
            print(f"   • {test}")
    
    if result.errors:
        print(f"\n🚨 错误的测试 ({len(result.errors)} 个):")
        for test, traceback in result.errors:
            print(f"   • {test}")
    
    print("\n🔄 下一步: 修正代码使测试通过...")