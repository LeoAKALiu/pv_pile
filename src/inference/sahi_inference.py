#!/usr/bin/env python3
"""
SAHI 推理脚本：使用 SAHI 进行切片推理。

功能：
1. 加载训练好的 YOLO 模型
2. 对输入图像/视频/目录进行切片推理
3. 合并切片结果
4. 保存推理结果（图像、JSON、统计信息）
5. 支持批量处理
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

try:
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    from sahi.utils.cv import read_image
except ImportError as e:
    print(f"Error: SAHI is not installed. Please install it with: pip install sahi")
    print(f"Original error: {e}")
    sys.exit(1)

try:
    from ultralytics import YOLO
except ImportError as e:
    print(f"Error: Ultralytics is not installed. Please install it with: pip install ultralytics")
    print(f"Original error: {e}")
    sys.exit(1)


def load_model(weights_path: str, device: str = "0", confidence_threshold: float = 0.25) -> AutoDetectionModel:
    """加载 YOLO 模型并包装为 SAHI AutoDetectionModel。

    Args:
        weights_path: 模型权重文件路径
        device: 设备 ('0', 'cpu' 等)
        confidence_threshold: 置信度阈值

    Returns:
        SAHI AutoDetectionModel 对象
    """
    weights = Path(weights_path)
    if not weights.exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")

    print(f"Loading model from: {weights_path}")
    print(f"Device: {device}, Confidence threshold: {confidence_threshold}")

    # 转换设备格式（SAHI 需要 'cuda:0' 格式）
    # 自动检测：如果没有指定或指定为数字，检查 CUDA 是否可用
    if device.isdigit():
        # 检查 CUDA 是否可用
        try:
            import torch
            if torch.cuda.is_available():
                device_str = f"cuda:{device}"
            else:
                print("⚠️  CUDA not available, falling back to CPU")
                device_str = "cpu"
        except ImportError:
            device_str = "cpu"
    elif device.lower() == "cpu":
        device_str = "cpu"
    else:
        device_str = device

    # 创建 SAHI AutoDetectionModel
    # 使用 "ultralytics" 作为 model_type，支持 YOLOv8/YOLOv11
    detection_model = AutoDetectionModel.from_pretrained(
        model_type="ultralytics",
        model_path=str(weights.absolute()),
        confidence_threshold=confidence_threshold,
        device=device_str,
    )

    return detection_model


def predict_single_image(
    image_path: Union[str, Path],
    detection_model: AutoDetectionModel,
    slice_height: int = 640,
    slice_width: int = 640,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    postprocess_type: str = "NMS",
    postprocess_match_metric: str = "IOS",
    postprocess_match_threshold: float = 0.5,
    postprocess_class_agnostic: bool = False,
) -> Tuple[np.ndarray, List]:
    """对单张图像进行切片推理。

    Args:
        image_path: 图像路径
        detection_model: SAHI 检测模型
        slice_height: 切片高度
        slice_width: 切片宽度
        overlap_height_ratio: 高度重叠比例
        overlap_width_ratio: 宽度重叠比例
        postprocess_type: 后处理类型 ('NMS', 'NMM', 'GREEDYNMM')
        postprocess_match_metric: 匹配度量 ('IOU', 'IOS')
        postprocess_match_threshold: 匹配阈值
        postprocess_class_agnostic: 是否类别无关

    Returns:
        (图像数组, 检测结果列表)
    """
    # 读取图像
    image = read_image(str(image_path))
    image_array = np.array(image)

    # 执行切片推理
    result = get_sliced_prediction(
        image=image_array,
        detection_model=detection_model,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
        postprocess_type=postprocess_type,
        postprocess_match_metric=postprocess_match_metric,
        postprocess_match_threshold=postprocess_match_threshold,
        postprocess_class_agnostic=postprocess_class_agnostic,
    )

    return image_array, result


def save_results(
    image_array: np.ndarray,
    result,
    output_path: Path,
    class_names: Optional[List[str]] = None,
    save_image: bool = True,
    save_json: bool = True,
) -> dict:
    """保存推理结果。

    Args:
        image_array: 原始图像数组
        result: SAHI PredictionResult 对象
        output_path: 输出路径（不含扩展名）
        class_names: 类别名称列表
        save_image: 是否保存标注图像
        save_json: 是否保存 JSON 结果

    Returns:
        统计信息字典
    """
    stats = {
        "total_objects": len(result.object_prediction_list),
        "class_counts": {},
    }

    # 统计类别
    for obj_pred in result.object_prediction_list:
        class_id = obj_pred.category.id
        class_name = class_names[class_id] if class_names and class_id < len(class_names) else f"class_{class_id}"
        stats["class_counts"][class_name] = stats["class_counts"].get(class_name, 0) + 1

    # 保存标注图像
    if save_image:
        result.export_visuals(export_dir=str(output_path.parent), file_name=output_path.stem)

    # 保存 JSON 结果
    if save_json:
        json_path = output_path.with_suffix(".json")
        coco_predictions = result.to_coco_predictions(image_id=0)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(coco_predictions, f, indent=2, ensure_ascii=False)
        print(f"  JSON saved: {json_path}")

    return stats


def process_image(
    image_path: Union[str, Path],
    detection_model: AutoDetectionModel,
    output_dir: Path,
    slice_height: int = 640,
    slice_width: int = 640,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    class_names: Optional[List[str]] = None,
    save_image: bool = True,
    save_json: bool = True,
) -> dict:
    """处理单张图像。

    Args:
        image_path: 图像路径
        detection_model: SAHI 检测模型
        output_dir: 输出目录
        slice_height: 切片高度
        slice_width: 切片宽度
        overlap_height_ratio: 高度重叠比例
        overlap_width_ratio: 宽度重叠比例
        class_names: 类别名称列表
        save_image: 是否保存标注图像
        save_json: 是否保存 JSON 结果

    Returns:
        统计信息字典
    """
    image_path = Path(image_path)
    print(f"Processing: {image_path.name}")

    # 执行推理
    image_array, result = predict_single_image(
        image_path,
        detection_model,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
    )

    # 保存结果
    output_path = output_dir / image_path.stem
    stats = save_results(image_array, result, output_path, class_names, save_image, save_json)

    print(f"  Detected {stats['total_objects']} objects")
    for class_name, count in stats["class_counts"].items():
        print(f"    {class_name}: {count}")

    return stats


def process_directory(
    input_dir: Union[str, Path],
    detection_model: AutoDetectionModel,
    output_dir: Path,
    slice_height: int = 640,
    slice_width: int = 640,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    class_names: Optional[List[str]] = None,
    save_image: bool = True,
    save_json: bool = True,
) -> dict:
    """批量处理目录中的图像。

    Args:
        input_dir: 输入目录
        detection_model: SAHI 检测模型
        output_dir: 输出目录
        slice_height: 切片高度
        slice_width: 切片宽度
        overlap_height_ratio: 高度重叠比例
        overlap_width_ratio: 宽度重叠比例
        class_names: 类别名称列表
        save_image: 是否保存标注图像
        save_json: 是否保存 JSON 结果

    Returns:
        总体统计信息
    """
    input_dir = Path(input_dir)
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}

    # 获取所有图像文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No images found in {input_dir}")
        return {}

    print(f"Found {len(image_files)} images")

    # 处理每张图像
    total_stats = {"total_images": len(image_files), "total_objects": 0, "class_counts": {}}

    for image_file in image_files:
        stats = process_image(
            image_file,
            detection_model,
            output_dir,
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=overlap_height_ratio,
            overlap_width_ratio=overlap_width_ratio,
            class_names=class_names,
            save_image=save_image,
            save_json=save_json,
        )

        total_stats["total_objects"] += stats["total_objects"]
        for class_name, count in stats["class_counts"].items():
            total_stats["class_counts"][class_name] = (
                total_stats["class_counts"].get(class_name, 0) + count
            )

    return total_stats


def load_class_names(yaml_path: Optional[Union[str, Path]] = None) -> Optional[List[str]]:
    """从 dataset.yaml 加载类别名称。

    Args:
        yaml_path: YAML 文件路径，如果为 None 则使用默认路径

    Returns:
        类别名称列表
    """
    if yaml_path is None:
        yaml_path = Path("/root/pv_pile/data/processed/dataset.yaml")
    else:
        yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        return None

    try:
        import yaml

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if "names" in data:
                if isinstance(data["names"], dict):
                    sorted_items = sorted(data["names"].items(), key=lambda x: int(x[0]))
                    return [name for _, name in sorted_items]
                elif isinstance(data["names"], list):
                    return data["names"]
    except Exception as e:
        print(f"Warning: Could not load class names from YAML: {e}")

    return None


def main() -> None:
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="SAHI inference for PV pile detection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 必需参数
    parser.add_argument(
        "--weights",
        type=str,
        default="/root/pv_pile/runs/detect/train4/weights/best.pt",
        help="Path to model weights file",
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to input image, video, or directory",
    )

    # 输出参数
    parser.add_argument(
        "--output-dir",
        type=str,
        default="runs/detect/predict",
        help="Output directory for results",
    )
    parser.add_argument(
        "--save-img",
        action="store_true",
        help="Save annotated images",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save results as JSON",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save any results (only display)",
    )

    # SAHI 切片参数
    parser.add_argument(
        "--slice-height",
        type=int,
        default=640,
        help="Slice height for SAHI (should match or be smaller than training slice size)",
    )
    parser.add_argument(
        "--slice-width",
        type=int,
        default=640,
        help="Slice width for SAHI",
    )
    parser.add_argument(
        "--overlap-height-ratio",
        type=float,
        default=0.2,
        help="Overlap height ratio (0.0-1.0)",
    )
    parser.add_argument(
        "--overlap-width-ratio",
        type=float,
        default=0.2,
        help="Overlap width ratio (0.0-1.0)",
    )

    # 检测参数
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="IoU threshold for NMS",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device to use ('0', 'cpu', etc.). Default: 'cpu' for CPU inference",
    )

    # 其他参数
    parser.add_argument(
        "--class-names-yaml",
        type=str,
        default=None,
        help="Path to dataset.yaml for class names",
    )
    parser.add_argument(
        "--view-img",
        action="store_true",
        help="Display results in a window",
    )

    args = parser.parse_args()

    # 确定保存选项
    save_image = args.save_img and not args.no_save
    save_json = args.save_json and not args.no_save
    if not save_image and not save_json and not args.view_img:
        save_image = True  # 默认保存图像

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载类别名称
    class_names = load_class_names(args.class_names_yaml)

    # 加载模型
    detection_model = load_model(args.weights, args.device, args.conf)

    # 处理输入
    source = Path(args.source)

    print("\n" + "=" * 80)
    print("SAHI Inference Configuration")
    print("=" * 80)
    print(f"  Model: {args.weights}")
    print(f"  Source: {source}")
    print(f"  Output: {output_dir}")
    print(f"  Slice size: {args.slice_width}×{args.slice_height}")
    print(f"  Overlap: {args.overlap_height_ratio*100:.0f}% (height), {args.overlap_width_ratio*100:.0f}% (width)")
    print(f"  Confidence: {args.conf}")
    print(f"  Device: {args.device}")
    print("=" * 80 + "\n")

    if source.is_file():
        # 单张图像
        if source.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}:
            stats = process_image(
                source,
                detection_model,
                output_dir,
                slice_height=args.slice_height,
                slice_width=args.slice_width,
                overlap_height_ratio=args.overlap_height_ratio,
                overlap_width_ratio=args.overlap_width_ratio,
                class_names=class_names,
                save_image=save_image,
                save_json=save_json,
            )
        else:
            print(f"Unsupported file type: {source.suffix}")
            sys.exit(1)
    elif source.is_dir():
        # 目录
        stats = process_directory(
            source,
            detection_model,
            output_dir,
            slice_height=args.slice_height,
            slice_width=args.slice_width,
            overlap_height_ratio=args.overlap_height_ratio,
            overlap_width_ratio=args.overlap_width_ratio,
            class_names=class_names,
            save_image=save_image,
            save_json=save_json,
        )
    else:
        print(f"Source not found: {source}")
        sys.exit(1)

    # 打印总结
    print("\n" + "=" * 80)
    print("Inference Summary")
    print("=" * 80)
    if "total_images" in stats:
        print(f"  Total images: {stats['total_images']}")
    print(f"  Total objects detected: {stats.get('total_objects', 0)}")
    if stats.get("class_counts"):
        print("  Class distribution:")
        for class_name, count in stats["class_counts"].items():
            print(f"    {class_name}: {count}")
    print(f"  Results saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()

