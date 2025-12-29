# -*- coding: utf-8 -*-
"""
电脑控制扩展
提供鼠标、键盘、屏幕截图等电脑操作功能
"""

import os
import sys
from typing import Dict, Callable, Tuple
from datetime import datetime

# 导入父目录的基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension


# 尝试导入 pyautogui
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class ComputerControlExtension(BaseExtension):
    """电脑控制扩展"""
    
    def __init__(self):
        super().__init__()
        self.name = "computer_control"
        self.description = "提供鼠标、键盘、屏幕截图等电脑操作功能"
        self.version = "1.0.0"
        self.author = "wzmwayne_and_iflow_ai"
        
        # 控制权限状态
        self.control_enabled = False
        
        # 截图目录
        self.screenshot_dir = "iflow_screenshots"
        self._ensure_screenshot_dir()
    
    def _ensure_screenshot_dir(self):
        """确保截图目录存在"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def get_prompt(self) -> str:
        """获取扩展提示词"""
        prompt = """
【电脑控制扩展】
此扩展提供电脑操作功能，需要用户授权后才能使用。

你可以调用以下工具来操作电脑（所有工具都需要用户确认）：
- @mouse_move(x,y) - 移动鼠标到指定坐标，例如 @mouse_move(500,300)
- @mouse_click(按钮) - 点击鼠标，按钮可以是 left、right、middle，例如 @mouse_click(left)
- @keyboard(文本) - 输入文本内容，例如 @keyboard(Hello World)
- @keyboard(key:按键) - 按下特殊按键，例如 @keyboard(key:enter)
  特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12, backspace, delete 等
- @screenshot() - 获取屏幕截图并保存，AI可以看到截图内容
- @view_screenshot(文件名) - 分析指定的屏幕截图内容
- @wait(秒数) - 等待指定秒数，例如 @wait(2)
- @request_computer_control() - 请求获得电脑操作权限，获得权限后所有工具和指令自动允许，无需用户确认

重要说明：
1. 所有工具默认需要用户确认后才执行
2. 使用 @request_computer_control() 获取权限后，所有操作将自动允许
3. 电脑控制权限适用于需要连续执行多个指令的场景
4. 当用户需要你进行图形界面操作时，按以下步骤进行：
   a. 首先调用 @screenshot() 查看当前屏幕内容
   b. 然后调用 @request_computer_control() 获取电脑控制权限
   c. 获得权限后，所有工具和指令将自动允许执行
   d. 在每一步操作前，必须先调用 @screenshot() 查看当前屏幕状态
   e. 依次执行控制操作（@mouse_move, @mouse_click, @keyboard 等）
   f. 完成操作后，必须调用 @screenshot() 查看操作结果，确认是否成功
   g. 如果需要等待界面响应，可以使用 @wait(秒数) 等待指定时间

