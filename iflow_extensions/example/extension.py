# -*- coding: utf-8 -*-
"""
示例扩展
这是一个简单的扩展示例，展示如何创建和注册扩展
"""

import os
import sys
from typing import Dict, Callable, Tuple
from datetime import datetime

# 导入父目录的基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension


class ExampleExtension(BaseExtension):
    """示例扩展类"""
    
    def __init__(self):
        super().__init__()
        self.name = "example"
        self.description = "这是一个扩展示例，展示如何创建自定义扩展"
        self.version = "1.0.0"
        self.author = "wzmwayne_and_iflow_ai"
        
        # 扩展配置（可选）
        self.config = {
            'greeting': '你好',
            'max_retries': 3
        }
    
    def on_load(self):
        """扩展加载时调用"""
        print(f"[示例扩展] {self.name} 已加载")
    
    def on_unload(self):
        """扩展卸载时调用"""
        print(f"[示例扩展] {self.name} 已卸载")
    
    def get_prompt(self) -> str:
        """返回扩展的提示词，将添加到系统提示词中"""
        prompt = """
【示例扩展】
此扩展提供简单的示例工具，展示扩展系统的使用方法。

你可以调用以下工具：
- @hello(名字) - 向指定的人打招呼，例如 @hello(张三)
- @get_time() - 获取当前时间
- @calculate(表达式) - 计算数学表达式，例如 @calculate(2+3*4)
- @repeat(内容,次数) - 重复指定内容，例如 @repeat(你好,3)

使用说明：
1. 这些工具不需要任何权限
2. 工具执行结果会返回给AI
3. 可以在对话中随时使用这些工具

示例：
- 用户说"向李四打招呼" -> AI调用 @hello(李四)
- 用户说"现在几点了" -> AI调用 @get_time()
- 用户说"计算10+20" -> AI调用 @calculate(10+20)
"""
        return prompt.strip()
    
    def get_tools(self) -> Dict[str, Callable]:
        """返回工具处理函数字典"""
        return {
            'hello': self.hello,
            'get_time': self.get_time,
            'calculate': self.calculate,
            'repeat': self.repeat,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """返回工具描述字典"""
        return {
            'hello': '向指定的人打招呼，格式: @hello(名字)',
            'get_time': '获取当前时间，格式: @get_time()',
            'calculate': '计算数学表达式，格式: @calculate(表达式)',
            'repeat': '重复指定内容，格式: @repeat(内容,次数)',
        }
    
    def hello(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        向指定的人打招呼
        
        参数:
            args: 名字
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        name = args.strip() if args else "朋友"
        greeting = self.config.get('greeting', '你好')
        return True, f"{greeting}，{name}！很高兴见到你。"
    
    def get_time(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        获取当前时间
        
        参数:
            args: 忽略
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        now = datetime.now()
        time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
        weekday = now.strftime("%A")
        weekday_map = {
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日',
        }
        chinese_weekday = weekday_map.get(weekday, weekday)
        return True, f"当前时间是：{time_str} {chinese_weekday}"
    
    def calculate(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        计算数学表达式
        
        参数:
            args: 数学表达式，例如 "2+3*4"
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        try:
            # 使用eval计算表达式（注意：在生产环境中应该使用更安全的方法）
            # 这里为了示例简单，只允许基本的数学运算
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in args):
                return False, "表达式包含非法字符，只支持数字和 + - * / ( )"
            
            result = eval(args)
            return True, f"计算结果：{args} = {result}"
        except ZeroDivisionError:
            return False, "错误：除数不能为零"
        except SyntaxError:
            return False, "错误：表达式语法错误"
        except Exception as e:
            return False, f"计算失败：{str(e)}"
    
    def repeat(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        重复指定内容
        
        参数:
            args: 内容和次数，格式: "内容,次数"
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message)
        """
        try:
            parts = args.split(',', 1)
            if len(parts) < 2:
                return False, "参数格式错误，应为: 内容,次数"
            
            content = parts[0].strip()
            times = int(parts[1].strip())
            
            if times <= 0:
                return False, "次数必须大于0"
            
            if times > 100:
                return False, "次数不能超过100"
            
            result = (content + " ") * times
            return True, result.strip()
        except ValueError:
            return False, "次数必须是数字"
        except Exception as e:
            return False, f"重复失败：{str(e)}"
    
    def get_config_schema(self) -> Dict[str, dict]:
        """返回配置项定义"""
        return {
            'greeting': {
                'type': 'string',
                'default': '你好',
                'description': '打招呼时的问候语',
            },
            'max_retries': {
                'type': 'int',
                'default': 3,
                'description': '最大重试次数',
            }
        }
    
    def get_dependencies(self) -> list:
        """返回依赖的包列表"""
        return []  # 此扩展不需要额外的依赖


# 扩展实例（必须）
Extension = ExampleExtension