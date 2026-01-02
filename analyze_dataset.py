#!/usr/bin/env python3
"""
分析 COCO 格式数据集的统计特征。

包括：
- 图像分辨率分布
- 每张图像的目标数量
- 目标尺寸（像素大小）
- 目标在图像中的分布
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def load_coco_json(json_path: str) -> Dict:
    """加载 COCO 格式的 JSON 文件。

    Args:
        json_path: COCO JSON 文件路径

    Returns:
        包含 images, annotations, categories 的字典
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_image_resolutions(
    images: List[Dict], images_dir: str
) -> Dict[str, any]:
    """分析图像分辨率。

    Args:
        images: COCO images 列表
        images_dir: 图像目录路径

    Returns:
        包含分辨率统计信息的字典
    """
    resolutions = []
    widths = []
    heights = []
    file_sizes = []

    for img_info in images:
        file_name = img_info['file_name']
        img_path = os.path.join(images_dir, file_name)

        if os.path.exists(img_path):
            # 从 JSON 获取尺寸
            width = img_info.get('width', 0)
            height = img_info.get('height', 0)

            if width == 0 or height == 0:
                # 如果 JSON 中没有，从实际图像读取
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                except Exception as e:
                    print(f"Warning: Could not read {file_name}: {e}")
                    continue

            resolutions.append((width, height))
            widths.append(width)
            heights.append(height)

            # 获取文件大小（MB）
            file_size = os.path.getsize(img_path) / (1024 * 1024)
            file_sizes.append(file_size)

    return {
        'resolutions': resolutions,
        'widths': widths,
        'heights': heights,
        'file_sizes': file_sizes,
        'count': len(resolutions),
        'width_stats': {
            'min': min(widths) if widths else 0,
            'max': max(widths) if widths else 0,
            'mean': np.mean(widths) if widths else 0,
            'median': np.median(widths) if widths else 0,
        },
        'height_stats': {
            'min': min(heights) if heights else 0,
            'max': max(heights) if heights else 0,
            'mean': np.mean(heights) if heights else 0,
            'median': np.median(heights) if heights else 0,
        },
        'file_size_stats': {
            'min': min(file_sizes) if file_sizes else 0,
            'max': max(file_sizes) if file_sizes else 0,
            'mean': np.mean(file_sizes) if file_sizes else 0,
            'median': np.median(file_sizes) if file_sizes else 0,
        },
    }


def analyze_annotations_per_image(
    images: List[Dict], annotations: List[Dict]
) -> Dict[str, any]:
    """分析每张图像的目标数量。

    Args:
        images: COCO images 列表
        annotations: COCO annotations 列表

    Returns:
        包含每张图像目标数量统计的字典
    """
    # 创建 image_id -> annotations 的映射
    img_to_anns = defaultdict(list)
    for ann in annotations:
        img_to_anns[ann['image_id']].append(ann)

    # 统计每张图像的目标数量
    counts_per_image = []
    for img in images:
        img_id = img['id']
        count = len(img_to_anns[img_id])
        counts_per_image.append(count)

    return {
        'counts': counts_per_image,
        'total_images': len(images),
        'total_annotations': len(annotations),
        'stats': {
            'min': min(counts_per_image) if counts_per_image else 0,
            'max': max(counts_per_image) if counts_per_image else 0,
            'mean': np.mean(counts_per_image) if counts_per_image else 0,
            'median': np.median(counts_per_image) if counts_per_image else 0,
            'std': np.std(counts_per_image) if counts_per_image else 0,
        },
        'distribution': {
            '0': sum(1 for c in counts_per_image if c == 0),
            '1-10': sum(1 for c in counts_per_image if 1 <= c <= 10),
            '11-50': sum(1 for c in counts_per_image if 11 <= c <= 50),
            '51-100': sum(1 for c in counts_per_image if 51 <= c <= 100),
            '101-200': sum(1 for c in counts_per_image if 101 <= c <= 200),
            '201-500': sum(1 for c in counts_per_image if 201 <= c <= 500),
            '500+': sum(1 for c in counts_per_image if c > 500),
        },
    }


