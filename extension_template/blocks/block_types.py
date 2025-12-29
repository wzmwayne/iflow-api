# -*- coding: utf-8 -*-
"""
积木块类型定义
"""

from typing import Dict, Any, List
try:
    from .base_block import BaseBlock, BlockCategory
except ImportError:
    from base_block import BaseBlock, BlockCategory


class BlockFactory:
    """积木块工厂"""
    
    _block_classes = {}
    
    @classmethod
    def register_block(cls, block_class):
        """注册积木块类"""
        cls._block_classes[block_class.__name__] = block_class
        return block_class
    
    @classmethod
    def create_block(cls, data: Dict[str, Any]) -> BaseBlock:
        """从字典创建积木块"""
        block_type = data.get('type')
        if block_type in cls._block_classes:
            block = cls._block_classes[block_type]()
            block.block_id = data.get('id', block.block_id)
            block.parameters = data.get('parameters', {})
            
            # 递归创建子积木块
            for child_data in data.get('children', []):
                child = cls.create_block(child_data)
                block.add_child(child)
            
            return block
        return None
    
    @classmethod
    def get_all_blocks(cls) -> List[BaseBlock]:
        """获取所有可用的积木块"""
        return [block_class() for block_class in cls._block_classes.values()]


@BlockFactory.register_block
class ExtensionInfoBlock(BaseBlock):
    """扩展信息积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.BASIC
    
    def get_color(self) -> str:
        return "#4CAF50"
    
    def get_name(self) -> str:
        return "扩展信息"
    
    def get_description(self) -> str:
        return "定义扩展的基本信息（名称、描述、版本、作者）"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'extension_name',
                'type': 'string',
                'label': '扩展名称',
                'default': 'my_extension',
                'required': True
            },
            {
                'name': 'description',
                'type': 'string',
                'label': '扩展描述',
                'default': '我的扩展',
                'required': True
            },
            {
                'name': 'version',
                'type': 'string',
                'label': '版本号',
                'default': '1.0.0',
                'required': True
            },
            {
                'name': 'author',
                'type': 'string',
                'label': '作者',
                'default': 'Your Name',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        name = self.get_parameter('extension_name', 'my_extension')
        desc = self.get_parameter('description', '我的扩展')
        version = self.get_parameter('version', '1.0.0')
        author = self.get_parameter('author', 'Your Name')
        
        code_lines = []
        code_lines.append(f'{prefix}self.name = "{name}"')
        code_lines.append(f'{prefix}self.description = "{desc}"')
        code_lines.append(f'{prefix}self.version = "{version}"')
        code_lines.append(f'{prefix}self.author = "{author}"')
        
        return '\n'.join(code_lines)


@BlockFactory.register_block
class ToolBlock(BaseBlock):
    """工具积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.TOOL
    
    def get_color(self) -> str:
        return "#2196F3"
    
    def get_name(self) -> str:
        return "工具"
    
    def get_description(self) -> str:
        return "定义一个工具函数"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'tool_name',
                'type': 'string',
                'label': '工具名称',
                'default': 'my_tool',
                'required': True
            },
            {
                'name': 'tool_description',
                'type': 'string',
                'label': '工具描述',
                'default': '我的工具',
                'required': True
            },
            {
                'name': 'tool_code',
                'type': 'code',
                'label': '工具代码',
                'default': '# 在这里编写工具代码\nresult = "操作结果"\nreturn True, result',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        name = self.get_parameter('tool_name', 'my_tool')
        desc = self.get_parameter('tool_description', '我的工具')
        code = self.get_parameter('tool_code', 'result = "操作结果"\nreturn True, result')
        
        header = f'{prefix}def {name}(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:'
        docstring = f'{prefix}    """{desc}"""'
        try_block = f'{prefix}    try:'
        code_lines = self._indent_code(code, indent + 2)
        except_block = f'{prefix}    except Exception as e:'
        return_block = f'{prefix}        return False, f"操作失败: " + str(e)'
        
        return '\n'.join([header, docstring, try_block, code_lines, except_block, return_block])
    
    def _indent_code(self, code: str, indent: int) -> str:
        """缩进代码"""
        prefix = " " * indent
        lines = code.split('\n')
        result = []
        for line in lines:
            if line.strip():
                result.append(prefix + line)
            else:
                result.append('')
        return '\n'.join(result)


@BlockFactory.register_block
class PromptBlock(BaseBlock):
    """提示词积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.PROMPT
    
    def get_color(self) -> str:
        return "#FF9800"
    
    def get_name(self) -> str:
        return "提示词"
    
    def get_description(self) -> str:
        return "定义扩展的提示词，让AI了解扩展功能"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'prompt_text',
                'type': 'text',
                'label': '提示词内容',
                'default': '【扩展名称】\n此扩展提供XX功能。\n\n可用工具：\n- @tool1(参数) - 工具描述\n\n使用说明：\n1. 何时使用工具1\n2. 何时使用工具2\n\n示例：\n- 用户说"XX" -> AI调用 @tool1(参数)',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        prompt = self.get_parameter('prompt_text', '')
        
        header = f'{prefix}def get_prompt(self) -> str:'
        docstring = f'{prefix}    """返回扩展的提示词"""'
        prompt_var = f'{prefix}    prompt = """'
        prompt_lines = self._indent_text(prompt, indent + 2)
        prompt_end = f'{prefix}"""'
        return_stmt = f'{prefix}    return prompt.strip()'
        
        return '\n'.join([header, docstring, prompt_var, prompt_lines, prompt_end, return_stmt])
    
    def _indent_text(self, text: str, indent: int) -> str:
        """缩进文本"""
        prefix = " " * indent
        lines = text.split('\n')
        return '\n'.join(prefix + line if line.strip() else line for line in lines)


@BlockFactory.register_block
class LifecycleBlock(BaseBlock):
    """生命周期积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.LIFECYCLE
    
    def get_color(self) -> str:
        return "#9C27B0"
    
    def get_name(self) -> str:
        return "生命周期"
    
    def get_description(self) -> str:
        return "定义扩展的生命周期方法（加载、卸载等）"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'lifecycle_type',
                'type': 'select',
                'label': '生命周期类型',
                'options': ['on_load', 'on_unload', 'on_before_tool_call', 'on_after_tool_call'],
                'default': 'on_load',
                'required': True
            },
            {
                'name': 'lifecycle_code',
                'type': 'code',
                'label': '生命周期代码',
                'default': 'print("扩展已加载")',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        lifecycle_type = self.get_parameter('lifecycle_type', 'on_load')
        code = self.get_parameter('lifecycle_code', 'print("扩展已加载")')
        
        header = f'{prefix}def {lifecycle_type}(self):'
        docstring = f'{prefix}    """{lifecycle_type}"""'
        code_lines = self._indent_code(code, indent + 2)
        
        return '\n'.join([header, docstring, code_lines])
    
    def _indent_code(self, code: str, indent: int) -> str:
        """缩进代码"""
        prefix = " " * indent
        lines = code.split('\n')
        return '\n'.join(prefix + line if line.strip() else line for line in lines)


@BlockFactory.register_block
class DependencyBlock(BaseBlock):
    """依赖积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.DEPENDENCY
    
    def get_color(self) -> str:
        return "#E91E63"
    
    def get_name(self) -> str:
        return "依赖包"
    
    def get_description(self) -> str:
        return "声明扩展需要的Python依赖包"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'packages',
                'type': 'list',
                'label': '依赖包列表',
                'default': 'requests, numpy',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        packages = self.get_parameter('packages', 'requests, numpy')
        package_list = [f'"{p.strip()}"' for p in packages.split(',')]
        
        return f'{prefix}def get_dependencies(self) -> list:\n{prefix}    """返回依赖的包列表"""\n{prefix}    return {package_list}'


@BlockFactory.register_block
class ConfigBlock(BaseBlock):
    """配置积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.CONFIG
    
    def get_color(self) -> str:
        return "#607D8B"
    
    def get_name(self) -> str:
        return "配置"
    
    def get_description(self) -> str:
        return "定义扩展的配置项"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'config_name',
                'type': 'string',
                'label': '配置名称',
                'default': 'api_key',
                'required': True
            },
            {
                'name': 'config_type',
                'type': 'select',
                'label': '配置类型',
                'options': ['string', 'int', 'bool', 'float'],
                'default': 'string',
                'required': True
            },
            {
                'name': 'config_default',
                'type': 'string',
                'label': '默认值',
                'default': '',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        prefix = " " * indent
        name = self.get_parameter('config_name', 'api_key')
        config_type = self.get_parameter('config_type', 'string')
        default = self.get_parameter('config_default', '')
        
        type_mapping = {
            'string': 'str',
            'int': 'int',
            'bool': 'bool',
            'float': 'float'
        }
        
        return f'{prefix}self.config["{name}"] = {type_mapping.get(config_type, "str")}("{default}")'


@BlockFactory.register_block
class AIGenerateBlock(BaseBlock):
    """AI生成积木块"""
    
    def get_category(self) -> BlockCategory:
        return BlockCategory.AI
    
    def get_color(self) -> str:
        return "#F44336"
    
    def get_name(self) -> str:
        return "AI生成"
    
    def get_description(self) -> str:
        return "使用AI生成工具代码"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'tool_description',
                'type': 'text',
                'label': '工具功能描述',
                'default': '这个工具用于计算数学表达式',
                'required': True
            },
            {
                'name': 'tool_name',
                'type': 'string',
                'label': '工具名称',
                'default': 'calculate',
                'required': True
            }
        ]
    
    def generate_code(self, indent: int = 0) -> str:
        # 这个积木块不会直接生成代码，而是通过AI生成
        prefix = " " * indent
        return f'{prefix}# AI生成的代码将在这里'
