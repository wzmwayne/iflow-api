#!/bin/bash
# iFlow Chat CLI 启动脚本
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

# 检查并设置虚拟环境
check_venv() {
    print_info "检查虚拟环境..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_DIR="$SCRIPT_DIR/venv"
    
    # 如果虚拟环境不存在，创建它
    if [ ! -d "$VENV_DIR" ]; then
        print_info "创建虚拟环境: $VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        
        if [ $? -eq 0 ]; then
            print_success "虚拟环境创建成功"
        else
            print_warning "虚拟环境创建失败，将使用系统 Python"
            return 1
        fi
    fi
    
    # 激活虚拟环境
    if [ -f "$VENV_DIR/bin/activate" ]; then
        print_info "激活虚拟环境..."
        source "$VENV_DIR/bin/activate"
        PYTHON_CMD="python"
        print_success "虚拟环境已激活"
        return 0
    else
        print_warning "虚拟环境激活脚本不存在，重新创建虚拟环境"
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
            PYTHON_CMD="python"
            print_success "虚拟环境已重新创建并激活"
            return 0
        else
            print_warning "虚拟环境创建失败，将使用系统 Python"
            return 1
        fi
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
    
    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        print_success "所有依赖已安装"
        return 0
    fi
    
    print_warning "缺少以下依赖: ${MISSING_DEPS[*]}"
    print_info "正在安装依赖..."
    
    # 使用清华镜像源临时安装
    print_info "使用清华镜像源安装..."
    
    # 检查是否在虚拟环境中
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_info "当前不在虚拟环境中，使用 --break-system-packages 参数"
        $PYTHON_CMD -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --break-system-packages "${MISSING_DEPS[@]}"
    else
        $PYTHON_CMD -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "${MISSING_DEPS[@]}"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "依赖安装成功"
    else
        print_error "依赖安装失败，请尝试手动安装:"
        echo "  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ${MISSING_DEPS[*]}"
        exit 1
    fi
}

# 启动程序
start_program() {
    print_info "启动 iFlow Chat CLI..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MAIN_SCRIPT="$SCRIPT_DIR/iflow.py"
    
    if [ ! -f "$MAIN_SCRIPT" ]; then
        print_error "找不到 iflow.py 文件"
        exit 1
    fi
    
    # 启动程序（使用 --cli 参数强制使用CLI模式）
    cd "$SCRIPT_DIR"
    $PYTHON_CMD iflow.py --cli
}

# 主函数
main() {
    echo ""
    echo "======================================"
    echo "  iFlow Chat CLI 启动脚本"
    echo "======================================"
    echo ""
    
    detect_os
    check_python
    check_venv
    check_dependencies
    start_program
}

# 运行主函数
main