def analyze_object_sizes(
    annotations: List[Dict], images: List[Dict]
) -> Dict[str, any]:
    """分析目标（桩）的像素尺寸。

    Args:
        annotations: COCO annotations 列表
        images: COCO images 列表（用于获取图像尺寸）

    Returns:
        包含目标尺寸统计的字典
    """
    # 创建 image_id -> image_info 的映射
    img_dict = {img['id']: img for img in images}

    widths = []
    heights = []
    areas = []
    aspect_ratios = []
    relative_sizes = []  # 目标面积 / 图像面积

    for ann in annotations:
        bbox = ann['bbox']  # [x, y, width, height]
        width = bbox[2]
        height = bbox[3]
        area = width * height

        widths.append(width)
        heights.append(height)
        areas.append(area)

        if height > 0:
            aspect_ratio = width / height
            aspect_ratios.append(aspect_ratio)

        # 计算相对尺寸
        img_id = ann['image_id']
        if img_id in img_dict:
            img = img_dict[img_id]
            img_area = img.get('width', 0) * img.get('height', 0)
            if img_area > 0:
                relative_size = area / img_area
                relative_sizes.append(relative_size)

    return {
        'widths': widths,
        'heights': heights,
        'areas': areas,
        'aspect_ratios': aspect_ratios,
        'relative_sizes': relative_sizes,
        'count': len(annotations),
        'width_stats': {
            'min': min(widths) if widths else 0,
            'max': max(widths) if widths else 0,
            'mean': np.mean(widths) if widths else 0,
            'median': np.median(widths) if widths else 0,
            'std': np.std(widths) if widths else 0,
        },
        'height_stats': {
            'min': min(heights) if heights else 0,
            'max': max(heights) if heights else 0,
            'mean': np.mean(heights) if heights else 0,
            'median': np.median(heights) if heights else 0,
            'std': np.std(heights) if heights else 0,
        },
        'area_stats': {
            'min': min(areas) if areas else 0,
            'max': max(areas) if areas else 0,
            'mean': np.mean(areas) if areas else 0,
            'median': np.median(areas) if areas else 0,
            'std': np.std(areas) if areas else 0,
        },
        'relative_size_stats': {
            'min': min(relative_sizes) if relative_sizes else 0,
            'max': max(relative_sizes) if relative_sizes else 0,
            'mean': np.mean(relative_sizes) if relative_sizes else 0,
            'median': np.median(relative_sizes) if relative_sizes else 0,
        },
    }


