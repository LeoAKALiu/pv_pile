#!/usr/bin/env python3
"""
数据预处理脚本：将 COCO 格式数据转换为 YOLO 格式，并进行切片处理。

功能：
1. 读取 COCO JSON 标注文件
2. 对图像进行切片（1280×1280，20%重叠）
3. 将 COCO 标注转换为 YOLO 格式
4. 为每个切片分配对应的标注
5. 划分数据集（训练/验证/测试）
6. 保存处理后的数据
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image
from tqdm import tqdm


def load_coco_json(json_path: str) -> Dict:
    """加载 COCO 格式的 JSON 文件。

    Args:
        json_path: COCO JSON 文件路径

    Returns:
        包含 images, annotations, categories 的字典
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def coco_bbox_to_yolo(
    bbox: List[float], img_width: int, img_height: int
) -> Tuple[float, float, float, float]:
    """将 COCO 格式的边界框转换为 YOLO 格式。

    COCO 格式: [x_min, y_min, width, height] (绝对像素值)
    YOLO 格式: [x_center, y_center, width, height] (归一化到 0-1)

    Args:
        bbox: COCO 格式边界框 [x_min, y_min, width, height]
        img_width: 图像宽度
        img_height: 图像高度

    Returns:
        YOLO 格式边界框 (x_center, y_center, width, height) 归一化坐标
    """
    x_min, y_min, width, height = bbox

    # 转换为中心点坐标
    x_center = x_min + width / 2.0
    y_center = y_min + height / 2.0

    # 归一化
    x_center_norm = x_center / img_width
    y_center_norm = y_center / img_height
    width_norm = width / img_width
    height_norm = height / img_height

    return (x_center_norm, y_center_norm, width_norm, height_norm)


def get_slice_coordinates(
    img_width: int, img_height: int, slice_size: int = 1280, overlap: float = 0.2
) -> List[Tuple[int, int, int, int]]:
    """计算图像切片的坐标。

    Args:
        img_width: 图像宽度
        img_height: 图像高度
        slice_size: 切片大小（正方形）
        overlap: 重叠比例（0-1之间）

    Returns:
        切片坐标列表，每个元素为 (x_min, y_min, x_max, y_max)
    """
    step = int(slice_size * (1 - overlap))
    slices = []

    y = 0
    while y < img_height:
        x = 0
        while x < img_width:
            x_max = min(x + slice_size, img_width)
            y_max = min(y + slice_size, img_height)

            # 确保切片至少有一定大小
            if x_max - x >= slice_size * 0.5 and y_max - y >= slice_size * 0.5:
                slices.append((x, y, x_max, y_max))

            x += step
            if x >= img_width:
                break

        y += step
        if y >= img_height:
            break

    return slices


def is_bbox_in_slice(
    bbox: List[float], slice_coords: Tuple[int, int, int, int]
) -> Tuple[bool, Optional[List[float]]]:
    """判断边界框是否在切片内，如果在则返回切片内的坐标。

    Args:
        bbox: COCO 格式边界框 [x_min, y_min, width, height]
        slice_coords: 切片坐标 (x_min, y_min, x_max, y_max)

    Returns:
        (是否在切片内, 切片内的边界框坐标，如果不在则为 None)
    """
    x_min, y_min, width, height = bbox
    x_max = x_min + width
    y_max = y_min + height

    slice_x_min, slice_y_min, slice_x_max, slice_y_max = slice_coords

    # 计算交集
    inter_x_min = max(x_min, slice_x_min)
    inter_y_min = max(y_min, slice_y_min)
    inter_x_max = min(x_max, slice_x_max)
    inter_y_max = min(y_max, slice_y_max)

    # 检查是否有交集
    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return (False, None)

    # 计算交集面积占原边界框面积的比例
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    bbox_area = width * height

    # 如果交集面积小于原边界框的 50%，则忽略
    if inter_area < bbox_area * 0.5:
        return (False, None)

    # 返回切片内的坐标（相对于切片）
    slice_bbox = [
        inter_x_min - slice_x_min,  # x_min 相对于切片
        inter_y_min - slice_y_min,  # y_min 相对于切片
        inter_x_max - inter_x_min,   # width
        inter_y_max - inter_y_min,    # height
    ]

    return (True, slice_bbox)


