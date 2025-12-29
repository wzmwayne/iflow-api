# 扩展开发模板

欢迎使用 iFlow 扩展开发模板！这个模板将帮助你快速创建一个功能完整的扩展。

## 目录结构

```
extension_template/
├── extension.py      # 扩展主文件（必须）
├── README.md         # 本文件（可选）
├── requirements.txt  # 依赖列表（可选）
└── setup.py          # 打包脚本（可选）
```

## 快速开始

### 1. 复制模板

将整个 `extension_template` 文件夹复制到 `iflow_extensions/` 目录下，并重命名为你的扩展名称：

```bash
# 从项目根目录
cp -r extension_template iflow_extensions/my_extension
```

### 2. 修改 extension.py

打开 `my_extension/extension.py`，修改以下内容：

- `YourExtension` 类名：改为你的扩展类名（使用大驼峰命名）
- `self.name`：扩展名称（使用小写字母和下划线）
- `self.description`：扩展描述
- `self.version`：版本号
- `self.author`：作者名

### 3. 实现工具函数

在 `get_tools()` 方法中注册你的工具，并实现对应的工具处理函数。

### 4. 测试扩展

```bash
python -c "
import sys
sys.path.insert(0, '.')
from iflow_extensions import extension_manager

extension_manager.load_extensions()
ext = extension_manager.extensions['your_extension_name']

# 测试工具
success, message = ext.tool1('参数')
print(success, message)
"
```

## 扩展开发指南

### 必须实现的方法

#### 1. `get_prompt()` - 提供提示词

```python
def get_prompt(self) -> str:
    """
    返回扩展的提示词，将添加到系统提示词中
    """
    return """
【扩展名称】
扩展功能描述。

可用工具：
- @tool_name(参数) - 工具描述

使用示例：
- 用户说"XX" -> AI调用 @tool_name(参数)
"""
```

#### 2. `get_tools()` - 注册工具

```python
def get_tools(self) -> Dict[str, Callable]:
    """
    返回工具处理函数字典
    """
    return {
        'tool_name': self.tool_function,
    }
```

#### 3. 工具处理函数

```python
def tool_function(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
    """
    工具处理函数
    
    参数:
        args: 工具参数字符串
        confirm_callback: 确认回调函数（可选）
    
    返回:
        (success, message) - (是否成功, 结果消息)
    """
    try:
        # 执行操作
        result = do_something(args)
        return True, f"成功: {result}"
    except Exception as e:
        return False, f"失败: {str(e)}"
```

### 可选实现的方法

#### 1. 生命周期方法

```python
def on_load(self):
    """扩展加载时调用"""
    pass

def on_unload(self):
    """扩展卸载时调用"""
    pass

def on_before_tool_call(self, tool_name: str, args: str):
    """工具调用前调用"""
    pass

def on_after_tool_call(self, tool_name: str, args: str, result: Tuple[bool, str]):
    """工具调用后调用"""
    pass
```

#### 2. 配置管理

```python
def get_config_schema(self) -> Dict[str, dict]:
    """定义配置项"""
    return {
        'option': {
            'type': 'string',
            'default': 'value',
            'description': '配置说明',
        }
    }

def load_config(self, config: Dict[str, any]):
    """加载配置"""
    self.config.update(config)
```

#### 3. 依赖检查

```python
def get_dependencies(self) -> list:
    """返回依赖的包列表"""
    return ['requests', 'numpy']

def check_dependencies(self) -> Tuple[bool, list]:
    """检查依赖是否已安装"""
    missing = []
    for package in self.get_dependencies():
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return len(missing) == 0, missing
```

## 打包扩展

### 方法1: 使用图形化编译器（推荐）

项目提供了图形化编译器，可以通过图形界面打包扩展。

**启动编译器：**

```bash
cd extension_template
python compiler.py
```

**使用步骤：**

1. 点击"浏览..."按钮选择扩展目录
2. 查看扩展信息（自动验证）
3. 点击"📦 打包扩展"按钮
4. 等待打包完成
5. 点击"📁 打开输出目录"查看生成的 .zip 文件

**功能特性：**

- 图形化界面，操作简单
- 自动验证扩展有效性
- 实时显示打包进度
- 显示详细的扩展信息
- 支持查看打包日志
- 保存上次使用的目录

### 方法2: 使用 setup.py（命令行）

创建 `setup.py` 文件：

