# -*- coding: utf-8 -*-
"""
测试代码生成器
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocks'))

from blocks import BaseBlock, BlockFactory
from block_types import (
    ExtensionInfoBlock, ToolBlock, PromptBlock, LifecycleBlock,
    DependencyBlock, ConfigBlock
)
from code_generator import ExtensionCodeGenerator


def test_simple_extension():
    """测试简单扩展生成"""
    print("=" * 60)
    print("测试 1: 简单扩展")
    print("=" * 60)
    
    generator = ExtensionCodeGenerator()
    
    # 添加扩展信息积木块
    info_block = ExtensionInfoBlock()
    info_block.set_parameter('extension_name', 'hello_world')
    info_block.set_parameter('description', '一个简单的打招呼扩展')
    info_block.set_parameter('version', '1.0.0')
    info_block.set_parameter('author', 'Test User')
    generator.add_block(info_block)
    
    # 添加工具积木块
    tool_block = ToolBlock()
    tool_block.set_parameter('tool_name', 'hello')
    tool_block.set_parameter('tool_description', '向用户打招呼')
    tool_block.set_parameter('tool_code', 'return True, "你好，世界！"')
    generator.add_block(tool_block)
    
    # 添加提示词积木块
    prompt_block = PromptBlock()
    prompt_block.set_parameter('prompt_text', '【打招呼扩展】\n此扩展用于向用户打招呼。\n\n可用工具：\n- @hello() - 向用户打招呼\n\n示例：\n- 用户说"你好" -> AI调用 @hello()')
    generator.add_block(prompt_block)
    
    # 生成代码
    code = generator.generate_extension_code()
    
    print("\n生成的代码:")
    print("-" * 60)
    print(code)
    print("-" * 60)
    
    # 保存到文件
    output_dir = os.path.join(os.path.dirname(__file__), 'make', 'hello_world', 'code')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extension.py')
    generator.save_to_file(output_file)
    print(f"\n✓ 代码已保存到: {output_file}")
    
    return True


def test_complete_extension():
    """测试完整扩展生成"""
    print("\n" + "=" * 60)
    print("测试 2: 完整扩展（包含所有功能）")
    print("=" * 60)
    
    generator = ExtensionCodeGenerator()
    
    # 添加扩展信息积木块
    info_block = ExtensionInfoBlock()
    info_block.set_parameter('extension_name', 'calculator')
    info_block.set_parameter('description', '一个计算器扩展')
    info_block.set_parameter('version', '2.0.0')
    info_block.set_parameter('author', 'Test User')
    generator.add_block(info_block)
    
    # 添加工具积木块
    tool1 = ToolBlock()
    tool1.set_parameter('tool_name', 'calculate')
    tool1.set_parameter('tool_description', '计算数学表达式')
    tool1.set_parameter('tool_code', '''try:
    result = eval(args)
    return True, f"计算结果: {result}"
except Exception as e:
    return False, f"计算错误: {str(e)}"''')
    generator.add_block(tool1)
    
    tool2 = ToolBlock()
    tool2.set_parameter('tool_name', 'square')
    tool2.set_parameter('tool_description', '计算平方')
    tool2.set_parameter('tool_code', '''try:
    num = float(args)
    result = num ** 2
    return True, f"{num} 的平方是 {result}"
except Exception as e:
    return False, f"计算错误: {str(e)}"''')
    generator.add_block(tool2)
    
    # 添加提示词积木块
    prompt_block = PromptBlock()
    prompt_block.set_parameter('prompt_text', '''【计算器扩展】
此扩展提供数学计算功能。

可用工具：
- @calculate(表达式) - 计算数学表达式
- @square(数字) - 计算数字的平方

使用说明：
1. 用户要求计算时使用 @calculate
2. 用户要求计算平方时使用 @square

示例：
- 用户说"计算 1+2*3" -> AI调用 @calculate("1+2*3")
- 用户说"5的平方是多少" -> AI调用 @square("5")''')
    generator.add_block(prompt_block)
    
    # 添加生命周期积木块
    lifecycle_block = LifecycleBlock()
    lifecycle_block.set_parameter('lifecycle_type', 'on_load')
    lifecycle_block.set_parameter('lifecycle_code', 'print("计算器扩展已加载")')
    generator.add_block(lifecycle_block)
    
    # 添加依赖积木块
    dep_block = DependencyBlock()
    dep_block.set_parameter('packages', 'math, random')
    generator.add_block(dep_block)
    
    # 添加配置积木块
    config_block = ConfigBlock()
    config_block.set_parameter('config_name', 'precision')
    config_block.set_parameter('config_type', 'int')
    config_block.set_parameter('config_default', '10')
    generator.add_block(config_block)
    
    # 生成代码
    code = generator.generate_extension_code()
    
    print("\n生成的代码:")
    print("-" * 60)
    print(code)
    print("-" * 60)
    
    # 保存到文件
    output_dir = os.path.join(os.path.dirname(__file__), 'make', 'calculator', 'code')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'extension.py')
    generator.save_to_file(output_file)
    print(f"\n✓ 代码已保存到: {output_file}")
    
    return True


def test_serialization():
    """测试积木块序列化和反序列化"""
    print("\n" + "=" * 60)
    print("测试 3: 积木块序列化和反序列化")
    print("=" * 60)
    
    # 创建积木块
    info_block = ExtensionInfoBlock()
    info_block.set_parameter('extension_name', 'test_ext')
    info_block.set_parameter('description', '测试扩展')
    info_block.set_parameter('version', '1.0.0')
    info_block.set_parameter('author', 'Test')
    
    # 序列化
    data = info_block.to_dict()
    print("\n序列化结果:")
    print(data)
    
    # 反序列化
    restored_block = BlockFactory.create_block(data)
    
    print("\n反序列化结果:")
    print(f"类型: {restored_block.__class__.__name__}")
    print(f"名称: {restored_block.get_name()}")
    print(f"参数: {restored_block.parameters}")
    
    # 验证
    assert restored_block.get_parameter('extension_name') == 'test_ext'
    assert restored_block.get_parameter('description') == '测试扩展'
    assert restored_block.get_parameter('version') == '1.0.0'
    assert restored_block.get_parameter('author') == 'Test'
    
    print("\n✓ 序列化和反序列化测试通过")
    
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("iFlow 积木块编译器 - 代码生成器测试")
    print("=" * 60)
    
    tests = [
        test_simple_extension,
        test_complete_extension,
        test_serialization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)