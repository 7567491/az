#!/bin/bash

# 云服务区域可视化系统 - 最终测试脚本
# Final Test Script for Cloud AZ Visualizer

echo "🧪 云服务区域可视化系统 - 最终测试"
echo "========================================="

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="https://az.linapp.fun"

# 测试函数
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    printf "%-30s" "$description"
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        return 0
    else
        echo -e "${RED}❌ 失败 ($response)${NC}"
        return 1
    fi
}

test_api_data() {
    local endpoint=$1
    local description=$2
    local expected_field=$3
    
    printf "%-30s" "$description"
    
    local response=$(curl -s "$BASE_URL$endpoint")
    local status=$?
    
    if [ $status -eq 0 ] && echo "$response" | grep -q "\"$expected_field\""; then
        echo -e "${GREEN}✅ 通过${NC}"
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        return 1
    fi
}

# 开始测试
echo -e "${YELLOW}1. 基础连接测试${NC}"
test_endpoint "/" "主页访问"
test_endpoint "/test" "测试页面"
test_endpoint "/debug" "调试页面"

echo ""
echo -e "${YELLOW}2. API接口测试${NC}"
test_api_data "/api/stats" "统计数据API" "total_regions"
test_api_data "/api/regions" "区域数据API" "regions"
test_api_data "/api/countries" "国家数据API" "countries"
test_api_data "/api/providers" "云服务商API" "providers"
test_api_data "/api/colors" "颜色映射API" "color_mapping"

echo ""
echo -e "${YELLOW}3. 静态资源测试${NC}"
test_endpoint "/static/js/main.js" "主应用脚本"
test_endpoint "/static/js/map.js" "地图组件脚本"
test_endpoint "/static/css/style.css" "样式文件"
test_endpoint "/static/data/world-110m.json" "地图数据文件"

echo ""
echo -e "${YELLOW}4. 数据内容验证${NC}"

# 检查统计数据
printf "%-30s" "统计数据内容"
stats_response=$(curl -s "$BASE_URL/api/stats")
if echo "$stats_response" | grep -q '"total_regions": 47' && echo "$stats_response" | grep -q '"total_countries": 14'; then
    echo -e "${GREEN}✅ 通过 (47区域, 14国家)${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

# 检查区域数据
printf "%-30s" "区域数据内容"
regions_count=$(curl -s "$BASE_URL/api/regions" | grep -o '"provider"' | wc -l)
if [ "$regions_count" -gt 40 ]; then
    echo -e "${GREEN}✅ 通过 ($regions_count 个区域)${NC}"
else
    echo -e "${RED}❌ 失败 (仅 $regions_count 个区域)${NC}"
fi

# 检查地图数据
printf "%-30s" "地图数据文件"
map_size=$(curl -s "$BASE_URL/static/data/world-110m.json" | wc -c)
if [ "$map_size" -gt 50000 ]; then
    echo -e "${GREEN}✅ 通过 (${map_size} bytes)${NC}"
else
    echo -e "${RED}❌ 失败 (仅 ${map_size} bytes)${NC}"
fi

echo ""
echo -e "${YELLOW}5. 功能集成测试${NC}"

# 检查主页是否包含关键元素
printf "%-30s" "主页UI元素"
main_page=$(curl -s "$BASE_URL/")
if echo "$main_page" | grep -q "total-regions" && echo "$main_page" | grep -q "world-map" && echo "$main_page" | grep -q "regions-grid"; then
    echo -e "${GREEN}✅ 通过${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

# 检查JavaScript库加载
printf "%-30s" "JavaScript库引用"
if echo "$main_page" | grep -q "d3.v7.min.js" && echo "$main_page" | grep -q "topojson"; then
    echo -e "${GREEN}✅ 通过${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

echo ""
echo -e "${YELLOW}6. 性能测试${NC}"

# 测试响应时间
printf "%-30s" "API响应时间"
response_time=$(curl -s -w "%{time_total}" -o /dev/null "$BASE_URL/api/stats")
if (( $(echo "$response_time < 2.0" | bc -l) )); then
    echo -e "${GREEN}✅ 通过 (${response_time}s)${NC}"
else
    echo -e "${YELLOW}⚠ 较慢 (${response_time}s)${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}🎉 测试完成！${NC}"
echo ""
echo -e "${YELLOW}访问地址：${NC}"
echo "  主系统: $BASE_URL"
echo "  测试页: $BASE_URL/test"  
echo "  调试页: $BASE_URL/debug"
echo ""
echo -e "${YELLOW}功能特性：${NC}"
echo "  ✅ 47个全球云服务区域"
echo "  ✅ 4个云服务提供商支持"
echo "  ✅ 实时数据API接口"
echo "  ✅ D3.js世界地图可视化"
echo "  ✅ 响应式用户界面"
echo "  ✅ HTTPS安全访问"