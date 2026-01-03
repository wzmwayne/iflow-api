# -*- coding: utf-8 -*-
"""
iFlow 扩展基类
所有扩展必须继承此类并实现相应方法
"""

from typing import Dict, Callable, List, Any, Optional, Tuple


class BaseExtension:
    """
    扩展基类
    
    所有扩展必须继承此类，并实现必要的方法。
    扩展可以提供工具函数、提示词、配置项等功能。
    """
    
    def __init__(self):
        """初始化扩展"""
        self.name = ""
        self.description = ""
        self.version = "1.0.0"
        self.author = ""
        self.enabled = True
        self.config = {}
    
    def get_name(self) -> str:
        """
        获取扩展名称
        必须唯一，用于标识扩展
        """
        return self.name
    
    def get_description(self) -> str:
        """获取扩展描述"""
        return self.description
    
    def get_version(self) -> str:
        """获取扩展版本号，格式: 主版本.次版本.修订号"""
        return self.version
    
    def get_author(self) -> str:
        """获取扩展作者"""
        return self.author
    
    def is_enabled(self) -> bool:
        """检查扩展是否启用"""
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        """设置扩展启用状态"""
        self.enabled = enabled
    
    def get_prompt(self) -> str:
        """
        获取扩展的提示词
        返回的提示词将被添加到系统提示词中，让AI了解扩展功能
        
        返回格式建议：
        - 使用【扩展名称】作为标题
        - 列出所有可用工具及其使用方法
        - 提供使用示例
        
        示例:
        '''
        【我的扩展】
        此扩展提供XX功能。
        
        可用工具：
        - @tool1(参数) - 工具描述
        - @tool2(参数) - 工具描述
        
        使用示例：
        用户说"帮我XX" -> AI调用 @tool1(参数)
        '''
        """
        return ""
    
    def get_tools(self) -> Dict[str, Callable]:
        """
        获取扩展提供的工具处理函数
        
        返回格式: {工具名: 工具处理函数}
        
        工具处理函数签名:
        def tool_handler(args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
            '''
            工具处理函数
            
            参数:
                args: 工具参数字符串，由AI传入
                confirm_callback: 确认回调函数（可选），用于需要用户确认的操作
                                  函数签名: confirm_callback(title: str, message: str) -> bool
                                  返回 True 表示用户同意，False 表示用户拒绝
            
            返回:
                (success, message) - (是否成功, 结果消息)
                success: bool - 操作是否成功
                message: str - 结果消息，将返回给AI
            '''
            ...
        
        示例:
        def my_tool(args: str) -> Tuple[bool, str]:
            try:
                result = do_something(args)
                return True, f"操作成功: {result}"
            except Exception as e:
                return False, f"操作失败: {str(e)}"
        
        return {
            'tool1': my_tool,
            'tool2': another_tool,
        }
        """
        return {}
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        获取工具描述
        用于帮助系统和AI理解工具用途
        
        返回格式: {工具名: 工具描述}
        
        示例:
        return {
            'tool1': '工具1的功能描述',
            'tool2': '工具2的功能描述',
        }
        """
        return {}
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        获取配置项定义
        定义扩展支持的配置项及其默认值
        
        返回格式:
        {
            '配置项名': {
                'type': '类型',  # string/int/float/bool/list/dict
                'default': 默认值,
                'description': '配置项描述',
                'required': False,  # 是否必需
                'options': [...]  # 可选值列表（仅用于枚举类型）
            }
        }
        
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
    
    def load_config(self, config: Dict[str, Any]):
        """
        加载配置
        
        参数:
            config: 配置字典
        """
        self.config = config
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置项值"""
        return self.config.get(key, default)
    
    def on_load(self):
        """
        扩展加载时调用
        可以在此处进行初始化操作
        """
        pass
    
    def on_unload(self):
        """
        扩展卸载时调用
        可以在此处进行清理操作
        """
        pass
    
    def on_before_tool_call(self, tool_name: str, args: str) -> Tuple[bool, str]:
        """
        工具调用前调用
        可以用于权限检查、参数验证等
        
        参数:
            tool_name: 工具名称
            args: 工具参数
        
        返回:
            (allowed, message) - (是否允许, 消息)
            allowed: False 时将阻止工具调用
        """
        return True, ""
    
    def on_after_tool_call(self, tool_name: str, args: str, result: Tuple[bool, str]):
        """
        工具调用后调用
        可以用于日志记录、结果处理等
        
        参数:
            tool_name: 工具名称
            args: 工具参数
            result: 工具执行结果 (success, message)
        """
        pass
    
    def get_dependencies(self) -> List[str]:
        """
        获取扩展依赖的Python包列表
        返回需要安装的包名列表
        
        示例:
        return ['requests', 'numpy']
        """
        return []
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """
        检查依赖是否已安装
        
        返回:
            (all_installed, missing_packages)
            all_installed: bool - 所有依赖是否都已安装
            missing_packages: List[str] - 未安装的包列表
        """
        missing = []
        for package in self.get_dependencies():
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        return len(missing) == 0, missing
    
    def get_ui_components(self) -> Dict[str, Any]:
        """
        获取扩展的UI组件（仅GUI版本使用）
        返回扩展提供的UI组件定义
        
        返回格式:
        {
            'menu_items': [
                {'label': '菜单项', 'callback': callback_function},
                ...
            ],
            'toolbar_buttons': [
                {'label': '按钮', 'icon': 'icon_name', 'callback': callback_function},
                ...
            ],
            'settings_panel': settings_widget_class,
        }
        """
        return {}
    
    def get_help_text(self) -> str:
        """
        获取扩展的帮助文本
        返回扩展的详细使用说明
        
        示例:
        return '''
        === 我的扩展帮助 ===
        
        功能描述：...
        
        使用方法：
        1. ...
        2. ...
        
        工具列表：
        - @tool1: ...
        - @tool2: ...
        
        配置项：
        - config1: ...
        - config2: ...
        '''
        """
        return ""
    
    def get_webhook_url(self) -> Optional[str]:
        """
        获取扩展的Webhook URL（可选）
        如果扩展支持Webhook，返回URL
        
        返回:
            Webhook URL字符串，如果不支持则返回None
        """
        return None
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        处理Webhook请求（可选）
        
        参数:
            payload: Webhook请求数据
        
        返回:
            (success, response_data)
        """
        return False, {}
    
    def export_data(self) -> Dict[str, Any]:
        """
        导出扩展数据（可选）
        用于备份或迁移扩展数据
        
        返回:
            扩展数据字典
        """
        return {
            'config': self.config,
            'name': self.name,
            'version': self.version,
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """
        导入扩展数据（可选）
        
        参数:
            data: 扩展数据字典
        
        返回:
            是否导入成功
        """
        try:
            if 'config' in data:
                self.config.update(data['config'])
            return True
        except Exception:
            return False