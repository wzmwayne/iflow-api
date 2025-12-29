# -*- coding: utf-8 -*-
"""
积木块编译器 - 命令行版本
用于通过命令行创建 iFlow 扩展
"""

import os
import sys
import json
from typing import List, Dict, Any

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocks'))

from blocks import BaseBlock, BlockFactory
from block_types import (
    ExtensionInfoBlock, ToolBlock, PromptBlock, LifecycleBlock,
    DependencyBlock, ConfigBlock
)
from code_generator import ExtensionCodeGenerator


class BlockCompilerCLI:
    """积木块编译器命令行界面"""
    
    def __init__(self):
        self.code_generator = ExtensionCodeGenerator()
        self.blocks: List[BaseBlock] = []
    
    def show_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("iFlow 积木块编译器 - 命令行版本")
            print("=" * 60)
            print(f"当前积木块数量: {len(self.blocks)}")
            print("\n可用操作:")
            print("1. 添加积木块")
            print("2. 查看当前积木块")
            print("3. 删除积木块")
            print("4. 生成代码")
            print("5. 保存项目")
            print("6. 加载项目")
            print("7. 清空所有积木块")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-7): ").strip()
            
            if choice == '0':
                print("再见！")
                break
            elif choice == '1':
                self._add_block()
            elif choice == '2':
                self._show_blocks()
            elif choice == '3':
                self._remove_block()
            elif choice == '4':
                self._generate_code()
            elif choice == '5':
                self._save_project()
            elif choice == '6':
                self._load_project()
            elif choice == '7':
                self._clear_blocks()
            else:
                print("无效的选择！")
    
    def _add_block(self):
        """添加积木块"""
        print("\n--- 可用的积木块类型 ---")
        print("1. 扩展信息 (ExtensionInfo)")
        print("2. 工具 (Tool)")
        print("3. 提示词 (Prompt)")
        print("4. 生命周期 (Lifecycle)")
        print("5. 依赖包 (Dependency)")
        print("6. 配置 (Config)")
        print("0. 返回")
        
        choice = input("\n请选择积木块类型 (0-6): ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            self._add_extension_info()
        elif choice == '2':
            self._add_tool()
        elif choice == '3':
            self._add_prompt()
        elif choice == '4':
            self._add_lifecycle()
        elif choice == '5':
            self._add_dependency()
        elif choice == '6':
            self._add_config()
        else:
            print("无效的选择！")
    
    def _add_extension_info(self):
        """添加扩展信息积木块"""
        print("\n--- 添加扩展信息积木块 ---")
        
        name = input("扩展名称 (默认: my_extension): ").strip() or "my_extension"
        desc = input("扩展描述 (默认: 我的扩展): ").strip() or "我的扩展"
        version = input("版本号 (默认: 1.0.0): ").strip() or "1.0.0"
        author = input("作者 (默认: Your Name): ").strip() or "Your Name"
        
        block = ExtensionInfoBlock()
        block.set_parameter('extension_name', name)
        block.set_parameter('description', desc)
        block.set_parameter('version', version)
        block.set_parameter('author', author)
        
        self.blocks.append(block)
        print(f"\n✓ 已添加扩展信息积木块: {name}")
    
    def _add_tool(self):
        """添加工具积木块"""
        print("\n--- 添加工具积木块 ---")
        
        tool_name = input("工具名称 (默认: my_tool): ").strip() or "my_tool"
        tool_desc = input("工具描述 (默认: 我的工具): ").strip() or "我的工具"
        
        print("\n工具代码 (输入完成后按 Ctrl+D 或输入 'END' 结束):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        
        tool_code = '\n'.join(lines) if lines else 'return True, "操作结果"'
        
        block = ToolBlock()
        block.set_parameter('tool_name', tool_name)
        block.set_parameter('tool_description', tool_desc)
        block.set_parameter('tool_code', tool_code)
        
        self.blocks.append(block)
        print(f"\n✓ 已添加工具积木块: {tool_name}")
    
    def _add_prompt(self):
        """添加提示词积木块"""
        print("\n--- 添加提示词积木块 ---")
        
        print("提示词内容 (输入完成后按 Ctrl+D 或输入 'END' 结束):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        
        prompt_text = '\n'.join(lines) if lines else '【扩展】此扩展提供功能。'
        
        block = PromptBlock()
        block.set_parameter('prompt_text', prompt_text)
        
        self.blocks.append(block)
        print("\n✓ 已添加提示词积木块")
    
    def _add_lifecycle(self):
        """添加生命周期积木块"""
        print("\n--- 添加生命周期积木块 ---")
        print("1. on_load (加载时)")
        print("2. on_unload (卸载时)")
        print("3. on_before_tool_call (工具调用前)")
        print("4. on_after_tool_call (工具调用后)")
        
        lc_choice = input("请选择生命周期类型 (1-4): ").strip()
        
        lc_map = {
            '1': 'on_load',
            '2': 'on_unload',
            '3': 'on_before_tool_call',
            '4': 'on_after_tool_call'
        }
        
        if lc_choice not in lc_map:
            print("无效的选择！")
            return
        
        lc_type = lc_map[lc_choice]
        
        print(f"\n{lc_type} 代码 (输入完成后按 Ctrl+D 或输入 'END' 结束):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        
        lc_code = '\n'.join(lines) if lines else 'print(f"{lc_type} called")'
        
        block = LifecycleBlock()
        block.set_parameter('lifecycle_type', lc_type)
        block.set_parameter('lifecycle_code', lc_code)
        
        self.blocks.append(block)
        print(f"\n✓ 已添加生命周期积木块: {lc_type}")
    
    def _add_dependency(self):
        """添加依赖包积木块"""
        print("\n--- 添加依赖包积木块 ---")
        
        packages = input("依赖包列表 (用逗号分隔，默认: requests): ").strip() or "requests"
        
        block = DependencyBlock()
        block.set_parameter('packages', packages)
        
        self.blocks.append(block)
        print(f"\n✓ 已添加依赖包积木块: {packages}")
    
    def _add_config(self):
        """添加配置积木块"""
        print("\n--- 添加配置积木块 ---")
        
        config_name = input("配置名称 (默认: api_key): ").strip() or "api_key"
        
        print("配置类型:")
        print("1. string")
        print("2. int")
        print("3. bool")
        print("4. float")
        
        type_choice = input("请选择配置类型 (1-4): ").strip()
        
        type_map = {
            '1': 'string',
            '2': 'int',
            '3': 'bool',
            '4': 'float'
        }
        
        config_type = type_map.get(type_choice, 'string')
        config_default = input("默认值 (默认: ): ").strip()
        
        block = ConfigBlock()
        block.set_parameter('config_name', config_name)
        block.set_parameter('config_type', config_type)
        block.set_parameter('config_default', config_default)
        
        self.blocks.append(block)
        print(f"\n✓ 已添加配置积木块: {config_name}")
    
    def _show_blocks(self):
        """显示当前积木块"""
        if not self.blocks:
            print("\n当前没有积木块")
            return
        
        print("\n--- 当前积木块列表 ---")
        for i, block in enumerate(self.blocks, 1):
            print(f"{i}. {block.get_name()} - {block.get_description()}")
    
    def _remove_block(self):
        """删除积木块"""
        if not self.blocks:
            print("\n当前没有积木块")
            return
        
        self._show_blocks()
        
        try:
            index = int(input("\n请输入要删除的积木块编号: ").strip()) - 1
            if 0 <= index < len(self.blocks):
                removed = self.blocks.pop(index)
                print(f"\n✓ 已删除: {removed.get_name()}")
            else:
                print("无效的编号！")
        except ValueError:
            print("请输入有效的数字！")
    
    def _generate_code(self):
        """生成代码"""
        if not self.blocks:
            print("\n当前没有积木块，请先添加积木块")
            return
        
        # 获取扩展名称
        ext_name = "my_extension"
        for block in self.blocks:
            if block.__class__.__name__ == 'ExtensionInfoBlock':
                ext_name = block.get_parameter('extension_name', 'my_extension')
                break
        
        # 生成代码
        self.code_generator.clear_blocks()
        for block in self.blocks:
            self.code_generator.add_block(block)
        
        code = self.code_generator.generate_extension_code()
        
        # 保存到 make 文件夹
        output_dir = os.path.join(os.path.dirname(__file__), 'make', ext_name, 'code')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extension.py')
        
        self.code_generator.save_to_file(output_file)
        
        print(f"\n✓ 代码已生成并保存到: {output_file}")
        
        # 询问是否查看代码
        view = input("\n是否查看生成的代码? (y/n): ").strip().lower()
        if view == 'y':
            print("\n" + "-" * 60)
            print(code)
            print("-" * 60)
    
    def _save_project(self):
        """保存项目"""
        if not self.blocks:
            print("\n当前没有积木块")
            return
        
        filename = input("\n请输入项目文件名 (默认: project.json): ").strip() or "project.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # 收集积木块数据
        blocks_data = [block.to_dict() for block in self.blocks]
        
        # 保存到文件
        data = {
            'version': '1.0.0',
            'blocks': blocks_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 项目已保存到: {filepath}")
    
    def _load_project(self):
        """加载项目"""
        filename = input("\n请输入项目文件名 (默认: project.json): ").strip() or "project.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not os.path.exists(filepath):
            print(f"\n文件不存在: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空当前积木块
            self.blocks.clear()
            
            # 加载积木块
            for block_data in data.get('blocks', []):
                block = BlockFactory.create_block(block_data)
                if block:
                    self.blocks.append(block)
            
            print(f"\n✓ 项目已加载: {filepath}")
            print(f"加载了 {len(self.blocks)} 个积木块")
            
        except Exception as e:
            print(f"\n✗ 加载项目失败: {str(e)}")
    
    def _clear_blocks(self):
        """清空所有积木块"""
        if not self.blocks:
            print("\n当前没有积木块")
            return
        
        confirm = input("\n确定要清空所有积木块吗? (y/n): ").strip().lower()
        if confirm == 'y':
            self.blocks.clear()
            print("\n✓ 已清空所有积木块")


def main():
    """主函数"""
    compiler = BlockCompilerCLI()
    compiler.show_menu()


if __name__ == "__main__":
    main()