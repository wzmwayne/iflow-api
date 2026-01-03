#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心流平台流式对话客户端 - GUI版本
现代化界面设计，类似ChatGPT网页版
使用PyQt5实现

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

import sys
import json
import os
import requests
import threading
import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

# PyQt5导入
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QPushButton, QLabel, QScrollArea, QFrame, QSplitter,
        QInputDialog, QMessageBox, QListWidget, QListWidgetItem, QMenu,
        QAction, QProgressBar, QStatusBar, QFileDialog, QComboBox,
        QCheckBox, QGroupBox, QLineEdit, QDialog, QDialogButtonBox,
        QTabWidget, QPlainTextEdit, QToolButton
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint
    from PyQt5.QtGui import (
        QTextCursor, QTextCharFormat, QColor, QFont, QIcon, QPalette,
        QTextDocument, QTextBlockFormat, QTextImageFormat, QCursor
    )
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("请运行: pip install PyQt5 PyQtWebEngine")
    sys.exit(1)

# 导入扩展管理器
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from iflow_extensions import extension_manager
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False
    extension_manager = None


# ============ 自定义弹窗 ============

class CustomMessageBox(QDialog):
    """自定义消息框"""

    def __init__(self, parent=None, title="", message="", buttons=QMessageBox.Ok, default_button=QMessageBox.NoButton):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        # 移除窗口边框
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # 拖动相关变量
        self._drag_position = None

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
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)

        title_bar.setLayout(title_layout)
        layout.addWidget(title_bar)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: #343541; border: none; }
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

        # 消息标签容器
        container = QWidget()
        container.setStyleSheet("background-color: #343541;")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(0)

        # 消息标签
        label = QLabel(message)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setOpenExternalLinks(True)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        label.setStyleSheet("""
            QLabel {
                color: #ECECF1;
                font-size: 14px;
                line-height: 1.8;
            }
            QLabel a { color: #4A90E2; text-decoration: underline; }
        """)

        container_layout.addWidget(label)
        container.setLayout(container_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 10, 20, 20)

        if buttons & QMessageBox.Ok:
            ok_btn = QPushButton("确定")
            ok_btn.clicked.connect(lambda: self.done(QMessageBox.Ok))
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10A37F;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #0D8A6A; }
                QPushButton:pressed { background-color: #0A7359; }
            """)
            if default_button == QMessageBox.Ok:
                ok_btn.setDefault(True)
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
        elif buttons & QMessageBox.Yes:
            yes_btn = QPushButton("确定")
            yes_btn.clicked.connect(lambda: self.done(QMessageBox.Yes))
            yes_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10A37F;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #0D8A6A; }
                QPushButton:pressed { background-color: #0A7359; }
            """)
            if default_button == QMessageBox.Yes:
                yes_btn.setDefault(True)
            btn_layout.addStretch()
            btn_layout.addWidget(yes_btn)

            no_btn = QPushButton("取消")
            no_btn.clicked.connect(lambda: self.done(QMessageBox.No))
            no_btn.setStyleSheet("""
                QPushButton {
                    background-color: #444654;
                    color: #ECECF1;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #565869; }
                QPushButton:pressed { background-color: #67677A; }
            """)
            if default_button == QMessageBox.No:
                no_btn.setDefault(True)
            btn_layout.addWidget(no_btn)

        layout.addLayout(btn_layout)

        # 设置整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #343541;
                border-radius: 8px;
            }
        """)
        self.setLayout(layout)

        # 设置固定大小为屏幕的三分之一
        screen = QApplication.desktop().screenGeometry()
        w = (screen.width() // 3) // 10 * 10
        h = (screen.height() // 3) // 10 * 10
        self.setFixedSize(w, h)

        # 居中显示
        self.move(screen.center() - self.rect().center())

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = None
            event.accept()
    
    @staticmethod
    def question(parent, title, message, buttons=QMessageBox.Yes | QMessageBox.No, default_button=QMessageBox.No):
        """显示询问对话框"""
        dialog = CustomMessageBox(parent, title, message, buttons, default_button)
        return dialog.exec_()

    @staticmethod
    def information(parent, title, message):
        """显示信息对话框"""
        dialog = CustomMessageBox(parent, title, message, QMessageBox.Ok, QMessageBox.Ok)
        return dialog.exec_()

    @staticmethod
    def warning(parent, title, message):
        """显示警告对话框"""
        dialog = CustomMessageBox(parent, title, message, QMessageBox.Ok, QMessageBox.Ok)
        return dialog.exec_()

    @staticmethod
    def critical(parent, title, message):
        """显示错误对话框"""
        dialog = CustomMessageBox(parent, title, message, QMessageBox.Ok, QMessageBox.Ok)
        return dialog.exec_()


# ============ 字体加载 ============
def load_custom_fonts():
    """加载自定义字体"""
    from PyQt5.QtGui import QFontDatabase

    main_font_family = None
    main_font_path = None  # 新增：保存字体文件路径
    genshin_fonts = {}

    try:
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

        # 加载主要中文字体
        main_font_path = os.path.join(font_dir, 'zh-cn.ttf')
        if os.path.exists(main_font_path):
            try:
                main_font_id = QFontDatabase.addApplicationFont(main_font_path)
                if main_font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(main_font_id)
                    if font_families:
                        main_font_family = font_families[0]
                        print(f"已加载主要字体: {main_font_family}")
                        print(f"字体文件 {main_font_path} 包含以下字体系列:")
                        for family in font_families:
                            print(f"  - {family}")
                    else:
                        print(f"警告: 字体文件 {main_font_path} 没有可用的字体系列")
                else:
                    print(f"警告: 无法加载字体文件 {main_font_path}")
            except Exception as e:
                print(f"警告: 加载主要字体时出错: {e}")
        else:
            print(f"警告: 字体文件不存在 {main_font_path}")

        # 加载 Genshin Impact 彩蛋字体
        genshin_font_dir = os.path.join(font_dir, 'Genshin-Impact')
        if os.path.exists(genshin_font_dir):
            for font_file in os.listdir(genshin_font_dir):
                if font_file.endswith('.ttf') or font_file.endswith('.otf'):
                    font_path = os.path.join(genshin_font_dir, font_file)
                    try:
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            font_families = QFontDatabase.applicationFontFamilies(font_id)
                            if font_families:
                                font_family = font_families[0]
                                # 使用文件名（不含扩展名）作为键
                                font_name = os.path.splitext(font_file)[0]
                                genshin_fonts[font_name] = font_family
                                print(f"已加载 Genshin 字体: {font_name} -> {font_family}")
                            else:
                                print(f"警告: 字体文件 {font_path} 没有可用的字体系列")
                        else:
                            print(f"警告: 无法加载字体文件 {font_path}")
                    except Exception as e:
                        print(f"警告: 加载 Genshin 字体 {font_file} 时出错: {e}")
        else:
            print(f"警告: Genshin 字体目录不存在 {genshin_font_dir}")

    except Exception as e:
        print(f"警告: 字体加载失败: {e}")
        print("将使用默认字体")

    return main_font_family, main_font_path, genshin_fonts


# 加载字体（延迟加载）
_MAIN_FONT_FAMILY = None
_GENSHIN_FONTS = {}
_FONTS_LOADED = False


def get_main_font_family():
    """获取主要字体系列名称"""
    global _MAIN_FONT_FAMILY, _MAIN_FONT_PATH, _FONTS_LOADED
    if not _FONTS_LOADED:
        _MAIN_FONT_FAMILY, _MAIN_FONT_PATH, _GENSHIN_FONTS = load_custom_fonts()
        _FONTS_LOADED = True
    return _MAIN_FONT_FAMILY, _MAIN_FONT_PATH


def get_genshin_fonts():
    """获取 Genshin 字体字典"""
    global _MAIN_FONT_FAMILY, _GENSHIN_FONTS, _FONTS_LOADED
    if not _FONTS_LOADED:
        _MAIN_FONT_FAMILY, _GENSHIN_FONTS = load_custom_fonts()
        _FONTS_LOADED = True
    return _GENSHIN_FONTS


# 向后兼容
MAIN_FONT_FAMILY = None
GENSHIN_FONTS = {}


# ============ 颜色主题 ============
class Theme:
    """现代深色主题 - 类似ChatGPT"""
    
    # 主背景色
    BACKGROUND = "#343541"
    SIDEBAR_BG = "#202123"
    CHAT_BG = "#343541"
    
    # 消息气泡颜色
    USER_MSG_BG = "#343541"
    ASSISTANT_MSG_BG = "#444654"
    
    # 文字颜色
    TEXT_PRIMARY = "#ECECF1"
    TEXT_SECONDARY = "#C5C5D2"
    TEXT_DIM = "#8E8EA0"
    
    # 强调色
    ACCENT = "#10a37f"
    ACCENT_HOVER = "#1a7f64"
    ACCENT_PRESSED = "#16604f"
    
    # 输入框颜色
    INPUT_BG = "#40414F"
    INPUT_TEXT = "#FFFFFF"
    INPUT_PLACEHOLDER = "#8E8EA0"
    
    # 滚动条颜色
    SCROLLBAR_BG = "#565869"
    SCROLLBAR_HANDLE = "#8E8EA0"
    
    # 边框和分隔线
    BORDER = "#4d4d4f"
    DIVIDER = "#2A2B32"
    
    # 状态颜色
    SUCCESS = "#10a37f"
    ERROR = "#ef4444"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"


# ============ 自定义组件 ============

class ModernButton(QPushButton):
    """现代化按钮"""
    
    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._setup_style()
    
    def _setup_style(self):
        if self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.ACCENT};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {Theme.ACCENT_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {Theme.ACCENT_PRESSED};
                }}
                QPushButton:disabled {{
                    background-color: {Theme.DIVIDER};
                    color: {Theme.TEXT_DIM};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Theme.TEXT_PRIMARY};
                    border: 1px solid {Theme.BORDER};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.ACCENT};
                    border-color: {Theme.ACCENT};
                }}
                QPushButton:disabled {{
                    color: {Theme.TEXT_DIM};
                    border-color: {Theme.DIVIDER};
                }}
            """)
    
    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._setup_style()


