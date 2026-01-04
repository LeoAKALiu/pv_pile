# PV Pile Detection - 光伏板桩基检测

基于 YOLOv11 和 SAHI 的无人机航拍图像中小目标检测项目。

## 📋 项目简介

本项目专注于**无人机正摄航拍图像中光伏板桩基小目标识别计数**，采用以下技术栈：

- **检测框架**: Ultralytics YOLOv11
- **推理框架**: SAHI (Slicing Aided Hyper Inference)
- **数据预处理**: 切片数据预处理方法
- **应用场景**: 大尺寸航拍图像中的小目标检测

## 🎯 项目特点

- ✅ **小目标检测优化**: 针对 20-30 像素的小目标进行优化
- ✅ **大图像处理**: 支持处理任意尺寸的航拍图像（无分辨率上限）
- ✅ **切片推理**: 使用 SAHI 进行切片推理，提高检测精度
- ✅ **完整工作流**: 从数据预处理到模型训练再到推理的完整流程

## 📊 最佳模型性能

- **模型**: YOLOv11n (train4)
- **mAP50**: 60.22%
- **mAP50-95**: 18.71%
- **模型路径**: `runs/detect/train4/weights/best.pt`

## 🚀 快速开始

### 🍎 Mac 用户快速开始

**推荐使用 Docker 方式**（最简单）：

```bash
# 1. 克隆项目
git clone https://github.com/LeoAKALiu/pv_pile.git
cd pv_pile

# 2. 运行设置脚本
./setup_mac.sh

# 3. 传输模型文件（从服务器）
scp user@server:/root/pv_pile/runs/detect/train4/weights/best.pt \
    runs/detect/train4/weights/

# 4. 运行推理
./run_inference_mac.sh input/your_image.jpg
```

详细说明请参考 [MAC_DEPLOYMENT_GUIDE.md](MAC_DEPLOYMENT_GUIDE.md)

---

### Linux 服务器环境

### 1. 环境准备

```bash
# 创建 conda 环境
conda create -n yolov11 python=3.10
conda activate yolov11

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据预处理

```bash
# 将 COCO 格式转换为 YOLO 格式，并进行切片处理
python src/data/preprocess.py \
    --coco-annotations DatasetId_853_1766643148/Annotations/coco_info.json \
    --images-dir DatasetId_853_1766643148/Images \
    --output-dir data/processed \
    --slice-size 640 \
    --overlap 0.2
```

### 3. 模型训练

```bash
# 基础训练
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 200 \
    --batch 16 \
    --imgsz 640 \
    --device 0

# 使用 screen 后台训练
bash start_training_screen.sh
```

### 4. 推理

```bash
# SAHI 切片推理
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source path/to/image.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --save-img \
    --save-json
```

## 📁 项目结构

```
pv_pile/
├── src/                    # 源代码
│   ├── data/               # 数据预处理
│   │   ├── preprocess.py   # COCO 转 YOLO + 切片
│   │   └── visualize_dataset.py
│   ├── models/             # 模型训练
│   │   └── trainer.py      # 训练脚本
│   └── inference/          # 推理模块
│       └── sahi_inference.py  # SAHI 推理
├── data/                   # 数据目录（不包含在 git 中）
├── runs/                   # 训练结果（不包含在 git 中）
├── scripts/                # 训练脚本
│   ├── start_training_screen.sh
│   └── ...
├── docs/                   # 文档
│   ├── AGENTS.md           # 项目开发指南
│   ├── QUICKSTART.md       # 快速开始
│   ├── EXPERIMENTS_SUMMARY.md  # 实验总结
│   └── ...
└── README.md              # 本文件
```

## 📚 文档

- **[AGENTS.md](AGENTS.md)**: 项目开发指南和规范
- **[QUICKSTART.md](QUICKSTART.md)**: 快速开始指南
- **[MAC_DEPLOYMENT_GUIDE.md](MAC_DEPLOYMENT_GUIDE.md)**: 🍎 Mac 部署指南（Docker 和直接安装）
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)**: Docker 使用指南
- **[CPU_INFERENCE_TEST_REPORT.md](CPU_INFERENCE_TEST_REPORT.md)**: CPU 推理测试报告
- **[EXPERIMENTS_SUMMARY.md](EXPERIMENTS_SUMMARY.md)**: 所有训练实验总结

## 🔧 主要功能

### 数据预处理

- COCO 格式转 YOLO 格式
- 大图像切片处理（支持重叠）
- 数据集划分（train/val/test）

### 模型训练

- 支持 YOLOv11 系列模型（n/s/m/l/x）
- 丰富的超参数配置
- 数据增强选项
- 后台训练支持（screen）

### 推理

- SAHI 切片推理
- 支持单张图像和批量处理
- 无分辨率上限
- 完整的可视化输出

## 📊 实验结果

详细实验结果请参考 [EXPERIMENTS_SUMMARY.md](EXPERIMENTS_SUMMARY.md)。

| 实验 | 模型 | mAP50 | mAP50-95 | 状态 |
|------|------|-------|----------|------|
| train4 | yolo11n | **60.22%** | **18.71%** | ✅ 最佳 |
| pv_pile_yolo11s8 | yolo11s | 54.20% | 16.59% | ✅ 完成 |
| train_final_v1 | yolo11n | 55.53% | 16.59% | ✅ 完成 |

## 🛠️ 技术栈

- **Python**: 3.10+
- **PyTorch**: 2.4.1+
- **Ultralytics YOLO**: YOLOv11
- **SAHI**: Slicing Aided Hyper Inference
- **CUDA**: 支持 GPU 加速

## 📝 使用示例

### 单张图像推理

```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source DatasetId_853_1766643148/Images/桩基照片.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --save-img \
    --save-json
```

### 批量处理

```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/processed/test/images \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.3 \
    --save-img \
    --save-json
```

## ⚠️ 注意事项

1. **数据文件**: `data/` 和 `runs/` 目录不包含在 git 中（太大），需要单独下载
2. **模型权重**: 训练好的模型权重需要单独下载
3. **环境配置**: 确保安装所有依赖，特别是 SAHI 和 Ultralytics

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 Ultralytics YOLO，遵循相应的开源许可证。

## 🙏 致谢

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [SAHI](https://github.com/obss/sahi)

---

*最后更新: 2025-01-27*


