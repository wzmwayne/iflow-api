# -*- coding: utf-8 -*-
"""
积木块基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum


class BlockCategory(Enum):
    """积木块类别"""
    BASIC = "基础"
    TOOL = "工具"
    PROMPT = "提示词"
    LIFECYCLE = "生命周期"
    CONFIG = "配置"
    DEPENDENCY = "依赖"
    AI = "AI辅助"


class BaseBlock(ABC):
    """积木块基类"""
    
    def __init__(self, block_id: str = None):
        self.block_id = block_id or self._generate_id()
        self.category = self.get_category()
        self.color = self.get_color()
        self.children = []
        self.parameters = {}
    
    @abstractmethod
    def get_category(self) -> BlockCategory:
        """获取积木块类别"""
        pass
    
    @abstractmethod
    def get_color(self) -> str:
        """获取积木块颜色"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取积木块名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取积木块描述"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[Dict[str, Any]]:
        """获取参数定义"""
        pass
    
    @abstractmethod
    def generate_code(self, indent: int = 0) -> str:
        """生成代码"""
        pass
    
    def set_parameter(self, key: str, value: Any):
        """设置参数值"""
        self.parameters[key] = value
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(key, default)
    
    def add_child(self, block: 'BaseBlock'):
        """添加子积木块"""
        self.children.append(block)
    
    def remove_child(self, block: 'BaseBlock'):
        """移除子积木块"""
        if block in self.children:
            self.children.remove(block)
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.block_id,
            'type': self.__class__.__name__,
            'category': self.category.value,
            'name': self.get_name(),
            'description': self.get_description(),
            'parameters': self.parameters,
            'children': [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseBlock':
        """从字典创建积木块"""
        # 这里需要根据类型创建对应的积木块
        from .block_types import BlockFactory
        return BlockFactory.create_block(data)