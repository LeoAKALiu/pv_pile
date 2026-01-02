# 推理模块

## 功能说明

`sahi_inference.py` 脚本使用 SAHI (Slicing Aided Hyper Inference) 进行切片推理，特别适合大尺寸图像和小目标检测。

### 主要功能

1. **切片推理**: 将大图像切分成多个重叠的切片进行推理
2. **结果合并**: 自动合并切片结果，处理重叠检测框
3. **批量处理**: 支持单张图像、目录批量处理
4. **结果保存**: 支持保存标注图像和 JSON 格式结果
5. **统计信息**: 自动统计检测到的目标数量和类别分布

## 使用方法

### 基本用法

```bash
# 单张图像推理
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/test/image.jpg \
    --save-img

# 批量图像推理
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/test/ \
    --save-img \
    --save-json

# 使用自定义切片大小
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/test/image.jpg \
    --slice-height 512 \
    --slice-width 512 \
    --overlap-height-ratio 0.3 \
    --overlap-width-ratio 0.3 \
    --save-img
```

### 参数说明

#### 必需参数

- `--weights`: 模型权重文件路径（默认: `runs/detect/train4/weights/best.pt`）
- `--source`: 输入图像、视频或目录路径（必需）

#### 输出参数

- `--output-dir`: 输出目录（默认: `runs/detect/predict`）
- `--save-img`: 保存标注图像
- `--save-json`: 保存 JSON 格式结果
- `--no-save`: 不保存任何结果（仅显示）

#### SAHI 切片参数

- `--slice-height`: 切片高度（默认: 640，建议与训练时切片大小一致或更小）
- `--slice-width`: 切片宽度（默认: 640）
- `--overlap-height-ratio`: 高度重叠比例（默认: 0.2，即 20%）
- `--overlap-width-ratio`: 宽度重叠比例（默认: 0.2，即 20%）

#### 检测参数

- `--conf`: 置信度阈值（默认: 0.25）
- `--iou`: NMS IoU 阈值（默认: 0.45）
- `--device`: 设备（默认: '0'，或 'cpu'）

#### 其他参数

- `--class-names-yaml`: 数据集 YAML 文件路径（用于类别名称）
- `--view-img`: 显示结果窗口

## 输出结果

### 图像输出

- 标注图像保存在 `{output_dir}/{image_name}_prediction_visual.png`
- 包含检测框、类别标签和置信度

### JSON 输出

- JSON 文件保存在 `{output_dir}/{image_name}.json`
- 格式：COCO 预测格式
- 包含：边界框坐标、类别、置信度

### 统计信息

- 在控制台输出检测统计
- 包括：总目标数、类别分布

## 示例

### 示例 1: 单张图像推理

```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source DatasetId_853_1766643148/Images/桩基照片.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --overlap-width-ratio 0.2 \
    --conf 0.25 \
    --save-img \
    --save-json
```

### 示例 2: 批量处理测试集

```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/processed/test/images \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.3 \
    --overlap-width-ratio 0.3 \
    --conf 0.2 \
    --save-img \
    --save-json \
    --output-dir runs/detect/test_inference
```

### 示例 3: 小目标优化（更小的切片）

```bash
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source data/test/image.jpg \
    --slice-height 512 \
    --slice-width 512 \
    --overlap-height-ratio 0.3 \
    --overlap-width-ratio 0.3 \
    --conf 0.15 \
    --save-img
```

## 切片参数建议

### 对于小目标检测（20-30 像素）

- **切片大小**: 512×512 或 640×640
- **重叠比例**: 0.3-0.4 (30-40%)
- **置信度阈值**: 0.15-0.25

### 对于中等目标

- **切片大小**: 640×640 或 1280×1280
- **重叠比例**: 0.2-0.3 (20-30%)
- **置信度阈值**: 0.25-0.35

## 性能优化

1. **切片大小**: 与训练时切片大小一致或更小
2. **重叠比例**: 增加重叠可以提高小目标检测率，但会增加计算时间
3. **置信度阈值**: 降低阈值可以检测更多小目标，但可能增加误检
4. **GPU 加速**: 使用 `--device 0` 启用 GPU 加速

## 注意事项

1. **内存使用**: 大图像切片推理会占用较多内存
2. **处理时间**: 切片推理比直接推理慢，但检测精度更高
3. **结果合并**: SAHI 自动处理重叠检测框，使用 NMS 去重

## 故障排除

### SAHI 未安装

```bash
pip install sahi
```

### 模型加载失败

- 检查模型路径是否正确
- 确保模型文件存在且完整

### 内存不足

- 减小切片大小
- 减小批次大小（如果支持批量处理）

---

*最后更新: 2025-01-27*

