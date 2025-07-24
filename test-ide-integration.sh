#!/bin/bash

# 完整的IDE模块测试脚本

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

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# 启动IDE模块Docker容器
start_ide_docker() {
    info "启动IDE模块Docker容器..."
    
    if [ ! -d "$SCRIPT_DIR/backend/app/modules/ide_module_dir" ]; then
        error "未找到IDE模块目录: $SCRIPT_DIR/backend/app/modules/ide_module_dir"
        exit 1
    fi
    
    cd "$SCRIPT_DIR/backend/app/modules/ide_module_dir"
    
    if [ ! -f "docker-compose.yml" ]; then
        error "未找到docker-compose.yml文件"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    
    # 检查环境变量文件是否存在，如果不存在则从示例创建
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        info "从.env.example创建.env文件..."
        cp .env.example .env
    fi
    
    # 加载环境变量
    if [ -f ".env" ]; then
        info "加载环境变量..."
        export $(grep -v '^#' .env | xargs)
    fi
    
    # 设置代理（如果环境变量中定义了代理）
    if [ -n "$HTTPS_PROXY" ]; then
        info "设置HTTPS代理: $HTTPS_PROXY"
        export https_proxy=$HTTPS_PROXY
    fi
    
    if [ -n "$HTTP_PROXY" ]; then
        info "设置HTTP代理: $HTTP_PROXY"
        export http_proxy=$HTTP_PROXY
    fi
    
    # 检查沙箱镜像是否存在
    if ! docker images | grep -q ${SANDBOX_IMAGE:-ide-sandbox:latest}; then
        info "构建沙箱镜像..."
        cd sandbox
        if ! docker build -t ${SANDBOX_IMAGE:-ide-sandbox:latest} -f Dockerfile.sandbox .; then
            error "沙箱镜像构建失败。请检查网络连接和Docker配置。"
            cd ..
            cd "$SCRIPT_DIR"
            exit 1
        fi
        cd ..
        info "沙箱镜像构建成功"
    else
        info "沙箱镜像已存在，跳过构建。"
    fi
    
    # 启动Docker容器
    info "启动Docker容器..."
    if ! docker-compose up -d; then
        error "Docker容器启动失败。"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    
    info "Docker容器启动成功"
    cd "$SCRIPT_DIR"
}

# 启动主后端服务
start_backend() {
    info "启动主后端服务..."
    cd "$SCRIPT_DIR/backend"
    
    # 检查虚拟环境
    if [ -f "venv/bin/activate" ]; then
        info "激活虚拟环境..."
        source venv/bin/activate
    else
        warn "未找到虚拟环境，使用系统Python"
    fi
    
    # 检查依赖
    if [ ! -f "requirements.txt" ]; then
        error "未找到requirements.txt文件"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    
    # 安装依赖（如果需要）
    if ! python -c "import fastapi" &> /dev/null; then
        info "安装依赖..."
        pip install -r requirements.txt
    fi
    
    info "启动后端服务..."
    if python run.py; then
        info "后端服务启动成功"
    else
        error "后端服务启动失败"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
}

# 主函数
main() {
    info "开始测试IDE模块集成..."
    
    # 检查Docker
    check_docker
    
    # 启动IDE模块Docker容器
    start_ide_docker
    
    # 启动主后端服务
    start_backend
    
    info "所有服务启动完成！"
    echo ""
    info "访问地址：http://localhost:8000"
    info "IDE模块API测试端点：http://localhost:8000/api/module/ide_module"
}

# 执行主函数
main "$@"