class ModernTextEdit(QTextEdit):
    """现代化文本输入框"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder
        self._setup_style()
        
        # 设置最大高度
        self.setMaximumHeight(150)
        self.setMinimumHeight(44)
        
        # 设置占位符
        self.setPlaceholderText(placeholder)
    
    def _setup_style(self):
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.INPUT_TEXT};
                border: 1px solid {Theme.BORDER};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                selection-background-color: {Theme.ACCENT};
            }}
            QTextEdit:focus {{
                border: 2px solid {Theme.ACCENT};
            }}
            QScrollBar:vertical {{
                background: {Theme.SCROLLBAR_BG};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.SCROLLBAR_HANDLE};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def keyPressEvent(self, event):
        # Ctrl+Enter 发送消息
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.parent().parent().send_message()
        else:
            super().keyPressEvent(event)


class MessageBubble(QWidget):
    """消息气泡组件"""
    
    def __init__(self, role: str, content: str, timestamp: str = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 背景颜色
        bg_color = Theme.ASSISTANT_MSG_BG if self.role == "assistant" else Theme.USER_MSG_BG
        
        # 主容器
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(8)
        
        # 头部（角色和时间）
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        role_name = "助手" if self.role == "assistant" else "你"
        role_color = Theme.ACCENT if self.role == "assistant" else Theme.TEXT_SECONDARY
        
        role_label = QLabel(role_name)
        role_label.setStyleSheet(f"""
            QLabel {{
                color: {role_color};
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_DIM};
                font-size: 12px;
            }}
        """)
        
        header_layout.addWidget(role_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        # 内容显示
        content_label = QLabel()
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.PlainText)
        content_label.setText(self.content)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        content_label.setCursor(Qt.IBeamCursor)
        
        # 获取背景色
        bg_color = Theme.ASSISTANT_MSG_BG if self.role == "assistant" else Theme.USER_MSG_BG
        
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 15px;
                line-height: 1.6;
                border: 1px solid {bg_color};
                border-radius: 4px;
                padding: 4px;
            }}
            QLabel:hover {{
                border: 1px solid {Theme.BORDER};
                background-color: {bg_color};
            }}
        """)
        
        container_layout.addLayout(header_layout)
        container_layout.addWidget(content_label)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        self.setLayout(layout)


class ChatMessageWidget(QWidget):
    """聊天消息组件（带头像）"""
    
    def __init__(self, role: str, content: str, timestamp: str = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self._setup_ui()
    
    def _setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 12, 20, 12)
        main_layout.setSpacing(12)
        
        # 头像
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        
        if self.role == "assistant":
            avatar.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #10a37f, stop:1 #1a7f64);
                    border-radius: 18px;
                }
            """)
            avatar.setText("AI")
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {Theme.ACCENT}, stop:1 {Theme.ACCENT_HOVER});
                    border-radius: 18px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
        else:
            avatar.setStyleSheet(f"""
                QLabel {{
                    background-color: {Theme.TEXT_SECONDARY};
                    border-radius: 18px;
                    color: {Theme.BACKGROUND};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
            avatar.setText("你")
            avatar.setAlignment(Qt.AlignCenter)
        
        # 消息内容
        message_widget = MessageBubble(self.role, self.content, self.timestamp)
        message_widget.setStyleSheet(f"""
            MessageBubble {{
                background-color: {Theme.ASSISTANT_MSG_BG if self.role == "assistant" else Theme.USER_MSG_BG};
            }}
        """)
        
        main_layout.addWidget(avatar)
        main_layout.addWidget(message_widget, 1)
        
        self.setLayout(main_layout)


class SidebarItem(QWidget):
    """侧边栏对话项"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, timestamp: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.timestamp = timestamp
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)
        
        # 图标
        icon_label = QLabel("💬")
        icon_label.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 16px;")
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
        """)
        title_label.setWordWrap(True)
        
        # 时间
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_DIM};
                font-size: 11px;
            }}
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label, 1)
        layout.addWidget(time_label)
        
        self.setLayout(layout)
        
        # 悬停效果
        self.setStyleSheet(f"""
            SidebarItem {{
                background-color: transparent;
                border-radius: 6px;
            }}
            SidebarItem:hover {{
                background-color: {Theme.ACCENT};
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ModernScrollArea(QScrollArea):
    """现代化滚动区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
    
    def _setup_style(self):
        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {Theme.SCROLLBAR_BG};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.SCROLLBAR_HANDLE};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)


# ============ API密钥管理 ============

