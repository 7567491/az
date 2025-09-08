#!/usr/bin/env python3
"""
区域分类功能测试
测试新的六大区分类逻辑：北美、南美、欧洲、亚太（不含中国）、中国、其他
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模拟前端区域分类逻辑的Python版本（用于测试）
class RegionClassifierForTest:
    """
    区域分类器 - Python版本用于测试
    """
    
    def __init__(self):
        self.country_to_region = {
            # 北美
            'US': 'north-america', 
            'CA': 'north-america',
            'MX': 'north-america',
            
            # 南美  
            'BR': 'south-america',
            'AR': 'south-america',
            'CL': 'south-america',
            'CO': 'south-america',
            'PE': 'south-america',
            
            # 欧洲
            'DE': 'europe', 'GB': 'europe', 'FR': 'europe',
            'IT': 'europe', 'ES': 'europe', 'NL': 'europe', 
            'SE': 'europe', 'FI': 'europe', 'IE': 'europe',
            
            # 亚太（不含中国）
            'JP': 'asia-pacific', 'KR': 'asia-pacific', 'SG': 'asia-pacific',
            'AU': 'asia-pacific', 'IN': 'asia-pacific', 'ID': 'asia-pacific',
            'MY': 'asia-pacific', 'TH': 'asia-pacific', 'PH': 'asia-pacific',
            'AE': 'asia-pacific', 'HK': 'asia-pacific',
            
            # 中国
            'CN': 'china'
        }
        
        self.continent_names = {
            'north-america': '🇺🇸 北美',
            'south-america': '🇧🇷 南美', 
            'europe': '🇪🇺 欧洲',
            'asia-pacific': '🌏 亚太地区',
            'china': '🇨🇳 中国',
            'others': '🌐 其他地区'
        }
        
        self.continent_order = ['north-america', 'south-america', 'europe', 'asia-pacific', 'china', 'others']
    
    def classify_region(self, country_code):
        """根据国家代码分类区域"""
        return self.country_to_region.get(country_code, 'others')
    
    def get_continent_name(self, continent_key):
        """获取大区中文名称"""
        return self.continent_names.get(continent_key, continent_key)
    
    def group_regions_by_continent(self, regions):
        """按大区分组区域"""
        grouped = {}
        for region in regions:
            continent = self.classify_region(region.get('country_code', ''))
            if continent not in grouped:
                grouped[continent] = []
            grouped[continent].append(region)
        return grouped
    
    def get_ordered_continents(self, grouped_regions):
        """获取排序后的大区列表"""
        return [continent for continent in self.continent_order if continent in grouped_regions]


class TestRegionClassification(unittest.TestCase):
    """区域分类功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.classifier = RegionClassifierForTest()
        
        # 测试数据 - 模拟真实的区域数据
        self.sample_regions = [
            # 北美
            {'region_id': 'us-east-1', 'region_name': 'Virginia', 'country_code': 'US', 'provider': 'aws'},
            {'region_id': 'ca-central-1', 'region_name': 'Toronto', 'country_code': 'CA', 'provider': 'aws'},
            {'region_id': 'na-south-1', 'region_name': 'Mexico', 'country_code': 'MX', 'provider': 'tencent'},
            
            # 南美
            {'region_id': 'sa-east-1', 'region_name': 'Sao Paulo', 'country_code': 'BR', 'provider': 'aws'},
            
            # 欧洲
            {'region_id': 'eu-west-1', 'region_name': 'Ireland', 'country_code': 'IE', 'provider': 'aws'},
            {'region_id': 'eu-central-1', 'region_name': 'Frankfurt', 'country_code': 'DE', 'provider': 'aws'},
            {'region_id': 'fra1', 'region_name': 'Frankfurt 1', 'country_code': 'DE', 'provider': 'digitalocean'},
            
            # 亚太（不含中国）
            {'region_id': 'ap-northeast-1', 'region_name': 'Tokyo', 'country_code': 'JP', 'provider': 'aws'},
            {'region_id': 'ap-southeast-1', 'region_name': 'Singapore', 'country_code': 'SG', 'provider': 'aws'},
            {'region_id': 'sgp1', 'region_name': 'Singapore 1', 'country_code': 'SG', 'provider': 'digitalocean'},
            {'region_id': 'ap-south', 'region_name': 'Mumbai', 'country_code': 'IN', 'provider': 'linode'},
            
            # 中国
            {'region_id': 'ap-beijing', 'region_name': '华北地区(北京)', 'country_code': 'CN', 'provider': 'tencent'},
            {'region_id': 'cn-hangzhou', 'region_name': '华东地区(杭州)', 'country_code': 'CN', 'provider': 'aliyun'},
            
            # 其他（未知国家）
            {'region_id': 'unknown-1', 'region_name': 'Unknown Region', 'country_code': 'XX', 'provider': 'unknown'},
        ]
    
    def test_country_code_mapping(self):
        """测试国家代码到大区的映射"""
        # 北美国家
        self.assertEqual(self.classifier.classify_region('US'), 'north-america')
        self.assertEqual(self.classifier.classify_region('CA'), 'north-america')
        self.assertEqual(self.classifier.classify_region('MX'), 'north-america')
        
        # 南美国家
        self.assertEqual(self.classifier.classify_region('BR'), 'south-america')
        self.assertEqual(self.classifier.classify_region('AR'), 'south-america')
        
        # 欧洲国家
        self.assertEqual(self.classifier.classify_region('DE'), 'europe')
        self.assertEqual(self.classifier.classify_region('GB'), 'europe')
        self.assertEqual(self.classifier.classify_region('FR'), 'europe')
        
        # 亚太国家（不含中国）
        self.assertEqual(self.classifier.classify_region('JP'), 'asia-pacific')
        self.assertEqual(self.classifier.classify_region('SG'), 'asia-pacific')
        self.assertEqual(self.classifier.classify_region('AU'), 'asia-pacific')
        self.assertEqual(self.classifier.classify_region('HK'), 'asia-pacific')
        
        # 中国
        self.assertEqual(self.classifier.classify_region('CN'), 'china')
        
        # 未知国家
        self.assertEqual(self.classifier.classify_region('XX'), 'others')
        self.assertEqual(self.classifier.classify_region(''), 'others')
    
    def test_continent_names(self):
        """测试大区中文名称"""
        self.assertEqual(self.classifier.get_continent_name('north-america'), '🇺🇸 北美')
        self.assertEqual(self.classifier.get_continent_name('south-america'), '🇧🇷 南美')
        self.assertEqual(self.classifier.get_continent_name('europe'), '🇪🇺 欧洲')
        self.assertEqual(self.classifier.get_continent_name('asia-pacific'), '🌏 亚太地区')
        self.assertEqual(self.classifier.get_continent_name('china'), '🇨🇳 中国')
        self.assertEqual(self.classifier.get_continent_name('others'), '🌐 其他地区')
        
        # 未知大区返回原值
        self.assertEqual(self.classifier.get_continent_name('unknown'), 'unknown')
    
    def test_region_grouping(self):
        """测试区域分组功能"""
        grouped = self.classifier.group_regions_by_continent(self.sample_regions)
        
        # 检查所有大区都存在
        self.assertIn('north-america', grouped)
        self.assertIn('south-america', grouped)
        self.assertIn('europe', grouped)
        self.assertIn('asia-pacific', grouped)
        self.assertIn('china', grouped)
        self.assertIn('others', grouped)
        
        # 检查每个大区的区域数量
        self.assertEqual(len(grouped['north-america']), 3)  # US, CA, MX
        self.assertEqual(len(grouped['south-america']), 1)   # BR
        self.assertEqual(len(grouped['europe']), 3)          # IE, DE x2
        self.assertEqual(len(grouped['asia-pacific']), 4)    # JP, SG x2, IN
        self.assertEqual(len(grouped['china']), 2)           # CN x2
        self.assertEqual(len(grouped['others']), 1)          # XX
    
    def test_continent_ordering(self):
        """测试大区排序"""
        grouped = self.classifier.group_regions_by_continent(self.sample_regions)
        ordered_continents = self.classifier.get_ordered_continents(grouped)
        
        expected_order = ['north-america', 'south-america', 'europe', 'asia-pacific', 'china', 'others']
        self.assertEqual(ordered_continents, expected_order)
    
    def test_specific_country_classifications(self):
        """测试特定国家的分类正确性"""
        test_cases = [
            # (国家代码, 期望的大区)
            ('US', 'north-america'),
            ('CA', 'north-america'), 
            ('BR', 'south-america'),
            ('DE', 'europe'),
            ('JP', 'asia-pacific'),
            ('CN', 'china'),
            ('HK', 'asia-pacific'),  # 香港归类为亚太
            ('SG', 'asia-pacific'),  # 新加坡归类为亚太
        ]
        
        for country_code, expected_continent in test_cases:
            with self.subTest(country=country_code):
                actual_continent = self.classifier.classify_region(country_code)
                self.assertEqual(
                    actual_continent, 
                    expected_continent,
                    f"国家 {country_code} 应该归类为 {expected_continent}，但实际为 {actual_continent}"
                )
    
    def test_empty_regions_handling(self):
        """测试空区域列表处理"""
        grouped = self.classifier.group_regions_by_continent([])
        self.assertEqual(grouped, {})
        
        ordered = self.classifier.get_ordered_continents(grouped)
        self.assertEqual(ordered, [])
    
    def test_region_distribution_balance(self):
        """测试区域分布合理性 - 确保中国单独分类"""
        grouped = self.classifier.group_regions_by_continent(self.sample_regions)
        
        # 中国必须单独分类
        china_regions = grouped.get('china', [])
        self.assertTrue(len(china_regions) > 0, "中国区域不能为空")
        
        # 所有中国区域都应该在china分类下
        for region in china_regions:
            self.assertEqual(region['country_code'], 'CN', "china分类下只能包含CN国家的区域")
        
        # 亚太地区不应该包含中国区域
        apac_regions = grouped.get('asia-pacific', [])
        for region in apac_regions:
            self.assertNotEqual(region['country_code'], 'CN', "亚太地区分类不应包含中国区域")


if __name__ == '__main__':
    print("🧪 开始运行区域分类测试 (TDD Red阶段)")
    print("=" * 60)
    
    # 运行测试
    unittest.main(verbosity=2)