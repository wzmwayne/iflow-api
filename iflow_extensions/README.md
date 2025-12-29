# iFlow 扩展系统文档

## 目录结构

```
iflow_extensions/
├── __init__.py              # 扩展管理器
├── base_extension.py        # 扩展基类
├── computer_control/        # 电脑控制扩展示例
│   └── extension.py
└── [其他扩展]/
    └── extension.py
```

## 扩展开发指南

### 1. 创建扩展文件夹

每个扩展必须有自己的文件夹，文件夹内必须包含 `extension.py` 文件。

```
iflow_extensions/
└── my_extension/
    └── extension.py
```

### 2. 编写扩展代码

在 `extension.py` 中创建扩展类，继承 `BaseExtension`：

```python
# -*- coding: utf-8 -*-
"""
我的扩展
"""

import os
import sys
from typing import Dict, Callable, Tuple

# 导入基类
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_extension import BaseExtension


class MyExtension(BaseExtension):
    """我的扩展类"""
    
    def __init__(self):
        super().__init__()
        self.name = "my_extension"           # 扩展名称（必须唯一）
        self.description = "扩展描述"        # 扩展描述
        self.version = "1.0.0"               # 版本号
        self.author = "作者名"               # 作者
    
    def get_prompt(self) -> str:
        """返回扩展的提示词，将添加到系统提示词中"""
        return """
【我的扩展】
此扩展提供XX功能。

可用工具：
- @my_tool(参数) - 工具描述

使用示例：
- 用户说"帮我XX" -> AI调用 @my_tool(参数)
"""
    
    def get_tools(self) -> Dict[str, Callable]:
        """返回工具处理函数字典"""
        return {
            'my_tool': self.my_tool,
        }
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """返回工具描述字典"""
        return {
            'my_tool': '工具描述',
        }
    
    def my_tool(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
        """
        工具处理函数
        
        参数:
            args: 工具参数字符串
            confirm_callback: 确认回调函数（可选）
        
        返回:
            (success, message) - (是否成功, 结果消息)
        """
        try:
            # 执行工具逻辑
            result = do_something(args)
            return True, f"操作成功: {result}"
        except Exception as e:
            return False, f"操作失败: {str(e)}"


# 扩展实例（必须）
Extension = MyExtension
```

### 3. 扩展生命周期方法

| 方法 | 说明 | 调用时机 |
|------|------|----------|
| `on_load()` | 扩展加载时调用 | 程序启动加载扩展时 |
| `on_unload()` | 扩展卸载时调用 | 程序退出或扩展禁用时 |
| `on_before_tool_call(tool_name, args)` | 工具调用前调用 | 每次工具调用前 |
| `on_after_tool_call(tool_name, args, result)` | 工具调用后调用 | 每次工具调用后 |

### 4. 配置管理

扩展可以支持配置项：

```python
def get_config_schema(self) -> Dict[str, Any]:
    """定义配置项"""
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

def load_config(self, config: Dict[str, Any]):
    """加载配置"""
    self.config = config

def get_config_value(self, key: str, default: Any = None) -> Any:
    """获取配置值"""
    return self.config.get(key, default)
```

### 5. 依赖检查

扩展可以声明依赖的Python包：

```python
def get_dependencies(self) -> List[str]:
    """返回依赖的包列表"""
    return ['requests', 'numpy']

def check_dependencies(self) -> Tuple[bool, List[str]]:
    """检查依赖是否已安装"""
    missing = []
    for package in self.get_dependencies():
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return len(missing) == 0, missing
```

### 6. UI组件（仅GUI版本）

扩展可以提供UI组件：

```python
def get_ui_components(self) -> Dict[str, Any]:
    """返回UI组件定义"""
    return {
        'menu_items': [
            {'label': '菜单项', 'callback': self.menu_callback},
        ],
        'toolbar_buttons': [
            {'label': '按钮', 'icon': 'icon_name', 'callback': self.button_callback},
        ],
    }

def menu_callback(self):
    """菜单项回调函数"""
    pass
```

### 7. Webhook支持（可选）

扩展可以支持Webhook：

```python
def get_webhook_url(self) -> Optional[str]:
    """返回Webhook URL"""
    return "https://example.com/webhook"

def handle_webhook(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """处理Webhook请求"""
    # 处理逻辑
    return True, {'status': 'success'}
```

### 8. 数据导入导出（可选）

扩展可以支持数据导入导出：

```python
def export_data(self) -> Dict[str, Any]:
    """导出扩展数据"""
    return {
        'config': self.config,
        'custom_data': self.custom_data,
    }

def import_data(self, data: Dict[str, Any]) -> bool:
    """导入扩展数据"""
    try:
        if 'config' in data:
            self.config.update(data['config'])
        return True
    except Exception:
        return False
```

