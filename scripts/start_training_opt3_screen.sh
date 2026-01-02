#!/bin/bash
# 使用 screen 启动方案三综合优化训练脚本

# 训练配置 - 方案三：综合优化
DATA_YAML="/root/pv_pile/data/processed/dataset.yaml"
MODEL="yolo11m.pt"  # 使用更大的模型
EPOCHS=250
BATCH=12  # 减小批次以适应更大的模型
IMGSZ=1280
DEVICE=0
WORKERS=8
PATIENCE=50
NAME="pv_pile_yolo11m_full_opt"
CONDA_ENV="/root/miniconda3/envs/yolov11"
PROJECT_DIR="/root/pv_pile"

# Screen 会话名称
SESSION_NAME="yolo_training_opt3"

# 检查 screen 是否已安装
if ! command -v screen &> /dev/null; then
    echo "Error: screen is not installed. Installing..."
    apt-get update && apt-get install -y screen
fi

# 检查是否已有同名会话
if screen -list | grep -q "$SESSION_NAME"; then
    echo "⚠️  Screen session '$SESSION_NAME' already exists!"
    echo "Attach to it with: screen -r $SESSION_NAME"
    echo "Or kill it first with: screen -S $SESSION_NAME -X quit"
    exit 1
fi

# 创建 screen 会话并启动训练
echo "🚀 Starting optimized training (方案三) in screen session '$SESSION_NAME'..."
echo "📝 Configuration:"
echo "   Model: $MODEL"
echo "   Epochs: $EPOCHS"
echo "   Batch: $BATCH"
echo "   Image Size: $IMGSZ"
echo "   Optimizations: No Mosaic, No Mixup, No Copy-Paste, Multi-Scale, Optimized LR"
echo ""
echo "📝 To attach: screen -r $SESSION_NAME"
echo "📝 To detach: Press Ctrl+A, then D"
echo "📝 To kill: screen -S $SESSION_NAME -X quit"
echo ""

cd "$PROJECT_DIR"

screen -dmS "$SESSION_NAME" bash -c "
    source /root/miniconda3/etc/profile.d/conda.sh && \
    conda activate $CONDA_ENV && \
    cd $PROJECT_DIR && \
    python src/models/trainer.py \
        --data $DATA_YAML \
        --model $MODEL \
        --epochs $EPOCHS \
        --batch $BATCH \
        --imgsz $IMGSZ \
        --device $DEVICE \
        --workers $WORKERS \
        --patience $PATIENCE \
        --name $NAME \
        --cos-lr \
        --close-mosaic 0 \
        --mosaic 0.0 \
        --mixup 0.0 \
        --copy-paste 0.0 \
        --lr0 0.005 \
        --lrf 0.001 \
        --warmup-epochs 5 \
        --multi-scale \
        2>&1 | tee training_opt3.log
"

sleep 2

# 检查会话是否成功创建
if screen -list | grep -q "$SESSION_NAME"; then
    echo "✅ Optimized training started successfully in screen session!"
    echo ""
    echo "Useful commands:"
    echo "  Attach to session:    screen -r $SESSION_NAME"
    echo "  List all sessions:     screen -ls"
    echo "  Detach from session:   Ctrl+A, then D"
    echo "  Kill session:          screen -S $SESSION_NAME -X quit"
    echo "  View training log:     tail -f $PROJECT_DIR/training_opt3.log"
else
    echo "❌ Failed to start training session"
    exit 1
fi