def process_single_image(
    img_info: Dict,
    annotations: List[Dict],
    images_dir: Path,
    output_dir: Path,
    slice_size: int = 1280,
    overlap: float = 0.2,
) -> int:
    """处理单张图像：切片并转换标注。

    Args:
        img_info: 图像信息字典
        annotations: 该图像的所有标注
        images_dir: 原始图像目录
        output_dir: 输出目录
        slice_size: 切片大小
        overlap: 重叠比例

    Returns:
        生成的切片数量
    """
    file_name = img_info['file_name']
    img_path = images_dir / file_name
    img_id = img_info['id']
    img_width = img_info['width']
    img_height = img_info['height']

    # 加载图像
    try:
        img = Image.open(img_path)
        # 确保使用实际图像尺寸
        img_width, img_height = img.size
    except Exception as e:
        print(f"Warning: Could not load image {file_name}: {e}")
        return 0

    # 计算切片坐标
    slice_coords_list = get_slice_coordinates(img_width, img_height, slice_size, overlap)

    slice_count = 0
    for idx, slice_coords in enumerate(slice_coords_list):
        x_min, y_min, x_max, y_max = slice_coords
        slice_width = x_max - x_min
        slice_height = y_max - y_min

        # 提取切片图像
        slice_img = img.crop((x_min, y_min, x_max, y_max))

        # 转换为 RGB 模式（JPEG 不支持 RGBA 等模式）
        if slice_img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            rgb_img = Image.new('RGB', slice_img.size, (255, 255, 255))
            if slice_img.mode == 'P':
                slice_img = slice_img.convert('RGBA')
            rgb_img.paste(slice_img, mask=slice_img.split()[-1] if slice_img.mode in ('RGBA', 'LA') else None)
            slice_img = rgb_img
        elif slice_img.mode != 'RGB':
            slice_img = slice_img.convert('RGB')

        # 生成切片文件名
        base_name = Path(file_name).stem
        slice_name = f"{base_name}_slice_{idx:04d}.jpg"
        slice_img_path = output_dir / "images" / slice_name

        # 保存切片图像
        slice_img.save(slice_img_path, quality=95)

        # 处理该切片的标注
        slice_annotations = []
        for ann in annotations:
            if ann['image_id'] != img_id:
                continue

            bbox = ann['bbox']
            in_slice, slice_bbox = is_bbox_in_slice(bbox, slice_coords)

            if in_slice and slice_bbox is not None:
                # 转换为 YOLO 格式（相对于切片）
                yolo_bbox = coco_bbox_to_yolo(slice_bbox, slice_width, slice_height)

                # YOLO 格式：class_id x_center y_center width height
                # COCO 类别 ID：如果从 1 开始则减 1，如果从 0 开始则直接使用
                category_id = ann['category_id']
                class_id = category_id if category_id == 0 else category_id - 1
                slice_annotations.append((class_id, yolo_bbox))

        # 保存标注文件
        label_name = f"{base_name}_slice_{idx:04d}.txt"
        label_path = output_dir / "labels" / label_name

        with open(label_path, 'w') as f:
            for class_id, (x_center, y_center, width, height) in slice_annotations:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        slice_count += 1

    return slice_count