def print_analysis_report(
    resolution_info: Dict,
    annotation_count_info: Dict,
    object_size_info: Dict,
) -> None:
    """打印分析报告。

    Args:
        resolution_info: 图像分辨率统计信息
        annotation_count_info: 每张图像目标数量统计
        object_size_info: 目标尺寸统计信息
    """
    print("=" * 80)
    print("数据集特征分析报告")
    print("=" * 80)

    # 1. 图像分辨率
    print("\n【1. 图像分辨率统计】")
    print(f"  总图像数: {resolution_info['count']}")
    print(f"\n  宽度 (Width):")
    print(f"    最小值: {resolution_info['width_stats']['min']:.0f} px")
    print(f"    最大值: {resolution_info['width_stats']['max']:.0f} px")
    print(f"    平均值: {resolution_info['width_stats']['mean']:.2f} px")
    print(f"    中位数: {resolution_info['width_stats']['median']:.0f} px")
    print(f"\n  高度 (Height):")
    print(f"    最小值: {resolution_info['height_stats']['min']:.0f} px")
    print(f"    最大值: {resolution_info['height_stats']['max']:.0f} px")
    print(f"    平均值: {resolution_info['height_stats']['mean']:.2f} px")
    print(f"    中位数: {resolution_info['height_stats']['median']:.0f} px")
    print(f"\n  文件大小:")
    print(f"    最小值: {resolution_info['file_size_stats']['min']:.2f} MB")
    print(f"    最大值: {resolution_info['file_size_stats']['max']:.2f} MB")
    print(f"    平均值: {resolution_info['file_size_stats']['mean']:.2f} MB")
    print(f"    中位数: {resolution_info['file_size_stats']['median']:.2f} MB")

    # 2. 每张图像的目标数量
    print("\n【2. 每张图像的目标数量（桩基数量）】")
    print(f"  总标注数: {annotation_count_info['total_annotations']}")
    print(f"  总图像数: {annotation_count_info['total_images']}")
    print(f"\n  统计信息:")
    print(f"    最小值: {annotation_count_info['stats']['min']:.0f}")
    print(f"    最大值: {annotation_count_info['stats']['max']:.0f}")
    print(f"    平均值: {annotation_count_info['stats']['mean']:.2f}")
    print(f"    中位数: {annotation_count_info['stats']['median']:.0f}")
    print(f"    标准差: {annotation_count_info['stats']['std']:.2f}")
    print(f"\n  分布情况:")
    dist = annotation_count_info['distribution']
    print(f"    0 个目标: {dist['0']} 张")
    print(f"    1-10 个: {dist['1-10']} 张")
    print(f"    11-50 个: {dist['11-50']} 张")
    print(f"    51-100 个: {dist['51-100']} 张")
    print(f"    101-200 个: {dist['101-200']} 张")
    print(f"    201-500 个: {dist['201-500']} 张")
    print(f"    500+ 个: {dist['500+']} 张")

    # 3. 目标尺寸
    print("\n【3. 目标（桩基）像素尺寸统计】")
    print(f"  总目标数: {object_size_info['count']}")
    print(f"\n  宽度 (Width):")
    print(f"    最小值: {object_size_info['width_stats']['min']:.2f} px")
    print(f"    最大值: {object_size_info['width_stats']['max']:.2f} px")
    print(f"    平均值: {object_size_info['width_stats']['mean']:.2f} px")
    print(f"    中位数: {object_size_info['width_stats']['median']:.2f} px")
    print(f"    标准差: {object_size_info['width_stats']['std']:.2f} px")
    print(f"\n  高度 (Height):")
    print(f"    最小值: {object_size_info['height_stats']['min']:.2f} px")
    print(f"    最大值: {object_size_info['height_stats']['max']:.2f} px")
    print(f"    平均值: {object_size_info['height_stats']['mean']:.2f} px")
    print(f"    中位数: {object_size_info['height_stats']['median']:.2f} px")
    print(f"    标准差: {object_size_info['height_stats']['std']:.2f} px")
    print(f"\n  面积 (Area):")
    print(f"    最小值: {object_size_info['area_stats']['min']:.2f} px²")
    print(f"    最大值: {object_size_info['area_stats']['max']:.2f} px²")
    print(f"    平均值: {object_size_info['area_stats']['mean']:.2f} px²")
    print(f"    中位数: {object_size_info['area_stats']['median']:.2f} px²")
    print(f"    标准差: {object_size_info['area_stats']['std']:.2f} px²")
    print(f"\n  相对尺寸 (目标面积 / 图像面积):")
    print(f"    最小值: {object_size_info['relative_size_stats']['min']:.6f}")
    print(f"    最大值: {object_size_info['relative_size_stats']['max']:.6f}")
    print(f"    平均值: {object_size_info['relative_size_stats']['mean']:.6f}")
    print(f"    中位数: {object_size_info['relative_size_stats']['median']:.6f}")

    # 4. 小目标判断
    print("\n【4. 小目标分析】")
    # 通常小目标定义为：面积 < 32x32 = 1024 px²，或相对尺寸 < 0.01
    small_objects = [
        a for a in object_size_info['areas']
        if a < 1024 or (object_size_info['relative_sizes'][object_size_info['areas'].index(a)] < 0.01
                       if object_size_info['areas'].index(a) < len(object_size_info['relative_sizes']) else False)
    ]
    small_count = len([a for a in object_size_info['areas'] if a < 1024])
    print(f"  面积 < 1024 px² (32x32) 的目标数: {small_count} ({small_count/object_size_info['count']*100:.2f}%)")
    
    very_small_count = len([a for a in object_size_info['areas'] if a < 256])  # 16x16
    print(f"  面积 < 256 px² (16x16) 的目标数: {very_small_count} ({very_small_count/object_size_info['count']*100:.2f}%)")

    print("\n" + "=" * 80)


def main() -> None:
    """主函数。"""
    dataset_dir = Path("/root/pv_pile/DatasetId_853_1766643148")
    json_path = dataset_dir / "Annotations" / "coco_info.json"
    images_dir = dataset_dir / "Images"

    print(f"正在加载数据集: {json_path}")
    coco_data = load_coco_json(str(json_path))

    print(f"正在分析图像分辨率...")
    resolution_info = analyze_image_resolutions(
        coco_data['images'], str(images_dir)
    )

    print(f"正在分析每张图像的目标数量...")
    annotation_count_info = analyze_annotations_per_image(
        coco_data['images'], coco_data['annotations']
    )

    print(f"正在分析目标尺寸...")
    object_size_info = analyze_object_sizes(
        coco_data['annotations'], coco_data['images']
    )

    print_analysis_report(resolution_info, annotation_count_info, object_size_info)


if __name__ == "__main__":
    main()

