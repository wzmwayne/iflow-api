# -*- coding: utf-8 -*-
"""
iFlow 扩展系统
支持动态加载扩展，每个扩展可以提供工具和提示词
"""

import os
import importlib.util
from typing import Dict, List, Callable, Any, Optional


class ExtensionManager:
    """扩展管理器"""
    
    def __init__(self, extensions_dir: str = "iflow_extensions"):
        self.extensions_dir = extensions_dir
        self.extensions: Dict[str, 'BaseExtension'] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.extension_prompts: List[str] = []
        
    def load_extensions(self):
        """加载所有扩展"""
        if not os.path.exists(self.extensions_dir):
            print(f"[扩展] 扩展目录不存在: {self.extensions_dir}")
            return
        
        # 遍历扩展目录
        for item in os.listdir(self.extensions_dir):
            ext_path = os.path.join(self.extensions_dir, item)
            
            # 跳过__init__.py和base_extension.py
            if item.startswith('__') or item.startswith('base_'):
                continue
            
            # 只处理目录
            if os.path.isdir(ext_path):
                self._load_extension(ext_path, item)
    
    def _load_extension(self, ext_path: str, ext_name: str):
        """加载单个扩展"""
        try:
            # 查找extension.py文件
            ext_file = os.path.join(ext_path, "extension.py")
            if not os.path.exists(ext_file):
                print(f"[扩展] 扩展 {ext_name} 缺少 extension.py 文件")
                return
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(f"{ext_name}.extension", ext_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取扩展类
            if hasattr(module, 'Extension'):
                extension = module.Extension()
                
                # 注册扩展
                self.extensions[ext_name] = extension
                
                # 注册工具
                tools = extension.get_tools()
                for tool_name, tool_handler in tools.items():
                    self.tool_handlers[tool_name] = tool_handler
                    print(f"[扩展] 已注册工具: {tool_name} (来自 {ext_name})")
                
                # 收集提示词
                prompt = extension.get_prompt()
                if prompt:
                    self.extension_prompts.append(prompt)
                    print(f"[扩展] 已加载提示词: {ext_name}")
                
                print(f"[扩展] 扩展 {ext_name} 加载成功")
            else:
                print(f"[扩展] 扩展 {ext_name} 缺少 Extension 类")
                
        except Exception as e:
            print(f"[扩展] 加载扩展 {ext_name} 失败: {e}")
    
    def get_tool_handler(self, tool_name: str) -> Optional[Callable]:
        """获取工具处理器"""
        return self.tool_handlers.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, str]:
        """获取所有工具及其描述"""
        tools = {}
        for ext_name, extension in self.extensions.items():
            ext_tools = extension.get_tool_descriptions()
            tools.update(ext_tools)
        return tools
    
    def get_extension_prompt(self) -> str:
        """获取所有扩展的提示词"""
        if not self.extension_prompts:
            return ""
        
        prompt = "\n\n【可用扩展功能】\n"
        prompt += "\n".join(self.extension_prompts)
        return prompt
    
    def has_tool(self, tool_name: str) -> bool:
        """检查是否存在某个工具"""
        return tool_name in self.tool_handlers


class BaseExtension:
    """扩展基类，所有扩展必须继承此类"""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.version = "1.0.0"
        self.author = ""
    
    def get_name(self) -> str:
        """获取扩展名称"""
        return self.name
    
    def get_description(self) -> str:
        """获取扩展描述"""
        return self.description
    
    def get_version(self) -> str:
        """获取扩展版本"""
        return self.version
    
    def get_author(self) -> str:
        """获取扩展作者"""
        return self.author
    
    def get_prompt(self) -> str:
        """
        获取扩展的提示词
        返回的提示词将被添加到系统提示词中
        """
        return ""
    
    def get_tools(self) -> Dict[str, Callable]:
        """
        获取扩展提供的工具
        返回格式: {工具名: 工具处理函数}
        """
        return {}
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        获取工具描述
        返回格式: {工具名: 工具描述}
        """
        return {}
    
    def on_load(self):
        """扩展加载时调用"""
        pass
    
    def on_unload(self):
        """扩展卸载时调用"""
        pass


# 全局扩展管理器实例
extension_manager = ExtensionManager()