#!/bin/bash
# 优化方案一：关闭 Mosaic + 优化学习率
# 预期提升：mAP50 +3-5%, mAP50-95 +2-3%
# 使用 screen 支持断开连接后继续运行

# 训练配置
DATA_YAML="/root/pv_pile/data/processed/dataset.yaml"
MODEL="yolo11n.pt"
EPOCHS=300
BATCH=16
IMGSZ=1280
DEVICE=0
WORKERS=8
PATIENCE=100
NAME="pv_pile_yolo11n_no_mosaic_opt1"
CONDA_ENV="/root/miniconda3/envs/yolov11"
PROJECT_DIR="/root/pv_pile"

# Screen 会话名称
SESSION_NAME="yolo_opt1"

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
echo "🚀 Starting training in screen session '$SESSION_NAME'..."
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
        --close-mosaic 0 \
        --mosaic 0.0 \
        --mixup 0.0 \
        --copy-paste 0.0 \
        --lr0 0.005 \
        --lrf 0.0001 \
        --warmup-epochs 5 \
        --cos-lr \
        --name $NAME \
        --project runs/detect \
        2>&1 | tee training_opt1.log
"

sleep 2

# 检查会话是否成功创建
if screen -list | grep -q "$SESSION_NAME"; then
    echo "✅ Training started successfully in screen session!"
    echo ""
    echo "Useful commands:"
    echo "  Attach to session:    screen -r $SESSION_NAME"
    echo "  List all sessions:     screen -ls"
    echo "  Detach from session:   Ctrl+A, then D"
    echo "  Kill session:          screen -S $SESSION_NAME -X quit"
    echo "  View training log:     tail -f $PROJECT_DIR/training_opt1.log"
else
    echo "❌ Failed to start training session"
    exit 1
fi

