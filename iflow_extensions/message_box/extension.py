# -*- coding: utf-8 -*-
"""
信息框扩展
提供普通和高级信息框功能，让AI可以向用户展示信息
"""

import os
import sys
from typing import Dict, Callable, Tuple

# 导入父目录的基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension

# PyQt5 导入
try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QDialog, QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
except ImportError:
    pass  # CLI 模式不需要这些


class MessageBoxExtension(BaseExtension):
    """信息框扩展"""
    
    def __init__(self):
        super().__init__()
        self.name = "message_box"
        self.description = "提供普通和高级信息框功能，让AI可以向用户展示信息"
        self.version = "1.0.0"
        self.author = "wzmwayne_and_iflow_ai"
    
    def get_prompt(self) -> str:
        """获取扩展提示词"""
        prompt = """
【信息框扩展】
此扩展提供信息框功能，让AI可以向用户展示信息。

可用工具：
- @show_message(标题,内容) - 显示普通信息框（仅确定按钮）
- @show_advanced_message(标题,内容,按钮列表) - 显示高级信息框（自定义按钮）

工具参数：
1. @show_message(标题,内容)
   - 标题: 信息框的标题
   - 内容: 要显示的信息内容
   - 说明: 自动显示确定按钮，点击后关闭

2. @show_advanced_message(标题,内容,按钮列表)
   - 标题: 信息框的标题
   - 内容: 要显示的信息内容
   - 按钮列表: 用竖线|分隔的按钮文字，按顺序显示，例如: 确定|取消|重试
   - 说明: 按钮从左到右按顺序显示，用户点击后返回按钮文字

使用场景：
- 展示重要信息、提醒、警告或错误
- 需要用户选择或确认的操作
- 向用户展示多个选项供选择

示例：
- 用户说"提醒我保存文件" -> 调用 @show_message(保存提醒,请记得保存您的工作)
- 用户说"询问用户是否继续" -> 调用 @show_advanced_message(确认操作,是否继续执行此操作？,继续|取消)
- 用户说"让用户选择操作方式" -> 调用 @show_advanced_message(选择方式,请选择操作方式,方式A|方式B|方式C)
"""
        return prompt.strip()
    
    def get_tools(self) -> Dict[str, Callable]:
        """获取工具处理函数"""
        return {
            'show_message': self.show_message,
            'show_advanced_message': self.show_advanced_message,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """获取工具描述"""
        return {
            'show_message': '显示普通信息框，格式: @show_message(标题,内容)',
            'show_advanced_message': '显示高级信息框，格式: @show_advanced_message(标题,内容,按钮列表)',
        }
    
    def show_message(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        显示普通信息框

        参数:
            args: 参数字符串，格式: "标题,内容"
            confirm_callback: 确认回调函数（可选，但此处不使用）

        返回:
            (success, message)
        """
        try:
            parts = args.split(',', 1)
            if len(parts) < 2:
                return False, "参数格式错误，应为: 标题,内容"

            title = parts[0].strip()
            content = parts[1].strip()

            # GUI版本：使用 CustomMessageBox
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                from iflow_chat_gui import CustomMessageBox

                CustomMessageBox.information(None, title, content)
                return True, "用户点击了确定"

            except ImportError:
                # CLI版本：打印信息
                print(f"\n{'='*50}")
                print(f"  {title}")
                print(f"{'='*50}")
                print(f"\n{content}\n")
                try:
                    input("\n按回车继续...")
                except (EOFError, KeyboardInterrupt):
                    pass
                return True, "用户点击了确定"

        except Exception as e:
            return False, f"显示信息框失败: {str(e)}"
    
    def show_advanced_message(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        显示高级信息框（自定义按钮，样式与对话界面一致，无边框）

        参数:
            args: 参数字符串，格式: "标题,内容,按钮列表"
            confirm_callback: 确认回调函数（可选，但此处不使用）

        返回:
            (success, message)
        """
        try:
            parts = args.split(',', 2)
            if len(parts) < 2:
                return False, "参数格式错误，应为: 标题,内容,按钮列表"

            title = parts[0].strip()
            content = parts[1].strip()
            button_list = parts[2].strip() if len(parts) > 2 else '确定'

            # 解析按钮列表
            buttons = [b.strip() for b in button_list.split('|') if b.strip()]

            if not buttons:
                buttons = ['确定']

            # GUI版本：使用自定义对话框
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

                # 创建自定义对话框（无边框）
                dialog = QDialog()
                dialog.setWindowTitle(title)
                dialog.setModal(True)
                dialog.setWindowFlags(dialog.windowFlags() | Qt.FramelessWindowHint)

                # 拖动相关变量
                dialog._drag_position = None

                # 主布局
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)

                # 标题栏
                title_bar = QWidget()
                title_bar.setFixedHeight(40)
                title_bar.setStyleSheet("""
                    QWidget {
                        background-color: #202123;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                    }
                """)
                title_layout = QHBoxLayout()
                title_layout.setContentsMargins(20, 0, 20, 0)

                title_label = QLabel(title)
                title_label.setStyleSheet("""
                    QLabel {
                        color: #ECECF1;
                        font-size: 16px;
                        font-weight: bold;
                    }
                """)
                title_layout.addWidget(title_label)
                title_layout.addStretch()

                # 关闭按钮
                close_btn = QPushButton("×")
                close_btn.setFixedSize(30, 30)
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #ECECF1;
                        border: none;
                        font-size: 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #E74C3C;
                        border-radius: 15px;
                    }
                """)
                close_btn.clicked.connect(dialog.reject)
                title_layout.addWidget(close_btn)

                title_bar.setLayout(title_layout)
                layout.addWidget(title_bar)

                # 滚动区域（与对话界面一致的样式）
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QScrollArea.NoFrame)
                scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #343541;
                        border: none;
                    }
                    QScrollBar:vertical {
                        background: #2C3E50;
                        width: 8px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:vertical {
                        background: #4A90E2;
                        border-radius: 4px;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: #5DADE2;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                """)

                # 内容容器（与消息气泡一致的样式）
                container = QWidget()
                container.setStyleSheet("""
                    QWidget {
                        background-color: #343541;
                    }
                """)
                container_layout = QVBoxLayout()
                container_layout.setContentsMargins(20, 20, 20, 20)
                container_layout.setSpacing(8)

                # 标题（与对话界面角色标签一致的样式）
                title_content_label = QLabel(title)
                title_content_label.setStyleSheet("""
                    QLabel {
                        color: #10A37F;
                        font-size: 14px;
                        font-weight: 600;
                    }
                """)
                container_layout.addWidget(title_content_label)

                # 内容标签（与对话界面一致的样式）
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                content_label.setTextFormat(Qt.RichText)
                content_label.setOpenExternalLinks(True)
                content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                content_label.setStyleSheet("""
                    QLabel {
                        color: #ECECF1;
                        font-size: 15px;
                        line-height: 1.6;
                    }
                    QLabel a { color: #4A90E2; text-decoration: underline; }
                """)

                container_layout.addWidget(content_label)
                container.setLayout(container_layout)
                scroll.setWidget(container)
                layout.addWidget(scroll, 1)

                # 按钮栏容器
                btn_container = QWidget()
                btn_container.setStyleSheet("""
                    QWidget {
                        background-color: #343541;
                        border-top: 1px solid #2C3E50;
                        border-bottom-left-radius: 8px;
                        border-bottom-right-radius: 8px;
                    }
                """)
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(20, 10, 20, 20)

                # 存储用户选择的按钮
                selected_button = [None]

                for btn_text in buttons:
                    btn = QPushButton(btn_text)
                    btn.clicked.connect(lambda checked, text=btn_text: selected_button.__setitem__(0, text) or dialog.done(0))
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #10A37F;
                            color: white;
                            padding: 8px 20px;
                            border: none;
                            border-radius: 4px;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #0D8A6A;
                        }
                        QPushButton:pressed {
                            background-color: #0A7359;
                        }
                    """)
                    btn_layout.addWidget(btn)

                btn_container.setLayout(btn_layout)
                layout.addWidget(btn_container)

                # 设置整体样式
                dialog.setStyleSheet("""
                    QDialog {
                        background-color: #343541;
                        border-radius: 8px;
                    }
                """)
                dialog.setLayout(layout)

                # 设置固定大小
                screen = QApplication.desktop().screenGeometry()
                w = (screen.width() // 3) // 10 * 10
                h = (screen.height() // 3) // 10 * 10
                dialog.setFixedSize(w, h)

                # 居中显示
                dialog.move(screen.center() - dialog.rect().center())

                # 添加鼠标事件处理（拖动）
                def mouse_press(event):
                    if event.button() == Qt.LeftButton:
                        dialog._drag_position = event.globalPos() - dialog.frameGeometry().topLeft()
                        event.accept()

                def mouse_move(event):
                    if event.buttons() == Qt.LeftButton and dialog._drag_position:
                        dialog.move(event.globalPos() - dialog._drag_position)
                        event.accept()

                def mouse_release(event):
                    if event.button() == Qt.LeftButton:
                        dialog._drag_position = None
                        event.accept()

                dialog.mousePressEvent = mouse_press
                dialog.mouseMoveEvent = mouse_move
                dialog.mouseReleaseEvent = mouse_release

                # 显示对话框
                dialog.exec_()

                # 返回用户选择的按钮
                if selected_button[0]:
                    return True, f"用户点击了: {selected_button[0]}"
                else:
                    return True, "用户关闭了对话框"

            except ImportError:
                # CLI版本：打印信息并让用户选择
                print(f"\n{'='*50}")
                print(f"  {title}")
                print(f"{'='*50}")
                print(f"\n{content}\n")

                # 显示按钮选项
                for i, btn in enumerate(buttons, 1):
                    print(f"  {i}. {btn}")

                # 获取用户选择
                try:
                    choice = input(f"\n请输入选项编号 (1-{len(buttons)}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(buttons):
                        selected = buttons[int(choice) - 1]
                        return True, f"用户点击了: {selected}"
                    else:
                        return True, "用户关闭了对话框"
                except (EOFError, KeyboardInterrupt):
                    return True, "用户关闭了对话框"

        except Exception as e:
            return False, f"显示高级信息框失败: {str(e)}"


# 扩展实例
Extension = MessageBoxExtension