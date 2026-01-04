# Mac 部署指南

本指南详细介绍如何在 Mac 上部署 PV Pile 检测系统并进行推理。

## 📋 目录

- [前置要求](#前置要求)
- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：直接安装](#方式二直接安装)
- [数据准备](#数据准备)
- [模型文件准备](#模型文件准备)
- [运行推理](#运行推理)
- [常见问题](#常见问题)

## 🔧 前置要求

### 系统要求

- **macOS**: 10.15 (Catalina) 或更高版本
- **内存**: 建议 8GB 或更多
- **存储**: 至少 10GB 可用空间
- **Python**: 3.8+ (如果使用直接安装方式)

### 必需软件

#### Docker 方式（推荐）

1. **Docker Desktop for Mac**
   - 下载: https://www.docker.com/products/docker-desktop
   - 安装后启动 Docker Desktop
   - 验证安装: `docker --version`

#### 直接安装方式

1. **Python 3.8+**
   ```bash
   # 使用 Homebrew 安装
   brew install python@3.11
   
   # 或使用 pyenv
   pyenv install 3.11.0
   pyenv global 3.11.0
   ```

2. **Homebrew** (可选，用于安装依赖)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

---

## 🐳 方式一：Docker 部署（推荐）

### 步骤 1: 获取项目代码

```bash
# 克隆或下载项目到本地
cd ~/Desktop  # 或你喜欢的目录
git clone https://github.com/LeoAKALiu/pv_pile.git
cd pv_pile
```

### 步骤 2: 准备数据目录

```bash
# 创建必要的目录
mkdir -p data/processed/test/images
mkdir -p runs/detect/train4/weights
mkdir -p input output
```

### 步骤 3: 传输模型文件

从服务器传输模型文件到 Mac：

```bash
# 在服务器上（使用 scp）
scp user@server:/root/pv_pile/runs/detect/train4/weights/best.pt \
    ~/Desktop/pv_pile/runs/detect/train4/weights/

# 或使用 rsync（推荐，支持断点续传）
rsync -avz --progress user@server:/root/pv_pile/runs/detect/train4/weights/best.pt \
    ~/Desktop/pv_pile/runs/detect/train4/weights/
```

### 步骤 4: 准备测试图像

```bash
# 将待推理的图像放入 input 目录
cp your_image.jpg input/
# 或
cp -r your_images_folder/* input/
```

### 步骤 5: 构建 Docker 镜像

```bash
# 在项目根目录
docker build -t pv_pile:latest .
```

构建时间约 5-10 分钟，取决于网络速度。

### 步骤 6: 运行推理

#### 方式 A: 单次运行（推荐）

```bash
# 单张图像推理
docker run -it --rm \
  -v "$(pwd)/runs:/app/runs" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
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
    --output-dir /app/output \
    --class-names-yaml /app/data/processed/dataset.yaml
```

#### 方式 B: 批量推理

```bash
docker run -it --rm \
  -v "$(pwd)/runs:/app/runs" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/ \
    --device cpu \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --overlap-width-ratio 0.2 \
    --conf 0.25 \
    --save-img \
    --save-json \
    --output-dir /app/output \
    --class-names-yaml /app/data/processed/dataset.yaml
```

#### 方式 C: 使用 docker-compose（推荐用于多次使用）

```bash
# 启动容器（后台运行）
docker-compose up -d

# 进入容器
docker-compose exec pv_pile bash

# 在容器内运行推理
python src/inference/sahi_inference.py \
  --weights /app/runs/detect/train4/weights/best.pt \
  --source /app/input/ \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir /app/output \
  --class-names-yaml /app/data/processed/dataset.yaml

# 退出容器
exit

# 停止容器
docker-compose down
```

### 步骤 7: 查看结果

```bash
# 查看输出目录
ls -lh output/

# 查看 JSON 结果
cat output/*.json

# 查看可视化图像
open output/*.png  # macOS 自动打开图像
```

---

## 💻 方式二：直接安装

如果你不想使用 Docker，可以直接在 Mac 上安装依赖。

### 步骤 1: 创建虚拟环境

```bash
cd ~/Desktop/pv_pile

# 使用 venv
python3 -m venv venv
source venv/bin/activate

# 或使用 conda
conda create -n pv_pile python=3.11
conda activate pv_pile
```

### 步骤 2: 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 如果遇到问题，可以逐个安装
pip install torch torchvision torchaudio  # CPU 版本
pip install ultralytics
pip install sahi
pip install opencv-python
pip install pillow numpy pyyaml
```

**注意**: Mac 上安装 PyTorch 时，默认会安装 CPU 版本，这是正确的。

### 步骤 3: 验证安装

```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "from ultralytics import YOLO; print('Ultralytics: OK')"
python -c "from sahi import AutoDetectionModel; print('SAHI: OK')"
```

### 步骤 4: 运行推理

```bash
# 激活虚拟环境（如果还没激活）
source venv/bin/activate

# 单张图像推理
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source input/your_image.jpg \
  --device cpu \
  --slice-height 640 \
  --slice-width 640 \
  --overlap-height-ratio 0.2 \
  --overlap-width-ratio 0.2 \
  --conf 0.25 \
  --save-img \
  --save-json \
  --output-dir output \
  --class-names-yaml data/processed/dataset.yaml

# 批量推理
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source input/ \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir output \
  --class-names-yaml data/processed/dataset.yaml
```

---

## 📦 数据准备

### 1. 模型权重文件

确保模型文件在正确位置：

```bash
# 检查模型文件
ls -lh runs/detect/train4/weights/best.pt

# 如果不存在，从服务器传输
scp user@server:/path/to/best.pt runs/detect/train4/weights/
```

### 2. 数据集配置文件

如果需要使用类别名称，准备 `dataset.yaml`:

```yaml
# data/processed/dataset.yaml
path: /app/data/processed
train: train/images
val: val/images
test: test/images

names:
  0: 桩基
```

### 3. 输入图像

将待推理的图像放入 `input/` 目录：

```bash
mkdir -p input
cp your_images/*.jpg input/
```

---

## 🚀 运行推理

### 快速开始脚本

创建一个便捷脚本 `run_inference.sh`:

```bash
#!/bin/bash

# 单张图像推理脚本
IMAGE=$1
OUTPUT_DIR=${2:-output}

docker run -it --rm \
  -v "$(pwd)/runs:/app/runs" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source "/app/input/$IMAGE" \
    --device cpu \
    --save-img \
    --save-json \
    --output-dir "/app/output/$OUTPUT_DIR" \
    --class-names-yaml /app/data/processed/dataset.yaml

echo "结果保存在: output/$OUTPUT_DIR"
```

使用方式：

```bash
chmod +x run_inference.sh
./run_inference.sh your_image.jpg
```

### Python 脚本示例

创建 `inference_mac.py`:

```python
#!/usr/bin/env python3
"""Mac 上的推理脚本示例"""

import subprocess
import sys
from pathlib import Path

def run_inference(image_path: str, output_dir: str = "output"):
    """运行推理"""
    cmd = [
        "python", "src/inference/sahi_inference.py",
        "--weights", "runs/detect/train4/weights/best.pt",
        "--source", image_path,
        "--device", "cpu",
        "--slice-height", "640",
        "--slice-width", "640",
        "--overlap-height-ratio", "0.2",
        "--overlap-width-ratio", "0.2",
        "--conf", "0.25",
        "--save-img",
        "--save-json",
        "--output-dir", output_dir,
        "--class-names-yaml", "data/processed/dataset.yaml"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python inference_mac.py <图像路径> [输出目录]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    run_inference(image_path, output_dir)
    print(f"✅ 推理完成！结果保存在: {output_dir}")
```

使用方式：

```bash
python inference_mac.py input/your_image.jpg
```

---

## ❓ 常见问题

### Q1: Docker 构建失败

**问题**: `ERROR: failed to solve`

**解决**:
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建（不使用缓存）
docker build --no-cache -t pv_pile:latest .
```

### Q2: 找不到模型文件

**问题**: `Model weights not found`

**解决**:
```bash
# 检查文件是否存在
ls -lh runs/detect/train4/weights/best.pt

# 检查挂载是否正确
docker run -it --rm \
  -v "$(pwd)/runs:/app/runs" \
  pv_pile:latest \
  ls -lh /app/runs/detect/train4/weights/best.pt
```

### Q3: 权限问题

**问题**: `Permission denied`

**解决**:
```bash
# 在 Mac 上调整权限
chmod -R 755 runs input output data
```

### Q4: 内存不足

**问题**: `Out of memory`

**解决**:
- 减小切片大小: `--slice-height 512 --slice-width 512`
- 减少重叠: `--overlap-height-ratio 0.1 --overlap-width-ratio 0.1`
- 一次处理少量图像

### Q5: 推理速度慢

**问题**: CPU 推理速度慢

**说明**: 这是正常的。CPU 推理速度约为 GPU 的 1/10-1/20。

**优化建议**:
- 减小切片大小
- 减少重叠比例
- 降低置信度阈值（如果允许）
- 使用更小的模型（yolo11n）

### Q6: 依赖安装失败（直接安装方式）

**问题**: `pip install` 失败

**解决**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或逐个安装
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install ultralytics -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install sahi -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q7: Apple Silicon (M1/M2/M3) 特殊问题

**问题**: 某些包不兼容

**解决**:
```bash
# 使用 conda-forge 安装 PyTorch
conda install pytorch torchvision -c pytorch

# 或使用预编译的 wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

## 📊 性能参考

### CPU 推理性能（Mac）

- **单张图像** (9 个切片): ~30-40 秒
- **批量处理**: 取决于图像数量和大小
- **内存占用**: ~2-4 GB

### 优化建议

1. **减小切片大小**: 从 640×640 降到 512×512
2. **减少重叠**: 从 20% 降到 10%
3. **分批处理**: 一次处理 10-20 张图像

---

## 🔗 相关文档

- [Docker 使用指南](DOCKER_GUIDE.md)
- [SAHI 推理文档](src/inference/README.md)
- [CPU 推理测试报告](CPU_INFERENCE_TEST_REPORT.md)

---

## 📝 快速参考

### Docker 快速命令

```bash
# 构建镜像
docker build -t pv_pile:latest .

# 单张图像推理
docker run -it --rm \
  -v "$(pwd)/runs:/app/runs" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  pv_pile:latest \
  python src/inference/sahi_inference.py \
    --weights /app/runs/detect/train4/weights/best.pt \
    --source /app/input/image.jpg \
    --device cpu \
    --save-img --save-json \
    --output-dir /app/output

# 使用 docker-compose
docker-compose up -d
docker-compose exec pv_pile bash
```

### 直接安装快速命令

```bash
# 激活环境
source venv/bin/activate

# 运行推理
python src/inference/sahi_inference.py \
  --weights runs/detect/train4/weights/best.pt \
  --source input/ \
  --device cpu \
  --save-img --save-json \
  --output-dir output
```

---

*最后更新: 2025-01-04*

