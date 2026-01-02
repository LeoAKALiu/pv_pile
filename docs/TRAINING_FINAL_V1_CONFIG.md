# train_final_v1 实验配置说明

## 🎯 实验目标

基于之前的实验结果，设计一个优化的训练配置，在保持 Mosaic 增强优势的同时，通过后期关闭 Mosaic 和轻微增强来提高定位精度。

## 📋 实验配置

### 模型
- **模型**: yolo11n.pt
- **可选**: 如果使用修改过 P2 头的 yaml，修改脚本中的 `MODEL` 变量

### 数据
- **数据集**: 现有数据 (`data/processed/dataset.yaml`)
- **增强**: 启用 Copy-Paste 增强 (copy-paste=0.1)

### 训练参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **imgsz** | 1280 | 保持与之前实验一致 |
| **epochs** | 200 | 标准训练轮数 |
| **batch** | 16 | 稳定的批次大小 |
| **mosaic** | 1.0 | 启用 Mosaic 增强 |
| **close_mosaic** | **20** | **关键！后20轮关闭 Mosaic** |
| **mixup** | 0.1 | 轻微 Mixup 增强，提高抗干扰能力 |
| **copy-paste** | 0.1 | 启用 Copy-Paste 增强 |

## 🔑 关键优化点

### 1. close_mosaic=20 (最重要)

**原理**:
- 训练前期使用 Mosaic 增强，提供更多上下文信息和数据多样性
- 训练后期（最后20轮）关闭 Mosaic，让模型专注于精确的定位
- 这可以结合 Mosaic 的优势和关闭 Mosaic 的定位精度

**预期效果**:
- 保持 Mosaic 带来的性能提升（mAP50）
- 提高定位精度（mAP50-95）
- 可能达到比 train4 更好的 mAP50-95

### 2. mixup=0.1

**原理**:
- 轻微的 Mixup 增强（0.1）可以提供额外的数据多样性
- 不会像完全关闭那样损失性能
- 有助于提高模型的抗干扰能力

### 3. copy-paste=0.1

**原理**:
- Copy-Paste 增强对小目标检测有帮助
- 可以增加小目标的出现频率
- 0.1 的强度不会过度干扰训练

## 🚀 使用方法

### 启动训练

```bash
./start_training_final_v1.sh
```

### 管理训练会话

```bash
# 查看所有 screen 会话
screen -ls

# 连接到训练会话
screen -r yolo_final_v1

# 从会话中分离（训练继续运行）
# 在 screen 内按：Ctrl+A，然后按 D

# 终止训练会话
screen -S yolo_final_v1 -X quit
```

### 查看训练日志

```bash
# 实时查看日志
tail -f training_final_v1.log

# 查看最后 100 行
tail -100 training_final_v1.log
```

## 📊 预期结果

### 与 train4 对比

| 指标 | train4 | final_v1 (预期) | 说明 |
|------|--------|----------------|------|
| mAP50 | 60.22% | **60-62%** | 保持或略提升 |
| mAP50-95 | 18.71% | **20-22%** | 显著提升（定位精度） |
| Precision | 63.31% | 63-65% | 略提升 |
| Recall | 63.66% | 63-65% | 略提升 |

### 优化原理

1. **close_mosaic=20**: 
   - 前 180 轮使用 Mosaic，获得数据多样性
   - 后 20 轮关闭 Mosaic，提高定位精度
   - 预期 mAP50-95 提升 1-3%

2. **mixup=0.1**:
   - 轻微增强，不会过度干扰
   - 提高模型鲁棒性

3. **copy-paste=0.1**:
   - 增加小目标出现频率
   - 有助于小目标检测

## 🔧 如果使用修改过的 P2 头 YAML

如果需要使用修改过 P2 头的模型配置：

1. 准备 YAML 文件（例如 `yolo11n_p2.yaml`）
2. 修改脚本中的 `MODEL` 变量：
   ```bash
   MODEL="yolo11n_p2.yaml"  # 改为你的 yaml 文件路径
   ```
3. 确保 YAML 文件在项目目录中或使用绝对路径

## 📝 训练命令（手动运行）

如果需要手动运行（不使用 screen）：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/miniconda3/envs/yolov11
cd /root/pv_pile

python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11n.pt \
    --epochs 200 \
    --batch 16 \
    --imgsz 1280 \
    --device 0 \
    --workers 8 \
    --patience 50 \
    --mosaic 1.0 \
    --mixup 0.1 \
    --copy-paste 0.1 \
    --close-mosaic 20 \
    --name train_final_v1 \
    --project runs/detect
```

## 🎯 实验假设

1. **close_mosaic=20 策略有效**:
   - 前期 Mosaic 提供多样性
   - 后期关闭提高定位精度
   - 预期 mAP50-95 提升

2. **轻微增强不会干扰**:
   - mixup=0.1 和 copy-paste=0.1 强度较低
   - 不会像完全关闭那样损失性能

3. **综合效果优于单一策略**:
   - 结合多种优化策略
   - 预期达到更好的平衡

## 📈 监控指标

训练过程中重点关注：

1. **mAP50**: 目标 > 60%
2. **mAP50-95**: 目标 > 20% (关键指标)
3. **Precision/Recall 平衡**: 保持在 60-65%
4. **训练损失**: 观察是否持续下降
5. **验证损失**: 观察是否过拟合

## ⚠️ 注意事项

1. **训练时间**: 200 epochs 预计需要 4-6 小时
2. **显存使用**: Batch=16 在 32GB 显存下应该足够
3. **早停**: patience=50，如果验证集指标不再提升会自动停止
4. **日志保存**: 所有输出保存在 `training_final_v1.log`

## 🔄 后续实验建议

如果 final_v1 效果好，可以尝试：

1. **调整 close_mosaic 值**: 测试 15, 25, 30
2. **调整 mixup 值**: 测试 0.05, 0.15, 0.2
3. **调整 copy-paste 值**: 测试 0.05, 0.15, 0.2
4. **使用 yolo11m**: 如果显存允许，尝试更大模型

---

*配置创建时间: 2025-01-27*
*实验名称: train_final_v1*


