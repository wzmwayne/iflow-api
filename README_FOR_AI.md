# README_FOR_AI.md

> **重要提示**：本文档是给后续开发的AI阅读的，请在开发过程中不断完善和更新本文档。

---

## 项目概述

iFlow Chat 是一个功能强大的AI对话客户端，支持命令行(CLI)和图形界面(GUI)两种模式。项目采用模块化设计，支持扩展系统，允许开发者通过扩展添加新功能。

### 开发者与免责声明

**开发者：** wzmwayne 和 iflowai

**免责声明：**
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。

### 核心特性

1. **双模式支持**：CLI和GUI两种运行模式
2. **扩展系统**：支持动态加载第三方扩展
3. **流式对话**：支持SSE流式响应
4. **AI工具调用**：AI可以调用系统工具和扩展工具
5. **对话历史**：支持对话历史的保存、加载、导出、导入
6. **调试模式**：支持调试窗口查看详细输出

### 项目结构

```
iflow api/
├── iflow.py                    # 统一入口程序
├── iflow_chat.py               # CLI版本
├── iflow_chat_gui.py           # GUI版本
├── iflow_config.json           # 配置文件
├── iflow_conversations/        # 对话历史目录
├── iflow_screenshots/          # 截图目录
├── fonts/                      # 字体目录
│   ├── zh-cn.ttf              # 主要中文字体
│   └── Genshin-Impact/        # Genshin Impact 彩蛋字体
│       ├── Deshret-Inscription/
│       ├── Font-Ainee/
│       ├── Inazuma-Brush/
│       ├── Khaenriah-Sun/
│       ├── Sumeru-Scribe/
│       └── Teyvat-Black/
├── iflow_extensions/           # 扩展目录
│   ├── __init__.py            # 扩展管理器
│   ├── base_extension.py      # 扩展基类
│   ├── README.md              # 扩展开发文档
│   ├── computer_control/      # 电脑控制扩展
│   │   └── extension.py
│   ├── message_box/           # 信息框扩展
│   │   └── extension.py
│   └── example/               # 示例扩展
│       └── extension.py
├── extension_template/         # 扩展开发模板
│   ├── extension.py           # 扩展模板代码
│   ├── README.md              # 模板使用说明
│   ├── setup.py               # 扩展打包脚本
│   ├── code_generator.py      # 代码生成器
│   ├── compiler.py            # 扩展打包器 (GUI)
│   ├── block_compiler.py      # 积木块图形化编译器
│   ├── block_compiler_cli.py  # 积木块命令行编译器
│   ├── demo_compiler.py       # 演示编译器
│   ├── test_generator.py      # 代码生成器测试
│   ├── blocks/                # 积木块系统
│   │   ├── __init__.py        # 积木块模块导出
│   │   ├── base_block.py      # 积木块基类
│   │   └── block_types.py     # 积木块类型定义
│   └── make/                  # 编译输出目录
│       ├── hello_world/       # 示例：打招呼扩展
│       ├── calculator/        # 示例：计算器扩展
│       └── demo_extension/    # 示例：演示扩展
├── README_FOR_AI.md            # AI开发文档
├── start_iflow_cli.sh         # Linux/Mac/Termux CLI启动脚本
├── start_iflow_cli.bat        # Windows CLI启动脚本
├── start_iflow_gui.sh         # Linux/Mac/Termux GUI启动脚本
└── start_iflow_gui.bat        # Windows GUI启动脚本
```

---

## 扩展系统详解

### 扩展架构

扩展系统基于插件架构，每个扩展都是一个独立的Python模块，继承自 `BaseExtension` 基类。

#### 扩展管理器 (ExtensionManager)

扩展管理器负责：
- 自动发现和加载扩展
- 管理扩展生命周期
- 提供扩展注册和查询接口

位置：`iflow_extensions/__init__.py`

#### 扩展基类 (BaseExtension)

所有扩展必须继承 `BaseExtension` 基类，实现必要的方法。

位置：`iflow_extensions/base_extension.py`

### 扩展开发指南

#### 1. 创建扩展目录

每个扩展必须有独立的目录，目录名即扩展名：

```
iflow_extensions/
└── my_extension/
    └── extension.py
```

#### 2. 编写扩展代码

在 `extension.py` 中创建扩展类：

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
        # 必须设置以下属性
        self.name = "my_extension"           # 扩展名称（必须唯一）
        self.description = "扩展描述"        # 扩展描述
        self.version = "1.0.0"               # 版本号
        self.author = "wzmwayne_and_iflow_ai"               # 作者
    
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

