# -*- coding: utf-8 -*-
"""
iFlow Chat - 心流对话客户端（统一入口）
支持命令行(CLI)和图形界面(GUI)两种模式

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

import sys
import os
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_gui_available():
    """检查GUI是否可用"""
    try:
        # 检查DISPLAY环境变量（Linux/Unix）
        if os.name != 'nt' and not os.environ.get('DISPLAY'):
            return False
        
        # 检查PyQt5是否已安装
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # 尝试创建QApplication实例，使用minimal平台避免X11依赖
        # 在测试环境中使用offscreen模式
        test_argv = sys.argv + ['-platform', 'minimal'] if os.name != 'nt' else sys.argv
        app = QApplication(test_argv)
        app.quit()
        return True
    except ImportError:
        return False
    except Exception:
        return False


def run_cli():
    """运行命令行版本"""
    try:
        from iflow_chat import IflowChatClient
        client = IflowChatClient(model="qwen3-coder-plus")
        client.run()
    except Exception as e:
        print(f"[错误] 启动CLI版本失败: {e}")
        sys.exit(1)


def run_gui():
    """运行图形界面版本"""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont
        from iflow_chat_gui import IflowChatGUI
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # 设置应用字体
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # 创建主窗口
        window = IflowChatGUI()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[错误] 启动GUI版本失败: {e}")
        print("\n请确保已安装PyQt5:")
        print("  pip install PyQt5 PyQtWebEngine")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='iFlow Chat - 心流对话客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s              # 自动选择模式（优先GUI）
  %(prog)s --cli        # 强制使用命令行模式
  %(prog)s --gui        # 强制使用图形界面模式
  %(prog)s --model gpt-4  # 指定模型
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='使用命令行模式'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='使用图形界面模式'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='qwen3-coder-plus',
        help='指定模型名称（默认: qwen3-coder-plus）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # 确定运行模式
    if args.cli and args.gui:
        print("[错误] 不能同时指定 --cli 和 --gui")
        parser.print_help()
        sys.exit(1)
    elif args.cli:
        # 强制CLI模式
        print("[信息] 使用命令行模式")
        run_cli()
    elif args.gui:
        # 强制GUI模式
        print("[信息] 使用图形界面模式")
        run_gui()
    else:
        # 自动选择模式
        gui_available = check_gui_available()
        
        if gui_available:
            print("[信息] 检测到图形界面可用，使用GUI模式")
            print("[提示] 使用 --cli 参数可强制使用命令行模式")
            run_gui()
        else:
            print("[信息] 图形界面不可用，使用命令行模式")
            print("[提示] 安装 PyQt5 可使用图形界面: pip install PyQt5 PyQtWebEngine")
            run_cli()


if __name__ == "__main__":
    main()