## 工具处理函数规范

### 函数签名

```python
def tool_handler(args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
    """
    工具处理函数
    
    参数:
        args: 工具参数字符串，由AI传入
        confirm_callback: 确认回调函数（可选）
                          函数签名: confirm_callback(title: str, message: str) -> bool
                          返回 True 表示用户同意，False 表示用户拒绝
    
    返回:
        (success, message) - (是否成功, 结果消息)
        success: bool - 操作是否成功
        message: str - 结果消息，将返回给AI
    """
    ...
```

### 使用确认回调

```python
def my_tool(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
    """需要用户确认的工具"""
    
    # 检查是否需要确认
    if confirm_callback:
        allowed = confirm_callback(
            "确认操作",
            "是否允许执行此操作？"
        )
        if not allowed:
            return False, "用户取消操作"
    
    # 执行操作
    return True, "操作成功"
```

### 错误处理

```python
def my_tool(self, args: str) -> Tuple[bool, str]:
    try:
        # 执行操作
        result = do_something(args)
        return True, f"成功: {result}"
    except ValueError as e:
        return False, f"参数错误: {str(e)}"
    except Exception as e:
        return False, f"操作失败: {str(e)}"
```

## 提示词编写规范

提示词将被添加到系统提示词中，让AI了解扩展功能。

### 格式建议

```
【扩展名称】
扩展功能简介。

可用工具：
- @tool1(参数) - 工具描述
- @tool2(参数) - 工具描述

使用说明：
1. 场景1 -> 使用 @tool1
2. 场景2 -> 使用 @tool2

示例：
- 用户说"帮我XX" -> AI调用 @tool1(参数)
```

### 示例

```
【天气查询扩展】
此扩展提供天气查询功能。

可用工具：
- @get_weather(城市) - 查询指定城市的天气，例如 @get_weather(北京)
- @get_forecast(城市, 天数) - 查询未来几天的天气预报，例如 @get_forecast(上海, 3)

使用说明：
- 当用户询问当前天气时，使用 @get_weather
- 当用户询问未来天气时，使用 @get_forecast

示例：
- 用户说"今天北京天气怎么样？" -> AI调用 @get_weather(北京)
- 用户说"上海未来三天天气如何？" -> AI调用 @get_forecast(上海, 3)
```

## 扩展测试

### 单元测试

```python
# test_my_extension.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iflow_extensions.my_extension.extension import Extension

def test_extension():
    ext = Extension()
    
    # 测试基本信息
    assert ext.get_name() == "my_extension"
    assert ext.get_version() == "1.0.0"
    
    # 测试工具
    tools = ext.get_tools()
    assert 'my_tool' in tools
    
    # 测试工具执行
    success, message = ext.my_tool("test")
    assert success == True
    
    print("测试通过!")

if __name__ == "__main__":
    test_extension()
```

## 常见问题

### Q: 如何调试扩展？

A: 在 `on_load()` 方法中添加日志：

```python
def on_load(self):
    print(f"[扩展] {self.name} 已加载")
```

### Q: 如何处理异步操作？

A: 使用线程或异步函数：

```python
import threading

def async_tool(self, args: str) -> Tuple[bool, str]:
    def worker():
        # 执行异步操作
        result = do_async_work()
        return result
    
    thread = threading.Thread(target=worker)
    thread.start()
    return True, "操作已启动"
```

### Q: 如何与其他扩展交互？

A: 通过扩展管理器获取其他扩展：

```python
# 在主程序中
other_ext = extension_manager.extensions.get('other_extension')
if other_ext:
    other_ext.some_method()
```

### Q: 如何禁用扩展？

A: 在扩展文件夹中添加 `disabled` 文件：

```bash
touch iflow_extensions/my_extension/disabled
```

扩展管理器会跳过包含 `disabled` 文件的扩展。

## 最佳实践

1. **命名规范**
   - 扩展名称使用小写字母和下划线
   - 工具名称使用小写字母和下划线
   - 类名使用大驼峰命名法

2. **错误处理**
   - 所有工具函数都应该有异常处理
   - 返回清晰的错误消息

3. **文档**
   - 为每个工具添加详细的文档字符串
   - 在提示词中提供使用示例

4. **性能**
   - 避免在工具中执行耗时操作
   - 必要时使用异步处理

5. **安全**
   - 敏感操作需要用户确认
   - 验证所有输入参数

## 扩展示例

完整的扩展示例请参考 `computer_control/extension.py`。

## 更新日志

### v1.0.0 (2025-01-01)
- 初始版本
- 支持基础扩展功能
- 提供电脑控制扩展示例