#### 3. 扩展生命周期方法

| 方法 | 说明 | 调用时机 |
|------|------|----------|
| `on_load()` | 扩展加载时调用 | 程序启动加载扩展时 |
| `on_unload()` | 扩展卸载时调用 | 程序退出或扩展禁用时 |
| `on_before_tool_call(tool_name, args)` | 工具调用前调用 | 每次工具调用前 |
| `on_after_tool_call(tool_name, args, result)` | 工具调用后调用 | 每次工具调用后 |

#### 4. 工具处理函数规范

**函数签名：**

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

**使用确认回调：**

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

**错误处理：**

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

#### 5. 提示词编写规范

提示词将被添加到系统提示词中，让AI了解扩展功能。

**格式建议：**

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

#### 6. 高级功能

**配置管理：**

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

**依赖检查：**

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

---

## 现有扩展说明

### 1. 电脑控制扩展 (computer_control)

**功能：** 提供鼠标、键盘、屏幕截图等电脑操作功能

**工具：**
- `@mouse_move(x,y)` - 移动鼠标到指定坐标
- `@mouse_click(按钮)` - 点击鼠标
- `@keyboard(文本或key:按键)` - 键盘输入
- `@screenshot()` - 获取屏幕截图
- `@view_screenshot(文件名)` - 分析屏幕截图
- `@wait(秒数)` - 等待指定秒数
- `@request_computer_control()` - 请求获得电脑操作权限

**权限要求：** 需要先调用 `@request_computer_control()` 获取权限

**依赖：** pyautogui

### 2. 信息框扩展 (message_box)

**功能：** 提供普通和高级信息框功能

**工具：**
- `@show_message(标题,内容)` - 显示普通信息框
- `@show_advanced_message(标题,内容,类型,按钮)` - 显示高级信息框

**权限要求：** 无需授权

**依赖：** 无

### 3. 示例扩展 (example)

**功能：** 展示扩展系统的使用方法

**工具：**
- `@hello(名字)` - 向指定的人打招呼
- `@get_time()` - 获取当前时间
- `@calculate(表达式)` - 计算数学表达式
- `@repeat(内容,次数)` - 重复指定内容

**权限要求：** 无需授权

**依赖：** 无

---

## 开发注意事项

### 1. 代码规范

- 使用 `# -*- coding: utf-8 -*-` 声明文件编码
- 所有函数和类必须有文档字符串
- 工具处理函数必须返回 `Tuple[bool, str]`
- 错误处理要完善，返回清晰的错误消息

### 2. 命名规范

- 扩展名称使用小写字母和下划线
- 工具名称使用小写字母和下划线
- 类名使用大驼峰命名法

### 3. 安全考虑

- 敏感操作需要用户确认
- 验证所有输入参数
- 避免使用 `eval()` 处理用户输入（除非必要且安全）
- 不要在日志中记录敏感信息

### 4. 性能优化

- 避免在工具中执行耗时操作
- 必要时使用异步处理
- 合理使用缓存

### 5. 兼容性

- 同时支持 CLI 和 GUI 两种模式
- 使用 `confirm_callback` 参数支持GUI确认对话框
- 在非交互式环境中也要能正常工作

### 6. 测试

- 为每个扩展编写单元测试
- 测试工具的各种边界情况
- 测试错误处理

---

## GUI 开发说明

### 字体系统

GUI版本支持自定义字体加载，用于提升界面的视觉效果。

**字体目录结构：**
```
fonts/
├── zh-cn.ttf              # 主要中文字体
└── Genshin-Impact/        # Genshin Impact 彩蛋字体
    ├── Deshret-Inscription/
    ├── Font-Ainee/
    ├── Inazuma-Brush/
    ├── Khaenriah-Sun/
    ├── Sumeru-Scribe/
    └── Teyvat-Black/
```

**字体加载机制：**

1. **主要字体加载**
   - 程序启动时自动加载 `fonts/zh-cn.ttf` 作为主要中文字体
   - 如果加载成功，整个应用将使用该字体
   - 如果加载失败，使用默认字体（Segoe UI）

2. **彩蛋字体加载**
   - 自动加载 `fonts/Genshin-Impact/` 目录下的所有字体文件
   - 加载的字体存储在全局变量 `GENSHIN_FONTS` 中
   - 可以在需要使用彩蛋字体时通过字体名称获取

