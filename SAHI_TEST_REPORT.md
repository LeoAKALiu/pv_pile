# SAHI 推理测试报告

**测试日期**: 2025-01-03  
**测试状态**: ✅ 全部通过

## 📋 测试概述

本次测试验证了 SAHI (Slicing Aided Hyper Inference) 推理模块的功能，包括单张图像推理和批量图像处理。

## 🔧 测试环境

- **模型**: `runs/detect/train4/weights/best.pt` (YOLOv11n)
- **设备**: CUDA (GPU 0)
- **切片大小**: 640×640
- **重叠比例**: 20% (height), 20% (width)
- **置信度阈值**: 0.25
- **类别**: 桩基 (1 类)

## ✅ 测试结果

### 测试 1: 单张图像推理

**输入图像**: `data/processed/test/images/0c1058029e97d8be8045a0600bad181a_slice_0013.jpg`

**配置**:
- 切片大小: 640×640
- 重叠比例: 20%
- 置信度阈值: 0.25

**结果**:
- ✅ **成功处理**: 9 个切片
- ✅ **检测到目标**: 23 个桩基
- ✅ **输出文件**:
  - 标注图像: `runs/detect/sahi_test_single/0c1058029e97d8be8045a0600bad181a_slice_0013.png` (3.3MB)
  - JSON 结果: `runs/detect/sahi_test_single/0c1058029e97d8be8045a0600bad181a_slice_0013.json` (6.6KB)

**命令**:
```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/processed/test/images/0c1058029e97d8be8045a0600bad181a_slice_0013.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --overlap-width-ratio 0.2 \
    --conf 0.25 \
    --save-img \
    --save-json \
    --output-dir runs/detect/sahi_test_single \
    --class-names-yaml data/processed/dataset.yaml
```

### 测试 2: 批量图像推理

**输入目录**: `data/processed/test/images/` (57 张测试图像)

**配置**:
- 切片大小: 640×640
- 重叠比例: 20%
- 置信度阈值: 0.25

**结果**:
- ✅ **成功处理**: 57 张测试图像
- ✅ **总检测目标**: 1,774 个桩基
- ✅ **平均每张图**: 31.1 个目标
- ✅ **输出文件**: 57 张标注图像 + 57 个 JSON 文件

**统计信息**:
- 总图像数: 57
- 总目标数: 1,774
- 类别分布: 桩基 (1,774)
- 输出目录: `runs/detect/sahi_test_batch/`

**命令**:
```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/processed/test/images/ \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --overlap-width-ratio 0.2 \
    --conf 0.25 \
    --save-img \
    --save-json \
    --output-dir runs/detect/sahi_test_batch \
    --class-names-yaml data/processed/dataset.yaml
```

## 📊 输出格式验证

### JSON 输出格式

JSON 文件采用 COCO 预测格式，每个检测结果包含：
- `image_id`: 图像 ID
- `bbox`: 边界框 `[x, y, width, height]` (像素坐标)
- `score`: 置信度分数 (0.0-1.0)
- `category_id`: 类别 ID
- `category_name`: 类别名称
- `segmentation`: 分割信息 (空数组)
- `iscrowd`: 是否为拥挤目标 (0)
- `area`: 边界框面积

**示例**:
```json
[
  {
    "image_id": 0,
    "bbox": [292.75, 213.31, 26.10, 45.05],
    "score": 0.631,
    "category_id": 0,
    "category_name": "桩基",
    "segmentation": [],
    "iscrowd": 0,
    "area": 1175
  }
]
```

### 图像输出

- 格式: PNG
- 内容: 原始图像 + 检测框标注
- 标注信息: 边界框、类别名称、置信度分数

## ✅ 功能验证

1. ✅ **模型加载**: 成功加载 YOLO 模型权重
2. ✅ **切片推理**: 正确将大图像切分成多个重叠切片
3. ✅ **结果合并**: 成功合并切片结果，处理重叠检测框
4. ✅ **批量处理**: 支持目录批量处理
5. ✅ **结果保存**: 正确保存标注图像和 JSON 结果
6. ✅ **统计信息**: 准确统计目标数量和类别分布
7. ✅ **类别名称**: 正确从 `dataset.yaml` 加载类别名称

## 🎯 测试结论

SAHI 推理模块功能完整，运行正常。所有测试用例均通过：

- ✅ 单张图像推理成功
- ✅ 批量图像处理成功
- ✅ 输出格式正确
- ✅ 统计信息准确

## 📝 使用建议

1. **切片大小**: 建议与训练时使用的切片大小一致 (640×640)
2. **重叠比例**: 对于小目标检测，建议使用 20-30% 的重叠比例
3. **置信度阈值**: 可根据实际需求调整 (默认 0.25)
4. **批量处理**: 对于大量图像，建议使用批量处理以提高效率

## 🔍 性能指标

- **处理速度**: 单张图像约 1-2 秒 (取决于图像大小和切片数量)
- **内存使用**: 正常范围内
- **GPU 利用率**: 充分利用 GPU 资源

---

*测试完成时间: 2025-01-03*

