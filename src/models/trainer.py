#!/usr/bin/env python3
"""
YOLO 模型训练脚本。

使用 Ultralytics YOLO 框架训练光伏板桩检测模型。

功能：
1. 加载预训练模型或从头训练
2. 支持多种 YOLO 模型（yolo11n/s/m/l/x）
3. 可配置的训练参数（epochs, batch, imgsz等）
4. 自动保存最佳模型和训练日志
5. 支持多 GPU 训练
6. 支持断点续训
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# 添加 ultralytics 到路径
ultralytics_path = Path(__file__).parent.parent.parent / "ultralytics"
if ultralytics_path.exists():
    sys.path.insert(0, str(ultralytics_path))

try:
    from ultralytics import YOLO
except ImportError as e:
    print(f"Error: Failed to import ultralytics. Please ensure dependencies are installed.")
    print(f"Install with: pip install ultralytics opencv-python torch torchvision")
    print(f"Original error: {e}")
    sys.exit(1)


def train_model(
    data: str,
    model: str = "yolo11n.pt",
    epochs: int = 100,
    imgsz: int = 1280,
    batch: int = 16,
    device: Optional[str] = None,
    workers: int = 8,
    project: str = "runs/detect",
    name: str = "train",
    resume: bool = False,
    amp: bool = True,
    patience: int = 50,
    save_period: int = -1,
    val: bool = True,
    plots: bool = True,
    verbose: bool = True,
    seed: int = 0,
    deterministic: bool = True,
    single_cls: bool = False,
    rect: bool = False,
    cos_lr: bool = False,
    close_mosaic: int = 10,
    resume_path: Optional[str] = None,
    **kwargs,
) -> None:
    """训练 YOLO 模型。

    Args:
        data: 数据集配置文件路径（YAML 格式）
        model: 模型文件路径或名称（如 'yolo11n.pt'）
        epochs: 训练轮数
        imgsz: 输入图像尺寸
        batch: 批次大小
        device: 设备（'0', '0,1,2,3' 或 'cpu'），None 表示自动选择
        workers: 数据加载器工作进程数
        project: 项目目录
        name: 运行名称
        resume: 是否从上次检查点继续训练
        amp: 是否使用自动混合精度
        patience: 早停耐心值（epochs）
        save_period: 每 N 个 epoch 保存一次检查点（-1 表示禁用）
        val: 是否在训练过程中进行验证
        plots: 是否生成训练曲线图
        verbose: 是否显示详细信息
        seed: 随机种子
        deterministic: 是否使用确定性算法
        single_cls: 是否将多类视为单类
        rect: 是否使用矩形训练
        cos_lr: 是否使用余弦学习率调度
        close_mosaic: 最后 N 个 epoch 关闭 Mosaic 增强
        resume_path: 恢复训练的检查点路径
        **kwargs: 其他训练参数
    """
    # 检查数据集文件
    data_path = Path(data)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset YAML file not found: {data_path}")

    # 加载模型
    print(f"Loading model: {model}")
    yolo_model = YOLO(model)

    # 准备训练参数
    train_args = {
        "data": str(data_path.absolute()),
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "workers": workers,
        "project": project,
        "name": name,
        "resume": resume,
        "amp": amp,
        "patience": patience,
        "save_period": save_period,
        "val": val,
        "plots": plots,
        "verbose": verbose,
        "seed": seed,
        "deterministic": deterministic,
        "single_cls": single_cls,
        "rect": rect,
        "cos_lr": cos_lr,
        "close_mosaic": close_mosaic,
    }

    # 添加设备参数
    if device is not None:
        train_args["device"] = device

    # 添加恢复路径
    if resume_path is not None:
        train_args["resume"] = resume_path

    # 添加其他参数
    train_args.update(kwargs)

    # 打印训练配置
    print("\n" + "=" * 80)
    print("Training Configuration:")
    print("=" * 80)
    for key, value in train_args.items():
        print(f"  {key}: {value}")
    print("=" * 80 + "\n")

    # 开始训练
    try:
        results = yolo_model.train(**train_args)
        print("\n✅ Training completed successfully!")
        print(f"Results saved to: {Path(project) / name}")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        raise


def main() -> None:
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="Train YOLO model for PV pile detection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 必需参数
    parser.add_argument(
        "--data",
        type=str,
        default="/root/pv_pile/data/processed/dataset.yaml",
        help="Path to dataset YAML file",
    )

    # 模型参数
    parser.add_argument(
        "--model",
        type=str,
        default="yolo11n.pt",
        choices=["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"],
        help="Model file or name (yolo11n/s/m/l/x)",
    )

    # 训练参数
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=1280,
        help="Input image size",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to use (e.g., '0', '0,1,2,3' or 'cpu'). None for auto",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of dataloader workers",
    )

    # 项目参数
    parser.add_argument(
        "--project",
        type=str,
        default="runs/detect",
        help="Project directory",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="train",
        help="Run name",
    )

    # 训练选项
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume training from last checkpoint",
    )
    parser.add_argument(
        "--resume-path",
        type=str,
        default=None,
        help="Path to checkpoint file to resume from",
    )
    parser.add_argument(
        "--no-amp",
        action="store_true",
        help="Disable automatic mixed precision",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=50,
        help="Early stopping patience (epochs)",
    )
    parser.add_argument(
        "--save-period",
        type=int,
        default=-1,
        help="Save checkpoint every N epochs (-1 to disable)",
    )
    parser.add_argument(
        "--no-val",
        action="store_true",
        help="Disable validation during training",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable plotting training curves",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed",
    )
    parser.add_argument(
        "--no-deterministic",
        action="store_true",
        help="Disable deterministic algorithms",
    )
    parser.add_argument(
        "--single-cls",
        action="store_true",
        help="Treat multi-class as single-class",
    )
    parser.add_argument(
        "--rect",
        action="store_true",
        help="Use rectangular training",
    )
    parser.add_argument(
        "--cos-lr",
        action="store_true",
        help="Use cosine learning rate scheduler",
    )
    parser.add_argument(
        "--close-mosaic",
        type=int,
        default=10,
        help="Disable mosaic augmentation for last N epochs",
    )

    # 数据增强参数
    parser.add_argument(
        "--mosaic",
        type=float,
        default=None,
        help="Mosaic augmentation probability (0.0-1.0)",
    )
    parser.add_argument(
        "--mixup",
        type=float,
        default=None,
        help="Mixup augmentation probability (0.0-1.0)",
    )
    parser.add_argument(
        "--copy-paste",
        type=float,
        default=None,
        help="Copy-paste augmentation probability (0.0-1.0)",
    )
    parser.add_argument(
        "--multi-scale",
        action="store_true",
        help="Enable multi-scale training",
    )
    parser.add_argument(
        "--degrees",
        type=float,
        default=None,
        help="Rotation degrees for augmentation",
    )
    parser.add_argument(
        "--translate",
        type=float,
        default=None,
        help="Translation fraction for augmentation",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Scale factor for augmentation",
    )
    parser.add_argument(
        "--hsv-h",
        type=float,
        default=None,
        help="HSV-H augmentation factor",
    )
    parser.add_argument(
        "--hsv-s",
        type=float,
        default=None,
        help="HSV-S augmentation factor",
    )
    parser.add_argument(
        "--hsv-v",
        type=float,
        default=None,
        help="HSV-V augmentation factor",
    )
    parser.add_argument(
        "--erasing",
        type=float,
        default=None,
        help="Random erasing probability",
    )

    # 学习率参数
    parser.add_argument(
        "--lr0",
        type=float,
        default=None,
        help="Initial learning rate",
    )
    parser.add_argument(
        "--lrf",
        type=float,
        default=None,
        help="Final learning rate (lr0 * lrf)",
    )
    parser.add_argument(
        "--warmup-epochs",
        type=float,
        default=None,
        help="Warmup epochs",
    )

    # 损失函数权重
    parser.add_argument(
        "--box",
        type=float,
        default=None,
        help="Box loss gain",
    )
    parser.add_argument(
        "--cls",
        type=float,
        default=None,
        help="Class loss gain",
    )
    parser.add_argument(
        "--dfl",
        type=float,
        default=None,
        help="DFL loss gain",
    )

    args = parser.parse_args()

    # 转换布尔参数
    train_kwargs = {
        "amp": not args.no_amp,
        "val": not args.no_val,
        "plots": not args.no_plots,
        "deterministic": not args.no_deterministic,
    }

    # 准备额外的训练参数
    extra_kwargs = {}
    
    # 数据增强参数
    if args.mosaic is not None:
        extra_kwargs["mosaic"] = args.mosaic
    if args.mixup is not None:
        extra_kwargs["mixup"] = args.mixup
    if args.copy_paste is not None:
        extra_kwargs["copy_paste"] = args.copy_paste
    if args.multi_scale:
        extra_kwargs["multi_scale"] = True
    if args.degrees is not None:
        extra_kwargs["degrees"] = args.degrees
    if args.translate is not None:
        extra_kwargs["translate"] = args.translate
    if args.scale is not None:
        extra_kwargs["scale"] = args.scale
    if args.hsv_h is not None:
        extra_kwargs["hsv_h"] = args.hsv_h
    if args.hsv_s is not None:
        extra_kwargs["hsv_s"] = args.hsv_s
    if args.hsv_v is not None:
        extra_kwargs["hsv_v"] = args.hsv_v
    if args.erasing is not None:
        extra_kwargs["erasing"] = args.erasing

    # 学习率参数
    if args.lr0 is not None:
        extra_kwargs["lr0"] = args.lr0
    if args.lrf is not None:
        extra_kwargs["lrf"] = args.lrf
    if args.warmup_epochs is not None:
        extra_kwargs["warmup_epochs"] = args.warmup_epochs

    # 损失函数权重
    if args.box is not None:
        extra_kwargs["box"] = args.box
    if args.cls is not None:
        extra_kwargs["cls"] = args.cls
    if args.dfl is not None:
        extra_kwargs["dfl"] = args.dfl

    # 开始训练
    train_model(
        data=args.data,
        model=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        resume=args.resume,
        resume_path=args.resume_path,
        patience=args.patience,
        save_period=args.save_period,
        seed=args.seed,
        single_cls=args.single_cls,
        rect=args.rect,
        cos_lr=args.cos_lr,
        close_mosaic=args.close_mosaic,
        **train_kwargs,
        **extra_kwargs,
    )


if __name__ == "__main__":
    main()

