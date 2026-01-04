# Docker 网络问题解决方案

## 🔧 问题：Docker 构建时网络超时

### 错误信息

```
ERROR: failed to build: failed to solve: DeadlineExceeded: failed to fetch oauth token: 
Post "https://auth.docker.io/token": dial tcp 69.171.247.32:443: i/o timeout
```

### 原因

无法连接到 Docker Hub 拉取基础镜像，常见原因：
1. 网络连接不稳定
2. 防火墙或代理设置
3. 在中国大陆访问 Docker Hub 较慢（需要镜像加速器）

## ✅ 解决方案

### 方案 1: 配置 Docker 镜像加速器（推荐，适用于中国大陆用户）

#### Mac (Docker Desktop)

1. **打开 Docker Desktop**
   - 点击菜单栏的 Docker 图标
   - 选择 "Settings"（设置）

2. **配置镜像加速器**
   - 在左侧菜单选择 "Docker Engine"
   - 在 JSON 配置编辑器中，添加 `registry-mirrors` 配置：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

3. **应用设置**
   - 点击 "Apply & Restart"
   - 等待 Docker 重启完成（约 10-30 秒）

4. **验证配置**
```bash
docker info | grep -A 10 "Registry Mirrors"
```

#### Linux

1. **编辑 Docker 配置文件**
```bash
sudo nano /etc/docker/daemon.json
```

2. **添加镜像加速器配置**
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

3. **重启 Docker 服务**
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

4. **验证配置**
```bash
docker info | grep -A 10 "Registry Mirrors"
```

### 方案 2: 重试构建

网络问题可能是暂时的，可以简单重试：

```bash
# 重试构建
./docker_start.sh build

# 或直接使用 docker build
docker build -t pv_pile:latest .
```

### 方案 3: 检查网络连接

```bash
# 测试 Docker Hub 连接
ping registry-1.docker.io

# 测试 DNS 解析
nslookup registry-1.docker.io

# 测试 HTTPS 连接
curl -I https://auth.docker.io
```

如果这些命令失败，说明网络连接有问题。

### 方案 4: 使用代理（如果已配置代理）

#### Mac (Docker Desktop)

1. 打开 Docker Desktop → Settings → Resources → Proxies
2. 配置代理设置：
   - Manual proxy configuration
   - 输入代理地址和端口
   - 如果需要，配置认证信息
3. 点击 "Apply & Restart"

#### Linux

创建或编辑 `/etc/systemd/system/docker.service.d/http-proxy.conf`:

```ini
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1"
```

然后重启：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 方案 5: 使用离线方式（最后手段）

如果网络问题持续存在，可以考虑：

1. **在其他网络环境下预先拉取镜像**
```bash
# 在其他地方先拉取基础镜像
docker pull python:3.11-slim

# 保存镜像
docker save python:3.11-slim -o python-3.11-slim.tar

# 在目标机器上加载镜像
docker load -i python-3.11-slim.tar
```

2. **然后在本机构建**
```bash
docker build -t pv_pile:latest .
```

## 🔍 验证修复

配置完成后，验证是否可以正常拉取镜像：

```bash
# 测试拉取一个小镜像
docker pull hello-world

# 如果成功，说明配置生效
```

然后重新运行构建：

```bash
./docker_start.sh build
```

## 📝 常用镜像加速器地址

### 国内镜像源

- **中科大镜像**: `https://docker.mirrors.ustc.edu.cn`
- **网易镜像**: `https://hub-mirror.c.163.com`
- **百度云镜像**: `https://mirror.baidubce.com`
- **阿里云镜像**（需要注册）: `https://your-id.mirror.aliyuncs.com`
- **腾讯云镜像**（需要注册）: `https://mirror.ccs.tencentyun.com`

### 配置多个镜像源

可以配置多个镜像源，Docker 会按顺序尝试：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

## ⚠️ 注意事项

1. **镜像源可靠性**: 不同的镜像源可能有不同的更新频率和稳定性
2. **安全性**: 使用官方或可信的镜像源
3. **性能**: 选择离你地理位置最近的镜像源通常会有更好的性能

## 🔗 相关文档

- [Docker 官方文档 - 配置镜像加速器](https://docs.docker.com/registry/recipes/mirror/)
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 完整部署指南

---

*最后更新: 2025-01-27*

