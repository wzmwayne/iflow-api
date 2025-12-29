@echo off
REM iFlow Chat GUI 启动脚本 (Windows)
REM 支持 Windows 7/8/10/11

setlocal enabledelayedexpansion

echo ======================================
echo   iFlow Chat GUI 启动脚本
echo ======================================
echo.

REM 检查 Python 是否安装
echo [信息] 检查 Python 安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [成功] 找到 Python: !PYTHON_VERSION!

REM 检查依赖
echo [信息] 检查依赖...
set MISSING_DEPS=

REM 检查 requests
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    set MISSING_DEPS=!MISSING_DEPS! requests
)

REM 检查 PyQt5
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    set MISSING_DEPS=!MISSING_DEPS! PyQt5
)

REM 检查 PyQtWebEngine
python -c "import PyQtWebEngine" >nul 2>&1
if %errorlevel% neq 0 (
    set MISSING_DEPS=!MISSING_DEPS! PyQtWebEngine
)

if "!MISSING_DEPS!"=="" (
    echo [成功] 所有依赖已安装
) else (
    echo [警告] 缺少以下依赖:!MISSING_DEPS!
    echo [信息] 正在使用清华镜像源安装依赖...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple!MISSING_DEPS!
    
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请尝试手动安装:
        echo   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple!MISSING_DEPS!
        pause
        exit /b 1
    )
    echo [成功] 依赖安装成功
)

REM 启动程序
echo [信息] 启动 iFlow Chat...

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set MAIN_SCRIPT=%SCRIPT_DIR%iflow.py

if not exist "%MAIN_SCRIPT%" (
    echo [错误] 找不到 iflow.py 文件
    pause
    exit /b 1
)

REM 切换到脚本目录并启动程序（使用 --gui 参数强制使用GUI模式）
cd /d "%SCRIPT_DIR%"
python iflow.py --gui

pause