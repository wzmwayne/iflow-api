# -*- coding: utf-8 -*-
"""
扩展名称：你的扩展名称
扩展描述：描述你的扩展功能
作者：wzmwayne_and_iflow_ai
版本：1.0.0
"""

import os
import sys
from typing import Dict, Callable, Tuple
from datetime import datetime

# 导入父目录的基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension


class YourExtension(BaseExtension):
    """
    你的扩展类
    
    继承自 BaseExtension，实现必要的方法来创建自定义扩展。
    """
    
    def __init__(self):
        """
        初始化扩展
        
        在这里设置扩展的基本信息和配置。
        """
        super().__init__()
        
        # ========== 必须设置的属性 ==========
        self.name = "your_extension"           # 扩展名称（必须唯一，使用小写字母和下划线）
        self.description = "描述你的扩展功能"  # 扩展描述（简短说明）
        self.version = "1.0.0"               # 版本号（遵循语义化版本）
        self.author = "wzmwayne_and_iflow_ai"              # 作者名
        
        # ========== 可选的配置 ==========
        self.config = {
            # 在这里定义扩展的配置项
            'option1': 'value1',
            'option2': 123,
        }
        
        # ========== 扩展状态 ==========
        # 在这里存储扩展的运行时状态
        self.state = {}
    
    # ========== 生命周期方法 ==========
    
    def on_load(self):
        """
        扩展加载时调用
        
        在这里执行一些初始化操作，比如：
        - 检查依赖
        - 初始化配置
        - 创建必要的文件或目录
        """
        print(f"[{self.name}] 扩展已加载")
        
        # 检查依赖
        missing = self.check_dependencies()[1]
        if missing:
            print(f"[{self.name}] 警告：缺少依赖: {', '.join(missing)}")
    
    def on_unload(self):
        """
        扩展卸载时调用
        
        在这里执行一些清理操作，比如：
        - 保存状态
        - 关闭连接
        - 释放资源
        """
        print(f"[{self.name}] 扩展已卸载")
    
    def on_before_tool_call(self, tool_name: str, args: str):
        """
        工具调用前调用
        
        参数:
            tool_name: 工具名称
            args: 工具参数
        
        在这里可以：
        - 记录日志
        - 检查权限
        - 验证参数
        """
        pass
    
    def on_after_tool_call(self, tool_name: str, args: str, result: Tuple[bool, str]):
        """
        工具调用后调用
        
        参数:
            tool_name: 工具名称
            args: 工具参数
            result: 工具返回结果 (success, message)
        
        在这里可以：
        - 记录日志
        - 更新状态
        - 触发后续操作
        """
        pass
    
    # ========== 必须实现的方法 ==========
    
    def get_prompt(self) -> str:
        """
        返回扩展的提示词，将添加到系统提示词中
        
        提示词格式建议：
        - 使用【扩展名称】作为标题
        - 清晰列出所有可用工具
        - 提供使用说明和示例
        
        返回:
            str: 提示词内容
        """
        prompt = """
【你的扩展名称】
此扩展提供XX功能。

你可以调用以下工具：
- @tool1(参数) - 工具1的描述
- @tool2(参数) - 工具2的描述

使用说明：
1. 何时使用工具1
2. 何时使用工具2

示例：
- 用户说"帮我XX" -> AI调用 @tool1(参数)
- 用户说"帮我YY" -> AI调用 @tool2(参数)
"""
        return prompt.strip()
    
    def get_tools(self) -> Dict[str, Callable]:
        """
        返回工具处理函数字典
        
        格式：{工具名称: 工具函数}
        
        返回:
            Dict[str, Callable]: 工具字典
        """
        return {
            'tool1': self.tool1,
            'tool2': self.tool2,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        返回工具描述字典
        
        格式：{工具名称: 工具描述}
        
        返回:
            Dict[str, str]: 工具描述字典
        """
        return {
            'tool1': '工具1的描述',
            'tool2': '工具2的描述',
        }
    
    # ========== 工具处理函数 ==========
    
    def tool1(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        工具1的处理函数
        
        参数:
            args: 工具参数字符串，由AI传入
            confirm_callback: 确认回调函数（可选）
                              函数签名: confirm_callback(title: str, message: str) -> bool
                              返回 True 表示用户同意，False 表示用户拒绝
        
        返回:
            Tuple[bool, str]: (是否成功, 结果消息)
            - success: bool - 操作是否成功
            - message: str - 结果消息，将返回给AI
        
        使用示例:
            # 不需要确认
            success, message = self.tool1("参数")
            
            # 需要确认
            if confirm_callback:
                allowed = confirm_callback("确认操作", "是否允许？")
                if not allowed:
                    return False, "用户取消操作"
        """
        try:
            # 解析参数
            params = self._parse_args(args)
            
            # 执行操作
            result = self._do_something(params)
            
            # 返回结果
            return True, f"操作成功: {result}"
            
        except ValueError as e:
            return False, f"参数错误: {str(e)}"
        except Exception as e:
            return False, f"操作失败: {str(e)}"
    
    def tool2(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        工具2的处理函数
        
        参数和返回值说明同 tool1
        """
        try:
            # 执行操作
            result = "操作结果"
            
            return True, result
            
        except Exception as e:
            return False, f"操作失败: {str(e)}"
    
    # ========== 辅助方法 ==========
    
    def _parse_args(self, args: str) -> dict:
        """
        解析工具参数
        
        参数:
            args: 参数字符串
        
        返回:
            dict: 解析后的参数字典
        
        示例:
            输入: "key1=value1,key2=value2"
            输出: {"key1": "value1", "key2": "value2"}
        """
        params = {}
        if not args:
            return params
        
        for pair in args.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key.strip()] = value.strip()
        
        return params
    
    def _do_something(self, params: dict) -> str:
        """
        执行具体操作的辅助方法
        
        参数:
            params: 参数字典
        
        返回:
            str: 操作结果
        """
        # 在这里实现具体的操作逻辑
        return "操作结果"
    
    # ========== 可选的高级方法 ==========
    
    def get_config_schema(self) -> Dict[str, dict]:
        """
        定义配置项
        
        返回:
            Dict[str, dict]: 配置项定义
        
        示例:
            return {
                'api_key': {
                    'type': 'string',
                    'default': '',
                    'description': 'API密钥',
                    'required': True
                },
                'timeout': {
                    'type': 'int',
                    'default': 30,
                    'description': '超时时间（秒）'
                }
            }
        """
        return {}
    
    def load_config(self, config: Dict[str, any]):
        """
        加载配置
        
        参数:
            config: 配置字典
        """
        self.config.update(config)
    
    def get_config_value(self, key: str, default: any = None) -> any:
        """
        获取配置值
        
        参数:
            key: 配置键
            default: 默认值
        
        返回:
            any: 配置值
        """
        return self.config.get(key, default)
    
    def get_dependencies(self) -> list:
        """
        返回依赖的包列表
        
        返回:
            list: 依赖包列表
        
        示例:
            return ['requests', 'numpy']
        """
        return []
    
    def check_dependencies(self) -> Tuple[bool, list]:
        """
        检查依赖是否已安装
        
        返回:
            Tuple[bool, list]: (是否全部已安装, 缺失的包列表)
        """
        missing = []
        for package in self.get_dependencies():
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        return len(missing) == 0, missing


# ========== 扩展实例（必须）==========

# 创建扩展实例并赋值给 Extension 变量
# 这是扩展管理器识别扩展的标准方式
Extension = YourExtension