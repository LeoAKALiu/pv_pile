# AGENTS.md

AGENTS.md 是用于指导 AI 编码代理的简单、开放格式文档。

本项目专注于**无人机正摄航拍图像中光伏板桩小目标识别计数**，基于 Ultralytics YOLO 模型，采用切片数据预处理方法进行训练，并使用 SAHI 进行推理。

## 项目概述

- **项目名称**: pv_pile (光伏板桩识别计数)
- **主要功能**: 使用深度学习模型识别和计数无人机航拍图像中的光伏板桩小目标
- **技术栈**: 
  - 基础模型: Ultralytics YOLO (YOLOv8/YOLOv11)
  - 数据预处理: 部分切片方法 (Tiled/Sliced Data Preprocessing)
  - 推理框架: SAHI (Slicing Aided Hyper Inference)
- **应用场景**: 无人机正摄航拍图像中的小目标检测与计数

## 开发环境设置

### 环境要求
- Python >= 3.8
- CUDA 支持的 GPU (推荐) 或 CPU
- Linux 系统 (项目主要针对 Linux 服务器)

### 安装依赖

```bash
# 使用 uv 安装依赖 (推荐)
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt

# 核心依赖包括:
# - ultralytics: YOLO 模型框架
# - sahi: 切片辅助推理
# - torch, torchvision: PyTorch 深度学习框架
# - opencv-python: 图像处理
# - numpy, pillow: 数据处理
```

### 项目结构

```
pv_pile/
├── src/                    # 源代码目录
│   ├── data/              # 数据处理模块
│   │   ├── preprocess.py  # 数据预处理（切片方法）
│   │   └── dataset.py     # 数据集加载
│   ├── models/            # 模型相关
│   │   └── trainer.py     # 训练脚本
│   ├── inference/         # 推理模块
│   │   └── sahi_inference.py  # SAHI 推理脚本
│   └── utils/             # 工具函数
├── tests/                 # 测试目录
├── data/                  # 数据目录
│   ├── raw/              # 原始数据
│   ├── processed/        # 处理后的数据
│   └── annotations/      # 标注文件
├── weights/              # 模型权重目录
├── runs/                 # 训练和推理结果
├── requirements.txt      # Python 依赖
├── pyproject.toml        # 项目配置
└── AGENTS.md            # 本文件
```

## 数据预处理说明

### 切片数据预处理方法

本项目使用**部分切片 (Tiled/Sliced)** 数据预处理方法来处理大尺寸航拍图像：

- **目的**: 将大尺寸航拍图像切分成多个重叠的小切片，提高小目标检测效果
- **实现位置**: `src/data/preprocess.py`
- **关键参数**:
  - `slice_height`: 切片高度 (默认: 640)
  - `slice_width`: 切片宽度 (默认: 640)
  - `overlap_height_ratio`: 高度重叠比例 (默认: 0.2)
  - `overlap_width_ratio`: 宽度重叠比例 (默认: 0.2)

### 数据准备步骤

```bash
# 1. 将原始航拍图像放入 data/raw/images/
# 2. 将标注文件放入 data/raw/annotations/ (YOLO 格式)
# 3. 运行数据预处理脚本
python src/data/preprocess.py --input-dir data/raw --output-dir data/processed --slice-size 640 --overlap 0.2
```

## 训练说明

### 使用 Ultralytics 进行训练

训练使用切片预处理后的数据，基于 Ultralytics YOLO 模型：

```bash
# 基础训练命令
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 100 \
    --imgsz 640 \
    --batch 16 \
    --device 0

# 使用预训练权重
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --weights weights/pretrained/yolo11n.pt \
    --epochs 100 \
    --imgsz 640 \
    --batch 16 \
    --device 0

# 多 GPU 训练
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 100 \
    --imgsz 640 \
    --batch 32 \
    --device 0,1,2,3
```

### 训练配置

- **模型选择**: 根据硬件资源选择 yolo11n/s/m/l/x
- **图像尺寸**: 建议使用 640x640 或 1280x1280 (根据切片大小)
- **批次大小**: 根据 GPU 显存调整 (通常 8-32)
- **数据增强**: 使用 Ultralytics 默认增强策略，针对小目标可适当调整

### 训练输出

训练结果保存在 `runs/detect/train/` 目录下：
- `weights/best.pt`: 最佳模型权重
- `weights/last.pt`: 最后一轮权重
- `results.png`: 训练曲线
- `confusion_matrix.png`: 混淆矩阵

## 推理说明

### 使用 SAHI 进行推理

推理阶段使用 SAHI 框架结合训练好的模型权重：

```bash
# 单张图像推理
python src/inference/sahi_inference.py \
    --weights weights/best.pt \
    --source data/test/image.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --save-img

# 批量图像推理
python src/inference/sahi_inference.py \
    --weights weights/best.pt \
    --source data/test/ \
    --slice-height 640 \
    --slice-width 640 \
    --save-img

# 视频推理
python src/inference/sahi_inference.py \
    --weights weights/best.pt \
    --source data/test/video.mp4 \
    --slice-height 640 \
    --slice-width 640 \
    --save-img

# 调整切片大小以优化小目标检测
python src/inference/sahi_inference.py \
    --weights weights/best.pt \
    --source data/test/image.jpg \
    --slice-height 512 \
    --slice-width 512 \
    --save-img
```