**字体加载代码示例：**

```python
# 加载字体
MAIN_FONT_FAMILY, GENSHIN_FONTS = load_custom_fonts()

# 使用主要字体
if MAIN_FONT_FAMILY:
    font = QFont(MAIN_FONT_FAMILY, 10)
    app.setFont(font)

# 使用彩蛋字体
if 'Teyvat-Black' in GENSHIN_FONTS:
    font = QFont(GENSHIN_FONTS['Teyvat-Black'], 12)
    widget.setFont(font)
```

**添加新字体：**

1. 将字体文件放入 `fonts/` 目录
2. 如果是主要字体，命名为 `zh-cn.ttf`
3. 如果是彩蛋字体，放入 `fonts/Genshin-Impact/` 子目录
4. 程序会自动加载新字体

### 调试窗口

当启用调试模式时，会显示一个调试窗口，用于查看CLI输出和原始响应。

**启用方法：**
- 点击工具栏的"调试模式"复选框
- 或使用指令 `/debug on`

**功能：**
- 显示所有调试输出
- 显示原始API响应
- 支持清空日志

### 消息自动滚动

AI对话时会自动滚动到底部，确保最新内容可见。

### 扩展工具调用

扩展工具通过 `_handle_ai_tool_call` 方法调用，支持确认回调。

---

## CLI 开发说明

### 交互式菜单

CLI版本使用伪图形化菜单，支持方向键导航。

### 自动补全

支持 Tab 键自动补全指令，输入部分指令后按 `?` 显示候选项。

### 调试模式

使用 `/debug on` 开启调试模式，会显示详细的API响应信息。

---

## 配置文件

### iflow_config.json

存储API密钥和更新时间：

```json
{
  "api_key": "your_api_key_here",
  "last_update": "2025-01-01T00:00:00"
}
```

---

## 积木块编译器使用指南

### 快速开始

#### 方法1：使用图形化编译器（推荐）

```bash
# 进入模板目录
cd extension_template

# 启动图形化编译器
python block_compiler.py
```

**界面介绍：**

1. **左侧 - 积木块库**
   - 显示所有可用的积木块
   - 双击积木块或点击"➕ 添加到工作区"按钮添加到工作区

2. **中间 - 工作区**
   - 拖拽积木块调整位置
   - 点击积木块选中，右侧会显示属性编辑器
   - 点击"🗑️ 清空"按钮清空工作区

3. **右侧 - 属性编辑器/代码预览**
   - **属性标签页**：编辑选中积木块的参数
   - **代码标签页**：实时预览生成的代码

4. **底部 - 工具栏**
   - **📄 新建**：新建项目，清空工作区
   - **📂 打开**：打开已保存的项目文件
   - **💾 保存**：保存当前项目
   - **⚡ 生成代码**：生成并保存 extension.py 文件
   - **📦 导出扩展**：导出为 ZIP 扩展包
   - **❌ 关闭**：关闭编译器

#### 方法2：使用命令行编译器

```bash
# 进入模板目录
cd extension_template

# 启动命令行编译器
python block_compiler_cli.py
```

### 创建扩展的步骤

#### 步骤1：添加扩展信息积木块

1. 在积木块库中双击"扩展信息"积木块
2. 在右侧属性编辑器中设置：
   - 扩展名称：`my_extension`
   - 扩展描述：`我的扩展`
   - 版本号：`1.0.0`
   - 作者：`wzmwayne_and_iflow_ai`

#### 步骤2：添加工具积木块

1. 双击"工具"积木块
2. 设置工具参数：
   - 工具名称：`hello`
   - 工具描述：`向用户打招呼`
   - 工具代码：
   ```python
   # 向用户打招呼
   return True, "你好！"
   ```

#### 步骤3：添加提示词积木块

1. 双击"提示词"积木块
2. 设置提示词内容：
   ```
   【我的扩展】
   此扩展用于向用户打招呼。

   可用工具：
   - @hello() - 向用户打招呼

   示例：
   - 用户说"你好" -> AI调用 @hello()
   ```

#### 步骤4：生成代码

1. 点击"⚡ 生成代码"按钮
2. 选择保存位置，保存为 `extension.py`
3. 查看生成的代码

#### 步骤5：导出扩展

1. 点击"📦 导出扩展"按钮
2. 选择保存位置，保存为 `.zip` 文件
3. 将导出的扩展导入到 iFlow 中

