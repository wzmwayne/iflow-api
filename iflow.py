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


def run_cli(debug_mode=False):
    """运行命令行版本"""
    try:
        from iflow_chat import IflowChatClient
        client = IflowChatClient(model="qwen3-coder-plus")
        client.run()
    except Exception as e:
        print(f"[错误] 启动CLI版本失败: {e}")
        if debug_mode:
            import traceback
            print("\n[调试信息] 详细错误堆栈:")
            traceback.print_exc()
        sys.exit(1)


def run_gui(debug_mode=False):
    """运行图形界面版本"""
    if debug_mode:
        print("[调试] 开始初始化 GUI...")
        print(f"[调试] Python 版本: {sys.version}")
        print(f"[调试] 操作系统: {os.name}")

    try:
        if debug_mode:
            print("[调试] 导入 PyQt5 模块...")

        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont

        if debug_mode:
            print("[调试] PyQt5 模块导入成功")
            print("[调试] 准备导入 iflow_chat_gui 模块...")

        # 强制刷新输出
        sys.stdout.flush()

        from iflow_chat_gui import IflowChatGUI, get_main_font_family

        if debug_mode:
            print("[调试] iflow_chat_gui 模块导入成功")
            print("[调试] 创建 QApplication 实例...")

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        if debug_mode:
            print("[调试] 加载自定义字体...")

        # 加载自定义字体
        main_font_family, main_font_path = get_main_font_family()

        if debug_mode:
            print("[调试] 设置应用字体...")

        # 设置应用字体
        if main_font_family:
            font = QFont(main_font_family, 10)
            # 强制使用指定字体，不使用系统回退
            font.setStyleHint(QFont.AnyStyle, QFont.PreferMatch)
            if debug_mode:
                print(f"[字体] 使用自定义字体: {main_font_family}")
                if main_font_path:
                    print(f"[字体] 字体文件路径: {main_font_path}")
        else:
            font = QFont("Segoe UI", 10)
            if debug_mode:
                print("[字体] 使用默认字体: Segoe UI")

        # 设置应用字体
        app.setFont(font)

        # 强制设置字体数据库的首选字体
        from PyQt5.QtGui import QFontDatabase
        if main_font_family and debug_mode:
            # 创建字体数据库实例
            font_db = QFontDatabase()
            # 获取所有可用的字体
            all_fonts = font_db.families()
            print(f"[字体] 系统中可用的字体总数: {len(all_fonts)}")
            if main_font_family in all_fonts:
                print(f"[字体] 字体 '{main_font_family}' 在字体数据库中")
            else:
                print(f"[字体] 警告: 字体 '{main_font_family}' 不在字体数据库中")

        if debug_mode:
            # 验证字体是否设置成功
            actual_font = app.font()
            print(f"[字体] 实际应用的字体: {actual_font.family()}")
            print(f"[字体] 字体详细信息: {actual_font}")
            print(f"[字体] 字体大小: {actual_font.pointSize()}")
            print(f"[字体] 字体粗细: {actual_font.weight()}")
            print(f"[字体] 字体风格: {actual_font.style()}")
            print(f"[字体] 字体是否为自定义: {actual_font.family() == main_font_family}")
            print("[调试] 创建主窗口...")

        # 创建主窗口
        window = IflowChatGUI()

        if debug_mode:
            print("[调试] 显示主窗口...")

        window.show()

        if debug_mode:
            print("[调试] 进入主事件循环...")

        sys.exit(app.exec_())
    except Exception as e:
        print(f"[错误] 启动GUI版本失败: {e}")
        if debug_mode:
            import traceback
            print("\n[调试信息] 详细错误堆栈:")
            traceback.print_exc()
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
  %(prog)s --debug      # 启用调试模式，显示详细错误信息
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
        '--debug',
        action='store_true',
        help='启用调试模式，显示详细错误堆栈信息'
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
        if args.debug:
            print("[调试] 调试模式已启用")
        run_cli(debug_mode=args.debug)
    elif args.gui:
        # 强制GUI模式
        print("[信息] 使用图形界面模式")
        if args.debug:
            print("[调试] 调试模式已启用")
        run_gui(debug_mode=args.debug)
    else:
        # 自动选择模式
        gui_available = check_gui_available()

        if gui_available:
            print("[信息] 检测到图形界面可用，使用GUI模式")
            print("[提示] 使用 --cli 参数可强制使用命令行模式")
            if args.debug:
                print("[调试] 调试模式已启用")
            run_gui(debug_mode=args.debug)
        else:
            print("[信息] 图形界面不可用，使用命令行模式")
            print("[提示] 安装 PyQt5 可使用图形界面: pip install PyQt5 PyQtWebEngine")
            if args.debug:
                print("[调试] 调试模式已启用")
            run_cli(debug_mode=args.debug)


if __name__ == "__main__":
    main()