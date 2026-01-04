# CPU 推理和 Docker 配置总结

**更新日期**: 2025-01-03  
**状态**: ✅ 完成

## 📋 更改概述

本次更新实现了两个主要功能：
1. ✅ **CPU 推理支持**: 修改 SAHI 推理脚本，默认使用 CPU 模式，并支持自动检测 CUDA 可用性
2. ✅ **Docker 容器化**: 创建完整的 Docker 配置，支持在 Mac 和其他平台上运行

## 🔧 代码更改

### 1. SAHI 推理脚本 (`src/inference/sahi_inference.py`)

#### 更改 1: 默认设备改为 CPU

```python
# 之前
parser.add_argument("--device", type=str, default="0", ...)

# 之后
parser.add_argument("--device", type=str, default="cpu", ...)
```

#### 更改 2: 添加自动 CUDA 检测

```python
# 自动检测 CUDA 是否可用
if device.isdigit():
    try:
        import torch
        if torch.cuda.is_available():
            device_str = f"cuda:{device}"
        else:
            print("⚠️  CUDA not available, falling back to CPU")
            device_str = "cpu"
    except ImportError:
        device_str = "cpu"
```

**效果**:
- 默认使用 CPU 模式（适合无 GPU 环境）
- 如果指定 GPU 设备但 CUDA 不可用，自动回退到 CPU
- 避免在无 GPU 环境下的错误

### 2. Docker 配置文件

#### 创建的文件

1. **Dockerfile**
   - 基于 Python 3.11-slim
   - 安装所有依赖
   - 配置工作目录和环境变量

2. **.dockerignore**
   - 排除不必要的文件（训练输出、日志、缓存等）
   - 减小镜像大小

3. **docker-compose.yml**
   - 配置卷挂载
   - 支持 CPU 和 GPU 模式
   - 便于管理

4. **文档**
   - `DOCKER_GUIDE.md`: 完整使用指南
   - `QUICK_DOCKER_START.md`: 快速开始指南
   - `docker_test.sh`: 测试脚本

## ✅ 测试结果

### CPU 推理测试

```bash
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source data/processed/test/images/0c1058029e97d8be8045a0600bad181a_slice_0013.jpg \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir runs/detect/sahi_test_cpu
```

**结果**:
- ✅ 成功加载模型（CPU 模式）
- ✅ 处理 9 个切片
- ✅ 检测到 23 个目标
- ✅ 正确保存结果

## 🐳 Docker 使用

### 快速开始

```bash
# 1. 构建镜像
docker build -t pv_pile:latest .

# 2. 运行推理
docker run -it --rm \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/your_image.jpg \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/output
```

### 使用 docker-compose

```bash
# 启动
docker-compose up -d

# 进入容器
docker-compose exec pv_pile bash

# 运行推理
python src/inference/sahi_inference.py \
  --weights /app/runs/detect/train4/weights/best.pt \
  --source /app/input/ \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir /app/output
```

## 📂 目录结构

```
pv_pile/
├── Dockerfile                 # Docker 镜像定义
├── .dockerignore             # Docker 忽略文件
├── docker-compose.yml        # Docker Compose 配置
├── docker_test.sh           # 测试脚本
├── DOCKER_GUIDE.md          # 完整 Docker 指南
├── QUICK_DOCKER_START.md    # 快速开始指南
└── CPU_AND_DOCKER_SETUP.md  # 本文档
```

## 🎯 使用场景

### 场景 1: 无 GPU 云服务器

```bash
# 直接使用 CPU 模式（默认）
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source input/ \
  --save-img \
  --save-json \
  --output-dir output
```

### 场景 2: Mac 本地使用

```bash
# 使用 Docker
docker build -t pv_pile:latest .
docker run -it --rm \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/output
```

### 场景 3: 有 GPU 的服务器

```bash
# 使用 GPU（如果可用）
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source input/ \
  --device 0 \
  --save-img \
  --save-json \
  --output-dir output
```

## 📝 注意事项

1. **CPU 模式性能**: CPU 推理比 GPU 慢，但对于小批量处理仍然可用
2. **内存使用**: CPU 模式内存占用较低
3. **模型大小**: 建议使用较小的模型（yolo11n）以获得更好的 CPU 性能
4. **Docker 卷挂载**: 确保所有必要的目录都已挂载
5. **文件权限**: 在 Mac 上可能需要调整文件权限

## 🔗 相关文档

- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - 完整 Docker 使用指南
- [QUICK_DOCKER_START.md](QUICK_DOCKER_START.md) - 快速开始指南
- [src/inference/README.md](src/inference/README.md) - SAHI 推理文档
- [SAHI_TEST_REPORT.md](SAHI_TEST_REPORT.md) - SAHI 测试报告

## ✅ 验证清单

- [x] CPU 推理功能正常
- [x] 自动 CUDA 检测工作正常
- [x] Dockerfile 创建完成
- [x] .dockerignore 配置完成
- [x] docker-compose.yml 创建完成
- [x] 文档完整
- [x] 测试脚本创建完成
- [x] CPU 模式测试通过

---

*最后更新: 2025-01-03*