### 高级功能

#### 添加依赖包

1. 双击"依赖包"积木块
2. 设置依赖包列表（用逗号分隔）：
   ```
   requests, numpy, pandas
   ```

#### 添加配置项

1. 双击"配置"积木块
2. 设置配置参数：
   - 配置名称：`api_key`
   - 配置类型：`string`
   - 默认值：`your_api_key_here`

#### 添加生命周期方法

1. 双击"生命周期"积木块
2. 选择生命周期类型：
   - `on_load` - 扩展加载时调用
   - `on_unload` - 扩展卸载时调用
   - `on_before_tool_call` - 工具调用前调用
   - `on_after_tool_call` - 工具调用后调用
3. 编写生命周期代码

### 项目保存和加载

#### 保存项目

1. 点击"💾 保存"按钮
2. 选择保存位置和文件名
3. 项目将保存为 `.json` 文件

#### 加载项目

1. 点击"📂 打开"按钮
2. 选择之前保存的项目文件
3. 工作区将恢复到保存时的状态

### 示例项目

项目提供了几个示例项目，位于 `extension_template/make/` 目录：

1. **hello_world** - 简单的打招呼扩展
2. **calculator** - 计算器扩展（包含依赖和配置）
3. **demo_extension** - 演示扩展

你可以打开这些示例项目，了解如何使用积木块编译器。

### 常见问题

#### Q: 生成的代码有错误怎么办？

A: 检查以下几点：
- 确保至少有一个"扩展信息"积木块
- 确保工具代码语法正确
- 确保提示词格式正确
- 查看代码预览中的错误提示

#### Q: 如何修改已生成的代码？

A: 你可以：
- 在积木块编译器中修改积木块参数，重新生成代码
- 直接编辑生成的 `extension.py` 文件

#### Q: 如何在扩展中使用外部API？

A: 在"依赖包"积木块中添加 `requests`，然后在工具代码中使用：
```python
import requests
response = requests.get('https://api.example.com/data')
return True, response.text
```

#### Q: 如何打包和分发扩展？

A: 使用扩展打包器：
```bash
cd extension_template
python compiler.py
```
选择扩展目录，点击"打包扩展"按钮。

---

## 扩展开发最佳实践

### 1. 从模板开始

项目提供了扩展开发模板，位于 `extension_template/` 目录。

**使用模板创建扩展：**

```bash
# 复制模板到扩展目录
cp -r extension_template iflow_extensions/my_extension

# 进入扩展目录
cd iflow_extensions/my_extension

# 修改 extension.py，实现你的扩展功能
```

**打包扩展：**

**方法1：使用图形化编译器（推荐）**

```bash
# 进入模板目录
cd extension_template

# 启动图形化编译器
python compiler.py
```

**方法2：使用命令行脚本**

```bash
# 进入模板目录
cd extension_template

# 使用 setup.py 打包扩展
python setup.py ../my_extension

# 生成的 .zip 文件可以用于分发
```

模板包含：
- `extension.py` - 详细的扩展模板代码，包含完整注释
- `README.md` - 扩展开发指南
- `setup.py` - 扩展打包脚本（命令行）
- `compiler.py` - 扩展打包脚本（图形化）

详细说明请参考 `extension_template/README.md`。

### 2. 从示例开始

参考 `iflow_extensions/example/extension.py` 了解完整的扩展示例。

### 2. 保持简单

扩展应该专注于单一功能，避免过于复杂。

### 3. 提供清晰的提示词

提示词应该清晰、简洁，包含使用示例。

### 4. 完善错误处理

所有工具都应该有完善的错误处理，返回清晰的错误消息。

### 5. 编写文档

为扩展编写详细的文档，包括功能说明、使用示例等。

### 6. 测试兼容性

确保扩展在CLI和GUI两种模式下都能正常工作。

---

## 如何贡献

### 提交扩展

1. 在 `iflow_extensions/` 目录下创建新的扩展目录
2. 编写扩展代码
3. 更新本文档，添加扩展说明
4. 测试扩展功能
5. 提交代码

### 报告问题

报告问题时请提供：
- 问题描述
- 复现步骤
- 错误日志
- 环境信息（操作系统、Python版本等）

---

## 常见问题

### Q: 如何禁用某个扩展？

A: 在扩展文件夹中创建 `disabled` 文件：
```bash
touch iflow_extensions/my_extension/disabled
```

