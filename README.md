# iFlow Chat

一个功能强大的 AI 对话客户端，支持命令行(CLI)和图形界面(GUI)两种模式，内置扩展系统，允许通过插件添加新功能。

## 📝 开发者与免责声明

**开发者：** wzmwayne 和 iflowai

**免责声明：**
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。

## ✨ 特性

- 🎭 **双模式支持**：CLI 和 GUI 两种运行模式，满足不同使用场景
- 🔌 **扩展系统**：支持动态加载第三方扩展，轻松扩展功能
- 🧱 **积木块编译器**：图形化拖拽式扩展开发工具，无需编程基础
- 💬 **流式对话**：支持 SSE 流式响应，实时显示 AI 回复
- 🛠️ **AI 工具调用**：AI 可以调用系统工具和扩展工具
- 📚 **对话历史**：支持对话历史的保存、加载、导出、导入
- 🐛 **调试模式**：支持调试窗口查看详细输出
- 🎨 **美观界面**：现代化的 GUI 设计，支持深色主题
- 📦 **扩展打包**：提供图形化和命令行两种扩展打包方式

## 🚀 快速开始

### 安装依赖

```bash
pip install requests PyQt5 PyQtWebEngine
```

### 运行程序

**使用统一入口（推荐）：**

```bash
# 自动选择模式（优先 GUI）
python iflow.py

# 强制使用 CLI 模式
python iflow.py --cli

# 强制使用 GUI 模式
python iflow.py --gui

# 指定模型
python iflow.py --model gpt-4
```

**使用启动脚本：**

**Linux/Mac/Termux:**

```bash
# GUI 模式
./start_iflow_gui.sh

# CLI 模式
./start_iflow_cli.sh
```

**Windows:**

```batch
REM GUI 模式
start_iflow_gui.bat

REM CLI 模式
start_iflow_cli.bat
```

### 首次使用

1. 运行程序后，输入您的 API 密钥
2. 开始与 AI 对话
3. 使用 `/help` 查看可用指令

## 📖 使用说明

### CLI 模式

CLI 模式提供伪图形化菜单界面，支持方向键导航。

**基本指令：**

- `/help` - 显示帮助信息
- `/info` - 显示当前配置信息
- `/debug on/off` - 开启/关闭调试模式
- `/api <key>` - 修改 API 密钥
- `/model <name>` - 修改模型名称
- `/url <url>` - 修改 API URL
- `/history` - 对话历史管理
- `/clear` - 清空当前对话历史
- `/export <file>` - 导出当前对话到文件
- `/import <file>` - 从文件导入对话
- `/stop` - 停止当前输出
- `/exit` - 退出程序

**扩展管理：**

- `/extension` - 显示扩展管理界面
- `/extension list` - 列出所有扩展
- `/extension info <扩展名>` - 查看扩展详情
- `/extension import` - 导入扩展
- `/extension delete <扩展名>` - 删除扩展

### GUI 模式

GUI 模式提供现代化的图形界面。

**主要功能：**

- 左侧边栏：对话历史管理、设置、扩展管理、帮助
- 右侧聊天区：消息显示、输入框、工具栏
- 状态栏：显示当前状态信息

**快捷键：**

- `Ctrl+Enter` - 发送消息

### AI 工具调用

AI 可以调用以下工具（需要用户确认）：

**系统指令：**

- `@/debug on/off` - 开启/关闭调试模式
- `@/api <key>` - 修改 API 密钥
- `@/model <name>` - 修改模型名称
- `@/url <url>` - 修改 API URL
- `@/history` - 打开对话历史管理
- `@/clear` - 清空当前对话
- `@/export <file>` - 导出对话
- `@/import <file>` - 导入对话
- `@/stop` - 停止输出
- `@/info` - 显示配置信息
- `@/help` - 显示帮助
- `@/exit` - 退出程序

**扩展工具：**

- `@cmd(命令)` - 执行系统命令
- `@show_message(标题,内容)` - 显示普通信息框
- `@show_advanced_message(标题,内容,类型,按钮)` - 显示高级信息框
- 其他扩展提供的工具

## 📁 项目结构

