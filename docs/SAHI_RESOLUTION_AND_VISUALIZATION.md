# SAHI 推理：分辨率限制与可视化说明

## 📐 输入图像分辨率

### ✅ 无硬性分辨率上限

SAHI 推理模块**没有硬性分辨率上限**，可以处理任意尺寸的图像。SAHI 的核心优势就是通过切片处理大尺寸图像。

### 实际限制因素

1. **内存限制**: 
   - 图像会被加载到内存中
   - 切片推理会创建多个切片副本
   - 建议可用内存 ≥ 图像大小 × 3-5 倍

2. **处理时间**:
   - 切片数量 = (图像宽度/切片宽度) × (图像高度/切片高度)
   - 处理时间与切片数量成正比

3. **实际测试**:
   - ✅ 已成功处理: **5712×3420 像素** (12MB) 的图像
   - ✅ 切片数: 77 个 (640×640 切片，20% 重叠)
   - ✅ 处理时间: 约 1-2 分钟（取决于 GPU）

### 大图像处理示例

```bash
# 处理大尺寸航拍图像（如 10000×8000 像素）
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source large_aerial_image.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.2 \
    --save-img
```

**计算切片数**:
- 图像: 10000×8000 像素
- 切片: 640×640，重叠 20%
- 有效切片步长: 640 × 0.8 = 512 像素
- 切片数: (10000/512) × (8000/512) ≈ 20 × 16 = **320 个切片**

### 内存估算

- 单张图像内存: 宽度 × 高度 × 3 (RGB) × 4 字节 (float32)
- 5712×3420 图像: 约 234 MB
- 加上切片处理: 约 500-1000 MB 总内存

## 🎨 可视化输出

### ✅ 有完整的可视化输出

推理结果包含**带标注的可视化图像**，显示所有检测到的目标。

### 可视化内容

1. **检测框**: 每个检测目标都有边界框
2. **类别标签**: 显示类别名称（如"桩基"）
3. **置信度**: 显示检测置信度分数
4. **原始分辨率**: 保持原始图像分辨率

### 输出文件

- **文件名**: `{原图像名}.png`
- **位置**: `{output_dir}/{原图像名}.png`
- **格式**: PNG (RGB)
- **分辨率**: 与输入图像相同

### 测试结果示例

**输入图像**:
- 文件名: `桩基照片.jpg`
- 尺寸: 5712×3420 像素
- 大小: 12 MB

**输出可视化**:
- 文件名: `桩基照片.png`
- 尺寸: 5712×3420 像素（保持原分辨率）
- 大小: 22 MB
- 内容: 包含 229 个检测框和标签

### 查看可视化结果

```bash
# 方法 1: 直接查看 PNG 文件
# 在文件管理器中打开
runs/detect/test_inference/桩基照片.png

# 方法 2: 使用 Python 查看
python -c "
from PIL import Image
img = Image.open('runs/detect/test_inference/桩基照片.png')
img.show()
"

# 方法 3: 使用图像查看器
# 在 Linux 上
xdg-open runs/detect/test_inference/桩基照片.png
```

### 可视化示例代码

```python
from PIL import Image
import matplotlib.pyplot as plt

# 加载可视化结果
img = Image.open('runs/detect/test_inference/桩基照片.png')

# 显示图像
plt.figure(figsize=(20, 12))
plt.imshow(img)
plt.axis('off')
plt.title('SAHI 推理结果 - 检测到 229 个桩基')
plt.tight_layout()
plt.savefig('visualization_result.png', dpi=150, bbox_inches='tight')
plt.show()
```

## 📊 输出文件说明

### 1. 可视化图像 (PNG)

- **格式**: PNG (RGB)
- **分辨率**: 与输入图像相同
- **内容**: 
  - 原始图像 + 检测框 + 标签 + 置信度
  - 检测框颜色根据类别自动分配
  - 标签显示类别名称和置信度

### 2. JSON 结果文件

- **格式**: COCO 预测格式
- **内容**:
  ```json
  [
    {
      "image_id": 0,
      "category_id": 0,
      "bbox": [x, y, width, height],
      "score": 0.6709
    },
    ...
  ]
  ```

### 3. 控制台统计

- 总目标数
- 类别分布
- 处理进度

## 🔍 大图像处理建议

### 1. 内存优化

如果遇到内存不足：

```bash
# 使用更小的切片
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source large_image.jpg \
    --slice-height 512 \
    --slice-width 512 \
    --save-img
```

### 2. 处理时间优化

```bash
# 减少重叠比例（但可能降低小目标检测率）
python src/inference/sahi_inference.py \
    --weights runs/detect/train4/weights/best.pt \
    --source large_image.jpg \
    --slice-height 640 \
    --slice-width 640 \
    --overlap-height-ratio 0.1 \
    --overlap-width-ratio 0.1 \
    --save-img
```

### 3. 超大图像处理

对于超大图像（> 20000×20000 像素），建议：

1. **分批处理**: 手动将图像切分成多个区域
2. **使用更大的切片**: 1280×1280 或 1920×1920
3. **增加系统内存**: 确保有足够的 RAM

## 📋 总结

### 分辨率限制

- ✅ **无硬性上限**: SAHI 可以处理任意尺寸图像
- ⚠️ **实际限制**: 受内存和处理时间限制
- ✅ **已测试**: 5712×3420 像素图像成功处理

### 可视化输出

- ✅ **完整可视化**: 包含检测框、标签、置信度
- ✅ **原始分辨率**: 保持输入图像分辨率
- ✅ **PNG 格式**: 高质量输出
- ✅ **自动保存**: 使用 `--save-img` 参数

---

*最后更新: 2025-01-27*
*测试图像: 5712×3420 像素，成功处理*

