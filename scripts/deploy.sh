#!/bin/bash

# 云服务区域可视化系统 - 部署脚本
# az.linapp.fun 域名配置

set -e

echo "🚀 开始部署 az.linapp.fun..."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/home/az/cloud-az-visualizer"
NGINX_CONFIG_SOURCE="$PROJECT_DIR/nginx/az.linapp.fun"
NGINX_CONFIG_DEST="/etc/nginx/sites-available/az.linapp.fun"
NGINX_LINK="/etc/nginx/sites-enabled/az.linapp.fun"

echo -e "${YELLOW}1. 检查系统环境...${NC}"

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}错误: 此脚本需要root权限运行${NC}"
   echo "请使用: sudo ./deploy.sh"
   exit 1
fi

# 检查nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}nginx 未安装，正在安装...${NC}"
    apt update
    apt install -y nginx
fi

echo -e "${YELLOW}2. 复制nginx配置文件...${NC}"

# 复制nginx配置
cp "$NGINX_CONFIG_SOURCE" "$NGINX_CONFIG_DEST"
echo -e "${GREEN}✓ nginx配置文件已复制${NC}"

# 创建软链接
if [ -L "$NGINX_LINK" ]; then
    rm "$NGINX_LINK"
fi
ln -s "$NGINX_CONFIG_DEST" "$NGINX_LINK"
echo -e "${GREEN}✓ nginx站点已启用${NC}"

echo -e "${YELLOW}3. 测试nginx配置...${NC}"

# 测试nginx配置
if nginx -t; then
    echo -e "${GREEN}✓ nginx配置测试通过${NC}"
else
    echo -e "${RED}✗ nginx配置测试失败${NC}"
    exit 1
fi

echo -e "${YELLOW}4. 配置SSL证书 (Let's Encrypt)...${NC}"

# 检查certbot是否安装
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}安装certbot...${NC}"
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# 暂时启动nginx以便申请证书
systemctl reload nginx

# 申请SSL证书
echo -e "${YELLOW}正在申请SSL证书...${NC}"
echo -e "${YELLOW}注意: 请确保域名 az.linapp.fun 已正确解析到此服务器IP${NC}"

certbot --nginx -d az.linapp.fun -d www.az.linapp.fun \
    --non-interactive \
    --agree-tos \
    --email admin@linapp.fun \
    --redirect

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSL证书申请成功${NC}"
else
    echo -e "${YELLOW}⚠ SSL证书申请失败，使用HTTP配置${NC}"
    # 使用HTTP版本的nginx配置
    cat > "$NGINX_CONFIG_DEST" << 'EOF'
server {
    listen 80;
    server_name az.linapp.fun www.az.linapp.fun;
    
    root /home/az/cloud-az-visualizer;
    index index.html;
    
    access_log /var/log/nginx/az.linapp.fun.access.log;
    error_log /var/log/nginx/az.linapp.fun.error.log;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/az/cloud-az-visualizer/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
fi

echo -e "${YELLOW}5. 设置项目权限...${NC}"

# 设置项目目录权限
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"

echo -e "${YELLOW}6. 创建systemd服务...${NC}"

# 创建systemd服务文件
cat > /etc/systemd/system/cloud-az-visualizer.service << EOF
[Unit]
Description=Cloud AZ Visualizer Flask App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 重载systemd并启用服务
systemctl daemon-reload
systemctl enable cloud-az-visualizer
systemctl start cloud-az-visualizer

echo -e "${YELLOW}7. 重启服务...${NC}"

# 重启nginx
systemctl restart nginx

# 检查服务状态
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ nginx 服务运行正常${NC}"
else
    echo -e "${RED}✗ nginx 服务启动失败${NC}"
fi

if systemctl is-active --quiet cloud-az-visualizer; then
    echo -e "${GREEN}✓ Flask应用运行正常${NC}"
else
    echo -e "${RED}✗ Flask应用启动失败${NC}"
fi

echo -e "${YELLOW}8. 设置防火墙...${NC}"

# 配置UFW防火墙
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow ssh
    echo -e "${GREEN}✓ 防火墙规则已设置${NC}"
fi

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}网站地址: https://az.linapp.fun${NC}"
echo ""
echo -e "${YELLOW}检查服务状态:${NC}"
echo "  systemctl status nginx"
echo "  systemctl status cloud-az-visualizer"
echo ""
echo -e "${YELLOW}查看日志:${NC}"
echo "  tail -f /var/log/nginx/az.linapp.fun.access.log"
echo "  tail -f /var/log/nginx/az.linapp.fun.error.log"
echo "  journalctl -u cloud-az-visualizer -f"