```
iflow api/
├── iflow.py                    # 统一入口程序
├── iflow_chat.py               # CLI 版本
├── iflow_chat_gui.py           # GUI 版本
├── iflow_config.json           # 配置文件
├── iflow_conversations/        # 对话历史目录
├── iflow_screenshots/          # 截图目录
├── iflow_extensions/           # 扩展目录
│   ├── __init__.py            # 扩展管理器
│   ├── base_extension.py      # 扩展基类
│   ├── README.md              # 扩展开发文档
│   ├── computer_control/      # 电脑控制扩展
│   ├── message_box/           # 信息框扩展
│   └── example/               # 示例扩展
├── extension_template/         # 扩展开发模板
│   ├── extension.py           # 扩展模板代码
│   ├── README.md              # 模板使用说明
│   ├── setup.py               # 扩展打包脚本（命令行）
│   ├── compiler.py            # 扩展打包器（图形化）
│   ├── code_generator.py      # 代码生成器
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
├── README.md                   # 本文件
├── README_FOR_AI.md            # AI 开发文档
├── start_iflow_cli.sh         # Linux/Mac/Termux CLI 启动脚本
├── start_iflow_cli.bat        # Windows CLI 启动脚本
├── start_iflow_gui.sh         # Linux/Mac/Termux GUI 启动脚本
└── start_iflow_gui.bat        # Windows GUI 启动脚本
```

## 🔌 扩展开发

### 创建新扩展

iFlow 提供三种方式创建扩展：

#### 方法1：使用积木块编译器（推荐，无需编程基础）

积木块编译器是一个图形化的拖拽式开发工具，类似编程猫和 mind++，让你无需编写代码就能创建扩展。

**启动图形化编译器：**

```bash
cd extension_template
python block_compiler.py
```

**使用步骤：**

1. 在左侧积木块库中双击选择积木块
2. 在中间工作区拖拽和调整积木块
3. 在右侧属性编辑器中配置积木块参数
4. 点击"⚡ 生成代码"生成扩展代码
5. 点击"📦 导出扩展"打包为 ZIP 文件

**可用积木块：**

- 🟢 **扩展信息** - 设置扩展名称、描述、版本、作者
- 🔵 **工具** - 定义工具函数和功能
- 🟠 **提示词** - 定义扩展的提示词
- 🟣 **生命周期** - 定义扩展加载、卸载等生命周期方法
- 🔴 **依赖包** - 声明 Python 依赖
- 🔷 **配置** - 定义扩展配置项

详细使用说明请参考 `README_FOR_AI.md` 中的"积木块编译器使用指南"章节。

#### 方法2：使用模板编写代码

```bash
# 复制模板到扩展目录
cp -r extension_template iflow_extensions/my_extension

# 进入扩展目录
cd iflow_extensions/my_extension

# 修改 extension.py，实现你的扩展功能
```

#### 方法3：从零开始创建

参考 `iflow_extensions/example/` 目录下的示例扩展，创建新的扩展。

### 打包扩展

**方法1：使用图形化打包器（推荐）**

```bash
cd extension_template
python compiler.py
```

**方法2：使用命令行脚本**

```bash
cd extension_template
python setup.py ../my_extension
```

**方法3：使用积木块编译器导出**

在积木块编译器中，点击"📦 导出扩展"按钮。

### 导入扩展

**GUI 版本：**
- 点击侧边栏的"🔌 扩展"按钮
- 点击"📥 导入扩展"
- 选择扩展的 zip 文件

**CLI 版本：**
```bash
/extension import
```

详细说明请参考：
- `extension_template/README.md` - 扩展开发指南
- `README_FOR_AI.md` - AI 开发文档

## 🔧 配置说明

### API 密钥

程序使用 `iflow_config.json` 存储配置：

```json
{
  "api_key": "your_api_key_here",
  "last_update": "2025-01-01T00:00:00"
}
```

API 密钥有效期为 7 天，过期后需要重新输入。

### 模型配置

默认使用 `qwen3-coder-plus` 模型，可以通过以下方式修改：

- GUI：在工具栏中选择模型
- CLI：使用 `/model <模型名>` 指令
- 命令行：使用 `--model <模型名>` 参数

## 🐛 调试模式

### CLI 模式

```bash
/extension debug on
```

### GUI 模式

在工具栏中勾选"调试模式"复选框，会弹出调试窗口，显示：
- CLI 输出
- 原始 API 响应
- 扩展加载日志
- 工具调用日志

## 📚 内置扩展

### 1. 电脑控制扩展 (computer_control)

