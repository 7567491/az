# 部署文档 - az.linapp.fun

## 🚀 快速部署

### 1. 环境准备

确保服务器已安装：
- Python 3.10+
- nginx
- certbot (用于SSL证书)

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量，填入真实API密钥
vim .env
```

### 3. 运行部署脚本

```bash
# 一键部署（需要root权限）
sudo ./scripts/deploy.sh
```

### 4. 手动步骤（如果自动部署失败）

```bash
# 1. 复制nginx配置
sudo cp nginx/az.linapp.fun.http /etc/nginx/sites-available/az.linapp.fun
sudo ln -s /etc/nginx/sites-available/az.linapp.fun /etc/nginx/sites-enabled/

# 2. 测试nginx配置
sudo nginx -t

# 3. 启动服务
sudo systemctl restart nginx
sudo systemctl enable nginx

# 4. 启动Flask应用
./scripts/start_app.sh

# 5. 设置SSL证书（可选）
sudo certbot --nginx -d az.linapp.fun
```

## 📋 检查清单

- [ ] 项目文件完整
- [ ] 虚拟环境已创建并安装依赖
- [ ] 环境变量已配置
- [ ] nginx配置文件已创建
- [ ] Flask应用可以正常启动
- [ ] 域名DNS已解析到服务器IP

## 🔧 服务管理

```bash
# 检查服务状态
systemctl status nginx
systemctl status cloud-az-visualizer

# 查看日志
tail -f /var/log/nginx/az.linapp.fun.access.log
tail -f /var/log/nginx/az.linapp.fun.error.log
journalctl -u cloud-az-visualizer -f

# 重启服务
sudo systemctl restart nginx
sudo systemctl restart cloud-az-visualizer
```

## 🌐 访问

- HTTP: http://az.linapp.fun
- HTTPS: https://az.linapp.fun (配置SSL后)

## 📁 文件结构

```
cloud-az-visualizer/
├── nginx/                  # nginx配置文件
├── scripts/               # 部署和管理脚本
├── app.py                # Flask主应用
├── .env                  # 环境变量（需要配置）
└── ...
```