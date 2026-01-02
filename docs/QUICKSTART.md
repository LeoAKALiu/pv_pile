# 快速开始指南

## 环境准备

### 1. 安装依赖

```bash
# 安装基础依赖
pip install ultralytics opencv-python torch torchvision numpy pillow tqdm pyyaml

# 或使用 uv（推荐）
uv pip install ultralytics opencv-python torch torchvision numpy pillow tqdm pyyaml
```

### 2. 验证安装

```bash
python3 -c "from ultralytics import YOLO; print('✅ Ultralytics installed successfully')"
```

## 数据预处理

如果还没有预处理数据，运行：

```bash
python src/data/preprocess.py \
    --input-dir DatasetId_853_1766643148 \
    --output-dir data/processed \
    --slice-size 1280 \
    --overlap 0.2
```

## 开始训练

### 基础训练（推荐）

```bash
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 100 \
    --batch 16 \
    --imgsz 1280 \
    --device 0
```

### 使用更大的模型（更准确但更慢）

```bash
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11s.pt \
    --epochs 150 \
    --batch 16 \
    --imgsz 1280 \
    --device 0
```

### 多 GPU 训练

```bash
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11m.pt \
    --epochs 200 \
    --batch 64 \
    --device 0,1,2,3
```

## 检查训练结果

训练完成后，结果保存在 `runs/detect/train/` 目录：

- `weights/best.pt` - 最佳模型权重
- `weights/last.pt` - 最后一轮权重
- `results.png` - 训练曲线图

## 可视化数据集

在训练前检查数据质量：

```bash
python src/data/visualize_dataset.py \
    --dataset-dir data/processed \
    --split train \
    --num-samples 10
```

## 下一步

训练完成后，可以使用 SAHI 进行推理，参考 `AGENTS.md` 中的推理说明。

