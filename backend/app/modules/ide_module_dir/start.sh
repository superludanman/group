#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 打印带颜色的消息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装和运行
check_docker() {
    info "检查Docker服务..."
    if ! command -v docker &> /dev/null; then
        error "Docker未安装。请安装Docker后再运行此脚本。"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        error "Docker服务未运行或当前用户没有权限访问Docker。"
        exit 1
    fi

    info "Docker服务正常运行。"
}

# 设置环境变量
setup_env() {
    info "设置环境变量..."
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            warn ".env文件不存在，正在从.env.example创建..."
            cp .env.example .env
        else
            error "未找到.env或.env.example文件。请创建.env文件。"
            exit 1
        fi
    fi

    # 加载环境变量
    export $(grep -v '^#' .env | xargs)
    info "环境变量已加载。"
}

# 设置代理
setup_proxy() {
    if [ -n "$HTTP_PROXY" ]; then
        info "设置HTTP代理: $HTTP_PROXY"
        export http_proxy=$HTTP_PROXY
    fi

    if [ -n "$HTTPS_PROXY" ]; then
        info "设置HTTPS代理: $HTTPS_PROXY"
        export https_proxy=$HTTPS_PROXY
    fi
}

# 构建Docker镜像
build_images() {
    info "构建Docker镜像..."
    
    # 检查沙箱镜像是否存在
    if ! docker images | grep -q ${SANDBOX_IMAGE:-ide-sandbox:latest}; then
        info "构建沙箱镜像..."
        cd sandbox
        docker build -t ${SANDBOX_IMAGE:-ide-sandbox:latest} -f Dockerfile.sandbox .
        cd ..
    else
        info "沙箱镜像已存在，跳过构建。"
    fi
}

# 保存镜像到文件
save_images() {
    local image_file="sandbox_image.tar"
    
    if [ ! -f "$image_file" ] || [ "$1" == "--force" ]; then
        info "保存沙箱镜像到文件..."
        docker save ${SANDBOX_IMAGE:-ide-sandbox:latest} -o $image_file
        info "镜像已保存到 $image_file"
    else
        info "镜像文件已存在，跳过保存。使用 --force 参数强制重新保存。"
    fi
}

# 启动后端服务
start_backend() {
    info "启动后端服务..."
    
    # 检查是否已经在运行
    if pgrep -f "uvicorn app:app" > /dev/null; then
        warn "后端服务似乎已经在运行。"
        read -p "是否要强制重启? (y/n): " restart
        if [ "$restart" != "y" ]; then
            info "保持当前服务运行。"
            return
        fi
        
        # 停止现有服务
        warn "停止现有服务..."
        pkill -f "uvicorn app:app" || true
        sleep 2
    fi
    
    # 启动服务
    info "启动服务，端口: ${PORT:-8080}..."
    if [ "${RELOAD:-False}" == "True" ]; then
        uvicorn app:app --host ${HOST:-0.0.0.0} --port ${PORT:-8080} --reload &
    else
        uvicorn app:app --host ${HOST:-0.0.0.0} --port ${PORT:-8080} &
    fi
    
    echo $! > .backend.pid
    info "后端服务已启动，PID: $(cat .backend.pid)"
}

# 显示使用方法
show_usage() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  --help               显示此帮助信息"
    echo "  --build-only         只构建Docker镜像，不启动服务"
    echo "  --save-images        保存Docker镜像到文件"
    echo "  --force-save         强制重新保存Docker镜像"
    echo "  --no-proxy           不使用代理"
}

# 主函数
main() {
    # 解析命令行参数
    BUILD_ONLY=false
    SAVE_IMAGES=false
    FORCE_SAVE=false
    USE_PROXY=true
    
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --help)
                show_usage
                exit 0
                ;;
            --build-only)
                BUILD_ONLY=true
                ;;
            --save-images)
                SAVE_IMAGES=true
                ;;
            --force-save)
                SAVE_IMAGES=true
                FORCE_SAVE=true
                ;;
            --no-proxy)
                USE_PROXY=false
                ;;
            *)
                warn "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
    
    check_docker
    setup_env
    
    if $USE_PROXY; then
        setup_proxy
    else
        info "不使用代理。"
    fi
    
    build_images
    
    if $SAVE_IMAGES; then
        if $FORCE_SAVE; then
            save_images "--force"
        else
            save_images
        fi
    fi
    
    if ! $BUILD_ONLY; then
        start_backend
    else
        info "仅构建模式，不启动后端服务。"
    fi
    
    info "启动脚本执行完成。"
}

# 执行主函数
main "$@"