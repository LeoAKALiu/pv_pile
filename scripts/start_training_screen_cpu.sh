#!/bin/bash
# 使用 screen 启动训练脚本（CPU 模式，用于 CUDA 兼容性问题）

# 训练配置
DATA_YAML="/root/pv_pile/data/processed/dataset.yaml"
MODEL="yolo11s.pt"
EPOCHS=200
BATCH=8  # CPU 模式使用较小的批次
IMGSZ=1280
DEVICE=cpu  # 使用 CPU
WORKERS=4  # CPU 模式使用较少的工作进程
PATIENCE=50
NAME="pv_pile_yolo11s_cpu"
CONDA_ENV="/root/miniconda3/envs/yolov11"
PROJECT_DIR="/root/pv_pile"

# Screen 会话名称
SESSION_NAME="yolo_training_cpu"

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
echo "🚀 Starting training in screen session '$SESSION_NAME' (CPU mode)..."
echo "⚠️  Note: CPU training will be much slower than GPU"
echo "📝 To attach: screen -r $SESSION_NAME"
echo "📝 To detach: Press Ctrl+A, then D"
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
        2>&1 | tee training_cpu.log
"

sleep 2

# 检查会话是否成功创建
if screen -list | grep -q "$SESSION_NAME"; then
    echo "✅ Training started successfully in screen session (CPU mode)!"
    echo ""
    echo "Useful commands:"
    echo "  Attach to session:    screen -r $SESSION_NAME"
    echo "  List all sessions:     screen -ls"
    echo "  Detach from session:   Ctrl+A, then D"
    echo "  Kill session:          screen -S $SESSION_NAME -X quit"
    echo "  View training log:     tail -f $PROJECT_DIR/training_cpu.log"
else
    echo "❌ Failed to start training session"
    exit 1
fi

