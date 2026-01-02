#!/usr/bin/env python3
"""
数据集可视化脚本：随机抽取图像并绘制标注框，用于检查数据预处理结果。

功能：
1. 随机抽取指定数量的图像
2. 读取 YOLO 格式标注
3. 在图像上绘制边界框和类别标签
4. 打印标注统计信息
5. 保存可视化结果
"""

import argparse
import random
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager


def load_yolo_annotations(label_path: Path) -> List[Tuple[int, float, float, float, float]]:
    """加载 YOLO 格式的标注文件。

    Args:
        label_path: 标注文件路径

    Returns:
        标注列表，每个元素为 (class_id, x_center, y_center, width, height)
    """
    annotations = []
    if not label_path.exists():
        return annotations

    with open(label_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                continue
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            annotations.append((class_id, x_center, y_center, width, height))

    return annotations


def yolo_to_bbox(
    x_center: float, y_center: float, width: float, height: float, img_width: int, img_height: int
) -> Tuple[int, int, int, int]:
    """将 YOLO 格式坐标转换为像素坐标边界框。

    Args:
        x_center: 归一化的中心点 x 坐标
        y_center: 归一化的中心点 y 坐标
        width: 归一化的宽度
        height: 归一化的高度
        img_width: 图像宽度
        img_height: 图像高度

    Returns:
        (x_min, y_min, x_max, y_max) 像素坐标
    """
    x_center_px = x_center * img_width
    y_center_px = y_center * img_height
    width_px = width * img_width
    height_px = height * img_height

    x_min = int(x_center_px - width_px / 2)
    y_min = int(y_center_px - height_px / 2)
    x_max = int(x_center_px + width_px / 2)
    y_max = int(y_center_px + height_px / 2)

    # 确保坐标在图像范围内
    x_min = max(0, min(x_min, img_width - 1))
    y_min = max(0, min(y_min, img_height - 1))
    x_max = max(0, min(x_max, img_width - 1))
    y_max = max(0, min(y_max, img_height - 1))

    return (x_min, y_min, x_max, y_max)


def draw_bbox_on_image(
    img: Image.Image,
    annotations: List[Tuple[int, float, float, float, float]],
    class_names: List[str],
    show_labels: bool = True,
) -> Image.Image:
    """在图像上绘制边界框。

    Args:
        img: PIL 图像对象
        annotations: 标注列表
        class_names: 类别名称列表
        show_labels: 是否显示类别标签

    Returns:
        绘制了边界框的图像
    """
    img = img.copy()
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    # 颜色列表（用于不同类别）
    colors = [
        (255, 0, 0),      # 红色
        (0, 255, 0),      # 绿色
        (0, 0, 255),      # 蓝色
        (255, 255, 0),    # 黄色
        (255, 0, 255),    # 洋红
        (0, 255, 255),    # 青色
        (128, 0, 128),    # 紫色
        (255, 165, 0),    # 橙色
    ]

    # 尝试加载字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            font = ImageFont.load_default()

    for class_id, x_center, y_center, width, height in annotations:
        # 转换为像素坐标
        x_min, y_min, x_max, y_max = yolo_to_bbox(
            x_center, y_center, width, height, img_width, img_height
        )

        # 选择颜色
        color = colors[class_id % len(colors)]

        # 绘制边界框
        draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)

        # 绘制类别标签
        if show_labels:
            class_name = class_names[class_id] if class_id < len(class_names) else f"Class_{class_id}"
            label = f"{class_name}"
            
            # 计算文本尺寸
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 绘制文本背景
            draw.rectangle(
                [x_min, y_min - text_height - 4, x_min + text_width + 4, y_min],
                fill=color,
            )
            # 绘制文本
            draw.text((x_min + 2, y_min - text_height - 2), label, fill=(255, 255, 255), font=font)

    return img


