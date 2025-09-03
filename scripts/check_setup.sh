#!/bin/bash

# 部署前检查脚本
# 验证所有配置文件和依赖

set -e

echo "🔍 云服务区域可视化系统 - 部署前检查"
echo "================================="

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/az/cloud-az-visualizer"
cd "$PROJECT_DIR"

echo -e "${YELLOW}1. 检查Python环境...${NC}"

# 检查Python版本
python3 --version
echo -e "${GREEN}✓ Python3 可用${NC}"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ 虚拟环境存在${NC}"
    source venv/bin/activate
    
    # 检查Flask
    if python -c "import flask" 2>/dev/null; then
        echo -e "${GREEN}✓ Flask 已安装${NC}"
    else
        echo -e "${RED}✗ Flask 未安装${NC}"
        exit 1
    fi
    
    deactivate
else
    echo -e "${RED}✗ 虚拟环境不存在${NC}"
    exit 1
fi

echo -e "${YELLOW}2. 检查项目文件...${NC}"

# 检查关键文件
files_to_check=(
    "app.py"
    "config.py"
    "requirements.txt"
    "database/models.py"
    "api/cloud_collector.py"
    "templates/index.html"
    "static/css/style.css"
    "static/js/main.js"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file 不存在${NC}"
    fi
done

echo -e "${YELLOW}3. 检查nginx配置...${NC}"

# 检查nginx配置文件
if [ -f "nginx/az.linapp.fun" ]; then
    echo -e "${GREEN}✓ HTTPS nginx配置文件存在${NC}"
else
    echo -e "${RED}✗ nginx配置文件不存在${NC}"
fi

if [ -f "nginx/az.linapp.fun.http" ]; then
    echo -e "${GREEN}✓ HTTP nginx配置文件存在${NC}"
else
    echo -e "${RED}✗ HTTP nginx配置文件不存在${NC}"
fi

echo -e "${YELLOW}4. 检查部署脚本...${NC}"

if [ -f "scripts/deploy.sh" ] && [ -x "scripts/deploy.sh" ]; then
    echo -e "${GREEN}✓ 部署脚本存在且可执行${NC}"
else
    echo -e "${RED}✗ 部署脚本问题${NC}"
fi

if [ -f "scripts/start_app.sh" ] && [ -x "scripts/start_app.sh" ]; then
    echo -e "${GREEN}✓ 启动脚本存在且可执行${NC}"
else
    echo -e "${RED}✗ 启动脚本问题${NC}"
fi

echo -e "${YELLOW}5. 检查环境变量...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env 文件存在${NC}"
    
    # 检查关键环境变量
    source .env
    
    if [ -n "$SECRET_KEY" ]; then
        echo -e "${GREEN}✓ SECRET_KEY 已设置${NC}"
    else
        echo -e "${YELLOW}⚠ SECRET_KEY 未设置${NC}"
    fi
    
    # 检查API密钥
    if [ -n "$LINODE_API_TOKEN" ]; then
        echo -e "${GREEN}✓ Linode API Token${NC}"
    fi
    
    if [ -n "$DIGITALOCEAN_API_TOKEN" ]; then
        echo -e "${GREEN}✓ DigitalOcean API Token${NC}"
    fi
    
    if [ -n "$TENCENT_SECRET_ID" ] && [ -n "$TENCENT_SECRET_KEY" ]; then
        echo -e "${GREEN}✓ 腾讯云 API 密钥${NC}"
    fi
    
    if [ -n "$ALIYUN_ACCESS_KEY_ID" ] && [ -n "$ALIYUN_ACCESS_KEY_SECRET" ]; then
        echo -e "${GREEN}✓ 阿里云 API 密钥${NC}"
    fi
else
    echo -e "${RED}✗ .env 文件不存在${NC}"
fi

echo -e "${YELLOW}6. 测试Flask应用启动...${NC}"

# 测试Flask应用能否正常导入
if python3 -c "import sys; sys.path.append('.'); from app import create_app; app = create_app(); print('Flask应用导入成功')" 2>/dev/null; then
    echo -e "${GREEN}✓ Flask应用可以正常启动${NC}"
else
    echo -e "${RED}✗ Flask应用启动失败${NC}"
fi

echo ""
echo -e "${GREEN}🎉 检查完成！${NC}"
echo ""
echo -e "${YELLOW}部署命令:${NC}"
echo "  sudo ./scripts/deploy.sh"
echo ""
echo -e "${YELLOW}手动启动Flask应用:${NC}"
echo "  ./scripts/start_app.sh"
echo ""
echo -e "${YELLOW}检查服务状态:${NC}"
echo "  systemctl status nginx"
echo "  systemctl status cloud-az-visualizer"