class APIKeyManager:
    """管理API密钥及过期时间"""
    
    CONFIG_FILE = "iflow_config.json"
    HISTORY_DIR = "iflow_conversations"
    SCREENSHOT_DIR = "iflow_screenshots"
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.last_update: Optional[datetime] = None
        self._load_config()
        self._ensure_history_dir()
        self._ensure_screenshot_dir()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    last_update_str = config.get('last_update')
                    if last_update_str:
                        self.last_update = datetime.fromisoformat(last_update_str)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def _ensure_history_dir(self):
        """确保历史对话目录存在"""
        if not os.path.exists(self.HISTORY_DIR):
            os.makedirs(self.HISTORY_DIR)
    
    def _ensure_screenshot_dir(self):
        """确保截图目录存在"""
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR)
    
    def _save_config(self):
        """保存配置文件"""
        config = {
            'api_key': self.api_key,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        self.last_update = datetime.now()
        self._save_config()
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return self.api_key
    
    def is_expired(self) -> bool:
        """检查是否超过7天"""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update > timedelta(days=7)
    
    def get_days_remaining(self) -> int:
        """获取剩余天数"""
        if not self.last_update:
            return 0
        delta = timedelta(days=7) - (datetime.now() - self.last_update)
        return max(0, delta.days)
    
    def save_conversation(self, messages: List[dict], name: Optional[str] = None) -> str:
        """保存对话历史"""
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = os.path.join(self.HISTORY_DIR, f"{name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return filename
    
    def list_conversations(self) -> List[Tuple[str, str, str]]:
        """列出所有对话历史，返回(文件名, 显示名称, 修改时间)列表"""
        conversations = []
        if os.path.exists(self.HISTORY_DIR):
            for filename in os.listdir(self.HISTORY_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.HISTORY_DIR, filename)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    display_name = filename[:-5]  # 去掉.json
                    conversations.append((filename, display_name, mtime.strftime("%Y-%m-%d %H:%M:%S")))
        # 按修改时间倒序排列
        conversations.sort(key=lambda x: x[2], reverse=True)
        return conversations
    
    def load_conversation(self, filename: str) -> Optional[List[dict]]:
        """加载指定的对话历史"""
        filepath = os.path.join(self.HISTORY_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载对话失败: {e}")
        return None


# ============ 流式对话线程 ============

class StreamChatThread(QThread):
    """流式对话线程"""
    
    message_received = pyqtSignal(str)  # 接收到的消息片段
    chat_finished = pyqtSignal(str)  # 完整消息
    error_occurred = pyqtSignal(str)  # 错误信息
    execution_result = pyqtSignal(str)  # 指令执行结果
    
    def __init__(self, api_url: str, api_key: str, model: str, messages: List[dict]):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.stop_flag = False
        self.lock = threading.Lock()
    
    def run(self):
        """执行流式对话"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            
            response.raise_for_status()
            
            assistant_response = ""
            
            for line in response.iter_lines(decode_unicode=True):
                with self.lock:
                    if self.stop_flag:
                        break
                
                if line:
                    line_str = line.strip()
                    if line_str.startswith('data:'):
                        data_str = line_str[5:]
                        if data_str.startswith(' '):
                            data_str = data_str[1:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'delta' in choice:
                                    delta = choice['delta']
                                    content = delta.get('content', '')
                                    if content:
                                        assistant_response += content
                                        self.message_received.emit(content)
                        except json.JSONDecodeError:
                            continue
            
            if assistant_response:
                self.chat_finished.emit(assistant_response)
            
        except requests.exceptions.HTTPError as e:
            self.error_occurred.emit(f"HTTP错误: {e}")
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"请求失败: {e}")
        except Exception as e:
            self.error_occurred.emit(f"发生异常: {e}")
    
    def stop(self):
        """停止对话"""
        with self.lock:
            self.stop_flag = True


# ============ 主窗口 ============

class IflowChatGUI(QMainWindow):
    """心流聊天客户端 - GUI版本"""
    
    def __init__(self):
        super().__init__()
        
        # 核心对象
        self.model = "qwen3-coder-plus"
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.key_manager = APIKeyManager()
        self.messages: List[dict] = []
        self.debug_mode = False
        self.is_streaming = False
        self.current_conversation_name: Optional[str] = None
        self.auto_save = True
        self.ai_control_enabled = False
        self.current_action = None
        self.console_output = ""
        
        # 流式对话线程
        self.chat_thread: Optional[StreamChatThread] = None
        self.current_assistant_response = ""
        
        # 扩展管理器
        self.extensions = {}
        self.extension_tools = {}
        self.extension_prompts = ""
        
        # 调试窗口
        self.debug_window = None
        
        # 拖动相关变量
        self._drag_position = None
        
        # 重定向控制台输出
        self._redirect_stdout()
        
        # 初始化UI
        self._init_ui()
        
        # 加载扩展
        self._load_extensions()
        
        # 初始化消息
        self._init_messages()
        
        # 检查API密钥
        QTimer.singleShot(100, self._check_api_key)
    
    def _load_extensions(self):
        """加载扩展"""
        if not EXTENSIONS_AVAILABLE or extension_manager is None:
            print("扩展管理器不可用，跳过扩展加载")
            return
        
        try:
            # 加载所有扩展
            extension_manager.load_extensions()
            self.extensions = extension_manager.extensions
            
            # 收集所有扩展的工具和提示词
            for ext_name, ext in self.extensions.items():
                # 收集工具
                tools = ext.get_tools()
                for tool_name, tool_func in tools.items():
                    self.extension_tools[tool_name] = (ext, tool_func)
                
                # 收集提示词
                prompt = ext.get_prompt()
                if prompt:
                    self.extension_prompts += prompt + "\n\n"
            
            print(f"已加载 {len(self.extensions)} 个扩展")
            print(f"已加载 {len(self.extension_tools)} 个工具")
        except Exception as e:
            print(f"加载扩展失败: {e}")
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("iFlow Chat - 心流对话")
        self.setGeometry(100, 100, 1200, 800)
        
        # 移除窗口边框
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # 设置窗口样式（添加圆角）
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.BACKGROUND};
                border-radius: 12px;
            }}
        """)
        
        # 主容器（带圆角）
        main_container = QWidget()
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SIDEBAR_BG};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # 标题
        title_label = QLabel("iFlow Chat - 心流对话")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 窗口控制按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ECECF1;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3E3F4B;
                border-radius: 15px;
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)
        
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
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)
        
        # 中央部件
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧边栏
        self.sidebar = self._create_sidebar()
        splitter.addWidget(self.sidebar)
        
        # 右侧聊天区域
        self.chat_area = self._create_chat_area()
        splitter.addWidget(self.chat_area)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 900])
        
        central_layout.addWidget(splitter)
        central_widget.setLayout(central_layout)
        main_layout.addWidget(central_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {Theme.SIDEBAR_BG};
                color: {Theme.TEXT_SECONDARY};
                border-top: 1px solid {Theme.BORDER};
            }}
        """)
        self.setStatusBar(self.status_bar)
        # 设置主容器
        main_container.setStyleSheet(f"""
            QWidget#mainContainer {{
                background-color: {Theme.BACKGROUND};
                border-radius: 12px;
                border: 1px solid {Theme.BORDER};
            }}
        """)
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)
    
    def _create_sidebar(self) -> QWidget:
        """创建左侧边栏"""
        from PyQt5.QtWidgets import QSizePolicy

        sidebar = QWidget()
        sidebar.setMinimumWidth(300)
        sidebar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SIDEBAR_BG};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题
        title_widget = QWidget()
        title_widget.setFixedHeight(60)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(16, 0, 16, 0)
        
        title_label = QLabel("iFlow Chat")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 新建对话按钮
        new_chat_btn = QPushButton("+")
        new_chat_btn.setFixedSize(32, 32)
        new_chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT_HOVER};
            }}
        """)
        new_chat_btn.clicked.connect(self._new_chat)
        title_layout.addWidget(new_chat_btn)
        
        title_widget.setLayout(title_layout)
        layout.addWidget(title_widget)
        
        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {Theme.BORDER};")
        layout.addWidget(divider)
        
        # 对话历史列表
        self.history_list = ModernScrollArea()
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(8, 8, 8, 8)
        self.history_layout.setSpacing(4)
        self.history_layout.addStretch()
        self.history_content.setLayout(self.history_layout)
        self.history_list.setWidget(self.history_content)
        layout.addWidget(self.history_list)
        
        # 底部按钮区域
        bottom_widget = QWidget()
        bottom_widget.setMinimumHeight(140)
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(10, 8, 10, 12)
        bottom_layout.setSpacing(8)

        # 设置按钮
        settings_btn = ModernButton("设置", primary=False)
        settings_btn.clicked.connect(self._show_settings)
        bottom_layout.addWidget(settings_btn)

        # 扩展管理按钮
        extension_btn = ModernButton("扩展", primary=False)
        extension_btn.clicked.connect(self._show_extension_manager)
        bottom_layout.addWidget(extension_btn)

        # 帮助按钮
        help_btn = ModernButton("帮助", primary=False)
        help_btn.clicked.connect(self._show_help)
        bottom_layout.addWidget(help_btn)

        # 退出按钮
        exit_btn = ModernButton("退出", primary=False)
        exit_btn.clicked.connect(self.close)
        bottom_layout.addWidget(exit_btn)

        bottom_widget.setLayout(bottom_layout)
        layout.addWidget(bottom_widget)
        
        sidebar.setLayout(layout)
        
        # 加载对话历史
        QTimer.singleShot(200, self._load_history_list)
        
        return sidebar
    
    def _create_chat_area(self) -> QWidget:
        """创建聊天区域"""
        chat_area = QWidget()
        chat_area.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.CHAT_BG};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.CHAT_BG};
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(20, 0, 20, 0)
        
        # 模型选择
        model_label = QLabel("模型:")
        model_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px;")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen3-coder-plus", "qwen3-coder", "qwen3-plus", "qwen3"])
        self.model_combo.setCurrentText(self.model)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        self.model_combo.currentTextChanged.connect(self._change_model)
        
        toolbar_layout.addWidget(model_label)
        toolbar_layout.addWidget(self.model_combo)
        toolbar_layout.addStretch()
        
        # 调试模式开关
        self.debug_checkbox = QCheckBox("调试模式")
        self.debug_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {Theme.BORDER};
                background-color: {Theme.INPUT_BG};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.ACCENT};
                border-color: {Theme.ACCENT};
            }}
        """)
        self.debug_checkbox.stateChanged.connect(self._toggle_debug)
        toolbar_layout.addWidget(self.debug_checkbox)
        
        toolbar.setLayout(toolbar_layout)
        layout.addWidget(toolbar)
        
        # 消息显示区域
        self.messages_scroll = ModernScrollArea()
        self.messages_content = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(0, 20, 0, 20)
        self.messages_layout.setSpacing(0)
        self.messages_layout.addStretch()
        self.messages_content.setLayout(self.messages_layout)
        self.messages_scroll.setWidget(self.messages_content)
        layout.addWidget(self.messages_scroll, 1)
        
        # 输入区域
        input_container = QWidget()
        input_container.setFixedHeight(100)
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.CHAT_BG};
                border-top: 1px solid {Theme.BORDER};
            }}
        """)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(20, 12, 20, 20)
        input_layout.setSpacing(12)
        
        # 输入框
        self.input_edit = ModernTextEdit("输入消息... (Ctrl+Enter 发送)")
        self.input_edit.setMinimumHeight(60)
        self.input_edit.setMaximumHeight(76)
        input_layout.addWidget(self.input_edit, 1)
        
        # 发送按钮
        self.send_btn = ModernButton("发送", primary=True)
        self.send_btn.setFixedSize(80, 60)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        # 停止按钮
        self.stop_btn = ModernButton("停止", primary=False)
        self.stop_btn.setFixedSize(80, 60)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_streaming)
        input_layout.addWidget(self.stop_btn)
        
        input_container.setLayout(input_layout)
        layout.addWidget(input_container)
        
        chat_area.setLayout(layout)
        
        return chat_area
    
    def _init_messages(self):
        """初始化消息"""
        system_prompt = r"""请使用中文回复。不要使用任何特殊格式（如Markdown、代码块、加粗、斜体等），不要使用特殊字符。直接以纯文本形式回答问题。

重要：你有权限通过指令访问和操作用户的计算机系统！

你可以调用以下系统指令来控制程序（所有指令都需要用户确认）：
- @/debug on/off - 开启/关闭调试模式
- @/api <key> - 修改API密钥
- @/model <name> - 修改模型名称
- @/url <url> - 修改API URL
- @/history - 打开对话历史管理界面
- @/clear - 清空当前对话历史
- @/export <file> - 导出当前对话到文件
- @/import <file> - 从文件导入对话
- @/stop - 停止当前输出
- @/info - 显示当前配置信息
- @/help - 显示帮助信息
- @/exit - 退出程序

你可以调用以下工具来操作电脑（所有工具都需要用户确认）：
- @cmd(命令) - 执行系统命令，如查看文件、运行程序、获取系统信息等
- @request_control() - 请求获得电脑操作权限，获得权限后所有工具和指令自动允许

使用 @/指令名 或 @tool_name(参数) 的格式来调用，例如：
系统指令示例：
- @/debug on
- @/export my_chat.json
- @/info

@cmd 工具示例：
- @cmd(dir)
- @cmd(type iflow_chat.py)
- @cmd(wmic logicaldisk get size,freespace,caption)
- @cmd(dir c:\ /s /o:s)
- @cmd(ipconfig)
- @cmd(tasklist)
- @cmd(netstat -ano)
- @cmd(type C:\Users\wayne\Documents\test.txt)

电脑操作工具示例（需要先调用 @request_control() 获取权限）：
- @request_control()
- @mouse_move(500,300)
- @mouse_click(left)
- @keyboard(Hello World)
- @screenshot()
- @view_screenshot(screenshot_20250101_120000.png)

重要说明：
1. 所有调用默认需要用户确认后才执行
2. 指令或工具执行后，执行结果会以用户身份发送给你
3. 收到执行结果后，请继续回复，对结果进行分析或解释
4. 你可以继续调用其他指令，形成多步骤操作
5. 必须在回复的末尾使用指令，其他位置的指令不会被识别和执行
6. 每次回复只能在一个位置使用指令，即在回复的最末尾
7. 每次对话只能使用一个指令
8. @cmd 工具不需要额外权限，可以直接使用
9. 鼠标、键盘、屏幕操作需要先调用 @request_control() 获取权限
10. 当用户需要你操作电脑时，优先使用 @cmd 工具执行命令，只有在需要图形界面操作时才使用鼠标键盘工具
11. 获得电脑控制权限后，所有工具和指令将自动允许执行，无需用户确认
12. 电脑控制权限适用于需要连续执行多个指令的场景

注意：默认情况下所有调用都需要用户确认后才执行。使用 @request_control() 获取权限后，所有操作将自动允许。

当用户要求你查看文件、运行程序、获取系统信息时，请主动使用 @cmd 工具。例如：
- 用户说"帮我看看当前目录有什么文件" -> 回复后加上 @cmd(dir)
- 用户说"帮我运行xxx程序" -> 回复后加上 @cmd(xxx程序路径)
- 用户说"帮我查看系统信息" -> 回复后加上 @cmd(systeminfo)

当用户要求你进行图形界面操作（如点击按钮、输入文字、截图）时，按以下步骤进行：
1. 首先调用 @screenshot() 查看当前屏幕内容
2. 然后调用 @request_control() 获取电脑控制权限
3. 获得权限后，所有工具和指令将自动允许执行
4. 在每一步操作前，必须先调用 @screenshot() 查看当前屏幕状态
5. 依次执行控制操作（@mouse_move, @mouse_click, @keyboard 等）
6. 完成操作后，必须调用 @screenshot() 查看操作结果，确认是否成功
7. 如果需要等待界面响应，可以使用 @wait(秒数) 等待指定时间

键盘输入说明：
- 输入文本：@keyboard(Hello World) - 输入文本内容
- 特殊按键：@keyboard(key:enter) - 按Enter键
- 特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12, backspace, delete 等

示例流程：
- 用户说"帮我点击屏幕上的某个按钮" -> 先 @screenshot() 查看屏幕，然后 @request_control() 获取权限，再 @screenshot() 确认位置，最后 @mouse_move() 和 @mouse_click() 执行操作，完成后 @screenshot() 查看结果"""
        
        # 添加扩展提示词
        if self.extension_prompts:
            system_prompt += "\n\n" + self.extension_prompts
        
        self.messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    def _check_api_key(self):
        """检查API密钥"""
        api_key = self.key_manager.get_api_key()
        if not api_key or self.key_manager.is_expired():
            self._input_api_key()
        else:
            days = self.key_manager.get_days_remaining()
            if days <= 3:
                self.status_bar.showMessage(f"⚠️ API密钥将在{days}天后过期")
    
    def _input_api_key(self):
        """输入API密钥"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("设置API密钥")
        dialog.setLabelText("请输入您的API密钥:")
        dialog.setTextEchoMode(QLineEdit.Password)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
            }}
        """)
        
        if dialog.exec_() == QInputDialog.Accepted:
            api_key = dialog.textValue().strip()
            if api_key:
                self.key_manager.set_api_key(api_key)
                self.status_bar.showMessage("✓ API密钥已保存")
            else:
                self.status_bar.showMessage("❌ API密钥不能为空")
    
    def _update_status(self):
        """更新状态栏"""
        status_text = f"模型: {self.model} | "
        if self.debug_mode:
            status_text += "🔍 调试模式 | "
        if self.ai_control_enabled:
            status_text += "🤖 AI控制 | "
        
        api_key = self.key_manager.get_api_key()
        if api_key:
            days = self.key_manager.get_days_remaining()
            if self.key_manager.is_expired():
                status_text += f"⚠️ 密钥已过期 {abs(days)} 天"
            else:
                status_text += f"✓ 密钥剩余 {days} 天"
        else:
            status_text += "❌ 未设置密钥"
        
        self.status_bar.showMessage(status_text)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = None
            event.accept()
    
    def _load_history_list(self):
        """加载对话历史列表"""
        # 清空现有列表
        for i in reversed(range(self.history_layout.count() - 1)):
            item = self.history_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # 加载对话历史
        conversations = self.key_manager.list_conversations()
        for filename, name, timestamp in conversations:
            item = SidebarItem(name, timestamp)
            item.clicked.connect(lambda f=filename: self._load_conversation(f))
            self.history_layout.insertWidget(self.history_layout.count() - 1, item)
    
    def _new_chat(self):
        """新建对话"""
        self.current_conversation_name = None
        # 保留system消息
        system_msg = None
        for msg in self.messages:
            if msg['role'] == 'system':
                system_msg = msg
                break
        self.messages = [system_msg] if system_msg else []
        
        # 清空消息显示
        self._clear_messages_display()
        self.status_bar.showMessage("✓ 已创建新对话")
    
    def _clear_messages_display(self):
        """清空消息显示"""
        for i in reversed(range(self.messages_layout.count() - 1)):
            item = self.messages_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
    
    def _load_conversation(self, filename: str):
        """加载对话历史"""
        loaded = self.key_manager.load_conversation(filename)
        if loaded:
            self.messages = loaded
            self.current_conversation_name = filename.replace('.json', '')
            
            # 清空并重新显示消息
            self._clear_messages_display()
            for msg in self.messages:
                if msg['role'] in ['user', 'assistant']:
                    self._add_message_widget(msg['role'], msg['content'])
            
            self.status_bar.showMessage(f"✓ 已加载对话: {self.current_conversation_name}")
        else:
            CustomMessageBox.warning(self, "错误", "加载对话失败")
    
    def _add_message_widget(self, role: str, content: str, timestamp: str = None):
        """添加消息到界面"""
        widget = ChatMessageWidget(role, content, timestamp)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, widget)
        
        # 滚动到底部
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """发送消息"""
        if self.is_streaming:
            return
        
        user_input = self.input_edit.toPlainText().strip()
        if not user_input:
            return
        
        # 检查API密钥
        if not self.key_manager.get_api_key():
            self._input_api_key()
            return
        
        # 处理指令
        if user_input.startswith('/'):
            self._handle_command(user_input)
            self.input_edit.clear()
            return
        
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 显示用户消息
        self._add_message_widget("user", user_input)
        self.input_edit.clear()
        
        # 开始流式对话
        self._start_streaming()
    
    def _start_streaming(self):
        """开始流式对话"""
        self.is_streaming = True
        self.current_assistant_response = ""
        
        # 更新UI状态
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.input_edit.setEnabled(False)
        
        # 添加助手消息占位符
        self._add_message_widget("assistant", "")
        self.current_assistant_widget = self.messages_layout.itemAt(self.messages_layout.count() - 2).widget()
        
        # 创建并启动流式对话线程
        self.chat_thread = StreamChatThread(
            self.api_url,
            self.key_manager.get_api_key(),
            self.model,
            self.messages
        )
        self.chat_thread.message_received.connect(self._on_message_received)
        self.chat_thread.chat_finished.connect(self._on_chat_finished)
        self.chat_thread.error_occurred.connect(self._on_error)
        self.chat_thread.start()
    
    def _on_message_received(self, content: str):
        """接收到消息片段"""
        self.current_assistant_response += content
        # 更新消息显示
        if hasattr(self, 'current_assistant_widget') and self.current_assistant_widget:
            # 更新消息内容
            message_bubble = self.current_assistant_widget.findChild(MessageBubble)
            if message_bubble:
                # 获取内容标签
                content_label = message_bubble.findChild(QLabel)
                if content_label:
                    content_label.setText(self.current_assistant_response)
                    # 确保自动换行
                    content_label.setWordWrap(True)
                    # 自动滚动到底部
                    QTimer.singleShot(10, self._scroll_to_bottom)
    
    def _on_chat_finished(self, full_response: str):
        """对话完成"""
        # 保存助手回复
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })
        
        # 自动保存对话
        if self.auto_save:
            if not self.current_conversation_name:
                self.current_conversation_name = self._generate_conversation_title()
            self.key_manager.save_conversation(self.messages, self.current_conversation_name)
            self._load_history_list()
        
        # 检查AI指令
        execution_results = self._execute_ai_commands(full_response)
        if execution_results:
            # 添加执行结果作为用户消息
            self.messages.append({
                "role": "user",
                "content": f"指令执行结果：{execution_results}\n\n请根据执行结果继续回复。"
            })
            self._add_message_widget("user", f"指令执行结果：{execution_results}")
            
            # 继续对话
            QTimer.singleShot(500, self._start_streaming)
        else:
            self._end_streaming()
    
    def _on_error(self, error_msg: str):
        """发生错误"""
        self._add_message_widget("assistant", f"❌ {error_msg}")
        self._end_streaming()
    
    def _end_streaming(self):
        """结束流式对话"""
        self.is_streaming = False
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_edit.setEnabled(True)
        self.input_edit.setFocus()
        self._update_status()
    
    def _stop_streaming(self):
        """停止流式对话"""
        if self.chat_thread:
            self.chat_thread.stop()
        self._end_streaming()
    
    def _execute_ai_commands(self, response: str) -> str:
        """执行AI回复中的指令"""
        cmd_pattern = r'@/(\w+)(?:\s+(.*))?'
        tool_pattern = r'@(\w+)\((.*?)\)'
        
        cmd_matches = list(re.finditer(cmd_pattern, response))
        tool_matches = list(re.finditer(tool_pattern, response))
        
        all_matches = []
        for match in cmd_matches:
            all_matches.append((match.start(), 'cmd', match))
        for match in tool_matches:
            all_matches.append((match.start(), 'tool', match))
        
        all_matches.sort(key=lambda x: x[0])
        
        if all_matches:
            last_match = all_matches[-1]
            match_type, match_obj = last_match[1], last_match[2]
            
            if match_type == 'cmd':
                cmd = match_obj.group(1)
                args = match_obj.group(2) if match_obj.group(2) else ""
                full_cmd = f"/{cmd}"
                if args:
                    full_cmd += f" {args}"
                
                if cmd.lower() == 'exit':
                    if self._confirm_action("AI请求退出程序", "是否允许AI退出程序？"):
                        self.close()
                    return "[系统] 用户取消了退出指令"
                else:
                    if self._confirm_action(f"AI请求执行指令", f"是否允许执行指令：{full_cmd}"):
                        result = self._handle_command(full_cmd)
                        return f"[系统] 指令 {full_cmd} 执行完成"
                    else:
                        return f"[系统] 用户取消了指令 {full_cmd}"
            
            elif match_type == 'tool':
                tool_name = match_obj.group(1)
                tool_args = match_obj.group(2) if match_obj.group(2) else ""
                
                if self._confirm_action(f"AI请求调用工具", f"是否允许调用工具：{tool_name}？"):
                    success, result = self._handle_ai_tool_call(tool_name, tool_args)
                    if success:
                        return f"[工具 {tool_name} 输出]:\n{result}"
                    else:
                        return f"[工具 {tool_name}] 执行失败: {result}"
                else:
                    return f"[系统] 用户取消了工具 {tool_name}"
        
        return ""
    
    def _confirm_action(self, title: str, message: str) -> bool:
        """确认操作"""
        if self.ai_control_enabled:
            return True
        
        reply = CustomMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def _handle_command(self, cmd: str) -> bool:
        """处理指令"""
        cmd = cmd.strip()
        if not cmd.startswith('/'):
            return False
        
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == '/help':
            self._show_help()
        elif command == '/info':
            self._show_info()
        elif command == '/debug':
            if args.lower() == 'on':
                self.debug_mode = True
                self.debug_checkbox.setChecked(True)
            elif args.lower() == 'off':
                self.debug_mode = False
                self.debug_checkbox.setChecked(False)
            self._update_status()
        elif command == '/api':
            if args:
                self.key_manager.set_api_key(args.strip())
                self.status_bar.showMessage("✓ API密钥已更新")
            else:
                self._input_api_key()
        elif command == '/model':
            if args:
                self.model = args.strip()
                self.model_combo.setCurrentText(self.model)
                self._update_status()
        elif command == '/url':
            if args:
                self.api_url = args.strip()
                self.status_bar.showMessage(f"✓ API URL已设置为: {args}")
        elif command == '/history':
            # 在GUI中，历史管理通过侧边栏实现
            self.status_bar.showMessage("请使用左侧边栏管理对话历史")
        elif command == '/clear':
            self._new_chat()
        elif command == '/export':
            if args:
                self._export_history(args.strip())
            else:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "导出对话", "", "JSON Files (*.json)"
                )
                if filename:
                    self._export_history(filename)
        elif command == '/import':
            if args:
                self._import_history(args.strip())
            else:
                filename, _ = QFileDialog.getOpenFileName(
                    self, "导入对话", "", "JSON Files (*.json)"
                )
                if filename:
                    self._import_history(filename)
        elif command == '/stop':
            self._stop_streaming()
        elif command == '/exit':
            self.close()
        
        return True
    
    def _handle_ai_tool_call(self, tool_name: str, tool_args: str) -> Tuple[bool, str]:
        """处理AI工具调用"""
        if tool_name == 'cmd':
            return self._execute_command(tool_args)
        elif tool_name == 'mouse_move':
            return self._mouse_move(tool_args)
        elif tool_name == 'mouse_click':
            return self._mouse_click(tool_args)
        elif tool_name == 'keyboard':
            return self._keyboard_input(tool_args)
        elif tool_name == 'screenshot':
            return self._take_screenshot()
        elif tool_name == 'view_screenshot':
            return self._view_screenshot(tool_args)
        elif tool_name == 'wait':
            return self._wait(tool_args)
        elif tool_name == 'request_control':
            return self._request_computer_control()
        elif tool_name in self.extension_tools:
            # 处理扩展工具
            ext, tool_func = self.extension_tools[tool_name]
            confirm_callback = lambda title, message: self._confirm_action(title, message)
            try:
                return tool_func(tool_args, confirm_callback)
            except Exception as e:
                return False, f"扩展工具执行失败: {str(e)}"
        else:
            return False, f"未知工具: {tool_name}"
    
    def _execute_command(self, command: str) -> Tuple[bool, str]:
        """执行系统命令"""
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            output = result.stdout
            if result.stderr:
                output += f"\n错误: {result.stderr}"
            return True, output
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, f"执行失败: {str(e)}"
    
    def _request_computer_control(self) -> Tuple[bool, str]:
        """请求AI电脑操作权限"""
        reply = CustomMessageBox.question(
            self,
            "AI电脑操作权限请求",
            "AI请求获得电脑操作权限\n\n允许AI模拟鼠标、键盘操作\n并获取屏幕内容",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.ai_control_enabled = True
            self._update_status()
            return True, "已获得电脑操作权限"
        else:
            return False, "用户拒绝授予权限"
    
    def _mouse_move(self, args: str) -> Tuple[bool, str]:
        """移动鼠标"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        try:
            parts = args.split(',')
            if len(parts) == 2:
                x, y = int(parts[0].strip()), int(parts[1].strip())
                self.current_action = f"移动鼠标到 ({x}, {y})"
                pyautogui.moveTo(x, y, duration=0.5)
                self.current_action = None
                return True, f"鼠标已移动到 ({x}, {y})"
            else:
                return False, "参数格式错误，应为: x,y"
        except Exception as e:
            self.current_action = None
            return False, f"移动鼠标失败: {str(e)}"
    
    def _mouse_click(self, args: str) -> Tuple[bool, str]:
        """鼠标点击"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        try:
            button = args.strip() if args else 'left'
            self.current_action = f"点击鼠标 {button}"
            pyautogui.click(button=button)
            self.current_action = None
            return True, f"已点击鼠标 {button}"
        except Exception as e:
            self.current_action = None
            return False, f"鼠标点击失败: {str(e)}"
    
    def _keyboard_input(self, args: str) -> Tuple[bool, str]:
        """键盘输入
        支持两种模式：
        1. 文本输入：@keyboard(Hello World) - 输入文本
        2. 特殊按键：@keyboard(key:enter) - 按Enter键
        特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12 等
        """
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行键盘操作"
        try:
            # 检查是否是特殊按键
            if args.startswith('key:'):
                key_name = args[4:].strip().lower()
                self.current_action = f"按下按键: {key_name}"
                pyautogui.press(key_name)
                self.current_action = None
                return True, f"已按下按键: {key_name}"
            else:
                # 普通文本输入
                self.current_action = f"输入文本: {args}"
                pyautogui.typewrite(args)
                self.current_action = None
                return True, f"已输入文本: {args}"
        except Exception as e:
            self.current_action = None
            return False, f"键盘输入失败: {str(e)}"
    
    def _take_screenshot(self) -> Tuple[bool, str]:
        """获取屏幕截图"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行截图操作"
        try:
            self.current_action = "正在截图..."
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.key_manager.SCREENSHOT_DIR, filename)
            screenshot.save(filepath)
            self.current_action = None
            return True, f"屏幕截图已保存到: {filepath}\n截图尺寸: {screenshot.size}"
        except Exception as e:
            self.current_action = None
            error_msg = str(e)
            if "pyscreeze" in error_msg or "Pillow" in error_msg:
                return False, f"获取屏幕截图失败: pyautogui依赖不兼容\n建议: pip install --upgrade pillow pyscreeze pyautogui\n错误详情: {error_msg}"
            else:
                return False, f"获取屏幕截图失败: {error_msg}"
    
    def _view_screenshot(self, filename: str) -> Tuple[bool, str]:
        """查看屏幕截图（让 AI 分析截图内容）"""
        filepath = os.path.join(self.key_manager.SCREENSHOT_DIR, filename)
        if not os.path.exists(filepath):
            return False, f"截图文件不存在: {filepath}"
        
        try:
            # 读取截图并让 AI 分析
            from PIL import Image
            
            # 将截图转换为 base64
            with open(filepath, 'rb') as f:
                img_data = f.read()
            
            import base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            return True, f"[屏幕截图: {filename}]\n[图像数据: {img_base64[:500]}...]\n请分析这个截图的内容"
            
        except Exception as e:
            return False, f"读取截图失败: {str(e)}"
    
    def _wait(self, args: str) -> Tuple[bool, str]:
        """等待指定秒数"""
        try:
            seconds = float(args.strip())
            if seconds <= 0:
                return False, "等待时间必须大于0"
            
            import time
            self.current_action = f"等待 {seconds} 秒..."
            time.sleep(seconds)
            self.current_action = None
            return True, f"已等待 {seconds} 秒"
        except ValueError:
            return False, "参数格式错误，应为秒数（数字）"
        except Exception as e:
            self.current_action = None
            return False, f"等待失败: {str(e)}"
    
    def _generate_conversation_title(self) -> str:
        """生成对话标题"""
        user_messages = [m['content'] for m in self.messages if m['role'] == 'user'][:3]
        if not user_messages:
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        
        context = "\n".join([f"用户: {msg}" for msg in user_messages])
        
        headers = {
            "Authorization": f"Bearer {self.key_manager.get_api_key()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个标题生成器。根据对话内容生成一个简短的中文标题（不超过10个字），不要使用任何标点符号或特殊字符。只返回标题内容，不要其他文字。"
                },
                {
                    "role": "user",
                    "content": f"请为以下对话生成一个标题：\n\n{context}"
                }
            ],
            "stream": False,
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    title = data['choices'][0]['message']['content'].strip()
                    title = title.replace('"', "'").replace('。', '').replace('，', '')
                    if title:
                        return title
        except Exception:
            pass
        
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _change_model(self, model_name: str):
        """更改模型"""
        self.model = model_name
        self._update_status()
    
    def _toggle_debug(self, state: int):
        """切换调试模式"""
        self.debug_mode = state == Qt.Checked
        self._update_status()
    
    def _show_settings(self):
        """显示设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # API密钥
        api_label = QLabel("API密钥:")
        api_edit = QLineEdit()
        api_edit.setText(self.key_manager.get_api_key() or "")
        api_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(api_label)
        layout.addWidget(api_edit)
        
        # API URL
        url_label = QLabel("API URL:")
        url_edit = QLineEdit()
        url_edit.setText(self.api_url)
        layout.addWidget(url_label)
        layout.addWidget(url_edit)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            if api_edit.text():
                self.key_manager.set_api_key(api_edit.text())
            if url_edit.text():
                self.api_url = url_edit.text()
            self.status_bar.showMessage("✓ 设置已保存")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
        <h2>用户指令:</h2>
        <ul>
            <li>/debug on/off - 开启/关闭调试模式</li>
            <li>/api &lt;key&gt; - 修改API密钥</li>
            <li>/model &lt;name&gt; - 修改模型名称</li>
            <li>/url &lt;url&gt; - 修改API URL</li>
            <li>/history - 对话历史管理</li>
            <li>/clear - 清空当前对话历史</li>
            <li>/export &lt;file&gt; - 导出当前对话到文件</li>
            <li>/import &lt;file&gt; - 从文件导入对话</li>
            <li>/stop - 停止当前输出</li>
            <li>/info - 显示当前配置信息</li>
            <li>/help - 显示此帮助信息</li>
            <li>/exit - 退出程序</li>
        </ul>
        
        <h2>AI调用指令（需用户确认）:</h2>
        <ul>
            <li>@/debug on/off - AI可以开启/关闭调试模式</li>
            <li>@/api &lt;key&gt; - AI可以修改API密钥</li>
            <li>@/model &lt;name&gt; - AI可以修改模型名称</li>
            <li>@/url &lt;url&gt; - AI可以修改API URL</li>
            <li>@/history - AI可以打开对话历史管理</li>
            <li>@/clear - AI可以清空当前对话</li>
            <li>@/export &lt;file&gt; - AI可以导出对话</li>
            <li>@/import &lt;file&gt; - AI可以导入对话</li>
            <li>@/stop - AI可以停止输出</li>
            <li>@/info - AI可以显示配置信息</li>
            <li>@/help - AI可以显示帮助</li>
            <li>@/exit - AI可以退出程序</li>
        </ul>
        
        <h2>AI工具（需用户确认）:</h2>
        <ul>
            <li>@cmd(命令) - AI可以执行系统命令（不需要额外权限）</li>
            <li>@request_control() - AI请求获得电脑操作权限，获得后所有操作自动允许</li>
            <li>@mouse_move(x,y) - AI移动鼠标到指定坐标（需权限）</li>
            <li>@mouse_click(按钮) - AI点击鼠标（需权限）</li>
            <li>@keyboard(文本或key:按键)  - AI输入键盘文本或特殊按键（需权限）</li>
            <li>@screenshot()   - AI获取屏幕截图并保存到 iflow_screenshots 文件夹（AI可以看到）</li>
            <li>@view_screenshot(文件名) - AI分析指定截图的内容</li>
            <li>@wait(秒数)     - AI等待指定秒数</li>
            <li>@show_message(标题,内容) - AI显示普通信息框</li>
            <li>@show_advanced_message(标题,内容,类型,按钮) - AI显示高级信息框</li>
        </ul>
        
        <h2>快捷键:</h2>
        <ul>
            <li>Ctrl+Enter - 发送消息</li>
        </ul>
        
        <h2>说明:</h2>
        <ul>
            <li>获得电脑操作权限后，所有工具和指令将自动允许执行，无需用户确认</li>
            <li>键盘输入支持两种模式：文本输入(keyboard(Hello))和特殊按键(keyboard(key:enter))</li>
            <li>特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12 等</li>
        </ul>
        """
        
        msg = CustomMessageBox(self, "帮助", help_text, QMessageBox.Ok, QMessageBox.Ok)
        msg.exec_()
    
    def _show_extension_manager(self):
        """显示扩展管理对话框"""
        dialog = ExtensionManagerDialog(self, self.extensions, self.extension_tools)
        dialog.exec_()
    
    def _show_info(self):
        """显示当前配置信息"""
        info_text = f"""
        <h2>当前配置:</h2>
        <p><b>模型:</b> {self.model}</p>
        <p><b>API URL:</b> {self.api_url}</p>
        <p><b>调试模式:</b> {'开启' if self.debug_mode else '关闭'}</p>
        <p><b>AI控制:</b> {'开启' if self.ai_control_enabled else '关闭'}</p>
        <p><b>对话轮数:</b> {len([m for m in self.messages if m['role'] == 'user'])}</p>
        <p><b>API密钥状态:</b> {'已设置' if self.key_manager.get_api_key() else '未设置'}</p>
        """
        
        if self.key_manager.get_api_key():
            days = self.key_manager.get_days_remaining()
            if self.key_manager.is_expired():
                info_text += f"<p><b>密钥过期状态:</b> 已过期 {abs(days)} 天</p>"
            else:
                info_text += f"<p><b>密钥过期状态:</b> 剩余 {days} 天</p>"
        
        # 添加扩展信息
        if self.extensions:
            info_text += "<h2>已加载扩展:</h2>"
            for ext_name, ext in self.extensions.items():
                info_text += f"<p><b>{ext_name}</b> (v{ext.version})</p>"
                info_text += f"<p>&nbsp;&nbsp;描述: {ext.description}</p>"
                info_text += f"<p>&nbsp;&nbsp;作者: {ext.author}</p>"
                tools = ext.get_tools()
                info_text += f"<p>&nbsp;&nbsp;工具: {', '.join(tools.keys())}</p>"
        
        msg = CustomMessageBox(self, "配置信息", info_text, QMessageBox.Ok, QMessageBox.Ok)
        msg.exec_()
    
    def _export_history(self, filename: str):
        """导出对话历史"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            self.status_bar.showMessage(f"✓ 对话历史已导出到 {filename}")
        except Exception as e:
            CustomMessageBox.warning(self, "错误", f"导出失败: {e}")
    
    def _import_history(self, filename: str):
        """导入对话历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_messages = json.load(f)
            
            has_system = any(msg['role'] == 'system' for msg in imported_messages)
            if not has_system:
                imported_messages.insert(0, {
                    "role": "system",
                    "content": "请使用中文回复。不要使用任何特殊格式（如Markdown、代码块、加粗、斜体等），不要使用特殊字符。直接以纯文本形式回答问题。"
                })
            
            self.messages = imported_messages
            self._clear_messages_display()
            for msg in self.messages:
                if msg['role'] in ['user', 'assistant']:
                    self._add_message_widget(msg['role'], msg['content'])
            
            self.status_bar.showMessage(f"✓ 对话历史已从 {filename} 导入")
        except Exception as e:
            CustomMessageBox.warning(self, "错误", f"导入失败: {e}")
    
    def _toggle_debug(self, state: int):
        """切换调试模式"""
        self.debug_mode = state == Qt.Checked
        self._update_status()
        
        # 显示或隐藏调试窗口
        if self.debug_mode:
            self._show_debug_window()
        else:
            self._hide_debug_window()
    
    def _redirect_stdout(self):
        """重定向标准输出到调试窗口"""
        import sys
        from io import StringIO
        from datetime import datetime
        
        class DebugOutput:
            def __init__(self, parent):
                self.parent = parent
            
            def write(self, text):
                if text.strip():  # 只输出非空内容
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.parent._log_to_debug(f"{text.rstrip()}")
            
            def flush(self):
                pass
        
        # 保存原始 stdout
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        
        # 设置新的输出
        sys.stdout = DebugOutput(self)
        sys.stderr = DebugOutput(self)
    
    def _restore_stdout(self):
        """恢复标准输出"""
        import sys
        if hasattr(self, '_original_stdout'):
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
    
    def _show_debug_window(self):
        """显示调试窗口"""
        if self.debug_window is None:
            self.debug_window = DebugWindow(self)
        self.debug_window.show()
        self.debug_window.append_log("=== 调试模式已开启 ===")
    
    def _hide_debug_window(self):
        """隐藏调试窗口"""
        if self.debug_window:
            self.debug_window.hide()
    
    def _log_to_debug(self, message: str):
        """记录日志到调试窗口"""
        if self.debug_window:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_window.append_log(f"[{timestamp}] {message}")


class DebugWindow(QMainWindow):
    """调试窗口 - 显示CLI输出和原始响应"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调试窗口")
        self.setGeometry(100, 100, 800, 600)
        
        # 移除窗口边框
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # 拖动相关变量
        self._drag_position = None
        
        # 主容器
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #404040;
            }
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # 标题
        title_label = QLabel("调试窗口")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 窗口控制按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
                border-radius: 15px;
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E74C3C;
                border-radius: 15px;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)
        
        # 中央部件
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # 工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #404040;
            }
        """)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        toolbar_title = QLabel("调试输出")
        toolbar_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        toolbar_layout.addWidget(toolbar_title)
        
        toolbar_layout.addStretch()
        
        clear_btn = QPushButton("清空")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
        clear_btn.clicked.connect(self.clear_log)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar.setLayout(toolbar_layout)
        central_layout.addWidget(toolbar)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
            }
        """)
        central_layout.addWidget(self.log_text)
        
        central_widget.setLayout(central_layout)
        main_layout.addWidget(central_widget)
        
        # 设置主容器
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = None
            event.accept()
    
    def append_log(self, message: str):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        # 直接添加消息，不额外包装
        self.log_text.append(f"{message}")
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = None
            event.accept()

    def closeEvent(self, event):
        """关闭事件"""
        # 不真正关闭，只是隐藏
        event.ignore()
        self.hide()


