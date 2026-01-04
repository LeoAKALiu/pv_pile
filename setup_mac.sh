#!/bin/bash
# Mac 环境设置脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📦 Mac 环境设置${NC}"
echo ""

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  警告: 此脚本专为 macOS 设计"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建必要目录
echo -e "${YELLOW}创建目录结构...${NC}"
mkdir -p data/processed/test/images
mkdir -p runs/detect/train4/weights
mkdir -p input output
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 检查 Docker
echo ""
echo -e "${YELLOW}检查 Docker...${NC}"
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker 已安装并运行${NC}"
        USE_DOCKER=true
    else
        echo -e "${YELLOW}⚠️  Docker 已安装但未运行，请启动 Docker Desktop${NC}"
        USE_DOCKER=false
    fi
else
    echo -e "${YELLOW}⚠️  Docker 未安装${NC}"
    echo "  安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
    USE_DOCKER=false
fi

# Docker 方式
if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo -e "${YELLOW}构建 Docker 镜像...${NC}"
    read -p "是否现在构建 Docker 镜像? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker build -t pv_pile:latest .
        echo -e "${GREEN}✅ Docker 镜像构建完成${NC}"
    fi
fi

# Python 环境方式
echo ""
echo -e "${YELLOW}设置 Python 环境...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
else
    read -p "是否创建 Python 虚拟环境? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Python 环境设置完成${NC}"
    fi
fi

# 检查模型文件
echo ""
echo -e "${YELLOW}检查模型文件...${NC}"
MODEL_PATH="runs/detect/train4/weights/best.pt"
if [ -f "$MODEL_PATH" ]; then
    echo -e "${GREEN}✅ 模型文件存在: $MODEL_PATH${NC}"
else
    echo -e "${YELLOW}⚠️  模型文件不存在: $MODEL_PATH${NC}"
    echo "  请从服务器传输模型文件:"
    echo "  scp user@server:/root/pv_pile/runs/detect/train4/weights/best.pt $MODEL_PATH"
fi

# 检查数据集配置
echo ""
echo -e "${YELLOW}检查数据集配置...${NC}"
if [ -f "data/processed/dataset.yaml" ]; then
    echo -e "${GREEN}✅ 数据集配置文件存在${NC}"
else
    echo -e "${YELLOW}⚠️  数据集配置文件不存在${NC}"
    echo "  创建默认配置..."
    mkdir -p data/processed
    cat > data/processed/dataset.yaml << EOF
path: /app/data/processed
train: train/images
val: val/images
test: test/images

names:
  0: 桩基
EOF
    echo -e "${GREEN}✅ 默认配置文件已创建${NC}"
fi

# 设置脚本权限
echo ""
echo -e "${YELLOW}设置脚本权限...${NC}"
chmod +x run_inference_mac.sh 2>/dev/null || true
chmod +x setup_mac.sh 2>/dev/null || true
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 完成
echo ""
echo -e "${GREEN}🎉 环境设置完成！${NC}"
echo ""
echo "下一步:"
echo "  1. 将待推理的图像放入 input/ 目录"
echo "  2. 运行推理: ./run_inference_mac.sh input/your_image.jpg"
echo "  3. 查看结果: open output/"
echo ""
echo "详细文档: MAC_DEPLOYMENT_GUIDE.md"

