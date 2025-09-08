/**
 * D3.js 世界地图可视化组件
 * World Map Visualization with D3.js
 */

class WorldMapVisualizer {
    constructor(containerId) {
        this.container = d3.select(containerId);
        this.svg = null;
        this.projection = null;
        this.path = null;
        this.worldData = null;
        this.countries = null;
        this.colorMapper = null;
        this.zoom = null;
        this.mapGroup = null;
        
        // 地图尺寸 - 放大一倍以显示更多细节
        this.width = 1680;
        this.height = 840;
        
        // 初始化翻译管理器
        this.translationManager = new TranslationManager();
        
        console.log('🗺️ 初始化世界地图可视化组件');
        this.init();
    }
    
    async init() {
        try {
            // 创建SVG容器
            this.createSVG();
            
            // 设置地图投影
            this.setupProjection();
            
            // 并行加载世界地图数据和翻译数据
            await Promise.all([
                this.loadWorldData(),
                this.translationManager.ensureLoaded()
            ]);
            
            // 渲染地图
            this.renderMap();
            
            console.log('✅ 世界地图初始化完成');
            
        } catch (error) {
            console.error('❌ 地图初始化失败:', error);
            this.showError('地图加载失败: ' + error.message);
        }
    }
    
    createSVG() {
        // 清空容器
        this.container.selectAll('*').remove();
        
        // 创建SVG元素
        this.svg = this.container
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .style('width', '100%')
            .style('height', 'auto')
            .style('background-color', '#1a202c');
        
        // 创建地图组，用于缩放和平移
        this.mapGroup = this.svg.append('g')
            .attr('class', 'map-group');
        
        // 设置缩放行为
        this.zoom = d3.zoom()
            .scaleExtent([0.3, 3])  // 缩放范围：30% 到 300%
            .on('zoom', (event) => {
                this.mapGroup.attr('transform', event.transform);
            });
        
        // 为SVG添加缩放行为
        this.svg.call(this.zoom);
        
        // 设置控制按钮事件监听
        this.setupControls();
    }
    
    setupProjection() {
        // 使用自然地球投影（D3.js内置）- 放大并调整中心
        this.projection = d3.geoNaturalEarth1()
            .scale(280)  // 进一步增加缩放比例
            .center([30, 10])  // 向东南调整中心点，减少左侧海洋和南极
            .translate([this.width / 2, this.height / 2])
            .clipExtent([[0, 0], [this.width, this.height]]);  // 裁剪边界
        
        // 创建路径生成器
        this.path = d3.geoPath().projection(this.projection);
    }
    
    async loadWorldData() {
        try {
            // 加载TopoJSON世界地图数据
            this.worldData = await d3.json('/static/data/world-110m.json');
            
            if (!this.worldData) {
                throw new Error('地图数据加载失败');
            }
            
            // 转换为GeoJSON格式
            this.countries = topojson.feature(this.worldData, this.worldData.objects.countries);
            
            console.log('✅ 世界地图数据加载完成', this.countries.features.length, '个国家');
            
        } catch (error) {
            console.error('❌ 地图数据加载失败:', error);
            throw error;
        }
    }
    
    renderMap() {
        // 绘制国家边界到地图组中
        const countryPaths = this.mapGroup.selectAll('.country')
            .data(this.countries.features)
            .enter()
            .append('path')
            .attr('class', 'country')
            .attr('d', this.path)
            .attr('fill', '#4a5568')
            .attr('stroke', '#2d3748')
            .attr('stroke-width', 0.8)
            .style('cursor', 'pointer');
        
        // 添加悬停效果
        countryPaths
            .on('mouseover', (event, d) => {
                d3.select(event.target)
                    .attr('stroke-width', 2)
                    .attr('stroke', '#e2e8f0');
                
                this.showTooltip(event, d);
            })
            .on('mouseout', (event, d) => {
                d3.select(event.target)
                    .attr('stroke-width', 0.8)
                    .attr('stroke', '#2d3748');
                
                this.hideTooltip();
            });
        
        console.log('✅ 地图渲染完成');
    }
    
    updateColors(regionsData, selectedProviders, colorMapping) {
        if (!this.svg || !regionsData) {
            return;
        }
        
        this.colorMapper = new MapColorMapper(colorMapping);
        
        // 按国家分组区域数据
        const countryProviders = this.groupRegionsByCountry(regionsData, selectedProviders);
        
        // 更新国家颜色
        this.mapGroup.selectAll('.country')
            .attr('fill', (d) => {
                const countryCode = this.getCountryCode(d.id);
                const providers = countryProviders[countryCode] || [];
                return this.colorMapper.getCountryColor(providers, selectedProviders);
            });
        
        console.log('🎨 地图颜色已更新', Object.keys(countryProviders).length, '个国家有服务');
    }
    
