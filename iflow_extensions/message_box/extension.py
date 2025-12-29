# -*- coding: utf-8 -*-
"""
信息框扩展
提供普通和高级信息框功能，让AI可以向用户展示信息
"""

import os
import sys
from typing import Dict, Callable, Tuple

# 导入父目录的基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension


class MessageBoxExtension(BaseExtension):
    """信息框扩展"""
    
    def __init__(self):
        super().__init__()
        self.name = "message_box"
        self.description = "提供普通和高级信息框功能，让AI可以向用户展示信息"
        self.version = "1.0.0"
        self.author = "wzmwayne_and_iflow_ai"
    
    def get_prompt(self) -> str:
        """获取扩展提示词"""
        prompt = """
【信息框扩展】
此扩展提供信息框功能，让AI可以向用户展示信息。

你可以调用以下工具来展示信息框：
- @show_message(标题,内容) - 显示普通信息框，格式: @show_message(标题,内容)
- @show_advanced_message(标题,内容,类型,按钮) - 显示高级信息框，格式: @show_advanced_message(标题,内容,类型,按钮)

普通信息框参数：
- 标题: 信息框的标题
- 内容: 要显示的信息内容

高级信息框参数：
- 标题: 信息框的标题
- 内容: 要显示的信息内容
- 类型: 信息框类型，可选: info(信息), warning(警告), error(错误), question(询问)，默认为 info
- 按钮: 按钮类型，可选: ok(确定), ok_cancel(确定/取消), yes_no(是/否)，默认为 ok

使用说明：
1. 当需要向用户展示重要信息时，使用 @show_message
2. 当需要更丰富的信息展示时，使用 @show_advanced_message
3. 高级信息框可以设置不同的类型和按钮，提供更好的用户体验

示例：
- 用户说"提醒我保存文件" -> @show_message(保存提醒,请记得保存您的工作)
- 用户说"警告用户操作风险" -> @show_advanced_message(操作警告,此操作可能会导致数据丢失,warning,yes_no)
- 用户说"显示错误信息" -> @show_advanced_message(错误,无法连接到服务器,error,ok)
"""
        return prompt.strip()
    
    def get_tools(self) -> Dict[str, Callable]:
        """获取工具处理函数"""
        return {
            'show_message': self.show_message,
            'show_advanced_message': self.show_advanced_message,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """获取工具描述"""
        return {
            'show_message': '显示普通信息框，格式: @show_message(标题,内容)',
            'show_advanced_message': '显示高级信息框，格式: @show_advanced_message(标题,内容,类型,按钮)',
        }
    
    def show_message(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        显示普通信息框
        
        参数:
            args: 参数字符串，格式: "标题,内容"
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        try:
            parts = args.split(',', 1)
            if len(parts) < 2:
                return False, "参数格式错误，应为: 标题,内容"
            
            title = parts[0].strip()
            content = parts[1].strip()
            
            if confirm_callback:
                # GUI版本：使用回调函数显示信息框
                # 这里简化处理，实际GUI版本需要实现自定义对话框
                confirm_callback(title, content)
                return True, f"已显示信息框: {title}"
            else:
                # CLI版本：打印信息
                print(f"\n{'='*50}")
                print(f"  {title}")
                print(f"{'='*50}")
                print(f"\n{content}\n")
                try:
                    input("\n按回车继续...")
                except (EOFError, KeyboardInterrupt):
                    pass
                return True, f"已显示信息框: {title}"
                
        except Exception as e:
            return False, f"显示信息框失败: {str(e)}"
    
    def show_advanced_message(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        显示高级信息框
        
        参数:
            args: 参数字符串，格式: "标题,内容,类型,按钮"
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        try:
            parts = args.split(',', 3)
            if len(parts) < 2:
                return False, "参数格式错误，应为: 标题,内容,类型,按钮"
            
            title = parts[0].strip()
            content = parts[1].strip()
            msg_type = parts[2].strip() if len(parts) > 2 else 'info'
            buttons = parts[3].strip() if len(parts) > 3 else 'ok'
            
            # 验证类型参数
            valid_types = ['info', 'warning', 'error', 'question']
            if msg_type not in valid_types:
                return False, f"类型参数错误，可选: {', '.join(valid_types)}"
            
            # 验证按钮参数
            valid_buttons = ['ok', 'ok_cancel', 'yes_no']
            if buttons not in valid_buttons:
                return False, f"按钮参数错误，可选: {', '.join(valid_buttons)}"
            
            # 类型图标映射
            type_icons = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'question': '❓'
            }
            
            icon = type_icons[msg_type]
            
            if confirm_callback:
                # GUI版本：使用回调函数显示高级信息框
                # 这里简化处理，实际GUI版本需要实现自定义对话框
                confirm_callback(f"{icon} {title}", f"{content}\n\n类型: {msg_type}\n按钮: {buttons}")
                return True, f"已显示高级信息框: {title} (类型: {msg_type})"
            else:
                # CLI版本：打印高级信息
                print(f"\n{'='*50}")
                print(f"  {icon} {title}")
                print(f"{'='*50}")
                print(f"\n{content}\n")
                print(f"类型: {msg_type}")
                print(f"按钮: {buttons}")
                
                # 根据按钮类型获取用户响应
                if buttons == 'ok':
                    try:
                        input("\n按回车继续...")
                    except (EOFError, KeyboardInterrupt):
                        pass
                    return True, f"用户点击了确定"
                elif buttons == 'ok_cancel':
                    try:
                        choice = input("\n输入 o 确定或 c 取消: ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        choice = 'c'
                    if choice == 'o':
                        return True, f"用户点击了确定"
                    else:
                        return True, f"用户点击了取消"
                elif buttons == 'yes_no':
                    try:
                        choice = input("\n输入 y 是 或 n 否: ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        choice = 'n'
                    if choice == 'y':
                        return True, f"用户点击了是"
                    else:
                        return True, f"用户点击了否"
                
        except Exception as e:
            return False, f"显示高级信息框失败: {str(e)}"


# 扩展实例
Extension = MessageBoxExtension