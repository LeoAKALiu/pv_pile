# 模型训练模块

## 功能说明

`trainer.py` 脚本用于训练 YOLO 模型进行光伏板桩检测。

### 主要功能

1. **支持多种 YOLO 模型**
   - yolo11n.pt (nano - 最小最快)
   - yolo11s.pt (small)
   - yolo11m.pt (medium)
   - yolo11l.pt (large)
   - yolo11x.pt (xlarge - 最大最准确)

2. **灵活的训练配置**
   - 可配置的训练轮数、批次大小、图像尺寸
   - 支持多 GPU 训练
   - 支持断点续训
   - 自动混合精度训练（AMP）

3. **训练监控**
   - 自动保存最佳模型
   - 生成训练曲线图
   - 验证集评估

## 使用方法

### 基本用法

```bash
# 使用默认参数训练（推荐）
python src/models/trainer.py

# 指定数据集路径
python src/models/trainer.py --data data/processed/dataset.yaml

# 使用不同的模型
python src/models/trainer.py --model yolo11s.pt

# 自定义训练参数
python src/models/trainer.py \
    --epochs 200 \
    --batch 32 \
    --imgsz 1280 \
    --device 0
```

### 高级用法

```bash
# 多 GPU 训练
python src/models/trainer.py \
    --model yolo11m.pt \
    --batch 64 \
    --device 0,1,2,3 \
    --epochs 150

# 断点续训
python src/models/trainer.py \
    --resume \
    --resume-path runs/detect/train/weights/last.pt

# 不使用 Mosaic 增强（针对小目标）
python src/models/trainer.py \
    --close-mosaic 0 \
    --epochs 100

# 使用余弦学习率调度
python src/models/trainer.py \
    --cos-lr \
    --epochs 200
```

### 参数说明

#### 必需参数
- `--data`: 数据集 YAML 配置文件路径（默认: `data/processed/dataset.yaml`）

#### 模型参数
- `--model`: 模型文件或名称（默认: `yolo11n.pt`）
  - 选项: `yolo11n.pt`, `yolo11s.pt`, `yolo11m.pt`, `yolo11l.pt`, `yolo11x.pt`

#### 训练参数
- `--epochs`: 训练轮数（默认: 100）
- `--imgsz`: 输入图像尺寸（默认: 1280，建议与切片大小一致）
- `--batch`: 批次大小（默认: 16，根据 GPU 显存调整）
- `--device`: 设备（默认: 自动选择）
  - `0`: 使用 GPU 0
  - `0,1,2,3`: 使用多个 GPU
  - `cpu`: 使用 CPU
- `--workers`: 数据加载器工作进程数（默认: 8）

#### 项目参数
- `--project`: 项目目录（默认: `runs/detect`）
- `--name`: 运行名称（默认: `train`）

#### 训练选项
- `--resume`: 从上次检查点继续训练
- `--resume-path`: 指定检查点文件路径
- `--no-amp`: 禁用自动混合精度（默认启用）
- `--patience`: 早停耐心值（默认: 50 epochs）
- `--save-period`: 每 N 个 epoch 保存一次检查点（默认: -1，禁用）
- `--no-val`: 训练过程中不进行验证
- `--no-plots`: 不生成训练曲线图
- `--seed`: 随机种子（默认: 0）
- `--no-deterministic`: 禁用确定性算法
- `--single-cls`: 将多类视为单类
- `--rect`: 使用矩形训练
- `--cos-lr`: 使用余弦学习率调度
- `--close-mosaic`: 最后 N 个 epoch 关闭 Mosaic 增强（默认: 10）

## 训练输出

训练结果保存在 `runs/detect/train/` 目录下：

```
runs/detect/train/
├── weights/
│   ├── best.pt          # 最佳模型权重（验证集上表现最好）
│   └── last.pt          # 最后一轮权重
├── args.yaml            # 训练参数配置
├── results.png          # 训练曲线图
├── confusion_matrix.png # 混淆矩阵
├── F1_curve.png         # F1 曲线
├── PR_curve.png         # 精确率-召回率曲线
└── results.csv          # 训练结果 CSV
```

## 训练建议

### 针对小目标检测的配置

```bash
# 使用较大的输入尺寸
python src/models/trainer.py --imgsz 1280

# 关闭 Mosaic 增强（对小目标可能不利）
python src/models/trainer.py --close-mosaic 0

# 使用较小的批次大小以增加图像尺寸
python src/models/trainer.py --batch 8 --imgsz 1280
```

### 显存优化

```bash
# 如果显存不足，减小批次大小
python src/models/trainer.py --batch 8

# 或使用更小的模型
python src/models/trainer.py --model yolo11n.pt --batch 16
```

### 多 GPU 训练

```bash
# 使用 4 个 GPU，批次大小相应增加
python src/models/trainer.py \
    --device 0,1,2,3 \
    --batch 64 \
    --workers 16
```

## 示例

### 快速测试训练（少量 epoch）

```bash
python src/models/trainer.py \
    --epochs 10 \
    --batch 8 \
    --imgsz 1280 \
    --name test_run
```

### 完整训练（推荐配置）

```bash
python src/models/trainer.py \
    --model yolo11s.pt \
    --epochs 200 \
    --batch 16 \
    --imgsz 1280 \
    --device 0 \
    --patience 50 \
    --cos-lr \
    --name pv_pile_detection
```

### 从检查点继续训练

```bash
python src/models/trainer.py \
    --resume \
    --resume-path runs/detect/train/weights/last.pt \
    --epochs 300
```

## 注意事项

1. **图像尺寸**: 建议使用 1280（与数据预处理时的切片大小一致）
2. **批次大小**: 根据 GPU 显存调整，通常 8-32
3. **训练时间**: 根据数据集大小和模型复杂度，可能需要数小时到数天
4. **早停**: 如果验证集指标不再提升，训练会自动停止（patience 参数控制）
5. **Mosaic 增强**: 对于小目标，可以考虑关闭或减少 Mosaic 增强的使用

## 故障排除

### 显存不足 (CUDA out of memory)

- 减小批次大小: `--batch 8`
- 减小图像尺寸: `--imgsz 640`
- 使用更小的模型: `--model yolo11n.pt`

### 训练速度慢

- 增加 `--workers` 参数
- 使用 GPU 训练: `--device 0`
- 使用自动混合精度: 确保 `--no-amp` 未设置

### 模型性能不佳

- 增加训练轮数: `--epochs 200`
- 使用更大的模型: `--model yolo11m.pt` 或 `yolo11l.pt`
- 检查数据质量
- 调整学习率（通过修改代码或使用超参数优化）