    groupRegionsByCountry(regionsData, selectedProviders) {
        const countryProviders = {};
        
        regionsData.forEach(region => {
            if (selectedProviders.includes(region.provider)) {
                const countryCode = region.country_code;
                if (!countryProviders[countryCode]) {
                    countryProviders[countryCode] = [];
                }
                if (!countryProviders[countryCode].includes(region.provider)) {
                    countryProviders[countryCode].push(region.provider);
                }
            }
        });
        
        return countryProviders;
    }
    
    getCountryCode(numericId) {
        // 将数字ID转换为ISO 3166-1 alpha-2国家代码 (完整映射)
        const idMapping = {
            // 亚洲国家
            '156': 'CN',  // 中国
            '392': 'JP',  // 日本
            '702': 'SG',  // 新加坡
            '410': 'KR',  // 韩国
            '356': 'IN',  // 印度
            '458': 'MY',  // 马来西亚
            '608': 'PH',  // 菲律宾
            '764': 'TH',  // 泰国
            '360': 'ID',  // 印尼
            '784': 'AE',  // 阿联酋
            '344': 'HK',  // 香港
            '096': 'BN',  // 文莱
            '462': 'MV',  // 马尔代夫
            '144': 'LK',  // 斯里兰卡
            '050': 'BD',  // 孟加拉国
            '064': 'BT',  // 不丹
            '524': 'NP',  // 尼泊尔
            '586': 'PK',  // 巴基斯坦
            '004': 'AF',  // 阿富汗
            '048': 'BH',  // 巴林
            '368': 'IQ',  // 伊拉克
            '364': 'IR',  // 伊朗
            '376': 'IL',  // 以色列
            '400': 'JO',  // 约旦
            '414': 'KW',  // 科威特
            '422': 'LB',  // 黎巴嫩
            '512': 'OM',  // 阿曼
            '634': 'QA',  // 卡塔尔
            '682': 'SA',  // 沙特阿拉伯
            '760': 'SY',  // 叙利亚
            '792': 'TR',  // 土耳其
            '887': 'YE',  // 也门
            
            // 北美国家
            '840': 'US',  // 美国
            '124': 'CA',  // 加拿大
            '484': 'MX',  // 墨西哥
            '320': 'GT',  // 危地马拉
            '084': 'BZ',  // 伯利兹
            '188': 'CR',  // 哥斯达黎加
            '558': 'NI',  // 尼加拉瓜
            '591': 'PA',  // 巴拿马
            '214': 'DO',  // 多米尼加
            '332': 'HT',  // 海地
            '388': 'JM',  // 牙买加
            '192': 'CU',  // 古巴
            
            // 南美国家
            '076': 'BR',  // 巴西
            '032': 'AR',  // 阿根廷
            '152': 'CL',  // 智利
            '170': 'CO',  // 哥伦比亚
            '604': 'PE',  // 秘鲁
            '858': 'UY',  // 乌拉圭
            '862': 'VE',  // 委内瑞拉
            '218': 'EC',  // 厄瓜多尔
            '600': 'PY',  // 巴拉圭
            '740': 'SR',  // 苏里南
            '328': 'GY',  // 圭亚那
            
            // 欧洲国家
            '276': 'DE',  // 德国
            '826': 'GB',  // 英国
            '250': 'FR',  // 法国
            '380': 'IT',  // 意大利
            '724': 'ES',  // 西班牙
            '528': 'NL',  // 荷兰
            '056': 'BE',  // 比利时
            '756': 'CH',  // 瑞士
            '040': 'AT',  // 奥地利
            '616': 'PL',  // 波兰
            '203': 'CZ',  // 捷克
            '703': 'SK',  // 斯洛伐克
            '348': 'HU',  // 匈牙利
            '642': 'RO',  // 罗马尼亚
            '100': 'BG',  // 保加利亚
            '191': 'HR',  // 克罗地亚
            '705': 'SI',  // 斯洛文尼亚
            '070': 'BA',  // 波斯尼亚和黑塞哥维那
            '688': 'RS',  // 塞尔维亚
            '499': 'ME',  // 黑山
            '807': 'MK',  // 北马其顿
            '008': 'AL',  // 阿尔巴尼亚
            '300': 'GR',  // 希腊
            '440': 'LT',  // 立陶宛
            '428': 'LV',  // 拉脱维亚
            '233': 'EE',  // 爱沙尼亚
            '246': 'FI',  // 芬兰
            '752': 'SE',  // 瑞典
            '578': 'NO',  // 挪威
            '208': 'DK',  // 丹麦
            '352': 'IS',  // 冰岛
            '372': 'IE',  // 爱尔兰
            '620': 'PT',  // 葡萄牙
            '643': 'RU',  // 俄罗斯
            '804': 'UA',  // 乌克兰
            '112': 'BY',  // 白俄罗斯
            '268': 'GE',  // 格鲁吉亚
            '051': 'AM',  // 亚美尼亚
            '031': 'AZ',  // 阿塞拜疆
            
            // 大洋洲国家
            '036': 'AU',  // 澳大利亚
            '554': 'NZ',  // 新西兰
            '242': 'FJ',  // 斐济
            '598': 'PG',  // 巴布亚新几内亚
            '090': 'SB',  // 所罗门群岛
            '548': 'VU',  // 瓦努阿图
            '584': 'MH',  // 马绍尔群岛
            '520': 'NR',  // 瑙鲁
            '296': 'KI',  // 基里巴斯
            '798': 'TV',  // 图瓦卢
            '882': 'WS',  // 萨摩亚
            '776': 'TO',  // 汤加
            
            // 非洲国家
            '012': 'DZ',  // 阿尔及利亚
            '818': 'EG',  // 埃及
            '434': 'LY',  // 利比亚
            '504': 'MA',  // 摩洛哥
            '788': 'TN',  // 突尼斯
            '710': 'ZA',  // 南非
            '566': 'NG',  // 尼日利亚
            '404': 'KE',  // 肯尼亚
            '818': 'EG',  // 埃及
            '231': 'ET',  // 埃塞俄比亚
            '834': 'TZ',  // 坦桑尼亚
            '800': 'UG',  // 乌干达
            '646': 'RW',  // 卢旺达
            '108': 'BI',  // 布隆迪
            '180': 'CD',  // 刚果民主共和国
            '178': 'CG',  // 刚果共和国
            '120': 'CM',  // 喀麦隆
            '140': 'CF',  // 中非共和国
            '148': 'TD',  // 乍得
            '854': 'BF',  // 布基纳法索
            '466': 'ML',  // 马里
            '562': 'NE',  // 尼日尔
            '624': 'GW',  // 几内亚比绍
            '324': 'GN',  // 几内亚
            '694': 'SL',  // 塞拉利昂
            '430': 'LR',  // 利比里亚
            '384': 'CI',  // 科特迪瓦
            '288': 'GH',  // 加纳
            '768': 'TG',  // 多哥
            '204': 'BJ',  // 贝宁
            '132': 'CV',  // 佛得角
            '270': 'GM',  // 冈比亚
            '686': 'SN',  // 塞内加尔
            '478': 'MR',  // 毛里塔尼亚
        };
        
        return idMapping[numericId] || numericId;
    }
    
