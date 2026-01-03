# -*- coding: utf-8 -*-
"""
积木块编译器演示脚本
自动创建一个示例扩展
"""

import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocks'))

from blocks import BaseBlock, BlockFactory
from block_types import (
    ExtensionInfoBlock, ToolBlock, PromptBlock, LifecycleBlock,
    DependencyBlock, ConfigBlock
)
from code_generator import ExtensionCodeGenerator


def create_demo_extension():
    """创建演示扩展"""
    print("=" * 60)
    print("iFlow 积木块编译器 - 演示")
    print("=" * 60)
    
    generator = ExtensionCodeGenerator()
    
    # 1. 添加扩展信息积木块
    print("\n1. 添加扩展信息积木块...")
    info_block = ExtensionInfoBlock()
    info_block.set_parameter('extension_name', 'demo_extension')
    info_block.set_parameter('description', '演示扩展 - 展示积木块编译器功能')
    info_block.set_parameter('version', '1.0.0')
    info_block.set_parameter('author', 'iFlow Team')
    generator.add_block(info_block)
    print("   ✓ 扩展信息已添加")
    
    # 2. 添加工具积木块
    print("\n2. 添加工具积木块...")
    tool_block = ToolBlock()
    tool_block.set_parameter('tool_name', 'greet')
    tool_block.set_parameter('tool_description', '向用户打招呼')
    tool_block.set_parameter('tool_code', '''name = args if args else "用户"
return True, f"你好，{name}！欢迎使用 iFlow！"''')
    generator.add_block(tool_block)
    print("   ✓ 工具 'greet' 已添加")
    
    # 3. 添加提示词积木块
    print("\n3. 添加提示词积木块...")
    prompt_block = PromptBlock()
    prompt_block.set_parameter('prompt_text', '''【演示扩展】
此扩展展示积木块编译器的功能。

可用工具：
- @greet(名字) - 向指定的人打招呼

使用说明：
当用户想要打招呼时，使用 @greet 工具。

示例：
- 用户说"你好" -> AI调用 @greet("用户")
- 用户说"你好，张三" -> AI调用 @greet("张三")''')
    generator.add_block(prompt_block)
    print("   ✓ 提示词已添加")
    
    # 4. 添加生命周期积木块
    print("\n4. 添加生命周期积木块...")
    lifecycle_block = LifecycleBlock()
    lifecycle_block.set_parameter('lifecycle_type', 'on_load')
    lifecycle_block.set_parameter('lifecycle_code', 'print("演示扩展已加载，积木块编译器工作正常！")')
    generator.add_block(lifecycle_block)
    print("   ✓ 生命周期方法已添加")
    
    # 5. 生成代码
    print("\n5. 生成代码...")
    code = generator.generate_extension_code()
    print("   ✓ 代码生成完成")
    
    # 6. 保存到文件
    print("\n6. 保存到文件...")
    output_dir = os.path.join(os.path.dirname(__file__), 'make', 'demo_extension', 'code')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extension.py')
    generator.save_to_file(output_file)
    print(f"   ✓ 代码已保存到: {output_file}")
    
    # 7. 显示生成的代码
    print("\n" + "=" * 60)
    print("生成的代码:")
    print("=" * 60)
    print(code)
    print("=" * 60)
    
    # 8. 显示文件结构
    print("\n" + "=" * 60)
    print("文件结构:")
    print("=" * 60)
    print("extension_template/")
    print("├── make/")
    print("│   ├── demo_extension/")
    print("│   │   ├── code/")
    print("│   │   │   └── extension.py")
    print("│   │   └── out/ (用于存放打包后的扩展)")
    print("│   ├── hello_world/")
    print("│   │   ├── code/")
    print("│   │   │   └── extension.py")
    print("│   │   └── out/")
    print("│   └── calculator/")
    print("│       ├── code/")
    print("│       │   └── extension.py")
    print("│       └── out/")
    
    print("\n" + "=" * 60)
    print("✓ 演示完成！")
    print("=" * 60)
    print("\n提示:")
    print("1. 使用 GUI 版本: python block_compiler.py (需要桌面环境)")
    print("2. 使用 CLI 版本: python block_compiler_cli.py (交互式)")
    print("3. 查看生成的代码: cat make/demo_extension/code/extension.py")
    print("4. 打包扩展: 使用 compiler.py")


if __name__ == "__main__":
    create_demo_extension()