### Q: 扩展如何获取用户输入？

A: 通过 `confirm_callback` 参数，在GUI中显示对话框，在CLI中使用 `input()`。

### Q: 如何在扩展中使用外部API？

A: 在扩展中导入 `requests` 库，调用外部API：
```python
import requests

def my_tool(self, args: str) -> Tuple[bool, str]:
    response = requests.get('https://api.example.com/data')
    return True, response.text
```

### Q: 扩展如何访问对话历史？

A: 扩展无法直接访问对话历史，但可以通过工具参数获取必要的信息。

### Q: 如何打包和分发扩展？

A: 有三种方法打包扩展：

**方法1：使用图形化打包器（推荐）**
```bash
cd extension_template
python compiler.py
```
选择扩展目录，点击"📦 打包扩展"按钮。

**方法2：使用命令行脚本**
```bash
cd extension_template
python setup.py ../my_extension
```

**方法3：使用积木块编译器导出**
在积木块编译器中，点击"📦 导出扩展"按钮。

生成的 .zip 文件可以通过扩展管理功能导入。

### Q: 如何使用扩展管理功能？

A: **GUI版本：** 点击侧边栏的"🔌 扩展"按钮
**CLI版本：** 使用 `/extension` 指令

可用子命令：
- `/extension` - 显示扩展管理界面
- `/extension list` - 列出所有扩展
- `/extension info <扩展名>` - 查看扩展详情
- `/extension import` - 导入扩展
- `/extension delete <扩展名>` - 删除扩展

### Q: 如何使用积木块编译器创建扩展？

A: **图形化版本：**
```bash
cd extension_template
python block_compiler.py
```

**命令行版本：**
```bash
cd extension_template
python block_compiler_cli.py
```

详细使用方法请参考"积木块编译器使用指南"章节。

---

## 已完成功能：积木块编译器

### 概述

积木块编译器是一个图形化的扩展开发工具，类似编程猫和 mind++ 的拖拽式编程界面，用于降低 iFlow 扩展开发门槛。

**目标：**
- ✅ 用户可以通过拖拽积木块来创建扩展
- ✅ 无需手写代码，降低编程门槛
- ✅ 自动生成可运行的扩展文件
- 🔄 支持AI辅助生成代码（待实现）

### 已完成的工作

#### 1. 积木块基础架构

位置：`extension_template/blocks/`

**文件结构：**
```
blocks/
├── __init__.py          # 积木块模块导出
├── base_block.py       # 积木块基类
└── block_types.py      # 积木块类型定义
```

**已实现的积木块类型：**

1. **ExtensionInfoBlock** - 扩展信息积木块
   - 设置扩展名称、描述、版本、作者
   - 颜色：#4CAF50（绿色）

2. **ToolBlock** - 工具积木块
   - 定义工具函数
   - 支持自定义工具代码
   - 颜色：#2196F3（蓝色）

3. **PromptBlock** - 提示词积木块
   - 定义扩展的提示词
   - 颜色：#FF9800（橙色）

4. **LifecycleBlock** - 生命周期积木块
   - 定义 on_load、on_unload 等方法
   - 颜色：#9C27B0（紫色）

5. **DependencyBlock** - 依赖包积木块
   - 声明Python依赖包
   - 颜色：#E91E63（粉色）

6. **ConfigBlock** - 配置积木块
   - 定义扩展配置项
   - 颜色：#607D8B（青色）

7. **AIGenerateBlock** - AI生成积木块
   - 使用AI生成工具代码（待完善）
   - 颜色：#F44336（红色）

#### 2. 代码生成器

位置：`extension_template/code_generator.py`

**功能：**
- ✅ 从积木块生成完整的扩展代码
- ✅ 自动处理代码格式和缩进
- ✅ 生成可运行的 extension.py 文件
- ✅ 支持多种积木块类型的代码生成

**已实现的方法：**
```python
class ExtensionCodeGenerator:
    - add_block(block)          # 添加积木块
    - remove_block(block)       # 移除积木块
    - clear_blocks()            # 清空积木块
    - generate_extension_code() # 生成完整代码
    - save_to_file(filepath)    # 保存到文件
```

#### 3. 图形化编译器界面

位置：`extension_template/block_compiler.py`

**已实现的功能：**

1. **积木块面板** (左侧)
   - ✅ 显示所有可用的积木块
   - ✅ 带颜色标识
   - ✅ 双击或按钮添加到工作区

