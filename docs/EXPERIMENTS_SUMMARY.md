# 训练实验总结报告

## 📊 实验概览

本报告总结了所有已完成的训练实验及其结果。

| 实验名称 | 模型 | Epochs | Batch | Mosaic | Cos LR | 最佳 mAP50 | 最佳 mAP50-95 | 最佳 Epoch | 状态 |
|---------|------|--------|-------|--------|--------|------------|---------------|------------|------|
| **train4** | yolo11n | 200 | 16 | 1.0 | ❌ | **60.22%** | **18.71%** | 185 | ✅ 最佳 |
| pv_pile_yolo11s8 | yolo11s | 200 | 16 | 1.0 | ✅ | 54.20% | 16.59% | 160 | ✅ 完成 |
| pv_pile_yolo11n_no_mosaic_opt1 | yolo11n | 300 | 16 | 0.0 | ✅ | 52.53% | 15.34% | 291 | ✅ 完成 |
| pv_pile_yolo11s7 | yolo11s | 200 | 32 | 1.0 | ✅ | 6.87% | 1.68% | 1 | ⚠️ 异常 |
| pv_pile_yolo11s5 | yolo11s | 200 | 32 | 1.0 | ✅ | 0.00% | 0.00% | 1 | ❌ 失败 |
| pv_pile_yolo11s6 | yolo11s | 200 | 32 | 1.0 | ✅ | 0.00% | 0.00% | 1 | ❌ 失败 |
| train3 | yolo11n | 200 | 16 | 1.0 | ❌ | 0.00% | 0.00% | 0 | ❌ 失败 |

## 🏆 最佳实验结果

### train4 (yolo11n, mosaic=1.0)

**配置**:
- 模型: yolo11n.pt
- 训练轮数: 200 epochs
- 批次大小: 16
- 图像尺寸: 1280×1280
- Mosaic: 1.0 (启用)
- Mixup: 0.0
- Copy-Paste: 0.0
- 余弦学习率: ❌ (未启用)
- 学习率: lr0=0.01, lrf=0.01

**最佳结果 (Epoch 185)**:
- **mAP50**: 60.22% 🏆
- **mAP50-95**: 18.71% 🏆
- **Precision**: 63.31%
- **Recall**: 63.66%

**最终结果 (Epoch 200)**:
- mAP50: 58.33%
- mAP50-95: 17.93%

**模型路径**: `runs/detect/train4/weights/best.pt`

---

## 📋 详细实验结果

### 1. train4 (基准实验 - 最佳性能)

**实验目的**: 使用 yolo11n 模型，启用 Mosaic 增强，作为性能基准。

**关键配置**:
- 模型: yolo11n.pt
- Epochs: 200
- Batch: 16
- Imgsz: 1280
- Mosaic: 1.0
- Cos LR: False
- 学习率: 默认 (lr0=0.01, lrf=0.01)

**结果**:
- ✅ **最佳 mAP50: 60.22%** (Epoch 185)
- ✅ **最佳 mAP50-95: 18.71%**
- Precision: 63.31%
- Recall: 63.66%

**结论**: 这是目前最佳的训练配置，Mosaic=1.0 对当前数据集有效。

---

### 2. pv_pile_yolo11s8 (yolo11s 实验)

**实验目的**: 使用更大的 yolo11s 模型，启用 Mosaic 和余弦学习率。

**关键配置**:
- 模型: yolo11s.pt
- Epochs: 200
- Batch: 16
- Imgsz: 1280
- Mosaic: 1.0
- Cos LR: ✅ True
- 学习率: 默认

**结果**:
- 最佳 mAP50: 54.20% (Epoch 160)
- 最佳 mAP50-95: 16.59%
- Precision: 59.61%
- Recall: 61.53%

**结论**: yolo11s 在当前配置下表现不如 yolo11n，说明模型容量不是瓶颈。

---

### 3. pv_pile_yolo11n_no_mosaic_opt1 (关闭 Mosaic 优化)

**实验目的**: 测试关闭 Mosaic 对小目标检测的影响，优化学习率策略。

