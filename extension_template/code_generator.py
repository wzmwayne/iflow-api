# -*- coding: utf-8 -*-
"""
代码生成器
从积木块生成扩展代码

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

from typing import List, Dict, Any
from datetime import datetime
try:
    from .blocks import BaseBlock
except ImportError:
    from blocks import BaseBlock


class ExtensionCodeGenerator:
    """扩展代码生成器"""
    
    def __init__(self):
        self.blocks: List[BaseBlock] = []
    
    def add_block(self, block: BaseBlock):
        """添加积木块"""
        self.blocks.append(block)
    
    def remove_block(self, block: BaseBlock):
        """移除积木块"""
        if block in self.blocks:
            self.blocks.remove(block)
    
    def clear_blocks(self):
        """清空所有积木块"""
        self.blocks = []
    
    def generate_extension_code(self) -> str:
        """生成完整的扩展代码"""
        # 分类积木块
        extension_info = None
        tools = []
        prompts = []
        lifecycles = []
        configs = []
        dependencies = []
        
        for block in self.blocks:
            if block.__class__.__name__ == 'ExtensionInfoBlock':
                extension_info = block
            elif block.__class__.__name__ == 'ToolBlock':
                tools.append(block)
            elif block.__class__.__name__ == 'PromptBlock':
                prompts.append(block)
            elif block.__class__.__name__ == 'LifecycleBlock':
                lifecycles.append(block)
            elif block.__class__.__name__ == 'ConfigBlock':
                configs.append(block)
            elif block.__class__.__name__ == 'DependencyBlock':
                dependencies.append(block)
        
        # 生成代码
        code = self._generate_header()
        code += self._generate_imports(dependencies)
        code += self._generate_class_definition(extension_info)
        code += self._generate_init_method(extension_info, configs)
        code += self._generate_lifecycle_methods(lifecycles)
        code += self._generate_get_prompt(prompts)
        code += self._generate_get_tools(tools)
        code += self._generate_get_tool_descriptions(tools)
        code += self._generate_tool_methods(tools)
        code += self._generate_dependency_methods(dependencies)
        code += self._generate_footer()
        
        return code
    
    def _generate_header(self) -> str:
        """生成文件头"""
        return '''# -*- coding: utf-8 -*-
"""
扩展名称：Your Extension
扩展描述：Your Description
作者：wzmwayne_and_iflow_ai
版本：1.0.0
"""

'''
    
    def _generate_imports(self, dependencies: List) -> str:
        """生成导入语句"""
        imports = [
            "import os",
            "import sys",
            "from typing import Dict, Callable, Tuple",
            "from datetime import datetime",
            "",
            "# 导入父目录的基类",
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
            "from base_extension import BaseExtension",
            ""
        ]
        
        # 添加依赖导入
        for dep_block in dependencies:
            packages = dep_block.get_parameter('packages', '')
            for pkg in packages.split(','):
                pkg = pkg.strip()
                if pkg:
                    imports.append(f"import {pkg}")
        
        imports.append("")
        imports.append("")
        return "\n".join(imports)
    
    def _generate_class_definition(self, extension_info: BaseBlock) -> str:
        """生成类定义"""
        if extension_info:
            name = extension_info.get_parameter('extension_name', 'MyExtension')
            desc = extension_info.get_parameter('description', '我的扩展')
        else:
            name = 'MyExtension'
            desc = '我的扩展'
        
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        
        return f'''class {class_name}(BaseExtension):
    """
    {desc}
    """
    
'''
    
    def _generate_init_method(self, extension_info: BaseBlock, configs: List) -> str:
        """生成 __init__ 方法"""
        code = '''    def __init__(self):
        super().__init__()
'''
        
        if extension_info:
            name = extension_info.get_parameter('extension_name', 'my_extension')
            desc = extension_info.get_parameter('description', '我的扩展')
            version = extension_info.get_parameter('version', '1.0.0')
            author = extension_info.get_parameter('author', 'wzmwayne_and_iflow_ai')
            
            code += f'''
        self.name = "{name}"
        self.description = "{desc}"
        self.version = "{version}"
        self.author = "{author}"
'''
        
        # 添加配置
        if configs:
            code += '''
        
        # 扩展配置
        self.config = {}
'''
            for config in configs:
                config_name = config.get_parameter('config_name', 'option')
                config_type = config.get_parameter('config_type', 'string')
                config_default = config.get_parameter('config_default', '')
                
                type_mapping = {
                    'string': 'str',
                    'int': 'int',
                    'bool': 'bool',
                    'float': 'float'
                }
                
                code += f'        self.config["{config_name}"] = {type_mapping.get(config_type, "str")}("{config_default}")\n'
        
        code += '\n'
        return code
    
    def _generate_lifecycle_methods(self, lifecycles: List) -> str:
        """生成生命周期方法"""
        code = ''
        
        # 按类型分组
        lifecycle_map = {}
        for lc in lifecycles:
            lc_type = lc.get_parameter('lifecycle_type', 'on_load')
            lifecycle_map[lc_type] = lc
        
        # 生成方法
        for lc_type in ['on_load', 'on_unload', 'on_before_tool_call', 'on_after_tool_call']:
            if lc_type in lifecycle_map:
                code += lifecycle_map[lc_type].generate_code(indent=4)
                code += '\n\n'
            else:
                # 生成空方法
                code += f'    def {lc_type}(self):\n'
                code += f'        """{lc_type}"""\n'
                code += f'        pass\n\n'
        
        return code
    
    def _generate_get_prompt(self, prompts: List) -> str:
        """生成 get_prompt 方法"""
        code = '''    def get_prompt(self) -> str:
        """返回扩展的提示词"""
'''
        
        if prompts:
            # 合并所有提示词
            prompt_code = '        prompt = """\\n'
            for prompt in prompts:
                prompt_text = prompt.get_parameter('prompt_text', '')
                prompt_code += prompt_text + '\\n\\n'
            prompt_code += '"""'
            code += '\n' + prompt_code
            code += '\n        return prompt.strip()'
        else:
            code += '\n        return ""'
        
        code += '\n\n'
        return code
    
    def _generate_get_tools(self, tools: List) -> str:
        """生成 get_tools 方法"""
        code = '''    def get_tools(self) -> Dict[str, Callable]:
        """返回工具处理函数字典"""
        return {
'''
        
        for tool in tools:
            tool_name = tool.get_parameter('tool_name', 'my_tool')
            code += f'            \'{tool_name}\': self.{tool_name},\n'
        
        code += '        }\n\n'
        return code
    
    def _generate_get_tool_descriptions(self, tools: List) -> str:
        """生成 get_tool_descriptions 方法"""
        code = '''    def get_tool_descriptions(self) -> Dict[str, str]:
        """返回工具描述字典"""
        return {
'''
        
        for tool in tools:
            tool_name = tool.get_parameter('tool_name', 'my_tool')
            tool_desc = tool.get_parameter('tool_description', '我的工具')
            code += f'            \'{tool_name}\': \'{tool_desc}\',\n'
        
        code += '        }\n\n'
        return code
    
    def _generate_tool_methods(self, tools: List) -> str:
        """生成工具方法"""
        code = ''
        
        for tool in tools:
            code += tool.generate_code(indent=4)
            code += '\n\n'
        
        return code
    
    def _generate_dependency_methods(self, dependencies: List) -> str:
        """生成依赖方法"""
        code = ''
        
        if dependencies:
            code += '''    def get_dependencies(self) -> list:
        """返回依赖的包列表"""
'''
            for dep in dependencies:
                packages = dep.get_parameter('packages', '')
                package_list = [f'"{p.strip()}"' for p in packages.split(',')]
                code += f'        return [{", ".join(package_list)}]\n\n'
            
            code += '''    def check_dependencies(self) -> Tuple[bool, list]:
        """检查依赖是否已安装"""
        missing = []
        for package in self.get_dependencies():
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        return len(missing) == 0, missing
'''
        else:
            code += '''    def get_dependencies(self) -> list:
        """返回依赖的包列表"""
        return []
'''
        
        code += '\n\n'
        return code
    
    def _generate_footer(self) -> str:
        """生成文件尾"""
        return '''# 扩展实例（必须）
Extension = <类名>
'''
    
    def save_to_file(self, filepath: str):
        """保存代码到文件"""
        code = self.generate_extension_code()
        
        # 替换类名占位符
        extension_info = None
        for block in self.blocks:
            if block.__class__.__name__ == 'ExtensionInfoBlock':
                extension_info = block
                break
        
        if extension_info:
            name = extension_info.get_parameter('extension_name', 'MyExtension')
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code = code.replace('<类名>', class_name)
        else:
            code = code.replace('<类名>', 'MyExtension')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return filepath