# 云服务区域可视化系统 - az.linapp.fun
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name az.linapp.fun www.az.linapp.fun;
    
    # 强制重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name az.linapp.fun www.az.linapp.fun;
    
    # SSL 证书配置 (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/az.linapp.fun/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/az.linapp.fun/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS 安全头
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # 网站根目录
    root /home/az/cloud-az-visualizer;
    index index.html;
    
    # 日志配置
    access_log /var/log/nginx/az.linapp.fun.access.log;
    error_log /var/log/nginx/az.linapp.fun.error.log;
    
    # 主应用代理到Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持 (未来扩展)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件直接服务 (性能优化)
    location /static/ {
        alias /home/az/cloud-az-visualizer/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 压缩静态文件
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/css application/javascript application/json image/svg+xml;
    }
    
    # API路由优化
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API缓存配置
        proxy_cache_bypass $http_upgrade;
        add_header X-Cache-Status $upstream_cache_status;
    }
    
    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # 安全配置 - 隐藏敏感文件
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|py|db)$ {
        deny all;
    }
    
    # 错误页面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}

# upstream 配置 (负载均衡支持 - 未来扩展)
upstream flask_app {
    server 127.0.0.1:5000;
    # server 127.0.0.1:5001;  # 多实例支持
}