# -*- coding: utf-8 -*-
"""
扩展图形化编译器
用于打包 iFlow 扩展

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime
from typing import Optional

# 尝试导入 PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
        QMessageBox, QGroupBox, QProgressBar, QStyle
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


class ExtensionPackager:
    """扩展打包器"""
    
    def __init__(self, extension_dir: str):
        self.extension_dir = extension_dir
        self.extension_name = os.path.basename(extension_dir)
    
    def pack(self, output_dir: str = None) -> str:
        """
        打包扩展为 zip 文件
        
        参数:
            output_dir: 输出目录，默认为当前目录
        
        返回:
            str: 打包文件的路径
        """
        if output_dir is None:
            output_dir = os.path.dirname(self.extension_dir)
        
        # 验证扩展目录
        if not self._validate_extension():
            raise ValueError(f"无效的扩展目录: {self.extension_dir}")
        
        # 获取扩展版本
        version = self._get_version()
        
        # 创建输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"{self.extension_name}_v{version}_{timestamp}.zip"
        )
        
        # 创建 zip 文件
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.extension_dir):
                # 跳过 __pycache__ 和 .pyc 文件
                dirs[:] = [d for d in dirs if d != '__pycache__']
                
                for file in files:
                    if file.endswith('.pyc') or file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.extension_dir)
                    zipf.write(file_path, arcname)
        
        return output_file
    
    def _validate_extension(self) -> bool:
        """验证扩展目录是否有效"""
        # 检查目录是否存在
        if not os.path.isdir(self.extension_dir):
            return False
        
        # 检查是否包含 extension.py
        extension_file = os.path.join(self.extension_dir, 'extension.py')
        if not os.path.exists(extension_file):
            return False
        
        # 检查是否定义了 Extension 变量
        try:
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            
            # 创建实例检查属性
            ext_instance = Extension()
            
            # 检查必要属性
            required_attrs = ['name', 'description', 'version', 'author']
            for attr in required_attrs:
                if not hasattr(ext_instance, attr):
                    return False
                if not getattr(ext_instance, attr):
                    return False
            
            # 检查必要方法
            required_methods = ['get_prompt', 'get_tools']
            for method in required_methods:
                if not hasattr(Extension, method):
                    return False
            
            return True
            
        except:
            return False
    
    def _get_version(self) -> str:
        """获取扩展版本"""
        try:
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            return Extension.version
        except:
            return "1.0.0"


class PackThread(QThread):
    """打包线程"""
    
    progress = pyqtSignal(str)  # 进度消息
    finished = pyqtSignal(bool, str, str)  # (成功, 消息, 输出文件)
    
    def __init__(self, extension_dir: str, output_dir: str = None):
        super().__init__()
        self.extension_dir = extension_dir
        self.output_dir = output_dir
    
    def run(self):
        """执行打包"""
        try:
            self.progress.emit("正在初始化打包器...")
            packager = ExtensionPackager(self.extension_dir)
            
            self.progress.emit("正在验证扩展...")
            if not packager._validate_extension():
                self.finished.emit(False, "扩展验证失败", "")
                return
            
            self.progress.emit("正在打包扩展...")
            output_file = packager.pack(self.output_dir)
            
            file_size = os.path.getsize(output_file)
            self.progress.emit(f"打包完成！文件大小: {file_size} 字节")
            
            self.finished.emit(True, "打包成功！", output_file)
            
        except Exception as e:
            self.finished.emit(False, f"打包失败: {str(e)}", "")


class ExtensionCompilerGUI(QMainWindow):
    """扩展编译器 GUI"""
    
    def __init__(self):
        super().__init__()
        self.extension_dir = ""
        self.pack_thread = None
        
        self._init_ui()
        self._load_last_extension()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("iFlow 扩展编译器 - by wzmwayne & iflowai")
        self.setGeometry(100, 100, 700, 600)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("iFlow 扩展编译器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 扩展目录选择组
        dir_group = QGroupBox("扩展目录")
        dir_layout = QVBoxLayout()
        
        # 路径输入
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择扩展目录...")
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_extension)
        path_layout.addWidget(browse_btn)
        
        dir_layout.addLayout(path_layout)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # 扩展信息组
        info_group = QGroupBox("扩展信息")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("选择扩展目录后显示扩展信息...")
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 打包操作组
        action_group = QGroupBox("打包操作")
        action_layout = QVBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        action_layout.addWidget(self.progress_bar)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.pack_btn = QPushButton("📦 打包扩展")
        self.pack_btn.clicked.connect(self._pack_extension)
        self.pack_btn.setEnabled(False)
        button_layout.addWidget(self.pack_btn)
        
        self.open_btn = QPushButton("📁 打开输出目录")
        self.open_btn.clicked.connect(self._open_output_dir)
        self.open_btn.setEnabled(False)
        button_layout.addWidget(self.open_btn)
        
        action_layout.addLayout(button_layout)
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # 日志输出组
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("打包日志将显示在这里...")
        log_layout.addWidget(self.log_text)
        
        # 清空日志按钮
        clear_log_layout = QHBoxLayout()
        clear_log_layout.addStretch()
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.setFixedWidth(100)
        clear_log_btn.clicked.connect(self._clear_log)
        clear_log_layout.addWidget(clear_log_btn)
        
        log_layout.addLayout(clear_log_layout)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        central_widget.setLayout(layout)
    
    def _browse_extension(self):
        """浏览扩展目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择扩展目录", self.extension_dir or ""
        )
        
        if directory:
            self.path_edit.setText(directory)
            self.extension_dir = directory
            self._validate_and_show_info()
            self._save_last_extension(directory)
    
    def _validate_and_show_info(self):
        """验证扩展并显示信息"""
        if not self.extension_dir:
            return
        
        try:
            packager = ExtensionPackager(self.extension_dir)
            
            if not packager._validate_extension():
                self.info_text.setText("❌ 无效的扩展目录\n\n请确保目录包含 extension.py 文件，并且定义了 Extension 类。")
                self.pack_btn.setEnabled(False)
                return
            
            # 获取扩展信息
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            
            ext_instance = Extension()
            
            # 显示扩展信息
            info = f"""✅ 扩展验证成功

名称: {ext_instance.name}
描述: {ext_instance.description}
版本: {ext_instance.version}
作者: {ext_instance.author}

工具: {', '.join(ext_instance.get_tools().keys())}"""
            
            self.info_text.setText(info)
            self.pack_btn.setEnabled(True)
            
        except Exception as e:
            self.info_text.setText(f"❌ 验证失败: {str(e)}")
            self.pack_btn.setEnabled(False)
    
    def _pack_extension(self):
        """打包扩展"""
        if not self.extension_dir:
            QMessageBox.warning(self, "警告", "请先选择扩展目录")
            return
        
        # 禁用按钮
        self.pack_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setValue(0)
        
        # 清空日志
        self.log_text.clear()
        
        # 创建并启动打包线程
        self.pack_thread = PackThread(self.extension_dir)
        self.pack_thread.progress.connect(self._on_pack_progress)
        self.pack_thread.finished.connect(self._on_pack_finished)
        self.pack_thread.start()
    
    def _on_pack_progress(self, message: str):
        """打包进度更新"""
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _on_pack_finished(self, success: bool, message: str, output_file: str):
        """打包完成"""
        self.progress_bar.setVisible(False)
        self.pack_btn.setEnabled(True)
        
        if success:
            self.log_text.append(f"\n✅ {message}")
            self.log_text.append(f"输出文件: {output_file}")
            self.open_btn.setEnabled(True)
            self.output_file = output_file
            
            QMessageBox.information(
                self, "成功",
                f"扩展打包成功！\n\n输出文件:\n{output_file}"
            )
        else:
            self.log_text.append(f"\n❌ {message}")
            QMessageBox.critical(self, "失败", message)
    
    def _open_output_dir(self):
        """打开输出目录"""
        if hasattr(self, 'output_file') and os.path.exists(self.output_file):
            output_dir = os.path.dirname(self.output_file)
            
            # 根据操作系统打开目录
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.startfile(output_dir)
            elif system == "Darwin":  # macOS
                import subprocess
                subprocess.run(["open", output_dir])
            else:  # Linux
                import subprocess
                subprocess.run(["xdg-open", output_dir])
        else:
            QMessageBox.warning(self, "警告", "输出文件不存在")
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def _load_last_extension(self):
        """加载上次使用的扩展目录"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), "compiler_config.json")
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_dir = config.get('last_extension_dir')
                    if last_dir and os.path.isdir(last_dir):
                        self.path_edit.setText(last_dir)
                        self.extension_dir = last_dir
                        self._validate_and_show_info()
        except:
            pass
    
    def _save_last_extension(self, directory: str):
        """保存上次使用的扩展目录"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), "compiler_config.json")
            config = {'last_extension_dir': directory}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass


def main():
    """主函数"""
    if not PYQT5_AVAILABLE:
        print("错误: 未安装 PyQt5")
        print("请运行: pip install PyQt5")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # 创建主窗口
    window = ExtensionCompilerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()