**关键配置**:
- 模型: yolo11n.pt
- Epochs: 300
- Batch: 16
- Imgsz: 1280
- **Mosaic: 0.0** (完全关闭)
- Mixup: 0.0
- Copy-Paste: 0.0
- Cos LR: ✅ True
- 学习率: lr0=0.005, lrf=0.0001 (优化)
- Warmup Epochs: 5

**结果**:
- 最佳 mAP50: 52.53% (Epoch 291)
- 最佳 mAP50-95: 15.34%
- Precision: 58.15%
- Recall: 59.94%

**与基准对比**:
- mAP50: **-7.69%** (60.22% → 52.53%)
- mAP50-95: **-3.37%** (18.71% → 15.34%)

**结论**: 
- ❌ **关闭 Mosaic 后性能显著下降**
- 说明当前数据集从 Mosaic 增强中受益
- 建议：尝试降低 Mosaic 强度 (0.3-0.5) 而非完全关闭

---

### 4. pv_pile_yolo11s7 (yolo11s, batch=32)

**实验目的**: 测试更大的批次大小。

**关键配置**:
- 模型: yolo11s.pt
- Epochs: 200
- Batch: 32 (较大)
- Mosaic: 1.0

**结果**:
- 最佳 mAP50: 6.87% (Epoch 1)
- 最佳 mAP50-95: 1.68%

**结论**: 训练异常，可能批次过大导致训练不稳定。

---

### 5-7. 其他失败/异常实验

- **pv_pile_yolo11s5, pv_pile_yolo11s6**: 训练失败，无有效结果
- **train3**: 训练异常，无有效结果

---

## 📈 关键发现

### 1. 模型选择

- **yolo11n 表现优于 yolo11s**: train4 (yolo11n) 达到 60.22% mAP50，而 yolo11s8 只有 54.20%
- **结论**: 对于当前数据集，模型容量不是瓶颈，yolo11n 已足够

### 2. Mosaic 增强的影响

- **启用 Mosaic (1.0)**: train4 达到 60.22% mAP50 ✅
- **关闭 Mosaic (0.0)**: opt1 只有 52.53% mAP50 ❌
- **性能下降**: -7.69% (相对下降 12.77%)
- **结论**: 当前数据集从 Mosaic 增强中显著受益，不应完全关闭

### 3. 学习率策略

- **默认学习率 + 无 Cos LR**: train4 表现最佳
- **优化学习率 + Cos LR**: opt1 表现较差（但可能受 Mosaic 关闭影响）
- **结论**: 需要进一步实验验证学习率策略的独立影响

### 4. 批次大小

- **Batch=16**: train4 和 opt1 都表现良好
- **Batch=32**: yolo11s7 训练异常
- **结论**: Batch=16 是更稳定的选择

### 5. 训练轮数

- **200 epochs**: train4 在 Epoch 185 达到最佳
- **300 epochs**: opt1 在 Epoch 291 达到最佳
- **结论**: 200 epochs 可能已足够，但需要根据早停策略调整

---

## 🎯 性能排名

1. **🥇 train4** (yolo11n, mosaic=1.0): **mAP50 = 60.22%**
2. **🥈 pv_pile_yolo11s8** (yolo11s, mosaic=1.0): mAP50 = 54.20%
3. **🥉 pv_pile_yolo11n_no_mosaic_opt1** (yolo11n, mosaic=0.0): mAP50 = 52.53%

---

## 💡 优化建议

### 基于当前实验结果

1. **保持 train4 的配置作为基准** ✅
   - yolo11n + Mosaic=1.0 是最佳组合

2. **尝试降低 Mosaic 强度** (推荐下一步)
   - 测试 Mosaic=0.3, 0.5, 0.7
   - 可能在小目标检测和增强效果之间找到平衡

3. **尝试更大的模型** (如果显存允许)
   - yolo11m 配合 Mosaic=1.0
   - 可能进一步提升性能

4. **优化学习率策略** (独立验证)
   - 在保持 Mosaic=1.0 的前提下测试优化学习率
   - 验证学习率优化的独立影响