2. **工作区** (中间)
   - ✅ 图形化场景
   - ✅ 支持积木块的拖拽和移动
   - ✅ 支持选择和删除积木块
   - ✅ 清空工作区功能

3. **属性编辑器** (右侧-属性标签页)
   - ✅ 显示选中积木块的信息
   - ✅ 编辑积木块参数
   - ✅ 支持多种参数类型（字符串、文本、代码、选择、列表、数字、布尔）

4. **代码预览** (右侧-代码标签页)
   - ✅ 实时显示生成的代码
   - ✅ 刷新代码预览
   - ✅ 深色主题代码显示

5. **工具栏** (底部)
   - ✅ 新建项目
   - ✅ 打开项目
   - ✅ 保存项目
   - ✅ 生成代码
   - ✅ 导出扩展

6. **项目保存和加载**
   - ✅ 保存积木块配置为 JSON 文件
   - ✅ 从 JSON 文件加载项目
   - ✅ 保存积木块位置信息

#### 4. 扩展打包器

位置：`extension_template/compiler.py`

**功能：**
- ✅ 验证扩展目录有效性
- ✅ 打包扩展为 ZIP 文件
- ✅ 自动生成带版本号和时间戳的文件名
- ✅ 图形化界面
- ✅ 进度显示和日志输出
- ✅ 记住上次使用的扩展目录

#### 5. 命令行编译器

位置：`extension_template/block_compiler_cli.py`

**功能：**
- ✅ 命令行版本的积木块编译器
- ✅ 支持从 JSON 项目文件生成代码
- ✅ 支持直接导出扩展

#### 6. 示例输出

位置：`extension_template/make/`

**已生成的示例扩展：**
- `hello_world/` - 简单的打招呼扩展
- `calculator/` - 计算器扩展（包含依赖和配置）
- `demo_extension/` - 演示扩展

### 待完成的工作

#### 1. 积木块连接功能

**需要实现的功能：**
- 积木块之间的连接线
- 积木块的嵌套关系
- 连接线的可视化（贝塞尔曲线）
- 连接关系的保存和加载

#### 2. AI辅助功能

**需要实现的功能：**

1. **AI代码生成**
   - 用户描述工具功能
   - AI自动生成工具代码
   - 代码自动填充到积木块中

2. **AI建议**
   - 根据用户输入推荐合适的积木块
   - 检测积木块的错误和冲突
   - 提供优化建议

#### 3. 高级功能

**需要实现的功能：**
- 积木块搜索和筛选
- 撤销和重做功能
- 积木块复制和粘贴
- 积木块分组
- 快捷键支持

#### 3. AI辅助功能

**需要实现的功能：**

1. **AI代码生成**
   - 用户描述工具功能
   - AI自动生成工具代码
   - 代码自动填充到积木块中

2. **AI建议**
   - 根据用户输入推荐合适的积木块
   - 检测积木块的错误和冲突
   - 提供优化建议

### 技术实现要点

#### 1. 拖拽功能（PyQt5）

```python
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap

class BlockItem(QGraphicsItem):
    """积木块图形项"""
    
    def mousePressEvent(self, event):
        # 开始拖拽
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.block_data)
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap)
        drag.exec_()
    
    def mouseMoveEvent(self, event):
        # 处理拖拽移动
        pass
    
    def mouseReleaseEvent(self, event):
        # 处理拖拽释放
        pass
```

#### 2. 积木块连接

使用贝塞尔曲线连接积木块：
```python
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath

class ConnectionItem(QGraphicsPathItem):
    """连接线"""
    
    def __init__(self, start_pos, end_pos):
        path = QPainterPath()
        path.moveTo(start_pos)
        # 使用贝塞尔曲线
        path.cubicTo(
            start_pos.x() + 50, start_pos.y(),
            end_pos.x() - 50, end_pos.y(),
            end_pos.x(), end_pos.y()
        )
        self.setPath(path)
```

#### 3. 项目保存和加载

```python
import json

def save_project(blocks, filepath):
    """保存项目到文件"""
    data = [block.to_dict() for block in blocks]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_project(filepath):
    """从文件加载项目"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    blocks = []
    for block_data in data:
        block = BaseBlock.from_dict(block_data)
        blocks.append(block)
    
    return blocks
```

### 代码生成器实现步骤

#### 步骤1：初始化代码生成器