```python
# -*- coding: utf-8 -*-
"""
扩展打包脚本
"""

import os
import shutil
import zipfile
from datetime import datetime


class ExtensionPackager:
    """扩展打包器"""
    
    def __init__(self, extension_dir: str):
        self.extension_dir = extension_dir
        self.extension_name = os.path.basename(extension_dir)
    
    def pack(self, output_dir: str = None) -> str:
        """
        打包扩展为 zip 文件
        
        参数:
            output_dir: 输出目录，默认为当前目录
        
        返回:
            str: 打包文件的路径
        """
        if output_dir is None:
            output_dir = os.path.dirname(self.extension_dir)
        
        # 创建输出文件名
        version = self._get_version()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"{self.extension_name}_v{version}_{timestamp}.zip"
        )
        
        # 创建 zip 文件
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.extension_dir)
                    zipf.write(file_path, arcname)
        
        print(f"[打包] 扩展已打包到: {output_file}")
        return output_file
    
    def _get_version(self) -> str:
        """获取扩展版本"""
        try:
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            return Extension.version
        except:
            return "1.0.0"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python setup.py <扩展目录>")
        print("示例: python setup.py ../my_extension")
        sys.exit(1)
    
    extension_dir = sys.argv[1]
    
    if not os.path.isdir(extension_dir):
        print(f"错误: 目录不存在: {extension_dir}")
        sys.exit(1)
    
    packager = ExtensionPackager(extension_dir)
    output_file = packager.pack()
    
    print(f"\n打包完成！")
    print(f"文件: {output_file}")
    print(f"\n使用方法:")
    print(f"  1. 将 {output_file} 复制到 iflow_extensions/ 目录")
    print(f"  2. 使用扩展管理功能导入")
```

打包扩展：

```bash
python setup.py ../my_extension
```

### 方法2: 手动打包

```bash
cd iflow_extensions
zip -r my_extension.zip my_extension/
```

## 扩展管理

### 导入扩展

**GUI版本：**
1. 点击侧边栏的"扩展管理"按钮
2. 点击"导入扩展"
3. 选择扩展的 zip 文件
4. 点击"导入"

**CLI版本：**
```bash
/extension import my_extension.zip
```

### 删除扩展

**GUI版本：**
1. 点击侧边栏的"扩展管理"按钮
2. 选择要删除的扩展
3. 点击"删除"

**CLI版本：**
```bash
/extension delete my_extension
```

### 查看扩展

**GUI版本：**
1. 点击侧边栏的"扩展管理"按钮
2. 查看扩展列表和详细信息

**CLI版本：**
```bash
/extension list
/extension info my_extension
```

## 最佳实践

### 1. 命名规范

- 扩展名称：使用小写字母和下划线，如 `my_extension`
- 类名：使用大驼峰命名法，如 `MyExtension`
- 工具名称：使用小写字母和下划线，如 `my_tool`

### 2. 错误处理

所有工具函数都应该有完善的错误处理：

```python
def my_tool(self, args: str) -> Tuple[bool, str]:
    try:
        # 验证参数
        if not args:
            return False, "参数不能为空"
        
        # 执行操作
        result = do_something(args)
        
        return True, f"成功: {result}"
        
    except ValueError as e:
        return False, f"参数错误: {str(e)}"
    except Exception as e:
        return False, f"操作失败: {str(e)}"
```

### 3. 用户确认

对于敏感操作，使用 `confirm_callback`：

```python
def sensitive_tool(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
    if confirm_callback:
        allowed = confirm_callback(
            "确认操作",
            "此操作可能会修改数据，是否继续？"
        )
        if not allowed:
            return False, "用户取消操作"
    
    # 执行操作
    return True, "操作成功"
```

### 4. 日志记录

使用 `print` 输出调试信息：

```python
def my_tool(self, args: str) -> Tuple[bool, str]:
    print(f"[{self.name}] 调用工具: my_tool({args})")
    
    # 执行操作
    result = do_something(args)
    
    print(f"[{self.name}] 工具执行完成")
    return True, result
```

### 5. 文档

为每个工具编写详细的文档字符串：

```python
def my_tool(self, args: str, confirm_callback: Callable = None) -> Tuple[bool, str]:
    """
    工具功能描述
    
    参数:
        args: 参数说明
        confirm_callback: 确认回调函数说明
    
    返回:
        Tuple[bool, str]: 返回值说明
    
    使用示例:
        >>> my_tool("参数")
        (True, "成功")
    """
    pass
```

## 常见问题

### Q: 扩展没有被识别？

A: 检查以下几点：
1. 扩展目录是否在 `iflow_extensions/` 目录下
2. 扩展目录中是否包含 `extension.py` 文件
3. `extension.py` 中是否定义了 `Extension` 变量
4. 扩展名称是否唯一

### Q: 工具没有被AI调用？

A: 检查以下几点：
1. 工具是否在 `get_tools()` 方法中注册
2. 提示词中是否包含工具说明
3. 工具名称格式是否正确（使用 `@tool_name(参数)` 格式）

### Q: 如何调试扩展？

A: 使用 `print` 输出调试信息：

```python
def my_tool(self, args: str) -> Tuple[bool, str]:
    print(f"[调试] 工具被调用: {args}")
    print(f"[调试] 参数类型: {type(args)}")
    
    # 执行操作
    result = do_something(args)
    
    print(f"[调试] 执行结果: {result}")
    return True, result
```

### Q: 扩展需要第三方库怎么办？

A: 在 `get_dependencies()` 方法中声明依赖：

```python
def get_dependencies(self) -> list:
    return ['requests', 'numpy']
```

然后在 `requirements.txt` 中列出依赖：

```
requests>=2.28.0
numpy>=1.24.0
```

## 示例扩展

参考 `../iflow_extensions/example/extension.py` 了解完整的扩展示例。

## 支持

如有问题，请参考主文档 `../README_FOR_AI.md` 或提交 Issue。