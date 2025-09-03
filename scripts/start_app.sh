#!/bin/bash

# Flask应用启动脚本
# 用于生产环境启动

set -e

# 项目路径
PROJECT_DIR="/home/az/cloud-az-visualizer"
cd "$PROJECT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=production

# 检查依赖
if [ ! -f "venv/bin/gunicorn" ]; then
    echo "安装gunicorn..."
    pip install gunicorn
fi

echo "🚀 启动Flask应用..."

# 使用gunicorn启动 (生产环境推荐)
exec gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --worker-class sync \
    --timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --preload \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --log-level info \
    app:app