示例流程：
- 用户说"帮我点击屏幕上的某个按钮" -> 先 @screenshot() 查看屏幕，然后 @request_computer_control() 获取权限，再 @screenshot() 确认位置，最后 @mouse_move() 和 @mouse_click() 执行操作，完成后 @screenshot() 查看结果
"""
        return prompt.strip()
    
    def get_tools(self) -> Dict[str, Callable]:
        """获取工具处理函数"""
        return {
            'mouse_move': self.mouse_move,
            'mouse_click': self.mouse_click,
            'keyboard': self.keyboard_input,
            'screenshot': self.take_screenshot,
            'view_screenshot': self.view_screenshot,
            'wait': self.wait,
            'request_computer_control': self.request_computer_control,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """获取工具描述"""
        return {
            'mouse_move': '移动鼠标到指定坐标，格式: @mouse_move(x,y)',
            'mouse_click': '点击鼠标，格式: @mouse_click(按钮)，按钮可选: left/right/middle',
            'keyboard': '键盘输入，格式: @keyboard(文本) 或 @keyboard(key:按键)',
            'screenshot': '获取屏幕截图，格式: @screenshot()',
            'view_screenshot': '分析屏幕截图，格式: @view_screenshot(文件名)',
            'wait': '等待指定秒数，格式: @wait(秒数)',
            'request_computer_control': '请求获得电脑操作权限，格式: @request_computer_control()',
        }
    
    def request_computer_control(self, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        请求获得电脑操作权限
        
        参数:
            confirm_callback: 确认回调函数，用于GUI版本显示确认对话框
                            函数签名: confirm_callback(title: str, message: str) -> bool
                            返回 True 表示用户同意，False 表示用户拒绝
        
        返回:
            (success, message) - (是否成功, 结果消息)
        """
        if confirm_callback:
            # 使用回调函数进行确认（GUI版本）
            allowed = confirm_callback(
                "AI电脑操作权限请求",
                "AI请求获得电脑操作权限\n\n允许AI模拟鼠标、键盘操作\n并获取屏幕内容"
            )
        else:
            # 命令行版本需要手动确认
            print("\n[系统] AI请求获得电脑操作权限")
            print("允许AI模拟鼠标、键盘操作并获取屏幕内容")
            confirm = input("是否允许？: ").strip().lower()
            allowed = confirm == 'y'
        
        if allowed:
            self.control_enabled = True
            return True, "已获得电脑操作权限"
        else:
            return False, "用户拒绝授予权限"
    
    def mouse_move(self, args: str) -> Tuple[bool, str]:
        """
        移动鼠标到指定坐标
        
        参数:
            args: 坐标参数，格式: "x,y"
        
        返回:
            (success, message)
        """
        if not PYAUTOGUI_AVAILABLE:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        
        if not self.control_enabled:
            return False, "需要先调用 @request_computer_control() 获取电脑操作权限"
        
        try:
            parts = args.split(',')
            if len(parts) == 2:
                x, y = int(parts[0].strip()), int(parts[1].strip())
                pyautogui.moveTo(x, y, duration=0.5)
                return True, f"鼠标已移动到 ({x}, {y})"
            else:
                return False, "参数格式错误，应为: x,y"
        except Exception as e:
            return False, f"移动鼠标失败: {str(e)}"
    
    def mouse_click(self, args: str) -> Tuple[bool, str]:
        """
        点击鼠标
        
        参数:
            args: 按钮参数，可选: left/right/middle，默认为 left
        
        返回:
            (success, message)
        """
        if not PYAUTOGUI_AVAILABLE:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        
        if not self.control_enabled:
            return False, "需要先调用 @request_computer_control() 获取电脑操作权限"
        
        try:
            button = args.strip() if args else 'left'
            pyautogui.click(button=button)
            return True, f"已点击鼠标 {button}"
        except Exception as e:
            return False, f"鼠标点击失败: {str(e)}"
    
    def keyboard_input(self, args: str) -> Tuple[bool, str]:
        """
        键盘输入
        
        支持两种模式：
        1. 文本输入：@keyboard(Hello World) - 输入文本
        2. 特殊按键：@keyboard(key:enter) - 按Enter键
        
        参数:
            args: 输入内容，可以是文本或 key:按键
        
        返回:
            (success, message)
        """
        if not PYAUTOGUI_AVAILABLE:
            return False, "pyautogui模块未安装，无法执行键盘操作"
        
        if not self.control_enabled:
            return False, "需要先调用 @request_computer_control() 获取电脑操作权限"
        
        try:
            # 检查是否是特殊按键
            if args.startswith('key:'):
                key_name = args[4:].strip().lower()
                pyautogui.press(key_name)
                return True, f"已按下按键: {key_name}"
            else:
                # 普通文本输入
                pyautogui.typewrite(args)
                return True, f"已输入文本: {args}"
        except Exception as e:
            return False, f"键盘输入失败: {str(e)}"
    
    def take_screenshot(self) -> Tuple[bool, str]:
        """
        获取屏幕截图
        
        返回:
            (success, message) - 成功时message包含截图文件路径
        """
        if not PYAUTOGUI_AVAILABLE:
            return False, "pyautogui模块未安装，无法执行截图操作"
        
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)
            return True, f"屏幕截图已保存到: {filepath}\n截图尺寸: {screenshot.size}"
        except Exception as e:
            error_msg = str(e)
            if "pyscreeze" in error_msg or "Pillow" in error_msg:
                return False, f"获取屏幕截图失败: pyautogui依赖不兼容\n建议: pip install --upgrade pillow pyscreeze pyautogui\n错误详情: {error_msg}"
            else:
                return False, f"获取屏幕截图失败: {error_msg}"
    
    def view_screenshot(self, filename: str) -> Tuple[bool, str]:
        """
        分析屏幕截图
        
        参数:
            filename: 截图文件名
        
        返回:
            (success, message) - 成功时message包含base64编码的图像数据
        """
        filepath = os.path.join(self.screenshot_dir, filename)
        if not os.path.exists(filepath):
            return False, f"截图文件不存在: {filepath}"
        
        try:
            # 读取截图并转换为base64
            with open(filepath, 'rb') as f:
                img_data = f.read()
            
            import base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            return True, f"[屏幕截图: {filename}]\n[图像数据: {img_base64[:500]}...]\n请分析这个截图的内容"
            
        except Exception as e:
            return False, f"读取截图失败: {str(e)}"
    
    def wait(self, args: str) -> Tuple[bool, str]:
        """
        等待指定秒数
        
        参数:
            args: 等待秒数（数字）
        
        返回:
            (success, message)
        """
        try:
            import time
            seconds = float(args.strip())
            if seconds <= 0:
                return False, "等待时间必须大于0"
            
            time.sleep(seconds)
            return True, f"已等待 {seconds} 秒"
        except ValueError:
            return False, "参数格式错误，应为秒数（数字）"
        except Exception as e:
            return False, f"等待失败: {str(e)}"
    
    def is_control_enabled(self) -> bool:
        """检查是否已获得控制权限"""
        return self.control_enabled
    
    def set_control_enabled(self, enabled: bool):
        """设置控制权限状态"""
        self.control_enabled = enabled


# 扩展实例
Extension = ComputerControlExtension