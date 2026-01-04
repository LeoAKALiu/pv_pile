#!/bin/bash
# Docker 快速启动脚本
# 用于快速启动和管理 PV Pile 检测系统的 Docker 容器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        echo "Mac: https://docs.docker.com/desktop/install/mac-install/"
        echo "Linux: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    
    print_success "Docker 环境检查通过"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    mkdir -p data/processed runs/detect weights input output
    print_success "目录创建完成"
}

# 构建 Docker 镜像
build_image() {
    print_info "构建 Docker 镜像..."
    docker build -t pv_pile:latest .
    print_success "镜像构建完成"
}

# 启动容器
start_container() {
    print_info "启动 Docker 容器..."
    
    # 检查是否使用 docker-compose 或 docker compose
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    $COMPOSE_CMD up -d
    print_success "容器启动完成"
    echo ""
    print_info "使用以下命令进入容器:"
    echo "  $COMPOSE_CMD exec pv_pile bash"
    echo ""
    print_info "使用以下命令查看日志:"
    echo "  $COMPOSE_CMD logs -f pv_pile"
}

# 停止容器
stop_container() {
    print_info "停止 Docker 容器..."
    
    if docker compose version &> /dev/null; then
        docker compose down
    else
        docker-compose down
    fi
    
    print_success "容器已停止"
}

# 进入容器
enter_container() {
    if docker compose version &> /dev/null; then
        docker compose exec pv_pile bash
    else
        docker-compose exec pv_pile bash
    fi
}

# 查看日志
view_logs() {
    if docker compose version &> /dev/null; then
        docker compose logs -f pv_pile
    else
        docker-compose logs -f pv_pile
    fi
}

# 运行推理示例
run_inference_example() {
    print_info "运行推理示例..."
    
    # 检查模型文件是否存在
    if [ ! -f "runs/detect/train4/weights/best.pt" ]; then
        print_warning "模型文件不存在: runs/detect/train4/weights/best.pt"
        print_info "请确保模型文件已准备好"
        return 1
    fi
    
    # 检查输入目录是否有文件
    if [ ! "$(ls -A input/ 2>/dev/null)" ]; then
        print_warning "input/ 目录为空，请先添加待检测的图像"
        return 1
    fi
    
    if docker compose version &> /dev/null; then
        docker compose exec pv_pile python src/inference/sahi_inference.py \
            --weights /app/runs/detect/train4/weights/best.pt \
            --source /app/input/ \
            --device cpu \
            --save-img \
            --save-json \
            --output-dir /app/output
    else
        docker-compose exec pv_pile python src/inference/sahi_inference.py \
            --weights /app/runs/detect/train4/weights/best.pt \
            --source /app/input/ \
            --device cpu \
            --save-img \
            --save-json \
            --output-dir /app/output
    fi
    
    print_success "推理完成，结果保存在 output/ 目录"
}

# 显示帮助信息
show_help() {
    echo "PV Pile Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build         构建 Docker 镜像"
    echo "  start         启动容器（使用 docker-compose）"
    echo "  stop          停止容器"
    echo "  restart       重启容器"
    echo "  shell         进入容器 shell"
    echo "  logs          查看容器日志"
    echo "  status        查看容器状态"
    echo "  inference     运行推理示例"
    echo "  setup         完整设置（创建目录 + 构建镜像 + 启动容器）"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup              # 首次设置"
    echo "  $0 start              # 启动容器"
    echo "  $0 shell              # 进入容器"
    echo "  $0 inference          # 运行推理"
}

# 查看容器状态
show_status() {
    print_info "容器状态:"
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
    echo ""
    print_info "镜像信息:"
    docker images | grep pv_pile || echo "未找到 pv_pile 镜像"
}

# 主函数
main() {
    case "${1:-help}" in
        build)
            check_docker
            create_directories
            build_image
            ;;
        start)
            check_docker
            create_directories
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            stop_container
            sleep 2
            start_container
            ;;
        shell)
            enter_container
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        inference)
            run_inference_example
            ;;
        setup)
            check_docker
            create_directories
            build_image
            start_container
            print_success "设置完成！"
            echo ""
            print_info "下一步:"
            echo "  1. 将模型文件放到: runs/detect/train4/weights/best.pt"
            echo "  2. 将待检测图像放到: input/ 目录"
            echo "  3. 运行: $0 shell 进入容器"
            echo "  4. 或运行: $0 inference 直接运行推理"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"

