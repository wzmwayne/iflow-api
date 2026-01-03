# -*- coding: utf-8 -*-
"""
积木块图形化编译器
用于通过拖拽积木块创建 iFlow 扩展

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional

# 尝试导入 PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
        QSplitter, QListWidget, QListWidgetItem, QGroupBox,
        QLineEdit, QFormLayout, QComboBox, QScrollArea, QFrame,
        QTabWidget, QCheckBox, QSpinBox, QDoubleSpinBox
    )
    from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QSize
    from PyQt5.QtGui import QFont, QColor, QDrag, QPixmap, QPainter
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# 导入积木块相关模块
try:
    from .blocks import BaseBlock, BlockFactory
    from .blocks.block_types import (
        ExtensionInfoBlock, ToolBlock, PromptBlock, LifecycleBlock,
        DependencyBlock, ConfigBlock, AIGenerateBlock
    )
    from .code_generator import ExtensionCodeGenerator
except ImportError:
    from blocks import BaseBlock, BlockFactory
    from blocks.block_types import (
        ExtensionInfoBlock, ToolBlock, PromptBlock, LifecycleBlock,
        DependencyBlock, ConfigBlock, AIGenerateBlock
    )
    from code_generator import ExtensionCodeGenerator


class BlockItem(QGraphicsRectItem):
    """积木块图形项"""
    
    def __init__(self, block: BaseBlock, scene_manager=None):
        super().__init__(0, 0, 200, 80)
        self.block = block
        self.scene_manager = scene_manager
        
        # 设置颜色
        color = QColor(block.get_color())
        self.setBrush(color)
        self.setPen(QPen(Qt.black, 2))
        
        # 设置可拖拽
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # 添加文本
        self.text_item = QGraphicsTextItem(block.get_name(), self)
        self.text_item.setDefaultTextColor(Qt.white)
        font = QFont("Arial", 10, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setPos(10, 10)
        self.text_item.setTextWidth(180)  # 设置文本宽度，自动换行
        
        # 添加描述
        self.desc_item = QGraphicsTextItem(block.get_description(), self)
        self.desc_item.setDefaultTextColor(Qt.white)
        font = QFont("Arial", 8)
        self.desc_item.setFont(font)
        self.desc_item.setPos(10, 35)
        self.desc_item.setTextWidth(180)  # 设置文本宽度，自动换行
        
        # 调整高度以适应内容
        self.adjust_size()
    
    def adjust_size(self):
        """调整大小以适应内容"""
        text_rect = self.text_item.boundingRect()
        desc_rect = self.desc_item.boundingRect()
        height = max(80, 10 + text_rect.height() + 10 + desc_rect.height() + 10)
        width = max(200, text_rect.width() + 20, desc_rect.width() + 20)
        self.setRect(0, 0, width, height)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
        if self.scene_manager:
            self.scene_manager.select_block(self)
    
    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsItem.ItemPositionChange and self.scene_manager:
            self.scene_manager.update_connections()
        return super().itemChange(change, value)


from PyQt5.QtGui import QPen


class BlockSceneManager:
    """积木块场景管理器"""
    
    def __init__(self, scene: QGraphicsScene):
        self.scene = scene
        self.block_items: List[BlockItem] = []
        self.connections: List = []
        self.selected_block: Optional[BlockItem] = None
    
    def add_block(self, block: BaseBlock, pos=(50, 50)) -> BlockItem:
        """添加积木块"""
        block_item = BlockItem(block, self)
        block_item.setPos(pos[0], pos[1])
        self.scene.addItem(block_item)
        self.block_items.append(block_item)
        return block_item
    
    def remove_block(self, block_item: BlockItem):
        """移除积木块"""
        if block_item in self.block_items:
            self.scene.removeItem(block_item)
            self.block_items.remove(block_item)
    
    def select_block(self, block_item: BlockItem):
        """选择积木块"""
        # 取消其他选择
        for item in self.block_items:
            if item != block_item:
                item.setSelected(False)
        
        self.selected_block = block_item
        block_item.setSelected(True)
        
        # 通知主窗口更新属性编辑器
        if hasattr(self, 'on_block_selected') and self.on_block_selected:
            self.on_block_selected(block_item.block if block_item else None)
    
    def update_connections(self):
        """更新连接线"""
        # TODO: 实现积木块连接线
        pass
    
    def get_all_blocks(self) -> List[BaseBlock]:
        """获取所有积木块"""
        return [item.block for item in self.block_items]
    
    def clear(self):
        """清空场景"""
        for item in self.block_items:
            self.scene.removeItem(item)
        self.block_items.clear()
        self.selected_block = None


class PropertyEditor(QScrollArea):
    """属性编辑器"""
    
    def __init__(self):
        super().__init__()
        self.current_block: Optional[BaseBlock] = None
        self.widgets: Dict[str, QWidget] = {}
        
        self.setWidgetResizable(True)
        self.setFixedWidth(300)
        
        # 创建内容部件
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.setWidget(self.content_widget)
    
    def set_block(self, block: Optional[BaseBlock]):
        """设置当前编辑的积木块"""
        self.current_block = block
        self._refresh_ui()
    
    def _refresh_ui(self):
        """刷新UI"""
        # 清空现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_block:
            self.content_layout.addWidget(QLabel("未选择积木块"))
            return
        
        # 显示积木块信息
        info_group = QGroupBox("积木块信息")
        info_layout = QFormLayout()
        
        info_layout.addRow("名称:", QLabel(self.current_block.get_name()))
        info_layout.addRow("描述:", QLabel(self.current_block.get_description()))
        info_layout.addRow("类别:", QLabel(self.current_block.get_category().value))
        
        info_group.setLayout(info_layout)
        self.content_layout.addWidget(info_group)
        
        # 显示参数编辑器
        params_group = QGroupBox("参数")
        params_layout = QFormLayout()
        
        self.widgets.clear()
        
        for param_def in self.current_block.get_parameters():
            param_name = param_def['name']
            param_type = param_def['type']
            param_label = param_def['label']
            param_default = param_def.get('default', '')
            
            if param_type == 'string':
                widget = QLineEdit()
                widget.setText(self.current_block.get_parameter(param_name, param_default))
                widget.textChanged.connect(lambda text, name=param_name: self._on_param_changed(name, text))
            
            elif param_type == 'text':
                widget = QTextEdit()
                widget.setMaximumHeight(100)
                widget.setText(self.current_block.get_parameter(param_name, param_default))
                widget.textChanged.connect(lambda: self._on_text_param_changed(param_name, widget))
            
            elif param_type == 'code':
                widget = QTextEdit()
                widget.setMaximumHeight(150)
                widget.setFont(QFont("Consolas", 10))
                widget.setText(self.current_block.get_parameter(param_name, param_default))
                widget.textChanged.connect(lambda: self._on_text_param_changed(param_name, widget))
            
            elif param_type == 'select':
                widget = QComboBox()
                options = param_def.get('options', [])
                widget.addItems(options)
                current_value = self.current_block.get_parameter(param_name, param_default)
                index = widget.findText(current_value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                widget.currentTextChanged.connect(lambda text, name=param_name: self._on_param_changed(name, text))
            
            elif param_type == 'list':
                widget = QLineEdit()
                widget.setText(self.current_block.get_parameter(param_name, param_default))
                widget.setPlaceholderText("用逗号分隔多个项目")
                widget.textChanged.connect(lambda text, name=param_name: self._on_param_changed(name, text))
            
            elif param_type == 'int':
                widget = QSpinBox()
                widget.setValue(int(self.current_block.get_parameter(param_name, param_default or 0)))
                widget.valueChanged.connect(lambda value, name=param_name: self._on_param_changed(name, str(value)))
            
            elif param_type == 'float':
                widget = QDoubleSpinBox()
                widget.setValue(float(self.current_block.get_parameter(param_name, param_default or 0.0)))
                widget.valueChanged.connect(lambda value, name=param_name: self._on_param_changed(name, str(value)))
            
            elif param_type == 'bool':
                widget = QCheckBox()
                widget.setChecked(str(self.current_block.get_parameter(param_name, param_default)).lower() in ('true', '1', 'yes'))
                widget.stateChanged.connect(lambda state, name=param_name: self._on_param_changed(name, 'true' if state else 'false'))
            
            else:
                widget = QLineEdit()
                widget.setText(self.current_block.get_parameter(param_name, param_default))
                widget.textChanged.connect(lambda text, name=param_name: self._on_param_changed(name, text))
            
            self.widgets[param_name] = widget
            params_layout.addRow(param_label + ":", widget)
        
        params_group.setLayout(params_layout)
        self.content_layout.addWidget(params_group)
        
        # 添加弹性空间
        self.content_layout.addStretch()
    
    def _on_param_changed(self, param_name: str, value: str):
        """参数变化回调"""
        if self.current_block:
            self.current_block.set_parameter(param_name, value)
    
    def _on_text_param_changed(self, param_name: str, widget: QTextEdit):
        """文本参数变化回调"""
        if self.current_block:
            self.current_block.set_parameter(param_name, widget.toPlainText())


class BlockCompilerGUI(QMainWindow):
    """积木块编译器图形界面"""
    
    def __init__(self):
        super().__init__()
        self.code_generator = ExtensionCodeGenerator()
        self.current_file = ""
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("iFlow 积木块编译器 - by wzmwayne & iflowai")
        self.setGeometry(100, 100, 1400, 900)
        
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
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #e8f5e9;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
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
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：积木块面板
        left_panel = self._create_block_panel()
        splitter.addWidget(left_panel)
        
        # 中间：工作区
        center_panel = self._create_workspace()
        splitter.addWidget(center_panel)
        
        # 右侧：属性编辑器和代码预览
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([250, 600, 350])
        main_layout.addWidget(splitter)
        
        # 底部：工具栏
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        central_widget.setLayout(main_layout)
    
    def _create_block_panel(self) -> QWidget:
        """创建积木块面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("📦 积木块库")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # 积木块列表
        self.block_list = QListWidget()
        self.block_list.setIconSize(QSize(32, 32))
        
        # 加载所有积木块
        all_blocks = BlockFactory.get_all_blocks()
        from PyQt5.QtGui import QIcon
        for block in all_blocks:
            item = QListWidgetItem(block.get_name())
            item.setToolTip(block.get_description())
            # 设置颜色图标
            color = QColor(block.get_color())
            pixmap = QPixmap(32, 32)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            item.setIcon(icon)
            item.setData(Qt.UserRole, block)
            self.block_list.addItem(item)
        
        self.block_list.itemDoubleClicked.connect(self._add_block_to_workspace)
        layout.addWidget(self.block_list)
        
        # 添加按钮
        add_btn = QPushButton("➕ 添加到工作区")
        add_btn.clicked.connect(self._add_selected_block)
        layout.addWidget(add_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _create_workspace(self) -> QWidget:
        """创建工作区"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("🎨 工作区")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._clear_workspace)
        title_layout.addWidget(clear_btn)
        
        layout.addLayout(title_layout)
        
        # 图形场景
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 600)
        
        self.scene_manager = BlockSceneManager(self.scene)
        # 设置积木块选择回调
        self.scene_manager.on_block_selected = self._on_block_selected
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setBackgroundBrush(QColor("#f0f0f0"))
        
        layout.addWidget(self.view)
        
        widget.setLayout(layout)
        return widget
    
    def _create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 属性编辑器标签页
        property_tab = QWidget()
        property_layout = QVBoxLayout()
        property_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("⚙️ 属性编辑器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
            }
        """)
        property_layout.addWidget(title_label)
        
        self.property_editor = PropertyEditor()
        property_layout.addWidget(self.property_editor)
        
        property_tab.setLayout(property_layout)
        tab_widget.addTab(property_tab, "属性")
        
        # 代码预览标签页
        code_tab = QWidget()
        code_layout = QVBoxLayout()
        code_layout.setContentsMargins(0, 0, 0, 0)
        
        code_title_layout = QHBoxLayout()
        code_title_label = QLabel("💻 代码预览")
        code_title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        code_title_layout.addWidget(code_title_label)
        code_title_layout.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self._refresh_code_preview)
        code_title_layout.addWidget(refresh_btn)
        
        code_layout.addLayout(code_title_layout)
        
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        code_layout.addWidget(self.code_preview)
        
        code_tab.setLayout(code_layout)
        tab_widget.addTab(code_tab, "代码")
        
        layout.addWidget(tab_widget)
        widget.setLayout(layout)
        return widget
    
    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        widget = QWidget()
        widget.setMaximumHeight(60)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 新建按钮
        new_btn = QPushButton("📄 新建")
        new_btn.clicked.connect(self._new_project)
        layout.addWidget(new_btn)
        
        # 打开按钮
        open_btn = QPushButton("📂 打开")
        open_btn.clicked.connect(self._open_project)
        layout.addWidget(open_btn)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self._save_project)
        layout.addWidget(save_btn)
        
        # 生成代码按钮
        generate_btn = QPushButton("⚡ 生成代码")
        generate_btn.clicked.connect(self._generate_code)
        layout.addWidget(generate_btn)
        
        # 导出扩展按钮
        export_btn = QPushButton("📦 导出扩展")
        export_btn.clicked.connect(self._export_extension)
        layout.addWidget(export_btn)
        
        # 关闭按钮
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _add_block_to_workspace(self, item: QListWidgetItem):
        """添加积木块到工作区"""
        block = item.data(Qt.UserRole)
        if block:
            # 创建新的积木块实例
            new_block = block.__class__()
            self.scene_manager.add_block(new_block)
            self._refresh_code_preview()
    
    def _add_selected_block(self):
        """添加选中的积木块"""
        current_item = self.block_list.currentItem()
        if current_item:
            self._add_block_to_workspace(current_item)
    
    def _clear_workspace(self):
        """清空工作区"""
        reply = QMessageBox.question(
            self, "确认",
            "确定要清空工作区吗？所有积木块将被删除。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.scene_manager.clear()
            self.property_editor.set_block(None)
            self._refresh_code_preview()
    
    def _refresh_code_preview(self):
        """刷新代码预览"""
        blocks = self.scene_manager.get_all_blocks()
        self.code_generator.clear_blocks()
        for block in blocks:
            self.code_generator.add_block(block)
        
        code = self.code_generator.generate_extension_code()
        self.code_preview.setText(code)
    
    def _on_block_selected(self, block: Optional[BaseBlock]):
        """积木块被选中时的回调"""
        self.property_editor.set_block(block)
    
    def _new_project(self):
        """新建项目"""
        reply = QMessageBox.question(
            self, "确认",
            "确定要新建项目吗？当前工作区将被清空。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.scene_manager.clear()
            self.property_editor.set_block(None)
            self.current_file = ""
            self._refresh_code_preview()
    
    def _open_project(self):
        """打开项目"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "iFlow 项目文件 (*.json)"
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 清空工作区
                self.scene_manager.clear()
                
                # 加载积木块
                for block_data in data.get('blocks', []):
                    block = BlockFactory.create_block(block_data)
                    if block:
                        pos = block_data.get('pos', [50, 50])
                        self.scene_manager.add_block(block, pos)
                
                self.current_file = filepath
                self._refresh_code_preview()
                
                QMessageBox.information(self, "成功", "项目加载成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载项目失败: {str(e)}")
    
    def _save_project(self):
        """保存项目"""
        if not self.current_file:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "保存项目", "", "iFlow 项目文件 (*.json)"
            )
            if not filepath:
                return
            if not filepath.endswith('.json'):
                filepath += '.json'
            self.current_file = filepath
        
        try:
            # 收集积木块数据
            blocks_data = []
            for block_item in self.scene_manager.block_items:
                block_data = block_item.block.to_dict()
                block_data['pos'] = [block_item.x(), block_item.y()]
                blocks_data.append(block_data)
            
            # 保存到文件
            data = {
                'version': '1.0.0',
                'blocks': blocks_data
            }
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "项目保存成功！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存项目失败: {str(e)}")
    
    def _generate_code(self):
        """生成代码"""
        blocks = self.scene_manager.get_all_blocks()
        
        if not blocks:
            QMessageBox.warning(self, "警告", "工作区为空，请先添加积木块。")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存代码", "extension.py", "Python 文件 (*.py)"
        )
        
        if filepath:
            try:
                self.code_generator.clear_blocks()
                for block in blocks:
                    self.code_generator.add_block(block)
                
                self.code_generator.save_to_file(filepath)
                QMessageBox.information(self, "成功", f"代码已保存到: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"生成代码失败: {str(e)}")
    
    def _export_extension(self):
        """导出扩展"""
        blocks = self.scene_manager.get_all_blocks()
        
        if not blocks:
            QMessageBox.warning(self, "警告", "工作区为空，请先添加积木块。")
            return
        
        # 先生成代码
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出扩展", "extension.zip", "ZIP 文件 (*.zip)"
        )
        
        if filepath:
            try:
                # 创建临时目录
                import tempfile
                temp_dir = tempfile.mkdtemp()
                
                # 生成 extension.py
                ext_file = os.path.join(temp_dir, 'extension.py')
                self.code_generator.clear_blocks()
                for block in blocks:
                    self.code_generator.add_block(block)
                self.code_generator.save_to_file(ext_file)
                
                # 打包为 zip
                import zipfile
                with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(ext_file, 'extension.py')
                
                # 清理临时目录
                import shutil
                shutil.rmtree(temp_dir)
                
                QMessageBox.information(self, "成功", f"扩展已导出到: {filepath}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出扩展失败: {str(e)}")


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
    window = BlockCompilerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()