def split_dataset(
    output_dir: Path, train_ratio: float = 0.7, val_ratio: float = 0.2, test_ratio: float = 0.1
) -> None:
    """划分数据集为训练集、验证集和测试集。

    Args:
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
    """
    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"

    # 获取所有图像文件
    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    total = len(image_files)

    # 计算划分点
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    # 随机打乱
    np.random.seed(42)
    indices = np.random.permutation(total)
    image_files = [image_files[i] for i in indices]

    # 创建子目录
    for split in ['train', 'val', 'test']:
        (output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    # 复制文件
    splits = [
        ('train', image_files[:train_end]),
        ('val', image_files[train_end:val_end]),
        ('test', image_files[val_end:]),
    ]

    for split_name, files in splits:
        print(f"Processing {split_name} set: {len(files)} images")
        for img_path in tqdm(files, desc=f"Copying {split_name}"):
            # 复制图像
            dst_img = output_dir / split_name / 'images' / img_path.name
            shutil.copy2(img_path, dst_img)

            # 复制标注
            label_name = img_path.stem + '.txt'
            src_label = labels_dir / label_name
            if src_label.exists():
                dst_label = output_dir / split_name / 'labels' / label_name
                shutil.copy2(src_label, dst_label)


def create_dataset_yaml(output_dir: Path, class_names: List[str]) -> None:
    """创建 YOLO 数据集配置文件。

    Args:
        output_dir: 输出目录
        class_names: 类别名称列表
    """
    yaml_content = f"""# YOLO Dataset Configuration
# Generated automatically by preprocess.py

path: {output_dir.absolute()}  # dataset root dir
train: train/images  # train images (relative to 'path')
val: val/images      # val images (relative to 'path')
test: test/images    # test images (relative to 'path')

# Classes
names:
"""
    for idx, name in enumerate(class_names):
        yaml_content += f"  {idx}: {name}\n"

    yaml_path = output_dir / "dataset.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print(f"Dataset YAML saved to: {yaml_path}")


def main() -> None:
    """主函数。"""
    parser = argparse.ArgumentParser(description='COCO to YOLO 数据预处理')
    parser.add_argument(
        '--input-dir',
        type=str,
        default='/root/pv_pile/DatasetId_853_1766643148',
        help='输入数据目录（包含 Images 和 Annotations 文件夹）',
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/root/pv_pile/data/processed',
        help='输出数据目录',
    )
    parser.add_argument(
        '--slice-size',
        type=int,
        default=1280,
        help='切片大小（默认: 1280）',
    )
    parser.add_argument(
        '--overlap',
        type=float,
        default=0.2,
        help='重叠比例（默认: 0.2，即 20%%）',
    )
    parser.add_argument(
        '--train-ratio',
        type=float,
        default=0.7,
        help='训练集比例（默认: 0.7）',
    )
    parser.add_argument(
        '--val-ratio',
        type=float,
        default=0.2,
        help='验证集比例（默认: 0.2）',
    )
    parser.add_argument(
        '--test-ratio',
        type=float,
        default=0.1,
        help='测试集比例（默认: 0.1）',
    )

    args = parser.parse_args()

    # 路径设置
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    json_path = input_dir / "Annotations" / "coco_info.json"
    images_dir = input_dir / "Images"

    # 检查输入
    if not json_path.exists():
        raise FileNotFoundError(f"COCO JSON file not found: {json_path}")
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    # 创建输出目录
    (output_dir / "images").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels").mkdir(parents=True, exist_ok=True)

    # 加载 COCO 数据
    print(f"Loading COCO JSON from: {json_path}")
    coco_data = load_coco_json(str(json_path))

    images = coco_data['images']
    annotations = coco_data['annotations']
    categories = coco_data['categories']

    print(f"Total images: {len(images)}")
    print(f"Total annotations: {len(annotations)}")
    print(f"Categories: {[cat['name'] for cat in categories]}")

    # 创建 image_id -> annotations 映射
    img_to_anns = {}
    for ann in annotations:
        img_id = ann['image_id']
        if img_id not in img_to_anns:
            img_to_anns[img_id] = []
        img_to_anns[img_id].append(ann)

    # 处理每张图像
    print(f"\nProcessing images with slice_size={args.slice_size}, overlap={args.overlap}")
    total_slices = 0
    for img_info in tqdm(images, desc="Processing images"):
        img_id = img_info['id']
        img_annotations = img_to_anns.get(img_id, [])
        slice_count = process_single_image(
            img_info,
            img_annotations,
            images_dir,
            output_dir,
            args.slice_size,
            args.overlap,
        )
        total_slices += slice_count

    print(f"\nTotal slices created: {total_slices}")

    # 划分数据集
    print("\nSplitting dataset...")
    split_dataset(output_dir, args.train_ratio, args.val_ratio, args.test_ratio)

    # 创建数据集 YAML
    class_names = [cat['name'] for cat in categories]
    create_dataset_yaml(output_dir, class_names)

    print(f"\n✅ Preprocessing completed!")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()

