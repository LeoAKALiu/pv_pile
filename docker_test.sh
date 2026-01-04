#!/bin/bash
# Docker 测试脚本
# 用于快速测试 Docker 镜像是否正常工作

set -e

echo "=== PV Pile Docker 测试 ==="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"
echo ""

# 检查镜像是否存在
if ! docker images | grep -q "pv_pile"; then
    echo "📦 构建 Docker 镜像..."
    docker build -t pv_pile:latest .
    echo ""
fi

echo "✅ Docker 镜像已就绪"
echo ""

# 创建测试目录
mkdir -p input output
echo "✅ 测试目录已创建"
echo ""

# 检查模型文件是否存在
if [ ! -f "runs/detect/train4/weights/best.pt" ]; then
    echo "⚠️  警告: 模型文件不存在 (runs/detect/train4/weights/best.pt)"
    echo "   请确保模型文件已准备好"
    echo ""
fi

echo "=== 测试命令 ==="
echo ""
echo "1. 进入容器:"
echo "   docker run -it --rm \\"
echo "     -v \$(pwd)/runs:/app/runs \\"
echo "     -v \$(pwd)/input:/app/input \\"
echo "     -v \$(pwd)/output:/app/output \\"
echo "     pv_pile:latest bash"
echo ""
echo "2. 运行推理（单张图像）:"
echo "   docker run -it --rm \\"
echo "     -v \$(pwd)/runs:/app/runs \\"
echo "     -v \$(pwd)/input:/app/input \\"
echo "     -v \$(pwd)/output:/app/output \\"
echo "     pv_pile:latest \\"
echo "     python src/inference/sahi_inference.py \\"
echo "       --weights /app/runs/detect/train4/weights/best.pt \\"
echo "       --source /app/input/your_image.jpg \\"
echo "       --device cpu \\"
echo "       --save-img \\"
echo "       --save-json \\"
echo "       --output-dir /app/output"
echo ""
echo "3. 使用 docker-compose:"
echo "   docker-compose up -d"
echo "   docker-compose exec pv_pile bash"
echo ""
echo "✅ 测试脚本完成"
echo ""
echo "📖 详细文档请参考:"
echo "   - DOCKER_GUIDE.md (完整指南)"
echo "   - QUICK_DOCKER_START.md (快速开始)"