提供鼠标、键盘、屏幕截图等电脑操作功能。

**工具：**
- `@mouse_move(x,y)` - 移动鼠标到指定坐标
- `@mouse_click(按钮)` - 点击鼠标（需权限）
- `@keyboard(文本或key:按键)` - 输入文本或特殊按键（需权限）
- `@screenshot()` - 获取屏幕截图（AI可见）
- `@view_screenshot(文件名)` - 分析屏幕截图
- `@wait(秒数)` - 等待指定秒数
- `@request_computer_control()` - 请求电脑操作权限

### 2. 信息框扩展 (message_box)

提供信息框功能，让 AI 可以向用户展示信息。

**工具：**
- `@show_message(标题,内容)` - 显示普通信息框
- `@show_advanced_message(标题,内容,类型,按钮)` - 显示高级信息框

### 3. 示例扩展 (example)

展示扩展系统的基本使用方法。

**工具：**
- `@hello(名字)` - 向指定的人打招呼
- `@get_time()` - 获取当前时间
- `@calculate(表达式)` - 计算数学表达式
- `@repeat(内容,次数)` - 重复指定内容

### 4. 积木块编译器 (extension_template)

图形化的扩展开发工具，无需编程基础即可创建扩展。

**功能：**
- 拖拽式积木块编程
- 实时代码预览
- 项目保存和加载
- 一键导出扩展

**启动方式：**
```bash
cd extension_template
python block_compiler.py
```

**示例项目：**
- `make/hello_world/` - 简单的打招呼扩展
- `make/calculator/` - 计算器扩展
- `make/demo_extension/` - 演示扩展

## ❓ 常见问题

### Q: 如何禁用某个扩展？

A: 在扩展文件夹中创建 `disabled` 文件：
```bash
touch iflow_extensions/my_extension/disabled
```

### Q: 如何使用积木块编译器创建扩展？

A: 积木块编译器是一个图形化的拖拽式开发工具，无需编程基础。

**启动方式：**
```bash
cd extension_template
python block_compiler.py
```

**基本步骤：**
1. 在左侧积木块库中双击选择积木块
2. 在中间工作区拖拽和调整积木块
3. 在右侧属性编辑器中配置积木块参数
4. 点击"⚡ 生成代码"生成扩展代码
5. 点击"📦 导出扩展"打包为 ZIP 文件

详细说明请参考 `README_FOR_AI.md` 中的"积木块编译器使用指南"章节。

### Q: 扩展如何获取用户输入？

A: 通过 `confirm_callback` 参数，在 GUI 中显示对话框，在 CLI 中使用 `input()`。

### Q: 如何在扩展中使用外部 API？

A: 在扩展中导入 `requests` 库，调用外部 API：
```python
import requests

def my_tool(self, args: str) -> Tuple[bool, str]:
    response = requests.get('https://api.example.com/data')
    return True, response.text
```

在积木块编译器中，可以添加"依赖包"积木块，填写 `requests`，然后在工具代码中使用。

### Q: GUI 模式无法启动？

A: 确保已安装 PyQt5 和 PyQtWebEngine：
```bash
pip install PyQt5 PyQtWebEngine
```

### Q: Termux 上如何使用 GUI 模式？

A: 需要安装和启动 X11 服务：
```bash
pkg install termux-x11
termux-x11 :0 &
export DISPLAY=:0
python iflow.py --gui
```

### Q: 生成的扩展代码有错误怎么办？

A: 检查以下几点：
- 确保至少有一个"扩展信息"积木块
- 确保工具代码语法正确
- 确保提示词格式正确
- 查看代码预览中的错误提示

### Q: 如何修改已生成的扩展代码？

A: 你可以：
- 在积木块编译器中修改积木块参数，重新生成代码
- 直接编辑生成的 `extension.py` 文件

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发扩展

参考 `extension_template/` 目录下的模板创建新扩展。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 📞 联系方式

- 项目地址：[GitHub](https://github.com/your-repo)
- 问题反馈：[Issues](https://github.com/your-repo/issues)
- 文档：[Wiki](https://github.com/your-repo/wiki)

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

---

**最后更新：** 2025-12-29

**维护者：** wzmwayne & iflowai

---

> 💡 **提示**：如需了解更多技术细节，请参考 `README_FOR_AI.md` 文档。