```python
from typing import List, Dict, Any
from .blocks import BaseBlock

class ExtensionCodeGenerator:
    """扩展代码生成器"""
    
    def __init__(self):
        self.blocks: List[BaseBlock] = []
```

#### 步骤2：生成文件头

```python
def _generate_header(self) -> str:
        """生成文件头"""
        return '''# -*- coding: utf-8 -*-
"""
扩展名称：Your Extension
扩展描述：Your Description
作者：wzmwayne_and_iflow_ai
版本：1.0.0
"""

'''```

#### 步骤3：生成导入语句

```python
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
```

#### 步骤4：生成类定义

```python
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
```

#### 步骤5：生成工具方法

```python
def _generate_tool_methods(self, tools: List) -> str:
    """生成工具方法"""
    code = ''
    
    for tool in tools:
        code += tool.generate_code()
        code += '\n\n'
    
    return code
```

#### 步骤6：保存到文件

```python
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
```

### 图形化界面实现步骤

#### 步骤1：创建主窗口

```python
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QTextEdit, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

class BlockCompilerGUI(QMainWindow):
    """积木块编译器图形界面"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iFlow 扩展积木块编译器 - by wzmwayne & iflowai")
        self.setGeometry(100, 100, 1200, 800)
        
        self.blocks = []
        self.code_generator = ExtensionCodeGenerator()
        
        self._init_ui()
```

#### 步骤2：创建积木块面板

```python
def _create_block_panel(self) -> QWidget:
    """创建积木块面板"""
    panel = QWidget()
    layout = QVBoxLayout()
    
    # 积木块列表
    self.block_list = QListWidget()
    self.block_list.setFixedWidth(250)
    
    # 加载所有积木块
    all_blocks = BlockFactory.get_all_blocks()
    for block in all_blocks:
        self.block_list.addItem(block.get_name())
    
    layout.addWidget(self.block_list)
    panel.setLayout(layout)
    return panel
```

#### 步骤3：创建工作区

```python
def _create_workspace(self) -> QWidget:
    """创建工作区"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # 使用 QGraphicsView 创建可拖拽区域
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
    
    self.scene = QGraphicsScene()
    self.view = QGraphicsView(self.scene)
    self.view.setAcceptDrops(True)
    
    layout.addWidget(self.view)
    widget.setLayout(layout)
    return widget
```

#### 步骤4：创建代码预览区

```python
def _create_code_preview(self) -> QWidget:
    """创建代码预览区"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    self.code_preview = QTextEdit()
    self.code_preview.setReadOnly(True)
    self.code_preview.setFont(QFont("Consolas", 10))
    
    layout.addWidget(self.code_preview)
    widget.setLayout(layout)
    return widget
```

#### 步骤5：实现拖拽功能

```python
def _init_drag_drop(self):
    """初始化拖拽功能"""
    self.view.setAcceptDrops(True)
    self.view.dragEnterEvent = self._drag_enter_event
    self.view.dragMoveEvent = self._drag_move_event
    self.view.dropEvent = self._drop_event

def _drag_enter_event(self, event):
    """拖拽进入事件"""
    if event.mimeData().hasText():
        event.acceptProposedAction()

def _drag_move_event(self, event):
    """拖拽移动事件"""
    event.acceptProposedAction()

def _drop_event(self, event):
    """拖拽释放事件"""
    block_data = event.mimeData().text()
    # 创建积木块并添加到场景
    self._add_block_to_scene(block_data)
    event.acceptProposedAction()
```

### 测试计划

#### 1. 单元测试

```python
import unittest
from blocks import BaseBlock, BlockFactory
from code_generator import ExtensionCodeGenerator

class TestCodeGenerator(unittest.TestCase):
    """测试代码生成器"""
    
    def test_generate_header(self):
        """测试生成文件头"""
        generator = ExtensionCodeGenerator()
        header = generator._generate_header()
        self.assertIn('# -*- coding: utf-8 -*-', header)
    
    def test_generate_class_definition(self):
        """测试生成类定义"""
        from blocks.block_types import ExtensionInfoBlock
        
        block = ExtensionInfoBlock()
        block.set_parameter('extension_name', 'test_extension')
        
        generator = ExtensionCodeGenerator()
        generator.add_block(block)
        
        class_def = generator._generate_class_definition(block)
        self.assertIn('class TestExtension', class_def)
```

#### 2. 集成测试

