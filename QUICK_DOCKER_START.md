# Docker 快速开始指南

## 🚀 快速启动（Mac）

### 1. 构建镜像

```bash
docker build -t pv_pile:latest .
```

### 2. 准备目录

```bash
mkdir -p input output
```

### 3. 运行推理（单张图像）

```bash
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

### 4. 批量推理

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

## 📝 使用 docker-compose（推荐）

### 1. 启动容器

```bash
docker-compose up -d
```

### 2. 进入容器

```bash
docker-compose exec pv_pile bash
```

### 3. 运行推理

```bash
python src/inference/sahi_inference.py \
  --weights /app/runs/detect/train4/weights/best.pt \
  --source /app/input/ \
  --device cpu \
  --save-img \
  --save-json \
  --output-dir /app/output
```

### 4. 退出并停止

```bash
exit
docker-compose down
```

## ⚙️ 参数说明

- `--device cpu`: 使用 CPU 推理（Mac 默认）
- `--device 0`: 使用 GPU（需要 NVIDIA GPU 和 nvidia-docker）
- `--slice-height 640`: 切片高度
- `--slice-width 640`: 切片宽度
- `--conf 0.25`: 置信度阈值
- `--save-img`: 保存标注图像
- `--save-json`: 保存 JSON 结果

## 📂 目录映射

- `runs/` → `/app/runs` (模型权重)
- `input/` → `/app/input` (输入图像)
- `output/` → `/app/output` (输出结果)

## 🔍 检查结果

```bash
ls -lh output/
```

结果文件：
- `*.png`: 标注图像
- `*.json`: 检测结果（COCO 格式）

---

详细文档请参考 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

