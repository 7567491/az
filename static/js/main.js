/**
 * 云服务区域可视化系统主应用
 * Cloud AZ Visualizer Main Application
 */

class CloudAZApp {
    constructor() {
        console.log('🚀 初始化云服务区域可视化系统');
        
        // 应用状态
        this.data = {
            providers: [],
            regions: [],
            countries: [],
            stats: {},
            colorMapping: {}
        };
        
        // 选中的云服务商
        this.selectedProviders = ['linode', 'digitalocean', 'aliyun', 'tencent'];
        
        // 初始化
        this.init();
    }
    
    async init() {
        try {
            // 绑定事件监听器
            this.bindEventListeners();
            
            // 加载初始数据
            await this.loadAllData();
            
            // 渲染界面
            this.renderUI();
            
            console.log('✅ 应用初始化完成');
            
        } catch (error) {
            console.error('❌ 应用初始化失败:', error);
            this.showMessage('应用初始化失败: ' + error.message, 'error');
        }
    }
    
    /**
     * 绑定事件监听器
     */
    bindEventListeners() {
        // 云服务商选择器
        const checkboxes = document.querySelectorAll('.provider-selection input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.handleProviderSelection(e);
            });
        });
        
        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.handleRefreshData();
            });
        }
        
        console.log('📡 事件监听器已绑定');
    }
    
    /**
     * 加载所有数据
     */
    async loadAllData() {
        console.log('📊 开始加载数据...');
        
        try {
            // 并发加载所有数据
            const [providersRes, regionsRes, countriesRes, statsRes, colorsRes] = await Promise.all([
                fetch('/api/providers'),
                fetch('/api/regions'),
                fetch('/api/countries'),
                fetch('/api/stats'),
                fetch('/api/colors')
            ]);
            
            // 解析响应
            const providers = await providersRes.json();
            const regions = await regionsRes.json();
            const countries = await countriesRes.json();
            const stats = await statsRes.json();
            const colors = await colorsRes.json();
            
            // 存储数据
            this.data.providers = providers.providers || [];
            this.data.regions = regions.regions || [];
            this.data.countries = countries.countries || [];
            this.data.stats = stats;
            this.data.colorMapping = colors.color_mapping || {};
            
            console.log('✅ 数据加载完成:', {
                providers: this.data.providers.length,
                regions: this.data.regions.length,
                countries: this.data.countries.length
            });
            
        } catch (error) {
            console.error('❌ 数据加载失败:', error);
            throw new Error('无法加载数据，请检查服务器连接');
        }
    }
    
    /**
     * 渲染用户界面
     */
    renderUI() {
        console.log('🎨 开始渲染界面...');
        
        // 更新统计信息
        this.updateStats();
        
        // 渲染区域列表
        this.renderRegionsList();
        
        // 初始化地图
        this.initializeMap();
        
        // 更新最后更新时间
        this.updateLastUpdatedTime();
        
        console.log('✅ 界面渲染完成');
    }
    
    /**
     * 初始化世界地图
     */
    async initializeMap() {
        try {
            console.log('🗺️ 初始化世界地图...');
            
            // 检查D3.js和WorldMapVisualizer是否可用
            if (typeof d3 === 'undefined') {
                throw new Error('D3.js 库未加载');
            }
            
            if (typeof WorldMapVisualizer === 'undefined') {
                throw new Error('WorldMapVisualizer 组件未加载');
            }
            
            // 创建地图可视化组件
            this.worldMap = new WorldMapVisualizer('#world-map');
            
            // 等待地图初始化完成后更新颜色
            setTimeout(() => {
                this.updateMapColors();
            }, 1000);
            
        } catch (error) {
            console.error('❌ 地图初始化失败:', error);
            this.showMapError('地图初始化失败: ' + error.message);
        }
    }
    
    /**
     * 显示地图错误
     */
    showMapError(message) {
        const mapContainer = document.getElementById('world-map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="text-align: center; padding: 100px; color: #dc3545;">
                    <div style="font-size: 48px; margin-bottom: 20px;">❌</div>
                    <div style="font-size: 18px; margin-bottom: 10px;">${message}</div>
                    <div style="font-size: 14px;">请刷新页面重试</div>
                </div>
            `;
        }
    }
    
    /**
     * 更新地图颜色
     */
    updateMapColors() {
        if (this.worldMap) {
            this.worldMap.updateColors(
                this.data.regions,
                this.selectedProviders,
                this.data.colorMapping
            );
        }
    }
    
    /**
     * 更新统计信息
     */
    updateStats() {
        const stats = this.data.stats;
        
        // 更新统计卡片
        this.updateStatCard('total-regions', stats.total_regions || 0);
        this.updateStatCard('total-countries', stats.total_countries || 0);
        this.updateStatCard('total-providers', this.data.providers.length);
        
        console.log('📈 统计信息已更新');
    }
    
    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    /**
     * 渲染区域列表
     */
    renderRegionsList() {
        const container = document.getElementById('regions-grid');
        if (!container) {
            console.error('❌ 区域容器 #regions-grid 未找到');
            return;
        }
        
        // 检查数据是否已加载
        if (!this.data.regions || this.data.regions.length === 0) {
            container.innerHTML = '<div class="loading">暂无区域数据</div>';
            console.warn('⚠️ 区域数据为空');
            return;
        }
        
        if (!this.data.providers || this.data.providers.length === 0) {
            container.innerHTML = '<div class="loading">暂无云服务商数据</div>';
            console.warn('⚠️ 云服务商数据为空');
            return;
        }
        
        // 按云服务商分组区域
        const regionsByProvider = this.groupRegionsByProvider();
        
        // 清空容器
        container.innerHTML = '';
        
        // 按指定顺序显示云服务商
        const providerOrder = ['linode', 'digitalocean', 'aliyun', 'tencent'];
        
        providerOrder.forEach(providerName => {
            const provider = this.data.providers.find(p => p.name === providerName);
            if (provider) {
                const providerRegions = regionsByProvider[provider.name] || [];
                const column = this.createProviderColumn(provider, providerRegions);
                container.appendChild(column);
            }
        });
        
        console.log('📋 区域列表已渲染:', {
            providers: this.data.providers.length,
            regions: this.data.regions.length,
            grouped: Object.keys(regionsByProvider).length
        });
    }
    
    /**
     * 按云服务商分组区域
     */
    groupRegionsByProvider() {
        const grouped = {};
        
        this.data.regions.forEach(region => {
            if (!grouped[region.provider]) {
                grouped[region.provider] = [];
            }
            grouped[region.provider].push(region);
        });
        
        return grouped;
    }
    
    /**
     * 创建云服务商列
     */
    createProviderColumn(provider, regions) {
        const column = document.createElement('div');
        column.className = 'provider-column';
        column.style.borderLeftColor = provider.color;
        
        // 标题
        const header = document.createElement('h4');
        header.innerHTML = `
            <span class="provider-badge" style="background: ${provider.color}"></span>
            ${provider.display_name} (${regions.length})
        `;
        column.appendChild(header);
        
        // 按大洲分组
        const regionsByContinent = this.groupRegionsByContinent(regions);
        
        // 渲染每个大区的区域 - 中国单列
        ['china', 'americas', 'europe-africa', 'apac', 'others'].forEach(continent => {
            const continentRegions = regionsByContinent[continent] || [];
            if (continentRegions.length > 0) {
                const section = this.createContinentSection(continent, continentRegions);
                column.appendChild(section);
            }
        });
        
        return column;
    }
    
    /**
     * 按大区分组区域 - 中国单列
     */
    groupRegionsByContinent(regions) {
        const grouped = {};
        
        regions.forEach(region => {
            let continent;
            
            // 中国区域单独分类
            if (region.country_code === 'CN' || region.region_id?.startsWith('cn-')) {
                continent = 'china';
            } else {
                // 其他区域按原分类
                continent = region.continent || 'others';
            }
            
            if (!grouped[continent]) {
                grouped[continent] = [];
            }
            grouped[continent].push(region);
        });
        
        return grouped;
    }
    
    /**
     * 创建大洲区域段
     */
    createContinentSection(continent, regions) {
        const section = document.createElement('div');
        section.className = 'continent-section';
        
        // 大洲标题
        const title = document.createElement('h5');
        title.textContent = this.getContinentName(continent);
        section.appendChild(title);
        
        // 区域列表
        const list = document.createElement('div');
        list.className = 'region-list';
        
        regions.forEach(region => {
            const item = document.createElement('div');
            item.className = 'region-item';
            item.innerHTML = `
                <span class="region-code">${region.region_id}</span>
                <span class="region-name">${region.region_name}</span>
            `;
            list.appendChild(item);
        });
        
        section.appendChild(list);
        return section;
    }
    
    /**
     * 获取大区中文名称
     */
    getContinentName(continent) {
        const names = {
            'china': '🇨🇳 中国',
            'americas': '🌎 美洲',
            'europe-africa': '🌍 欧洲-非洲', 
            'apac': '🌏 亚太地区',
            'others': '🌐 其他地区'
        };
        return names[continent] || continent;
    }
    
    
    /**
     * 处理云服务商选择
     */
    handleProviderSelection(event) {
        const providerId = event.target.id;
        const isChecked = event.target.checked;
        
        if (isChecked && !this.selectedProviders.includes(providerId)) {
            this.selectedProviders.push(providerId);
        } else if (!isChecked) {
            this.selectedProviders = this.selectedProviders.filter(p => p !== providerId);
        }
        
        console.log('🎛️ 云服务商选择已更新:', this.selectedProviders);
        
        // 重新渲染区域列表
        this.renderRegionsList();
        
        // 更新地图（如果已实现）
        this.updateMapColors();
    }
    
    
    /**
     * 处理数据刷新
     */
    async handleRefreshData() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (!refreshBtn) return;
        
        // 禁用按钮并显示加载状态
        refreshBtn.disabled = true;
        refreshBtn.textContent = '🔄 刷新中...';
        
        try {
            console.log('🔄 开始刷新数据...');
            
            // 调用刷新API
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 重新加载数据
                await this.loadAllData();
                
                // 重新渲染界面
                this.renderUI();
                
                this.showMessage(`数据刷新成功！更新了 ${result.regions_by_provider ? Object.values(result.regions_by_provider).reduce((a, b) => a + b, 0) : 0} 个区域`, 'success');
                
                console.log('✅ 数据刷新完成');
            } else {
                throw new Error(result.error || '刷新失败');
            }
            
        } catch (error) {
            console.error('❌ 数据刷新失败:', error);
            this.showMessage('数据刷新失败: ' + error.message, 'error');
            
        } finally {
            // 恢复按钮状态
            refreshBtn.disabled = false;
            refreshBtn.textContent = '🔄 刷新数据';
        }
    }
    
    /**
     * 更新最后更新时间
     */
    updateLastUpdatedTime() {
        const element = document.getElementById('last-updated');
        if (element) {
            const now = new Date();
            element.textContent = `最后更新: ${now.toLocaleDateString('zh-CN')}`;
        }
        
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleDateString('zh-CN');
        }
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'success') {
        // 调用全局的showMessage函数
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    /**
     * 获取应用状态（用于调试）
     */
    getState() {
        return {
            selectedProviders: this.selectedProviders,
            dataLoaded: {
                providers: this.data.providers.length,
                regions: this.data.regions.length,
                countries: this.data.countries.length
            },
            stats: this.data.stats
        };
    }
}

// 颜色计算工具函数
class ColorMapper {
    constructor(colorMapping) {
        this.colors = colorMapping;
    }
    
    /**
     * 计算国家颜色
     * @param {Array} countryProviders - 该国家拥有的云服务商列表
     * @param {Array} selectedProviders - 当前选中的云服务商列表
     * @returns {string} 颜色代码
     */
    calculateCountryColor(countryProviders, selectedProviders) {
        const activeProviders = countryProviders.filter(p => selectedProviders.includes(p));
        
        // 如果包含Linode且有其他云服务商 → 红色
        if (activeProviders.length > 1 && activeProviders.includes('linode')) {
            return '#e74c3c';
        }
        
        // 单个云服务商 → 对应颜色
        if (activeProviders.length === 1) {
            return this.colors[activeProviders[0]] || '#cccccc';
        }
        
        // 多个但不含Linode → 按优先级显示第一个
        if (activeProviders.length > 1) {
            return this.colors[activeProviders[0]] || '#cccccc';
        }
        
        // 无服务 → 白色
        return '#ffffff';
    }
}

// 导出给全局使用
window.CloudAZApp = CloudAZApp;
window.ColorMapper = ColorMapper;

console.log('📦 Cloud AZ Visualizer 主应用模块加载完成');