#!/bin/bash
# 训练优化脚本 - 针对小目标检测的优化配置

# 方案一：关闭 Mosaic，优化学习率（推荐）
echo "方案一：关闭 Mosaic，优化学习率"
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11s.pt \
    --epochs 200 \
    --batch 16 \
    --imgsz 1280 \
    --device 0 \
    --close-mosaic 0 \
    --mosaic 0.0 \
    --lr0 0.005 \
    --lrf 0.001 \
    --warmup-epochs 5 \
    --name pv_pile_yolo11s_opt1 \
    --cos-lr

# 方案二：使用更大的模型（如果显存足够）
# echo "方案二：使用 yolo11m"
# python src/models/trainer.py \
#     --data data/processed/dataset.yaml \
#     --model yolo11m.pt \
#     --epochs 200 \
#     --batch 12 \
#     --imgsz 1280 \
#     --device 0 \
#     --name pv_pile_yolo11m \
#     --cos-lr

# 方案三：数据增强优化
# echo "方案三：小目标优化增强"
# python src/models/trainer.py \
#     --data data/processed/dataset.yaml \
#     --model yolo11s.pt \
#     --epochs 200 \
#     --batch 16 \
#     --imgsz 1280 \
#     --device 0 \
#     --mosaic 0.3 \
#     --mixup 0.0 \
#     --copy-paste 0.0 \
#     --degrees 5.0 \
#     --translate 0.05 \
#     --name pv_pile_yolo11s_opt2 \
#     --cos-lr

