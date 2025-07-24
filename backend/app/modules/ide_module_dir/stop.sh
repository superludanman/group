#!/bin/bash

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

# 停止后端服务
stop_backend() {
    info "停止后端服务..."
    
    if [ -f .backend.pid ]; then
        PID=$(cat .backend.pid)
        if ps -p $PID > /dev/null; then
            info "停止PID为 $PID 的进程..."
            kill $PID
            sleep 2
            
            # 检查进程是否仍在运行
            if ps -p $PID > /dev/null; then
                warn "进程未响应，正在强制终止..."
                kill -9 $PID || true
            fi
            
            info "后端服务已停止。"
        else
            warn "PID文件存在，但进程 $PID 不存在。"
        fi
        
        rm -f .backend.pid
    else
        # 尝试通过进程名查找
        PIDS=$(pgrep -f "uvicorn app:app" || true)
        if [ -n "$PIDS" ]; then
            info "找到后端服务进程: $PIDS"
            for PID in $PIDS; do
                info "停止PID为 $PID 的进程..."
                kill $PID || true
            done
            
            sleep 2
            
            # 检查是否有进程仍在运行
            REMAINING=$(pgrep -f "uvicorn app:app" || true)
            if [ -n "$REMAINING" ]; then
                warn "某些进程未响应，正在强制终止..."
                for PID in $REMAINING; do
                    kill -9 $PID || true
                done
            fi
            
            info "后端服务已停止。"
        else
            warn "未找到运行中的后端服务进程。"
        fi
    fi
}

# 清理Docker容器
cleanup_containers() {
    info "清理Docker容器..."
    
    # 获取配置
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    # 查找并停止相关容器
    CONTAINERS=$(docker ps -q --filter "name=ide-sandbox-" || true)
    if [ -n "$CONTAINERS" ]; then
        info "停止并移除沙箱容器..."
        docker stop $CONTAINERS || true
        docker rm $CONTAINERS || true
        info "沙箱容器已清理。"
    else
        info "未找到运行中的沙箱容器。"
    fi
    
    # 可选：移除网络
    if [ "$1" == "--clean-all" ]; then
        NETWORK=${DOCKER_NETWORK:-ide-network}
        if docker network ls | grep -q $NETWORK; then
            info "移除Docker网络: $NETWORK..."
            docker network rm $NETWORK || warn "无法移除网络 $NETWORK，可能被其他容器使用。"
        fi
    fi
}

# 显示使用方法
show_usage() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  --help               显示此帮助信息"
    echo "  --clean-all          彻底清理（包括网络等资源）"
}

# 主函数
main() {
    # 解析命令行参数
    CLEAN_ALL=false
    
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --help)
                show_usage
                exit 0
                ;;
            --clean-all)
                CLEAN_ALL=true
                ;;
            *)
                warn "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
    
    stop_backend
    
    if $CLEAN_ALL; then
        cleanup_containers "--clean-all"
    else
        cleanup_containers
    fi
    
    info "停止脚本执行完成。"
}

# 执行主函数
main "$@"