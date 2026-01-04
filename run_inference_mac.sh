#!/bin/bash
# Mac 上的推理脚本
# 用法: ./run_inference_mac.sh <图像路径> [输出目录]

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <图像路径或目录> [输出目录]"
    echo ""
    echo "示例:"
    echo "  $0 input/image.jpg"
    echo "  $0 input/ output/my_results"
    exit 1
fi

SOURCE=$1
OUTPUT_DIR=${2:-output}

# 检查源文件/目录是否存在
if [ ! -e "$SOURCE" ]; then
    echo "❌ 错误: 源文件/目录不存在: $SOURCE"
    exit 1
fi

# 检查模型文件
MODEL_PATH="runs/detect/train4/weights/best.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ 错误: 模型文件不存在: $MODEL_PATH"
    echo "请确保模型文件已从服务器传输到本地"
    exit 1
fi

echo -e "${GREEN}🚀 开始推理...${NC}"
echo "  源文件: $SOURCE"
echo "  输出目录: $OUTPUT_DIR"
echo "  模型: $MODEL_PATH"
echo ""

# 检查是否使用 Docker
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${YELLOW}使用 Docker 运行...${NC}"
    
    # 确保输出目录存在
    mkdir -p "$OUTPUT_DIR"
    
    docker run -it --rm \
      -v "$(pwd)/runs:/app/runs" \
      -v "$(pwd)/input:/app/input" \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/data:/app/data" \
      -v "$(pwd)/$(dirname "$SOURCE"):/app/$(dirname "$SOURCE")" \
      pv_pile:latest \
      python src/inference/sahi_inference.py \
        --weights /app/runs/detect/train4/weights/best.pt \
        --source "/app/$SOURCE" \
        --device cpu \
        --slice-height 640 \
        --slice-width 640 \
        --overlap-height-ratio 0.2 \
        --overlap-width-ratio 0.2 \
        --conf 0.25 \
        --save-img \
        --save-json \
        --output-dir "/app/$OUTPUT_DIR" \
        --class-names-yaml /app/data/processed/dataset.yaml
else
    echo -e "${YELLOW}使用本地 Python 运行...${NC}"
    
    # 检查虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python src/inference/sahi_inference.py \
      --weights "$MODEL_PATH" \
      --source "$SOURCE" \
      --device cpu \
      --slice-height 640 \
      --slice-width 640 \
      --overlap-height-ratio 0.2 \
      --overlap-width-ratio 0.2 \
      --conf 0.25 \
      --save-img \
      --save-json \
      --output-dir "$OUTPUT_DIR" \
      --class-names-yaml data/processed/dataset.yaml
fi

echo ""
echo -e "${GREEN}✅ 推理完成！${NC}"
echo "  结果保存在: $OUTPUT_DIR"
echo ""
echo "查看结果:"
echo "  ls -lh $OUTPUT_DIR"
echo "  open $OUTPUT_DIR  # macOS 打开文件夹"