    showTooltip(event, countryData) {
        const tooltip = d3.select('body')
            .selectAll('.map-tooltip')
            .data([1])
            .join('div')
            .attr('class', 'map-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('padding', '8px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', 1000);
        
        const countryCode = this.getCountryCode(countryData.id);
        const chineseName = this.translationManager.getCountryName(countryCode);
        
        tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .html(`${chineseName} (${countryCode})`);
    }
    
    hideTooltip() {
        d3.select('body').selectAll('.map-tooltip').remove();
    }
    
    showError(message) {
        this.container
            .html(`
                <div style="text-align: center; padding: 50px; color: #dc3545;">
                    <h3>❌ ${message}</h3>
                    <p>请检查网络连接或联系技术支持</p>
                </div>
            `);
    }
    
    resize() {
        // 响应式调整 - 保持宽高比
        const containerWidth = this.container.node().getBoundingClientRect().width;
        const scale = Math.min(containerWidth / this.width, 1);
        
        this.svg
            .style('width', '100%')
            .style('height', (this.height * scale) + 'px')
            .style('max-height', this.height + 'px');
    }
    
    // 设置控制按钮事件监听
    setupControls() {
        // 等待DOM加载完成再绑定事件
        setTimeout(() => {
            // 缩放控制
            const zoomInBtn = document.getElementById('zoom-in');
            const zoomOutBtn = document.getElementById('zoom-out');
            
            if (zoomInBtn) {
                zoomInBtn.addEventListener('click', () => this.zoomIn());
            }
            if (zoomOutBtn) {
                zoomOutBtn.addEventListener('click', () => this.zoomOut());
            }
            
            // 移动控制
            const moveUpBtn = document.getElementById('move-up');
            const moveDownBtn = document.getElementById('move-down');
            const moveLeftBtn = document.getElementById('move-left');
            const moveRightBtn = document.getElementById('move-right');
            
            if (moveUpBtn) moveUpBtn.addEventListener('click', () => this.moveMap(0, -50));
            if (moveDownBtn) moveDownBtn.addEventListener('click', () => this.moveMap(0, 50));
            if (moveLeftBtn) moveLeftBtn.addEventListener('click', () => this.moveMap(-50, 0));
            if (moveRightBtn) moveRightBtn.addEventListener('click', () => this.moveMap(50, 0));
            
            console.log('✅ 地图控制按钮已设置');
        }, 100);
    }
    
    // 放大地图
    zoomIn() {
        if (!this.zoom || !this.svg) return;
        
        this.svg.transition().duration(300).call(
            this.zoom.scaleBy, 1.5
        );
        console.log('🔍 地图放大');
    }
    
    // 缩小地图
    zoomOut() {
        if (!this.zoom || !this.svg) return;
        
        this.svg.transition().duration(300).call(
            this.zoom.scaleBy, 1 / 1.5
        );
        console.log('🔍 地图缩小');
    }
    
    // 移动地图
    moveMap(deltaX, deltaY) {
        if (!this.zoom || !this.svg) return;
        
        this.svg.transition().duration(300).call(
            this.zoom.translateBy, deltaX, deltaY
        );
        console.log(`🗺️ 地图移动: (${deltaX}, ${deltaY})`);
    }
    
    // 重置地图视图
    resetView() {
        if (!this.zoom || !this.svg) return;
        
        this.svg.transition().duration(500).call(
            this.zoom.transform,
            d3.zoomIdentity
        );
        console.log('🏠 地图视图已重置');
    }
}

/**
 * 翻译管理器 - 处理国家和区域的中文名称
 */
class TranslationManager {
    constructor() {
        this.translations = null;
        this.isLoaded = false;
        this.loadTranslations();
    }
    
