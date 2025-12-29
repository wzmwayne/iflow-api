#!/bin/bash
# iFlow Chat 启动脚本
# 支持 Linux, macOS, Android Termux

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-android"* ]]; then
        OS="termux"
        PYTHON_CMD="python"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        PYTHON_CMD="python3"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PYTHON_CMD="python3"
    else
        OS="unknown"
        PYTHON_CMD="python"
    fi
    print_info "检测到操作系统: $OS"
}

# 检查 Python 是否安装
check_python() {
    print_info "检查 Python 安装..."
    
    if ! command -v $PYTHON_CMD &> /dev/null; then
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
            print_success "找到 Python: $(python --version)"
        else
            print_error "未找到 Python，请先安装 Python 3.8 或更高版本"
            exit 1
        fi
    else
        print_success "找到 Python: $($PYTHON_CMD --version)"
    fi
}

# 检查并安装依赖
check_dependencies() {
    print_info "检查依赖..."
    
    MISSING_DEPS=()
    
    # 检查 requests
    if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
        MISSING_DEPS+=("requests")
    fi
    
    # 检查 PyQt5
    if ! $PYTHON_CMD -c "import PyQt5" 2>/dev/null; then
        MISSING_DEPS+=("PyQt5")
    fi
    
    # 检查 PyQtWebEngine
    if ! $PYTHON_CMD -c "import PyQtWebEngine" 2>/dev/null; then
        MISSING_DEPS+=("PyQtWebEngine")
    fi
    
    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        print_success "所有依赖已安装"
        return 0
    fi
    
    print_warning "缺少以下依赖: ${MISSING_DEPS[*]}"
    print_info "正在安装依赖..."
    
    # 使用清华镜像源临时安装
    print_info "使用清华镜像源安装..."
    $PYTHON_CMD -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "${MISSING_DEPS[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "依赖安装成功"
    else
        print_error "依赖安装失败，请尝试手动安装:"
        echo "  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ${MISSING_DEPS[*]}"
        exit 1
    fi
}

# 检查并启动 X11 服务（仅 Termux）
check_x11() {
    if [ "$OS" != "termux" ]; then
        return 0
    fi
    
    print_info "检查 X11 服务..."
    
    # 检查 termux-x11 是否安装
    if ! command -v termux-x11 &> /dev/null; then
        print_warning "未安装 termux-x11，正在安装..."
        pkg install -y termux-x11
    fi
    
    # 检查 X11 服务是否运行
    if ! pgrep -f "termux-x11" > /dev/null; then
        print_info "启动 Termux X11 服务..."
        # 不使用 tcp=6000 参数，使用默认配置
        termux-x11 :0 > /dev/null 2>&1 &
        sleep 3
        
        if pgrep -f "termux-x11" > /dev/null; then
            print_success "X11 服务已启动"
        else
            print_warning "X11 服务启动失败，将尝试直接运行程序"
            print_info "如果程序无法启动，请手动运行: termux-x11 :0"
        fi
    else
        print_success "X11 服务已在运行"
    fi
    
    # 设置 DISPLAY 环境变量
    export DISPLAY=:0
    print_info "已设置 DISPLAY=:0"
    
    # 设置 XDG_RUNTIME_DIR
    export XDG_RUNTIME_DIR=/data/data/com.termux/files/usr/tmp/runtime-$(whoami)
}

# 启动程序
start_program() {
    print_info "启动 iFlow Chat..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MAIN_SCRIPT="$SCRIPT_DIR/iflow.py"
    
    if [ ! -f "$MAIN_SCRIPT" ]; then
        print_error "找不到 iflow.py 文件"
        exit 1
    fi
    
    # 启动程序（使用 --gui 参数强制使用GUI模式）
    cd "$SCRIPT_DIR"
    $PYTHON_CMD iflow.py --gui
}

# 主函数
main() {
    echo ""
    echo "======================================"
    echo "  iFlow Chat GUI 启动脚本"
    echo "======================================"
    echo ""
    
    detect_os
    check_python
    check_dependencies
    check_x11
    start_program
}

# 运行主函数
main