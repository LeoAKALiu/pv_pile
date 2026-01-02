# 数据预处理模块

## 功能说明

`preprocess.py` 脚本用于将 COCO 格式的数据集转换为 YOLO 格式，并进行切片处理。

### 主要功能

1. **读取 COCO JSON 标注文件**
   - 支持标准的 COCO 格式标注文件
   - 自动解析图像信息和标注信息

2. **图像切片处理**
   - 将大尺寸图像切分为指定大小的切片（默认 1280×1280）
   - 支持可配置的重叠比例（默认 20%）
   - 自动处理边界情况

3. **标注格式转换**
   - 将 COCO 格式（绝对坐标）转换为 YOLO 格式（归一化坐标）
   - 自动将标注分配到对应的切片
   - 过滤掉切片外的标注（保留至少 50% 在切片内的标注）

4. **数据集划分**
   - 自动划分为训练集、验证集和测试集
   - 默认比例：70% / 20% / 10%
   - 使用固定随机种子确保可重复性

5. **生成数据集配置**
   - 自动生成 YOLO 格式的 `dataset.yaml` 配置文件

## 使用方法

### 基本用法

```bash
# 使用默认参数
python src/data/preprocess.py

# 指定输入输出目录
python src/data/preprocess.py \
    --input-dir /path/to/DatasetId_853_1766643148 \
    --output-dir /path/to/data/processed

# 自定义切片参数
python src/data/preprocess.py \
    --slice-size 1280 \
    --overlap 0.2

# 自定义数据集划分比例
python src/data/preprocess.py \
    --train-ratio 0.7 \
    --val-ratio 0.2 \
    --test-ratio 0.1
```

### 参数说明

- `--input-dir`: 输入数据目录，应包含 `Images/` 和 `Annotations/` 文件夹
- `--output-dir`: 输出数据目录，处理后的数据将保存在此
- `--slice-size`: 切片大小（像素），默认 1280
- `--overlap`: 重叠比例（0-1），默认 0.2（20%）
- `--train-ratio`: 训练集比例，默认 0.7
- `--val-ratio`: 验证集比例，默认 0.2
- `--test-ratio`: 测试集比例，默认 0.1

## 输出结构

处理完成后，输出目录结构如下：

```
data/processed/
├── images/              # 所有切片图像（临时，划分后会删除）
├── labels/              # 所有切片标注（临时，划分后会删除）
├── train/
│   ├── images/          # 训练集图像
│   └── labels/          # 训练集标注
├── val/
│   ├── images/          # 验证集图像
│   └── labels/          # 验证集标注
├── test/
│   ├── images/          # 测试集图像
│   └── labels/          # 测试集标注
└── dataset.yaml         # YOLO 数据集配置文件
```

## 注意事项

1. **标注过滤规则**：只有至少 50% 面积在切片内的标注才会被保留
2. **切片命名**：格式为 `{原图名}_slice_{序号}.jpg`，标注文件对应为 `.txt`
3. **类别 ID**：COCO 格式的类别 ID 从 1 开始，会自动转换为 YOLO 格式（从 0 开始）
4. **图像格式**：输出图像统一为 JPG 格式，质量 95%

## 示例

处理完整数据集：

```bash
python src/data/preprocess.py \
    --input-dir /root/pv_pile/DatasetId_853_1766643148 \
    --output-dir /root/pv_pile/data/processed \
    --slice-size 1280 \
    --overlap 0.2
```

处理完成后，可以使用生成的 `dataset.yaml` 进行训练：

```bash
yolo train data=data/processed/dataset.yaml model=yolo11n.pt epochs=100
```