5. **多尺度训练**
   - 启用 multi-scale 训练
   - 可能提高泛化能力

---

## 📊 实验配置对比表

| 实验 | 模型 | Batch | Mosaic | Cos LR | lr0 | lrf | Warmup | Epochs | mAP50 |
|------|------|-------|--------|--------|-----|-----|--------|--------|-------|
| train4 | yolo11n | 16 | 1.0 | ❌ | 0.01 | 0.01 | 3 | 200 | **60.22%** |
| yolo11s8 | yolo11s | 16 | 1.0 | ✅ | 0.01 | 0.01 | 3 | 200 | 54.20% |
| opt1 | yolo11n | 16 | 0.0 | ✅ | 0.005 | 0.0001 | 5 | 300 | 52.53% |

---

## 🔍 失败实验分析

### pv_pile_yolo11s5, pv_pile_yolo11s6
- **问题**: 训练失败，无有效结果
- **可能原因**: 
  - 批次大小过大 (batch=32)
  - 显存不足
  - 训练早期中断

### train3
- **问题**: 训练异常，无有效结果
- **可能原因**: 
  - 训练配置问题
  - 数据加载问题

---

## 📝 数据集信息

- **训练集**: 389 张图像 (10,265 个标注)
- **验证集**: 111 张图像 (3,130 个标注)
- **测试集**: 57 张图像 (1,527 个标注)
- **类别**: 桩基 (1 类)
- **目标特点**: 小目标 (20-30 像素)
- **图像尺寸**: 切片后 1280×1280

---

## 🎯 下一步实验建议

### 高优先级

1. **降低 Mosaic 强度实验**
   ```bash
   # Mosaic = 0.3
   python src/models/trainer.py --mosaic 0.3 --name pv_pile_yolo11n_mosaic_0.3
   
   # Mosaic = 0.5
   python src/models/trainer.py --mosaic 0.5 --name pv_pile_yolo11n_mosaic_0.5
   ```

2. **yolo11m 实验**
   ```bash
   python src/models/trainer.py --model yolo11m.pt --batch 12 --name pv_pile_yolo11m
   ```

### 中优先级

3. **学习率优化实验** (保持 Mosaic=1.0)
   ```bash
   python src/models/trainer.py --lr0 0.005 --lrf 0.0001 --warmup-epochs 5 --cos-lr --name pv_pile_yolo11n_lr_opt
   ```

4. **多尺度训练**
   ```bash
   python src/models/trainer.py --multi-scale --name pv_pile_yolo11n_multiscale
   ```

---

## 📁 模型文件位置

| 实验 | 最佳模型路径 |
|------|------------|
| train4 | `runs/detect/train4/weights/best.pt` |
| pv_pile_yolo11s8 | `runs/detect/pv_pile_yolo11s8/weights/best.pt` |
| pv_pile_yolo11n_no_mosaic_opt1 | `runs/detect/pv_pile_yolo11n_no_mosaic_opt1/weights/best.pt` |

---

## 📅 实验时间线

- **train4**: 基准实验，达到最佳性能 60.22%
- **pv_pile_yolo11s8**: yolo11s 实验，性能 54.20%
- **pv_pile_yolo11n_no_mosaic_opt1**: 关闭 Mosaic 优化实验，性能下降至 52.53%

---

## 🎓 经验总结

1. **小目标检测不一定需要关闭 Mosaic**
   - 当前数据集从 Mosaic 增强中受益
   - 完全关闭 Mosaic 导致性能下降 12.77%

2. **模型选择很重要**
   - yolo11n 在当前数据集上表现优于 yolo11s
   - 说明模型容量不是瓶颈

3. **批次大小需要谨慎选择**
   - Batch=16 表现稳定
   - Batch=32 可能导致训练不稳定

4. **训练轮数需要根据早停策略调整**
   - 200 epochs 可能已足够
   - 最佳性能通常出现在训练后期

---

*报告生成时间: 2025-01-27*
*项目路径: /root/pv_pile*