### SAHI 推理参数

- `--weights`: 训练好的模型权重路径
- `--source`: 输入图像/视频/目录路径
- `--slice-height`: SAHI 切片高度 (建议与训练时切片大小一致或更小)
- `--slice-width`: SAHI 切片宽度
- `--conf`: 置信度阈值 (默认: 0.25)
- `--iou`: NMS IoU 阈值 (默认: 0.45)
- `--save-img`: 保存推理结果
- `--view-img`: 实时显示推理结果

### 推理输出

推理结果保存在 `runs/detect/predict/` 目录下，包含：
- 标注了检测框的图像
- 检测结果 JSON 文件 (可选)
- 计数统计信息

## 测试指令

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_data_preprocess.py

# 运行测试并显示覆盖率
pytest tests/ --cov=src --cov-report=html

# 运行测试并显示详细输出
pytest tests/ -v

# 运行特定测试函数
pytest tests/test_inference.py::test_sahi_inference -v
```

### 测试要求

- 所有测试必须通过才能提交代码
- 新增功能必须包含相应的测试用例
- 测试文件应放在 `tests/` 目录下，遵循 `test_*.py` 命名规范
- 使用 pytest fixtures 进行测试数据管理

## 代码质量

### 代码格式化

```bash
# 使用 Ruff 进行代码检查和格式化
ruff check src/
ruff format src/

# 或使用 pre-commit hooks
pre-commit run --all-files
```

### 类型检查

```bash
# 使用 mypy 进行类型检查
mypy src/
```

### 代码规范

- 所有函数和类必须包含类型注解
- 所有函数和类必须包含 docstring (遵循 Google 风格)
- 遵循 PEP 8 代码风格
- 使用 Ruff 进行代码格式化 (line-length=120)

## PR 指令

### Pull Request 规范

- **标题格式**: `[功能模块] 简短描述`
  - 示例: `[数据预处理] 添加切片数据增强功能`
  - 示例: `[推理] 优化 SAHI 推理性能`
  - 示例: `[训练] 修复多 GPU 训练内存泄漏问题`

### PR 检查清单

在提交 PR 前，确保：

1. ✅ 代码已通过所有测试 (`pytest tests/`)
2. ✅ 代码已通过 lint 检查 (`ruff check src/`)
3. ✅ 代码已格式化 (`ruff format src/`)
4. ✅ 类型检查通过 (`mypy src/`)
5. ✅ 添加了必要的文档和注释
6. ✅ 更新了相关文档 (如 README.md)
7. ✅ 提交信息清晰明确

### 提交前命令

```bash
# 运行完整检查流程
pytest tests/                    # 运行测试
ruff check src/                  # 代码检查
ruff format src/                 # 代码格式化
mypy src/                        # 类型检查
```

## 开发工作流

### 1. 数据准备
```bash
# 准备原始数据和标注
# 运行数据预处理
python src/data/preprocess.py --input-dir data/raw --output-dir data/processed
```

### 2. 模型训练
```bash
# 训练模型
python src/models/trainer.py --data data/processed/dataset.yaml --model yolo11n.pt --epochs 100
```

### 3. 模型验证
```bash
# 在验证集上评估模型
python src/models/validator.py --weights weights/best.pt --data data/processed/dataset.yaml
```

### 4. 模型推理
```bash
# 使用 SAHI 进行推理
python src/inference/sahi_inference.py --weights weights/best.pt --source data/test/
```

## 常见问题

### 小目标检测效果不佳

- 减小切片尺寸 (如 512x512 或 640x640)
- 增加数据增强强度
- 使用更大的输入图像尺寸
- 调整 NMS 和置信度阈值

### 训练内存不足

- 减小批次大小 (`--batch`)
- 减小图像尺寸 (`--imgsz`)
- 使用梯度累积
- 使用更小的模型 (yolo11n 而不是 yolo11x)

### SAHI 推理速度慢

- 调整切片大小和重叠比例
- 使用更小的模型
- 使用 GPU 加速 (`--device 0`)
- 考虑使用 TensorRT 或 ONNX 优化

## 参考资料

- [Ultralytics 文档](https://docs.ultralytics.com/)
- [SAHI 文档](https://github.com/obss/sahi)
- [YOLO 模型文档](https://docs.ultralytics.com/models/)
- [AGENTS.md 标准](https://github.com/agentsmd/agents.md)

## 贡献指南

欢迎贡献代码！请确保：
1. 遵循项目的代码规范和测试要求
2. 添加适当的文档和注释
3. 提交前运行所有检查
4. 创建清晰的 PR 描述

---

*最后更新: 2025-01-27*

