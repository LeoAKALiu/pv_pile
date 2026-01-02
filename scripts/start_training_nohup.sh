#!/bin/bash
# 使用 nohup 启动训练脚本，支持断开连接后继续运行

# 训练配置
DATA_YAML="/root/pv_pile/data/processed/dataset.yaml"
MODEL="yolo11s.pt"
EPOCHS=200
BATCH=32
IMGSZ=1280
DEVICE=0
WORKERS=8
PATIENCE=50
NAME="pv_pile_yolo11s"
CONDA_ENV="/root/miniconda3/envs/yolov11"
PROJECT_DIR="/root/pv_pile"

# 日志文件
LOG_FILE="$PROJECT_DIR/training.log"
PID_FILE="$PROJECT_DIR/training.pid"

# 检查是否已有训练进程
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Training process already running (PID: $OLD_PID)"
        echo "Kill it first with: kill $OLD_PID"
        exit 1
    else
        echo "Removing stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

echo "🚀 Starting training with nohup..."
echo "📝 Log file: $LOG_FILE"
echo "📝 PID file: $PID_FILE"
echo ""

cd "$PROJECT_DIR"

# 使用 nohup 启动训练
nohup bash -c "
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
        --cos-lr
" > "$LOG_FILE" 2>&1 &

# 保存进程 ID
TRAIN_PID=$!
echo $TRAIN_PID > "$PID_FILE"

sleep 2

# 检查进程是否还在运行
if ps -p "$TRAIN_PID" > /dev/null 2>&1; then
    echo "✅ Training started successfully!"
    echo "   PID: $TRAIN_PID"
    echo "   Log: $LOG_FILE"
    echo ""
    echo "Useful commands:"
    echo "  View log:              tail -f $LOG_FILE"
    echo "  Check process:         ps -p $TRAIN_PID"
    echo "  Kill training:         kill $TRAIN_PID"
    echo "  Or use PID file:       kill \$(cat $PID_FILE)"
else
    echo "❌ Failed to start training"
    echo "Check log file: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