```python
def test_full_generation():
    """测试完整代码生成"""
    from blocks.block_types import (
        ExtensionInfoBlock, ToolBlock, PromptBlock
    )
    
    generator = ExtensionCodeGenerator()
    
    # 添加积木块
    info_block = ExtensionInfoBlock()
    info_block.set_parameter('extension_name', 'my_extension')
    info_block.set_parameter('description', '我的扩展')
    info_block.set_parameter('version', '1.0.0')
    info_block.set_parameter('author', 'wzmwayne_and_iflow_ai')
    
    tool_block = ToolBlock()
    tool_block.set_parameter('tool_name', 'hello')
    tool_block.set_parameter('tool_description', '打招呼')
    tool_block.set_parameter('tool_code', 'return True, "你好！"')
    
    prompt_block = PromptBlock()
    prompt_block.set_parameter('prompt_text', '【扩展】测试扩展')
    
    generator.add_block(info_block)
    generator.add_block(tool_block)
    generator.add_block(prompt_block)
    
    # 生成代码
    code = generator.generate_extension_code()
    
    # 验证代码
    assert 'class MyExtension' in code
    assert 'def hello' in code
    assert 'def get_prompt' in code
```

### 开发优先级

**已完成：**
1. ✅ 创建积木块基础架构
2. ✅ 实现各种积木块类型
3. ✅ 实现代码生成器
4. ✅ 创建图形化界面基础框架
5. ✅ 实现拖拽功能
6. ✅ 实现代码预览功能
7. ✅ 实现项目保存和加载
8. ✅ 实现属性编辑器
9. ✅ 实现扩展打包器
10. ✅ 实现命令行编译器
11. ✅ 实现代码高亮（深色主题）

**高优先级：**
1. ⬜ 实现积木块连接功能
2. ⬜ 实现AI代码生成功能

**中优先级：**
3. ⬜ 实现积木块搜索和筛选
4. ⬜ 实现撤销和重做功能
5. ⬜ 实现积木块复制和粘贴

**低优先级：**
6. ⬜ 实现AI建议功能
7. ⬜ 实现积木块分组
8. ⬜ 实现快捷键支持

### 参考资料

- PyQT5 Graphics View Framework: https://doc.qt.io/qt-5/qgraphicsview.html
- 拖拽操作: https://doc.qt.io/qt-5/dnd.html
- 代码生成模式: https://refactoring.guru/design-patterns/template-method

---

## 更新日志

### 2025-01-03
- ✅ 实现字体加载系统
  - 支持加载自定义中文字体 (fonts/zh-cn.ttf)
  - 支持加载 Genshin Impact 彩蛋字体
  - 自动检测和应用自定义字体
- ✅ 优化侧边栏布局
  - 侧边栏宽度改为动态分配
  - 底部按钮区域高度改为动态分配
  - 修复按钮显示不完整的问题
- ✅ 修复批处理文件问题
  - 修复 URL 拼接错误导致命令解析失败
  - 修复 MISSING_DEPS 变量前导空格问题
  - 将批处理文件编码从 UTF-8 转换为系统默认编码

### 2025-12-29
- ✅ 完成代码生成器 (code_generator.py)
- ✅ 完成积木块图形化编译器 (block_compiler.py)
- ✅ 完成扩展打包器 (compiler.py)
- ✅ 完成命令行编译器 (block_compiler_cli.py)
- ✅ 实现项目保存和加载功能
- ✅ 实现代码预览功能
- ✅ 实现属性编辑器
- ✅ 生成示例扩展 (hello_world, calculator, demo_extension)
- ✅ 完善积木块类型定义和参数系统
- ✅ 实现积木块拖拽和移动功能
- ✅ 实现扩展导出功能

### 2025-01-01
- 创建 README_FOR_AI.md
- 添加示例扩展
- 完善扩展系统文档
- 添加扩展开发模板 (extension_template/)
- 添加扩展打包脚本
- 添加扩展管理功能（GUI和CLI）
- 添加信息框扩展
- 启动积木块编译器开发
- 创建积木块基础架构
- 实现各种积木块类型

---

## 联系方式

- 项目地址：[GitHub](https://github.com/your-repo)
- 问题反馈：[Issues](https://github.com/your-repo/issues)

---

**最后更新：** 2025-01-03

**维护者：** wzmwayne & iflowai

---

> **请后续开发的AI在开发过程中不断完善和更新本文档，确保文档的准确性和完整性。**