    async loadTranslations() {
        try {
            const response = await fetch('/static/data/translations.json');
            this.translations = await response.json();
            this.isLoaded = true;
            console.log('✅ 翻译数据加载完成');
        } catch (error) {
            console.error('❌ 翻译数据加载失败:', error);
            this.translations = { countries: {}, regions: {} };
            this.isLoaded = true;
        }
    }
    
    getCountryName(countryCode) {
        if (!this.translations) return countryCode;
        return this.translations.countries[countryCode] || countryCode;
    }
    
    getRegionName(regionId) {
        if (!this.translations) return regionId;
        return this.translations.regions[regionId] || regionId;
    }
    
    // 确保翻译数据已加载
    async ensureLoaded() {
        if (!this.isLoaded) {
            await this.loadTranslations();
        }
    }
}

/**
 * 地图颜色映射工具类
 */
class MapColorMapper {
    constructor(colorMapping = {}) {
        // 默认颜色配置 - 适配暗色主题
        this.colors = {
            linode: '#3498db',      // 蓝色
            digitalocean: '#ffb3d9', // 浅粉色  
            aliyun: '#ff8c00',       // 橘黄色
            tencent: '#2ecc71',      // 绿色
            multiple_with_linode: '#e74c3c', // 红色（多云且包含Linode）
            default: '#4a5568'       // 暗色主题默认颜色
        };
        
        // 合并自定义颜色映射
        Object.assign(this.colors, colorMapping);
    }
    
    getCountryColor(providers, selectedProviders) {
        const activeProviders = providers.filter(p => selectedProviders.includes(p));
        
        if (activeProviders.length === 0) {
            return this.colors.default;
        }
        
        if (activeProviders.length > 1 && activeProviders.includes('linode')) {
            return this.colors.multiple_with_linode;
        }
        
        if (activeProviders.length === 1) {
            return this.colors[activeProviders[0]] || this.colors.default;
        }
        
        // 多云但不包含Linode，显示第一个的颜色
        return this.colors[activeProviders[0]] || this.colors.default;
    }
}

// 创建全局翻译管理器实例
window.translationManager = new TranslationManager();

// 导出到全局
window.WorldMapVisualizer = WorldMapVisualizer;
window.MapColorMapper = MapColorMapper;
window.TranslationManager = TranslationManager;