# ============ 扩展管理对话框 ============

class ExtensionManagerDialog(QDialog):
    """扩展管理对话框"""
    
    def __init__(self, parent=None, extensions=None, extension_tools=None):
        super().__init__(parent)
        self.extensions = extensions or {}
        self.extension_tools = extension_tools or {}
        self.setWindowTitle("扩展管理")
        self.setFixedSize(800, 600)
        
        # 移除窗口边框
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # 拖动相关变量
        self._drag_position = None
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SIDEBAR_BG};
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # 标题
        title_label = QLabel("扩展管理")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}
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
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT_HOVER};
            }}
            QListWidget {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.ACCENT};
                color: white;
            }}
            QTextEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        
        self._init_ui()
        self._load_extensions()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 导入按钮
        import_btn = QPushButton("📥 导入扩展")
        import_btn.clicked.connect(self._import_extension)
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        
        # 删除按钮
        delete_btn = QPushButton("🗑️ 删除扩展")
        delete_btn.clicked.connect(self._delete_extension)
        toolbar_layout.addWidget(delete_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._load_extensions)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar.setLayout(toolbar_layout)
        layout.addWidget(toolbar)
        
        # 扩展列表
        self.extension_list = QListWidget()
        self.extension_list.itemClicked.connect(self._on_extension_selected)
        layout.addWidget(self.extension_list)
        
        # 扩展详情
        detail_label = QLabel("扩展详情")
        detail_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        layout.addWidget(self.detail_text)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        content_widget.setLayout(layout)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_position = None
            event.accept()
    
    def _load_extensions(self):
        """加载扩展列表"""
        self.extension_list.clear()
        
        if not self.extensions:
            self.extension_list.addItem("没有加载任何扩展")
            return
        
        for name, ext in self.extensions.items():
            item_text = f"{name} - {ext.description}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, name)
            self.extension_list.addItem(item)
    
    def _on_extension_selected(self, item):
        """扩展被选中"""
        ext_name = item.data(Qt.UserRole)
        ext = self.extensions.get(ext_name)
        
        if ext:
            detail = f"""
名称: {ext.name}
描述: {ext.description}
版本: {ext.version}
作者: {ext.author}

工具:
"""
            tools = ext.get_tools()
            for tool_name in tools.keys():
                detail += f"  - {tool_name}\n"
            
            self.detail_text.setText(detail)
    
    def _import_extension(self):
        """导入扩展"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择扩展文件", "", "ZIP Files (*.zip)"
        )
        
        if not filename:
            return
        
        try:
            import zipfile
            import shutil
            
            # 获取扩展目录
            extensions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "iflow_extensions")
            
            # 解压扩展
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                # 获取扩展名称（zip文件中的第一个文件夹）
                zip_ref.extractall(extensions_dir)
            
            CustomMessageBox.information(self, "成功", "扩展导入成功！\n请重启程序以加载新扩展。")
            
        except Exception as e:
            CustomMessageBox.warning(self, "错误", f"导入失败: {str(e)}")
    
    def _delete_extension(self):
        """删除扩展"""
        current_item = self.extension_list.currentItem()
        
        if not current_item:
            CustomMessageBox.warning(self, "警告", "请先选择要删除的扩展")
            return
        
        ext_name = current_item.data(Qt.UserRole)
        
        if not ext_name or ext_name == "没有加载任何扩展":
            return
        
        reply = CustomMessageBox.question(
            self,
            "确认删除",
            f"确定要删除扩展 '{ext_name}' 吗？\n\n此操作将删除扩展文件夹，无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                ext_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "iflow_extensions",
                    ext_name
                )
                
                if os.path.exists(ext_dir):
                    shutil.rmtree(ext_dir)
                    CustomMessageBox.information(self, "成功", "扩展删除成功！\n请重启程序以生效。")
                else:
                    CustomMessageBox.warning(self, "错误", "扩展目录不存在")
                    
            except Exception as e:
                CustomMessageBox.warning(self, "错误", f"删除失败: {str(e)}")


# ============ 主程序入口 ============

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 加载自定义字体
    main_font_family, main_font_path = get_main_font_family()
    genshin_fonts = get_genshin_fonts()

    # 设置应用字体
    if main_font_family:
        font = QFont(main_font_family, 10)
        print(f"使用自定义字体: {main_font_family}")
        if main_font_path:
            print(f"字体文件路径: {main_font_path}")
    else:
        font = QFont("Segoe UI", 10)
        print("使用默认字体: Segoe UI")
    app.setFont(font)

    # 验证字体是否设置成功
    actual_font = app.font()
    print(f"[字体] 实际应用的字体: {actual_font.family()}")

    # 创建主窗口
    window = IflowChatGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()