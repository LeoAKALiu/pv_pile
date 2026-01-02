#!/bin/bash
# train_final_v1 实验：优化配置
# 关键优化点：
# - close_mosaic=20 (后20轮关闭Mosaic增强，提高定位精度)
# - mixup=0.1 (轻微Mixup增强，提高抗干扰能力)
# - copy-paste=0.1 (启用Copy-Paste增强)
# 使用 screen 支持断开连接后继续运行

# 训练配置
DATA_YAML="/root/pv_pile/data/processed/dataset.yaml"
MODEL="yolo11n.pt"  # 如果需要使用修改过的 yaml，改为 yaml 文件路径
EPOCHS=200
BATCH=16
IMGSZ=1280
DEVICE=0
WORKERS=8
PATIENCE=50
NAME="train_final_v1"
CONDA_ENV="/root/miniconda3/envs/yolov11"
PROJECT_DIR="/root/pv_pile"

# 数据增强参数
MOSAIC=1.0
MIXUP=0.1
COPY_PASTE=0.1
CLOSE_MOSAIC=20  # 关键：后20轮关闭Mosaic

# Screen 会话名称
SESSION_NAME="yolo_final_v1"

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
echo "🚀 Starting train_final_v1 experiment in screen session '$SESSION_NAME'..."
echo "📝 To attach: screen -r $SESSION_NAME"
echo "📝 To detach: Press Ctrl+A, then D"
echo "📝 To kill: screen -S $SESSION_NAME -X quit"
echo ""
echo "实验配置:"
echo "  - 模型: $MODEL"
echo "  - Epochs: $EPOCHS"
echo "  - Batch: $BATCH"
echo "  - Imgsz: $IMGSZ"
echo "  - Mosaic: $MOSAIC"
echo "  - Mixup: $MIXUP"
echo "  - Copy-Paste: $COPY_PASTE"
echo "  - Close Mosaic: 最后 $CLOSE_MOSAIC 轮关闭"
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
        --mosaic $MOSAIC \
        --mixup $MIXUP \
        --copy-paste $COPY_PASTE \
        --close-mosaic $CLOSE_MOSAIC \
        --name $NAME \
        --project runs/detect \
        2>&1 | tee training_final_v1.log
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
    echo "  View training log:     tail -f $PROJECT_DIR/training_final_v1.log"
else
    echo "❌ Failed to start training session"
    exit 1
fi


