import os
import asyncio
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
from database.models import DatabaseManager, Provider, Country, AvailabilityZone
from api.cloud_collector import CloudAPICollector

# 加载环境变量
load_dotenv()


def create_app(test_config=None):
    """Flask应用工厂函数"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 配置
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
            DATABASE=os.getenv('DATABASE_URL', 'database/cloud_az.db')
        )
    else:
        app.config.from_mapping(test_config)
    
    # 启用CORS
    CORS(app)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager(app.config['DATABASE'])
    
    @app.route('/')
    def index():
        """主页路由"""
        return render_template('index.html')
    
    @app.route('/api/regions')
    def get_regions():
        """获取所有区域数据API"""
        try:
            providers_filter = request.args.get('providers', '')
            selected_providers = providers_filter.split(',') if providers_filter else []
            
            regions = _get_all_regions(db_manager, selected_providers)
            return jsonify({
                'success': True,
                'regions': regions,
                'total': len(regions)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/countries')
    def get_countries():
        """获取国家数据API"""
        try:
            continent_filter = request.args.get('continent', '')
            countries_data = db_manager.get_all_countries_with_providers()
            
            if continent_filter:
                countries_data = [c for c in countries_data if c['continent'] == continent_filter]
            
            return jsonify({
                'success': True,
                'countries': countries_data,
                'total': len(countries_data)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/providers')
    def get_providers():
        """获取云服务商数据API"""
        try:
            providers_data = _get_all_providers(db_manager)
            return jsonify({
                'success': True,
                'providers': providers_data,
                'total': len(providers_data)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/refresh', methods=['POST'])
    def refresh_data():
        """刷新所有云服务数据API"""
        try:
            # 创建API收集器
            collector = CloudAPICollector()
            
            # 异步收集数据
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            regions_data = loop.run_until_complete(collector.collect_all_regions())
            loop.close()
            
            # 更新数据库
            collector.update_database(db_manager, regions_data)
            
            # 统计更新结果
            total_regions = sum(len(regions) for regions in regions_data.values())
            
            return jsonify({
                'success': True,
                'message': f'Successfully updated {total_regions} regions',
                'updated_at': datetime.now().isoformat(),
                'regions_by_provider': {k: len(v) for k, v in regions_data.items()}
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'updated_at': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/stats')
    def get_stats():
        """获取统计数据API"""
        try:
            stats = _get_statistics(db_manager)
            return jsonify(stats)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/colors')
    def get_color_mapping():
        """获取颜色映射API"""
        try:
            providers_data = _get_all_providers(db_manager)
            color_mapping = {
                provider['name']: provider['color'] 
                for provider in providers_data
            }
            
            return jsonify({
                'success': True,
                'color_mapping': color_mapping
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/test')
    def test_page():
        """测试页面"""
        try:
            with open('test_frontend.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return "测试页面未找到", 404
    
    @app.route('/debug')
    def debug_page():
        """调试页面"""
        try:
            with open('debug.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return "调试页面未找到", 404
    
    @app.route('/quick')
    def quick_test():
        """快速测试页面"""
        try:
            with open('quick_test.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return "快速测试页面未找到", 404
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({
            'success': False,
            'error': 'Not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


def _get_all_regions(db_manager, provider_filter=None):
    """获取所有区域数据的辅助函数"""
    import sqlite3
    
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    query = '''
    SELECT az.region_id, az.region_name, p.name as provider_name,
           az.country_code, az.continent, az.status
    FROM availability_zones az
    JOIN providers p ON az.provider_id = p.id
    WHERE az.status = 'available'
    '''
    
    params = []
    if provider_filter:
        placeholders = ','.join('?' * len(provider_filter))
        query += f' AND p.name IN ({placeholders})'
        params.extend(provider_filter)
    
    query += ' ORDER BY p.name, az.region_id'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    regions = []
    for row in rows:
        regions.append({
            'region_id': row[0],
            'region_name': row[1],
            'provider': row[2],
            'country_code': row[3],
            'continent': row[4],
            'status': row[5]
        })
    
    return regions


def _get_all_providers(db_manager):
    """获取所有云服务商数据的辅助函数"""
    import sqlite3
    
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, display_name, color FROM providers ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    
    providers = []
    for row in rows:
        providers.append({
            'id': row[0],
            'name': row[1],
            'display_name': row[2],
            'color': row[3]
        })
    
    return providers


def _get_statistics(db_manager):
    """获取统计数据的辅助函数"""
    import sqlite3
    
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # 总区域数
    cursor.execute('SELECT COUNT(*) FROM availability_zones WHERE status = "available"')
    total_regions = cursor.fetchone()[0]
    
    # 总国家数
    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM availability_zones WHERE status = "available"')
    total_countries = cursor.fetchone()[0]
    
    # 总云服务商数
    cursor.execute('SELECT COUNT(*) FROM providers')
    total_providers = cursor.fetchone()[0]
    
    # 每个云服务商的区域数
    cursor.execute('''
    SELECT p.name, COUNT(az.id)
    FROM providers p
    LEFT JOIN availability_zones az ON p.id = az.provider_id AND az.status = "available"
    GROUP BY p.id, p.name
    ORDER BY p.name
    ''')
    regions_by_provider = dict(cursor.fetchall())
    
    # 每个大洲的区域数
    cursor.execute('''
    SELECT continent, COUNT(*)
    FROM availability_zones
    WHERE status = "available"
    GROUP BY continent
    ORDER BY continent
    ''')
    regions_by_continent = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'success': True,
        'total_regions': total_regions,
        'total_countries': total_countries,
        'total_providers': total_providers,
        'regions_by_provider': regions_by_provider,
        'regions_by_continent': regions_by_continent
    }


def init_database():
    """初始化数据库和基础数据"""
    db_manager = DatabaseManager()
    db_manager.create_tables()
    
    # 插入云服务商基础数据
    providers_data = [
        Provider(name='linode', display_name='Linode', color='#3498db', api_endpoint='https://api.linode.com/v4/'),
        Provider(name='digitalocean', display_name='DigitalOcean', color='#ffb3d9', api_endpoint='https://api.digitalocean.com/v2/'),
        Provider(name='aliyun', display_name='阿里云', color='#ff8c00', api_endpoint='https://ecs.aliyuncs.com/'),
        Provider(name='tencent', display_name='腾讯云', color='#2ecc71', api_endpoint='https://cvm.tencentcloudapi.com/')
    ]
    
    for provider in providers_data:
        existing = db_manager.get_provider_by_name(provider.name)
        if not existing:
            db_manager.create_provider(provider)
            print(f"Created provider: {provider.display_name}")


if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 创建应用
    app = create_app()
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)