def visualize_dataset(
    dataset_dir: Path,
    split: str = "train",
    num_samples: int = 10,
    output_dir: Optional[Path] = None,
    class_names: Optional[List[str]] = None,
) -> None:
    """可视化数据集。

    Args:
        dataset_dir: 数据集根目录
        split: 数据集划分（train/val/test）
        num_samples: 抽取的样本数量
        output_dir: 输出目录，如果为 None 则不保存
        class_names: 类别名称列表
    """
    images_dir = dataset_dir / split / "images"
    labels_dir = dataset_dir / split / "labels"

    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    if not labels_dir.exists():
        raise FileNotFoundError(f"Labels directory not found: {labels_dir}")

    # 获取所有图像文件
    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    
    if len(image_files) == 0:
        print(f"No images found in {images_dir}")
        return

    # 随机抽取
    num_samples = min(num_samples, len(image_files))
    selected_files = random.sample(image_files, num_samples)

    # 默认类别名称
    if class_names is None:
        class_names = ["桩基"]  # 根据实际类别修改

    print(f"\n{'='*80}")
    print(f"可视化数据集: {split}")
    print(f"总图像数: {len(image_files)}")
    print(f"抽取样本数: {num_samples}")
    print(f"{'='*80}\n")

    # 统计信息
    total_objects = 0
    class_counts = {}

    # 处理每张图像
    for idx, img_file in enumerate(selected_files, 1):
        # 加载图像
        img = Image.open(img_file)
        img_width, img_height = img.size

        # 加载标注
        label_file = labels_dir / f"{img_file.stem}.txt"
        annotations = load_yolo_annotations(label_file)

        # 统计
        total_objects += len(annotations)
        for class_id, _, _, _, _ in annotations:
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

        # 打印信息
        print(f"[{idx}/{num_samples}] {img_file.name}")
        print(f"  图像尺寸: {img_width}×{img_height}")
        print(f"  目标数量: {len(annotations)}")
        
        if len(annotations) > 0:
            print(f"  标注详情:")
            for ann_idx, (class_id, x_center, y_center, width, height) in enumerate(annotations[:5], 1):
                class_name = class_names[class_id] if class_id < len(class_names) else f"Class_{class_id}"
                x_min, y_min, x_max, y_max = yolo_to_bbox(x_center, y_center, width, height, img_width, img_height)
                bbox_width = x_max - x_min
                bbox_height = y_max - y_min
                print(f"    {ann_idx}. {class_name}: center=({x_center:.4f}, {y_center:.4f}), "
                      f"size=({width:.4f}, {height:.4f}), "
                      f"bbox=[{x_min}, {y_min}, {x_max}, {y_max}], "
                      f"pixel_size={bbox_width}×{bbox_height}")
            if len(annotations) > 5:
                print(f"    ... 还有 {len(annotations) - 5} 个目标")
        else:
            print(f"  ⚠️  无标注")
        print()

        # 绘制边界框
        if len(annotations) > 0:
            img_with_bbox = draw_bbox_on_image(img, annotations, class_names, show_labels=True)
        else:
            img_with_bbox = img

        # 保存可视化结果
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{split}_{img_file.stem}_visualized.jpg"
            img_with_bbox.save(output_file, quality=95)
            print(f"  ✅ 已保存: {output_file}")

    # 打印统计信息
    print(f"\n{'='*80}")
    print(f"统计信息:")
    print(f"  总目标数: {total_objects}")
    print(f"  平均每张图: {total_objects/num_samples:.2f} 个目标")
    print(f"  类别分布:")
    for class_id, count in sorted(class_counts.items()):
        class_name = class_names[class_id] if class_id < len(class_names) else f"Class_{class_id}"
        print(f"    {class_name} (ID: {class_id}): {count} 个")
    print(f"{'='*80}\n")


def load_class_names_from_yaml(yaml_path: Path) -> List[str]:
    """从 dataset.yaml 文件加载类别名称。

    Args:
        yaml_path: YAML 文件路径

    Returns:
        类别名称列表
    """
    if not yaml_path.exists():
        return None

    try:
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if 'names' in data:
                # names 可能是字典或列表
                if isinstance(data['names'], dict):
                    # 如果是字典，按 key 排序
                    sorted_items = sorted(data['names'].items(), key=lambda x: int(x[0]))
                    return [name for _, name in sorted_items]
                elif isinstance(data['names'], list):
                    return data['names']
    except Exception as e:
        print(f"Warning: Could not load class names from YAML: {e}")

    return None


def main() -> None:
    """主函数。"""
    parser = argparse.ArgumentParser(description='可视化数据集')
    parser.add_argument(
        '--dataset-dir',
        type=str,
        default='/root/pv_pile/data/processed',
        help='数据集目录',
    )
    parser.add_argument(
        '--split',
        type=str,
        choices=['train', 'val', 'test'],
        default='train',
        help='数据集划分（train/val/test）',
    )
    parser.add_argument(
        '--num-samples',
        type=int,
        default=10,
        help='抽取的样本数量（默认: 10）',
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/root/pv_pile/data/visualizations',
        help='可视化结果输出目录',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='随机种子（默认: 42）',
    )

    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)
    np.random.seed(args.seed)

    dataset_dir = Path(args.dataset_dir)
    output_dir = Path(args.output_dir) if args.output_dir else None

    # 尝试从 dataset.yaml 加载类别名称
    yaml_path = dataset_dir / "dataset.yaml"
    class_names = load_class_names_from_yaml(yaml_path)
    if class_names is None:
        class_names = ["桩基"]  # 默认类别名称
        print(f"Warning: Using default class names: {class_names}")

    print(f"Class names: {class_names}")

    # 可视化
    visualize_dataset(
        dataset_dir=dataset_dir,
        split=args.split,
        num_samples=args.num_samples,
        output_dir=output_dir,
        class_names=class_names,
    )


if __name__ == "__main__":
    main()

