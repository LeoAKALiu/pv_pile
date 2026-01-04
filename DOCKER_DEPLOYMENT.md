# Docker 部署指南

本指南介绍如何在本机使用 Docker 部署 PV Pile 检测系统。

## 📋 目录

- [快速开始](#快速开始)
- [前置要求](#前置要求)
- [部署步骤](#部署步骤)
- [使用方法](#使用方法)
- [常见问题](#常见问题)

## 🚀 快速开始

### 一键部署

```bash
# 克隆项目（如果还没有）
git clone <repository-url>
cd pv_pile

# 一键设置（构建镜像 + 启动容器）
./docker_start.sh setup
```

### 手动部署

```bash
# 1. 构建镜像
docker build -t pv_pile:latest .

# 2. 创建必要目录
mkdir -p data/processed runs/detect weights input output

# 3. 启动容器
docker-compose up -d

# 4. 进入容器
docker-compose exec pv_pile bash
```

## 📦 前置要求

### 必需软件

1. **Docker Desktop** (Mac/Windows) 或 **Docker Engine** (Linux)
   - Mac: [下载 Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [安装 Docker Engine](https://docs.docker.com/engine/install/)
   - Windows: [下载 Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

2. **Docker Compose**
   - Docker Desktop 已包含 Docker Compose
   - Linux 需要单独安装: `sudo apt-get install docker-compose-plugin`

### 系统要求

- **内存**: 至少 4GB RAM（推荐 8GB+）
- **磁盘空间**: 至少 5GB 可用空间
- **操作系统**: macOS, Linux, Windows (WSL2)

## 🔧 部署步骤

### 步骤 1: 准备项目

```bash
# 进入项目目录
cd pv_pile

# 确保有执行权限
chmod +x docker_start.sh
```

### 步骤 2: 准备模型文件

将训练好的模型权重文件放到正确位置：

```bash
# 创建目录（如果不存在）
mkdir -p runs/detect/train4/weights

# 将模型文件复制到该目录
# 例如: cp /path/to/best.pt runs/detect/train4/weights/best.pt
```

### 步骤 3: 准备输入数据

```bash
# 创建输入目录
mkdir -p input

# 将待检测的图像复制到 input/ 目录
# 例如: cp /path/to/images/*.jpg input/
```

### 步骤 4: 构建和启动

使用便捷脚本：

```bash
./docker_start.sh setup
```

或手动执行：

```bash
# 构建镜像
docker build -t pv_pile:latest .

# 启动容器
docker-compose up -d
```

## 📖 使用方法

### 使用便捷脚本

```bash
# 查看所有命令
./docker_start.sh help

# 启动容器
./docker_start.sh start

# 进入容器
./docker_start.sh shell

# 运行推理
./docker_start.sh inference

# 查看日志
./docker_start.sh logs

# 查看状态
./docker_start.sh status

# 停止容器
./docker_start.sh stop
```

### 使用 Docker Compose

```bash
# 启动容器
docker-compose up -d

# 进入容器
docker-compose exec pv_pile bash

# 查看日志
docker-compose logs -f pv_pile

# 停止容器
docker-compose down
```

### 在容器内运行推理

#### 单张图像推理

```bash
# 进入容器
docker-compose exec pv_pile bash

# 运行推理
python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/your_image.jpg \
    --device cpu \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --overlap-width-ratio 0.2 \
    --conf 0.25 \
    --save-img \
    --save-json \
    --output-dir /app/output
```

#### 批量推理

```bash
python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/output
```

#### 直接运行（不进入容器）

```bash
docker-compose exec pv_pile python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/output
```

## 📂 目录结构

项目目录结构：

```
pv_pile/
├── docker_start.sh          # Docker 管理脚本
├── Dockerfile               # Docker 镜像定义
├── docker-compose.yml       # Docker Compose 配置
├── requirements.txt         # Python 依赖
├── input/                   # 输入图像目录（挂载到容器）
├── output/                  # 输出结果目录（挂载到容器）
├── runs/                    # 模型权重和训练结果（挂载到容器）
│   └── detect/
│       └── train4/
│           └── weights/
│               └── best.pt  # 模型权重文件
├── data/                    # 数据集目录（挂载到容器）
└── src/                     # 源代码
```

## 🔍 验证部署

### 检查容器状态

```bash
# 使用脚本
./docker_start.sh status

# 或使用 docker-compose
docker-compose ps
```

### 测试推理

```bash
# 使用脚本运行推理
./docker_start.sh inference

# 或手动运行
docker-compose exec pv_pile python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/output
```

### 查看结果

```bash
# 查看输出目录
ls -lh output/

# 结果文件包括:
# - *.png: 标注后的图像
# - *.json: 检测结果（COCO 格式）
```

## ⚙️ 配置说明

### Docker Compose 配置

`docker-compose.yml` 中的主要配置：

- **volumes**: 目录挂载，确保数据持久化
- **environment**: 环境变量设置
- **restart**: 容器重启策略

### 修改配置

如需修改配置，编辑 `docker-compose.yml`：

```yaml
services:
  pv_pile:
    # 添加 GPU 支持（仅 Linux + NVIDIA GPU）
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

## 🐛 常见问题

### 问题 1: Docker 未安装

**错误**: `docker: command not found`

**解决**: 
- Mac: 下载并安装 [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- Linux: 按照 [官方文档](https://docs.docker.com/engine/install/) 安装 Docker Engine

### 问题 2: 权限错误

**错误**: `Permission denied`

**解决**:
```bash
# Mac/Linux: 确保脚本有执行权限
chmod +x docker_start.sh

# 确保目录有正确权限
chmod -R 755 input output runs data
```

### 问题 3: 模型文件未找到

**错误**: `Model weights not found`

**解决**:
```bash
# 检查模型文件是否存在
ls -lh runs/detect/train4/weights/best.pt

# 如果不存在，需要先准备模型文件
mkdir -p runs/detect/train4/weights
# 然后复制模型文件到该目录
```

### 问题 4: Docker 构建时网络超时

**错误**: `DeadlineExceeded: failed to fetch oauth token` 或 `dial tcp: i/o timeout`

**原因**: 无法连接到 Docker Hub 或网络连接不稳定（在中国大陆很常见）

**解决方案**:

#### 方案 1: 配置 Docker 镜像加速器（推荐，适用于中国大陆用户）

**Mac (Docker Desktop)**:
1. 打开 Docker Desktop
2. 点击设置图标（⚙️）→ Settings
3. 选择 Docker Engine
4. 在 JSON 配置中添加镜像加速器：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

5. 点击 "Apply & Restart"
6. 等待 Docker 重启完成

**Linux**:
编辑 `/etc/docker/daemon.json`（如果不存在则创建）：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

然后重启 Docker：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 方案 2: 重试构建

网络问题可能是暂时的，可以重试：
```bash
# 重试构建
docker build -t pv_pile:latest .

# 或使用更长的超时时间
docker build --network=host -t pv_pile:latest .
```

#### 方案 3: 检查网络连接

```bash
# 测试 Docker Hub 连接
ping registry-1.docker.io

# 检查 DNS
nslookup registry-1.docker.io
```

#### 方案 4: 使用代理（如果有）

如果使用代理，需要在 Docker Desktop 中配置代理：
1. Docker Desktop → Settings → Resources → Proxies
2. 配置代理设置

### 问题 5: 容器启动失败

**错误**: 容器无法启动

**解决**:
```bash
# 查看详细日志
docker-compose logs pv_pile

# 检查镜像是否构建成功
docker images | grep pv_pile

# 重新构建镜像
docker build --no-cache -t pv_pile:latest .
```

### 问题 6: 内存不足

**错误**: `Out of memory`

**解决**:
- 减小批次大小
- 减小切片大小（`--slice-height` 和 `--slice-width`）
- 减少同时处理的图像数量
- 增加 Docker 的内存限制（Docker Desktop → Settings → Resources）

### 问题 7: 端口冲突

**错误**: `port is already allocated`

**解决**: 
- 当前配置未使用端口映射，如果添加了端口映射，可以修改 `docker-compose.yml` 中的端口号

## 📊 性能优化

### CPU 模式优化

1. **减小切片大小**: 使用 512×512 而不是 640×640
2. **减少重叠**: 降低 `--overlap-height-ratio` 和 `--overlap-width-ratio`
3. **批量处理**: 一次处理少量图像

### 内存优化

1. **限制并发**: 避免同时处理太多图像
2. **清理缓存**: 定期清理 `output/` 目录
3. **使用更小的模型**: yolo11n 比 yolo11m 占用更少内存

## 🔗 相关文档

- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - 详细的 Docker 使用指南
- [QUICK_DOCKER_START.md](QUICK_DOCKER_START.md) - 快速开始指南
- [README.md](README.md) - 项目主文档

## 📝 注意事项

1. **数据持久化**: 所有重要数据都通过卷挂载，容器删除后数据不会丢失
2. **模型权重**: 确保模型权重文件已正确放置
3. **输入输出**: 输入图像放在 `input/` 目录，结果保存在 `output/` 目录
4. **资源限制**: 根据系统资源调整推理参数

## 🎯 下一步

部署完成后，你可以：

1. 将待检测图像放入 `input/` 目录
2. 运行推理: `./docker_start.sh inference`
3. 查看结果: `ls -lh output/`
4. 根据需要调整推理参数

---

*最后更新: 2025-01-27*

