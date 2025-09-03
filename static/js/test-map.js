/**
 * 地图功能测试脚本
 * Map Functionality Tests
 */

// 简单的测试框架
class SimpleTest {
    constructor() {
        this.tests = [];
        this.results = [];
    }
    
    test(name, fn) {
        this.tests.push({ name, fn });
    }
    
    async run() {
        console.log('🧪 开始运行地图功能测试...');
        
        for (const test of this.tests) {
            try {
                await test.fn();
                this.results.push({ name: test.name, status: '✅ 通过' });
                console.log(`✅ ${test.name}`);
            } catch (error) {
                this.results.push({ name: test.name, status: '❌ 失败', error: error.message });
                console.error(`❌ ${test.name}: ${error.message}`);
            }
        }
        
        this.printResults();
    }
    
    printResults() {
        console.log('\n📊 测试结果:');
        this.results.forEach(result => {
            console.log(`${result.status} ${result.name}`);
            if (result.error) {
                console.log(`   错误: ${result.error}`);
            }
        });
        
        const passed = this.results.filter(r => r.status.includes('✅')).length;
        const total = this.results.length;
        console.log(`\n总计: ${passed}/${total} 测试通过`);
    }
    
    assert(condition, message) {
        if (!condition) {
            throw new Error(message);
        }
    }
    
    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(`${message}: 期望 ${expected}, 实际 ${actual}`);
        }
    }
}

// 创建测试实例
const mapTests = new SimpleTest();

// 测试1: 检查D3.js是否加载
mapTests.test('D3.js库加载测试', () => {
    mapTests.assert(typeof d3 !== 'undefined', 'D3.js库未加载');
    mapTests.assert(typeof topojson !== 'undefined', 'TopoJSON库未加载');
});

// 测试2: 检查地图数据文件
mapTests.test('地图数据文件测试', async () => {
    const response = await fetch('/static/data/world-110m.json');
    mapTests.assert(response.ok, '地图数据文件请求失败');
    
    const data = await response.json();
    mapTests.assert(data.type === 'Topology', '地图数据格式错误');
    mapTests.assert(data.objects && data.objects.countries, '国家数据不存在');
});

// 测试3: WorldMapVisualizer类测试
mapTests.test('WorldMapVisualizer类测试', () => {
    mapTests.assert(typeof WorldMapVisualizer !== 'undefined', 'WorldMapVisualizer类未定义');
    
    // 创建测试容器
    const testContainer = document.createElement('div');
    testContainer.id = 'test-map';
    document.body.appendChild(testContainer);
    
    // 测试实例化
    const map = new WorldMapVisualizer('#test-map');
    mapTests.assert(map instanceof WorldMapVisualizer, '地图实例创建失败');
    
    // 清理
    document.body.removeChild(testContainer);
});

// 测试4: ColorMapper类测试  
mapTests.test('ColorMapper类测试', () => {
    mapTests.assert(typeof ColorMapper !== 'undefined', 'ColorMapper类未定义');
    
    const colorMapper = new ColorMapper();
    
    // 测试单个云服务商颜色
    const linodeColor = colorMapper.getCountryColor(['linode'], ['linode']);
    mapTests.assertEqual(linodeColor, '#3498db', 'Linode颜色错误');
    
    // 测试多云服务商且包含Linode的情况
    const multiColor = colorMapper.getCountryColor(['linode', 'digitalocean'], ['linode', 'digitalocean']);
    mapTests.assertEqual(multiColor, '#e74c3c', '多云含Linode颜色错误');
    
    // 测试无服务情况
    const noServiceColor = colorMapper.getCountryColor([], ['linode']);
    mapTests.assertEqual(noServiceColor, '#e0e0e0', '无服务颜色错误');
});

// 测试5: API接口测试
mapTests.test('API接口测试', async () => {
    const endpoints = ['/api/regions', '/api/countries', '/api/providers', '/api/stats', '/api/colors'];
    
    for (const endpoint of endpoints) {
        const response = await fetch(endpoint);
        mapTests.assert(response.ok, `${endpoint} 接口请求失败`);
        
        const data = await response.json();
        mapTests.assert(typeof data === 'object', `${endpoint} 返回数据格式错误`);
    }
});

// 测试6: 主应用集成测试
mapTests.test('主应用集成测试', () => {
    mapTests.assert(typeof CloudAZApp !== 'undefined', 'CloudAZApp类未定义');
    
    // 检查应用是否已初始化
    mapTests.assert(window.app instanceof CloudAZApp, '主应用未正确初始化');
    
    // 检查数据结构
    const app = window.app;
    mapTests.assert(typeof app.data === 'object', '应用数据结构错误');
    mapTests.assert(Array.isArray(app.selectedProviders), '选中云服务商列表错误');
});

// 导出测试函数
window.runMapTests = () => mapTests.run();

// 自动运行测试（如果页面完全加载）
if (document.readyState === 'complete') {
    setTimeout(() => window.runMapTests(), 2000);
} else {
    window.addEventListener('load', () => {
        setTimeout(() => window.runMapTests(), 2000);
    });
}