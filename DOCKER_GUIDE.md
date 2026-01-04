# Docker 使用指南

本指南介绍如何使用 Docker 运行 PV Pile 检测系统，支持在 Mac 和其他平台上使用。

## 📋 目录

- [快速开始](#快速开始)
- [构建镜像](#构建镜像)
- [运行容器](#运行容器)
- [使用示例](#使用示例)
- [数据挂载](#数据挂载)
- [GPU 支持](#gpu-支持)
- [故障排除](#故障排除)

## 🚀 快速开始

### 1. 构建 Docker 镜像

```bash
docker build -t pv_pile:latest .
```

### 2. 运行容器（CPU 模式）

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/weights:/app/weights \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
  bash
```

### 3. 使用 docker-compose（推荐）

```bash
# 启动容器
docker-compose up -d

# 进入容器
docker-compose exec pv_pile bash

# 停止容器
docker-compose down
```

## 🔨 构建镜像

### 基本构建

```bash
docker build -t pv_pile:latest .
```

### 带标签的构建

```bash
docker build -t pv_pile:1.0.0 -t pv_pile:latest .
```

### 查看镜像

```bash
docker images | grep pv_pile
```

## 🏃 运行容器

### 方式 1: 直接运行命令

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/weights:/app/weights \
  -v $(pwd)/runs:/app/runs \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/data/processed/test/images/ \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir /app/runs/detect/docker_test
```

### 方式 2: 交互式 shell

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/weights:/app/weights \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
  bash
```

在容器内运行：

```bash
# 单张图像推理
python src/inference/sahi_inference.py \
  --weights /app/runs/detect/train4/weights/best.pt \
  --source /app/input/image.jpg \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir /app/output

# 批量推理
python src/inference/sahi_inference.py \
  --weights /app/runs/detect/train4/weights/best.pt \
  --source /app/input/ \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir /app/output
```

### 方式 3: 使用 docker-compose

编辑 `docker-compose.yml`，然后：

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

# 停止
docker-compose down
```

## 📝 使用示例

### 示例 1: 单张图像推理

```bash
# 准备输入图像
mkdir -p input
cp your_image.jpg input/

# 运行推理
docker run -it --rm \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
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

### 示例 2: 批量推理

```bash
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

### 示例 3: 训练模型（CPU 模式）

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/runs:/app/runs \
  pv_pile:latest \
  python src/models/trainer.py \
    --data /app/data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 100 \
    --batch 8 \
    --device cpu \
    --imgsz 640
```

## 📂 数据挂载

### 推荐的目录结构

```
项目根目录/
├── data/              # 数据集（挂载到 /app/data）
│   ├── processed/
│   └── raw/
├── weights/           # 模型权重（挂载到 /app/weights）
├── runs/              # 训练和推理结果（挂载到 /app/runs）
├── input/             # 输入图像（挂载到 /app/input）
└── output/            # 输出结果（挂载到 /app/output）
```

### 挂载说明

- `data/`: 包含数据集和配置文件
- `weights/`: 预训练模型权重（可选）
- `runs/`: 训练结果和模型权重
- `input/`: 待推理的图像
- `output/`: 推理结果输出

## 🎮 GPU 支持

### 使用 NVIDIA GPU（Linux）

1. 安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. 运行容器时添加 `--gpus all`:

```bash
docker run -it --rm \
  --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/runs:/app/runs \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device 0 \
    --save-img \
    --save-json \
    --output-dir /app/output
```

3. 使用 docker-compose（取消注释 GPU 配置）:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Mac GPU 支持

Mac 上的 GPU 支持有限：
- **Apple Silicon (M1/M2/M3)**: 可以使用 Metal Performance Shaders (MPS)，但需要特殊配置
- **Intel Mac**: 仅支持 CPU

对于 Mac 用户，建议使用 CPU 模式。

## 🔧 故障排除

### 问题 1: 找不到模型文件

**错误**: `Model weights not found`

**解决**: 确保模型权重文件已挂载到容器中：

```bash
# 检查文件是否存在
docker run -it --rm \
  -v $(pwd)/runs:/app/runs \
  pv_pile:latest \
  ls -lh /app/runs/detect/train4/weights/best.pt
```

### 问题 2: 权限问题

**错误**: `Permission denied`

**解决**: 在 Mac 上，可能需要调整文件权限：

```bash
chmod -R 755 data runs input output
```

### 问题 3: 内存不足

**错误**: `Out of memory`

**解决**: 
- 减小批次大小
- 减小切片大小
- 使用更小的模型（yolo11n 而不是 yolo11m）

### 问题 4: 依赖缺失

**错误**: `ModuleNotFoundError`

**解决**: 重新构建镜像：

```bash
docker build --no-cache -t pv_pile:latest .
```

### 问题 5: CUDA 相关错误（CPU 模式）

**错误**: CUDA 相关错误但使用 CPU 模式

**解决**: 确保使用 `--device cpu` 参数：

```bash
python src/inference/sahi_inference.py \
  --device cpu \
  ...
```

## 📊 性能优化

### CPU 模式优化

1. **减小批次大小**: 对于 CPU，建议使用较小的切片
2. **减少重叠**: 降低重叠比例可以减少计算量
3. **使用更小的模型**: yolo11n 比 yolo11m 快得多

### 内存优化

1. **限制并发**: 一次处理少量图像
2. **清理缓存**: 定期清理不需要的输出文件

## 🔗 相关文档

- [SAHI 推理文档](src/inference/README.md)
- [训练文档](src/models/README.md)
- [项目结构](PROJECT_STRUCTURE.md)

## 📝 注意事项

1. **数据持久化**: 所有重要数据都应通过卷挂载，避免容器删除后数据丢失
2. **模型权重**: 确保模型权重文件已正确挂载
3. **输出目录**: 确保输出目录有写权限
4. **资源限制**: 根据系统资源调整批次大小和切片大小

---

*最后更新: 2025-01-03*

