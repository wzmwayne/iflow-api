#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心流平台流式对话客户端
支持API密钥7天过期提醒
使用qwen3-coder-plus模型进行流式对话
支持指令控制：/debug, /api, /model, /history, /stop, /help

开发者: wzmwayne 和 iflowai

免责声明:
本程序仅供学习和研究使用。使用本程序所产生的任何后果由使用者自行承担。
开发者不对因使用本程序而导致的任何损失或损害承担责任。
请遵守相关法律法规，不得将本程序用于任何非法用途。

使用本程序即表示您同意上述免责声明。
"""

import requests
import json
import os
import threading
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

# Windows平台键盘检测
if sys.platform == 'win32':
    import msvcrt

# Windows平台兼容性处理
if sys.platform == 'win32':
    try:
        import pyreadline3 as readline
    except ImportError:
        readline = None
else:
    import readline

# pyautogui 导入（可能失败，在需要时处理）
try:
    import pyautogui
except ImportError:
    pyautogui = None

# 导入扩展管理器
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from iflow_extensions import extension_manager
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False
    extension_manager = None


class TerminalUI:
    """终端伪图形化界面"""
    
    @staticmethod
    def clear_screen():
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def get_key():
        """获取按键（Windows平台）"""
        if os.name == 'nt':
            return msvcrt.getch()
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch.encode('utf-8')
    
    @staticmethod
    def show_menu(title: str, options: List[str], selected: int = 0) -> int:
        """显示菜单并返回选择的索引"""
        while True:
            TerminalUI.clear_screen()
            print("=" * 50)
            print(f"  {title}")
            print("=" * 50)
            print()
            
            for i, option in enumerate(options):
                prefix = "► " if i == selected else "  "
                print(f"{prefix}{option}")
            
            print()
            print("使用 ↑↓ 选择，回车确认")
            
            key = TerminalUI.get_key()
            
            # 处理方向键
            if os.name == 'nt':
                if key == b'\xe0':  # Windows方向键前缀
                    key = TerminalUI.get_key()
                    if key == b'H':  # 上
                        selected = (selected - 1) % len(options)
                    elif key == b'P':  # 下
                        selected = (selected + 1) % len(options)
                elif key == b'\r':  # 回车
                    return selected
            else:
                if key == b'\x1b':  # Linux方向键前缀
                    TerminalUI.get_key()  # 跳过[
                    arrow = TerminalUI.get_key()
                    if arrow == b'A':  # 上
                        selected = (selected - 1) % len(options)
                    elif arrow == b'B':  # 下
                        selected = (selected + 1) % len(options)
                elif key == b'\r':  # 回车
                    return selected
    
    @staticmethod
    def show_list(title: str, items: List[Tuple[str, str]], selected: int = 0) -> Optional[int]:
        """显示列表并返回选择的索引，0表示取消"""
        options = ["取消"] + [f"{name} ({mtime})" for _, name, mtime in items]
        result = TerminalUI.show_menu(title, options, selected + 1)
        return result - 1 if result > 0 else None
    
    @staticmethod
    def input_line(prompt: str) -> str:
        """输入一行文本"""
        print(prompt, end='', flush=True)
        return input().strip()


class APIKeyManager:
    """管理API密钥及过期时间"""
    
    CONFIG_FILE = "iflow_config.json"
    HISTORY_DIR = "iflow_conversations"
    SCREENSHOT_DIR = "iflow_screenshots"
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.last_update: Optional[datetime] = None
        self._load_config()
        self._ensure_history_dir()
        self._ensure_screenshot_dir()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    last_update_str = config.get('last_update')
                    if last_update_str:
                        self.last_update = datetime.fromisoformat(last_update_str)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def _ensure_history_dir(self):
        """确保历史对话目录存在"""
        if not os.path.exists(self.HISTORY_DIR):
            os.makedirs(self.HISTORY_DIR)
    
    def _ensure_screenshot_dir(self):
        """确保截图目录存在"""
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR)
    
    def _save_config(self):
        """保存配置文件"""
        config = {
            'api_key': self.api_key,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        self.last_update = datetime.now()
        self._save_config()
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return self.api_key
    
    def is_expired(self) -> bool:
        """检查是否超过7天"""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update > timedelta(days=7)
    
    def get_days_remaining(self) -> int:
        """获取剩余天数"""
        if not self.last_update:
            return 0
        delta = timedelta(days=7) - (datetime.now() - self.last_update)
        return max(0, delta.days)
    
    def save_conversation(self, messages: List[dict], name: Optional[str] = None) -> str:
        """保存对话历史"""
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = os.path.join(self.HISTORY_DIR, f"{name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return filename
    
    def list_conversations(self) -> List[Tuple[str, str, str]]:
        """列出所有对话历史，返回(文件名, 显示名称, 修改时间)列表"""
        conversations = []
        if os.path.exists(self.HISTORY_DIR):
            for filename in os.listdir(self.HISTORY_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.HISTORY_DIR, filename)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    display_name = filename[:-5]  # 去掉.json
                    conversations.append((filename, display_name, mtime.strftime("%Y-%m-%d %H:%M:%S")))
        # 按修改时间倒序排列
        conversations.sort(key=lambda x: x[2], reverse=True)
        return conversations
    
    def load_conversation(self, filename: str) -> Optional[List[dict]]:
        """加载指定的对话历史"""
        filepath = os.path.join(self.HISTORY_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载对话失败: {e}")
        return None


class IflowChatClient:
    """心流聊天客户端"""
    
    def __init__(self, model: str = "qwen3-coder-plus"):
        self.model = model
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.key_manager = APIKeyManager()
        self.messages: List[dict] = []
        self.debug_mode = False
        self.stop_flag = False
        self.is_streaming = False
        self.lock = threading.Lock()
        self.current_conversation_name: Optional[str] = None
        self.auto_save = True
        self.log_file = "iflow.log"
        self.ai_control_enabled = False  # AI电脑操作权限
        self.status_window = None  # 状态窗口
        self.status_thread = None  # 状态更新线程
        self.status_running = False  # 状态窗口运行标志
        self.current_action = None  # AI当前正在执行的操作
        self.console_output = ""  # 控制台输出
        
        # 扩展管理器
        self.extensions = {}
        self.extension_tools = {}
        self.extension_prompts = ""
        
        # 加载扩展
        self._load_extensions()
        
        # 添加system提示词
        system_prompt = """请使用中文回复。不要使用任何特殊格式（如Markdown、代码块、加粗、斜体等），不要使用特殊字符。直接以纯文本形式回答问题。

重要：你有权限通过指令访问和操作用户的计算机系统！

你可以调用以下系统指令来控制程序（所有指令都需要用户确认）：
- @/debug on/off - 开启/关闭调试模式
- @/api <key> - 修改API密钥
- @/model <name> - 修改模型名称
- @/url <url> - 修改API URL
- @/history - 打开对话历史管理界面
- @/clear - 清空当前对话历史
- @/export <file> - 导出当前对话到文件
- @/import <file> - 从文件导入对话
- @/stop - 停止当前输出
- @/info - 显示当前配置信息
- @/help - 显示帮助信息
- @/exit - 退出程序

你可以调用以下工具来操作电脑（所有工具都需要用户确认）：
- @cmd(命令) - 执行系统命令，如查看文件、运行程序、获取系统信息等
- @request_control() - 请求获得电脑操作权限，获得权限后所有工具和指令自动允许

使用 @/指令名 或 @tool_name(参数) 的格式来调用，例如：
系统指令示例：
- @/debug on
- @/export my_chat.json
- @/info

@cmd 工具示例：
- @cmd(dir)
- @cmd(type iflow_chat.py)
- @cmd(wmic logicaldisk get size,freespace,caption)
- @cmd(dir c:\\ /s /o:s)
- @cmd(ipconfig)
- @cmd(tasklist)
- @cmd(netstat -ano)
- @cmd(type C:\\Users\\wayne\\Documents\\test.txt)

电脑操作工具示例（需要先调用 @request_control()）：
- @request_control()
- @mouse_move(500,300)
- @mouse_click(left)
- @keyboard(Hello World)
- @screenshot()
- @view_screenshot(screenshot_20250101_120000.png)

重要说明：
1. 所有调用默认需要用户确认后才执行
2. 指令或工具执行后，执行结果会以用户身份发送给你
3. 收到执行结果后，请继续回复，对结果进行分析或解释
4. 你可以继续调用其他指令，形成多步骤操作
5. 必须在回复的末尾使用指令，其他位置的指令不会被识别和执行
6. 每次回复只能在一个位置使用指令，即在回复的最末尾
7. 每次对话只能使用一个指令
8. @cmd 工具不需要额外权限，可以直接使用
9. 鼠标、键盘、屏幕操作需要先调用 @request_control() 获取权限
10. 当用户需要你操作电脑时，优先使用 @cmd 工具执行命令，只有在需要图形界面操作时才使用鼠标键盘工具
11. 获得电脑控制权限后，所有工具和指令将自动允许执行，无需用户确认
12. 电脑控制权限适用于需要连续执行多个指令的场景

注意：默认情况下所有调用都需要用户确认后才执行。使用 @request_control() 获取权限后，所有操作将自动允许。

当用户要求你查看文件、运行程序、获取系统信息时，请主动使用 @cmd 工具。例如：
- 用户说"帮我看看当前目录有什么文件" -> 回复后加上 @cmd(dir)
- 用户说"帮我运行xxx程序" -> 回复后加上 @cmd(xxx程序路径)
- 用户说"帮我查看系统信息" -> 回复后加上 @cmd(systeminfo)

当用户要求你进行图形界面操作（如点击按钮、输入文字、截图）时，按以下步骤进行：
1. 首先调用 @screenshot() 查看当前屏幕内容
2. 然后调用 @request_control() 获取电脑控制权限
3. 获得权限后，所有工具和指令将自动允许执行
4. 在每一步操作前，必须先调用 @screenshot() 查看当前屏幕状态
5. 依次执行控制操作（@mouse_move, @mouse_click, @keyboard 等）
6. 完成操作后，必须调用 @screenshot() 查看操作结果，确认是否成功
7. 如果需要等待界面响应，可以使用 @wait(秒数) 等待指定时间

键盘输入说明：
- 输入文本：@keyboard(Hello World) - 输入文本内容
- 特殊按键：@keyboard(key:enter) - 按Enter键
- 特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12, backspace, delete 等

示例流程：
- 用户说"帮我点击屏幕上的某个按钮" -> 先 @screenshot() 查看屏幕，然后 @request_control() 获取权限，再 @screenshot() 确认位置，最后 @mouse_move() 和 @mouse_click() 执行操作，完成后 @screenshot() 查看结果"""
        
        # 添加扩展提示词
        if self.extension_prompts:
            system_prompt += "\n\n" + self.extension_prompts
        
        self.messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 自动补全候选项
        self.commands = [
            '/debug on', '/debug off',
            '/api', '/model', '/url',
            '/history', '/clear',
            '/export', '/import',
            '/extension list', '/extension info', '/extension import', '/extension delete',
            '/stop', '/info', '/help', '/exit'
        ]
        
        # 设置readline自动补全（如果可用）
        self.readline_available = readline is not None
        if self.readline_available:
            try:
                readline.set_completer(self.completer)
                readline.parse_and_bind('tab: complete')
                readline.set_completer_delims(' \t\n')
            except Exception:
                self.readline_available = False
    
    def completer(self, text: str, state: int) -> Optional[str]:
        """自动补全函数"""
        options = [cmd for cmd in self.commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None
    
    def show_completions(self, text: str) -> Optional[str]:
        """显示匹配的候选项"""
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]
        if matches:
            print(f"\n[补全] 匹配的候选项:")
            for i, match in enumerate(matches, 1):
                print(f"  {i}. {match}")
            print(f"  0. 取消")
            choice = input(f"\n请选择 (0-{len(matches)}): ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(matches):
                    return matches[idx - 1]
            return None
        return None
    
    def check_api_key(self) -> bool:
        """检查API密钥是否有效"""
        api_key = self.key_manager.get_api_key()
        if not api_key:
            print("\n[系统] 未检测到API密钥，请先输入您的API密钥")
            return False
        
        if self.key_manager.is_expired():
            days = self.key_manager.get_days_remaining()
            print(f"\n[提醒] 您的API密钥已使用超过7天（已过期{abs(days)}天），建议重新输入")
            return False
        else:
            days = self.key_manager.get_days_remaining()
            if days <= 3:
                print(f"\n[提醒] 您的API密钥将在{days}天后过期，建议重新输入")
            return True
    
    def input_api_key(self):
        """输入API密钥"""
        while True:
            api_key = input("请输入您的API密钥: ").strip()
            if api_key:
                self.key_manager.set_api_key(api_key)
                print("✓ API密钥已保存")
                break
            print("API密钥不能为空，请重新输入")
    
    def show_help(self):
        """显示帮助信息"""
        TerminalUI.clear_screen()
        print("=" * 50)
        print("用户指令:")
        print("  /debug on/off  - 开启/关闭调试模式")
        print("  /api <key>     - 修改API密钥")
        print("  /model <name>  - 修改模型名称")
        print("  /url <url>     - 修改API URL")
        print("  /history       - 对话历史管理（新建/选择历史对话）")
        print("  /clear         - 清空当前对话历史")
        print("  /export <file> - 导出当前对话到文件")
        print("  /import <file> - 从文件导入对话")
        print("  /extension     - 扩展管理（查看/导入/删除扩展）")
        print("  /stop          - 停止当前输出")
        print("  /info          - 显示当前配置信息")
        print("  /help          - 显示此帮助信息")
        print("  /exit          - 退出程序")
        print("\nAI调用指令（需用户确认，获得控制权限后自动允许）:")
        print("  @/debug on/off - AI可以开启/关闭调试模式")
        print("  @/api <key>    - AI可以修改API密钥")
        print("  @/model <name> - AI可以修改模型名称")
        print("  @/url <url>    - AI可以修改API URL")
        print("  @/history      - AI可以打开对话历史管理")
        print("  @/clear        - AI可以清空当前对话")
        print("  @/export <file>- AI可以导出对话")
        print("  @/import <file>- AI可以导入对话")
        print("  @/stop         - AI可以停止输出")
        print("  @/info         - AI可以显示配置信息")
        print("  @/help         - AI可以显示帮助")
        print("  @/exit         - AI可以退出程序")
        print("\nAI工具（需用户确认，获得控制权限后自动允许）:")
        print("  @cmd(命令)     - AI可以执行系统命令（不需要额外权限）")
        print("  @request_control() - AI请求获得电脑操作权限，获得后所有操作自动允许")
        print("  @mouse_move(x,y) - AI移动鼠标到指定坐标（需权限）")
        print("  @mouse_click(按钮) - AI点击鼠标（需权限）")
        print("  @keyboard(文本或key:按键)  - AI输入键盘文本或特殊按键（需权限）")
        print("  @screenshot()   - AI获取屏幕截图并保存到 iflow_screenshots 文件夹（AI可以看到）")
        print("  @view_screenshot(文件名) - AI分析指定截图的内容")
        print("  @wait(秒数)     - AI等待指定秒数")
        print("  @show_message(标题,内容) - AI显示普通信息框")
        print("  @show_advanced_message(标题,内容,类型,按钮) - AI显示高级信息框")
        if self.readline_available:
            print("\n自动补全:")
            print("  Tab 键         - 自动补全指令")
            print("  ? 键           - 显示候选项列表（输入部分指令后）")
        print("\n说明:")
        print("  - 每次对话后自动保存到 iflow_conversations 目录")
        print("  - 历史对话不会被自动删除")
        print("  - 使用 ↑↓ 方向键选择，回车键确认")
        print("  - AI调用指令和工具默认需要用户确认")
        print("  - 使用 @request_control() 获得电脑操作权限后，所有操作自动允许")
        print("  - 电脑控制权限适用于需要连续执行多个指令的场景")
        print("  - cmd工具输出只在调试模式下显示，但会记录到日志")
        print("  - 所有日志记录到 iflow.log 文件")
        print("  - @cmd工具不需要额外权限，可以直接使用")
        print("  - 鼠标、键盘、屏幕操作需要先调用 @request_control() 获取权限")
        print("  - 权限请求窗口会显示在左上角并顶置")
        print("=" * 50)
        input("\n按回车继续...")
    
    def show_extension_manager(self):
        """显示扩展管理界面"""
        while True:
            options = ["查看扩展列表", "查看扩展详情", "导入扩展", "删除扩展", "返回"]
            selected = TerminalUI.show_menu("扩展管理", options)
            
            if selected == 0:
                # 查看扩展列表
                self._list_extensions()
                input("\n按回车继续...")
            elif selected == 1:
                # 查看扩展详情
                self._show_extension_detail()
                input("\n按回车继续...")
            elif selected == 2:
                # 导入扩展
                self._import_extension()
                input("\n按回车继续...")
            elif selected == 3:
                # 删除扩展
                self._delete_extension()
                input("\n按回车继续...")
            elif selected == 4:
                # 返回
                return
    
    def _list_extensions(self):
        """列出所有扩展"""
        TerminalUI.clear_screen()
        print("=" * 50)
        print("已加载的扩展:")
        print("=" * 50)
        
        if not self.extensions:
            print("没有加载任何扩展")
            return
        
        for i, (name, ext) in enumerate(self.extensions.items(), 1):
            print(f"\n{i}. {name}")
            print(f"   描述: {ext.description}")
            print(f"   版本: {ext.version}")
            print(f"   作者: {ext.author}")
        
        print(f"\n总计: {len(self.extensions)} 个扩展")
        print("=" * 50)
    
    def _show_extension_detail(self):
        """显示扩展详情"""
        if not self.extensions:
            print("没有加载任何扩展")
            return
        
        # 选择扩展
        ext_names = list(self.extensions.keys())
        options = ext_names + ["返回"]
        selected = TerminalUI.show_menu("选择扩展", options)
        
        if selected == len(ext_names):
            return
        
        ext_name = ext_names[selected]
        ext = self.extensions[ext_name]
        
        # 显示详情
        TerminalUI.clear_screen()
        print("=" * 50)
        print(f"扩展详情: {ext_name}")
        print("=" * 50)
        print(f"名称: {ext.name}")
        print(f"描述: {ext.description}")
        print(f"版本: {ext.version}")
        print(f"作者: {ext.author}")
        
        # 显示工具
        tools = ext.get_tools()
        print(f"\n工具 ({len(tools)} 个):")
        for tool_name in tools.keys():
            print(f"  - {tool_name}")
        
        # 显示提示词
        prompt = ext.get_prompt()
        if prompt:
            print(f"\n提示词:")
            print(prompt)
        
        print("=" * 50)
    
    def _import_extension(self):
        """导入扩展"""
        TerminalUI.clear_screen()
        print("=" * 50)
        print("导入扩展")
        print("=" * 50)
        
        # 输入压缩包路径
        zip_path = input("请输入扩展压缩包路径: ").strip()
        
        if not zip_path:
            print("已取消")
            return
        
        if not os.path.exists(zip_path):
            print(f"错误: 文件不存在: {zip_path}")
            return
        
        try:
            import zipfile
            import shutil
            
            # 获取扩展目录
            extensions_dir = "iflow_extensions"
            
            # 解压扩展
            print("正在解压...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extensions_dir)
            
            print("✓ 扩展导入成功！")
            print("请重启程序以加载新扩展。")
            
        except Exception as e:
            print(f"✗ 导入失败: {str(e)}")
        
        print("=" * 50)
    
    def _delete_extension(self):
        """删除扩展"""
        if not self.extensions:
            print("没有加载任何扩展")
            return
        
        # 选择扩展
        ext_names = list(self.extensions.keys())
        options = ext_names + ["返回"]
        selected = TerminalUI.show_menu("选择要删除的扩展", options)
        
        if selected == len(ext_names):
            return
        
        ext_name = ext_names[selected]
        
        # 确认删除
        print(f"\n确定要删除扩展 '{ext_name}' 吗？")
        print("此操作将删除扩展文件夹，无法撤销。")
        confirm = input("确认删除？(y/n): ").strip().lower()
        
        if confirm != 'y':
            print("已取消")
            return
        
        try:
            ext_dir = os.path.join("iflow_extensions", ext_name)
            
            if os.path.exists(ext_dir):
                import shutil
                shutil.rmtree(ext_dir)
                print(f"✓ 扩展 '{ext_name}' 删除成功！")
                print("请重启程序以生效。")
            else:
                print(f"错误: 扩展目录不存在: {ext_dir}")
                
        except Exception as e:
            print(f"✗ 删除失败: {str(e)}")
    
    def show_info(self):
        """显示当前配置信息"""
        TerminalUI.clear_screen()
        print("=" * 50)
        print("当前配置:")
        print(f"  模型: {self.model}")
        print(f"  API URL: {self.api_url}")
        print(f"  调试模式: {'开启' if self.debug_mode else '关闭'}")
        print(f"  AI控制: {'开启' if self.ai_control_enabled else '关闭'}")
        print(f"  对话轮数: {len([m for m in self.messages if m['role'] == 'user'])}")
        print(f"  API密钥状态: {'已设置' if self.key_manager.get_api_key() else '未设置'}")
        if self.key_manager.get_api_key():
            days = self.key_manager.get_days_remaining()
            if self.key_manager.is_expired():
                print(f"  密钥过期状态: 已过期 {abs(days)} 天")
            else:
                print(f"  密钥过期状态: 剩余 {days} 天")
        
        # 添加扩展信息
        if self.extensions:
            print("\n已加载扩展:")
            for ext_name, ext in self.extensions.items():
                print(f"  {ext_name} (v{ext.version})")
                print(f"    描述: {ext.description}")
                print(f"    作者: {ext.author}")
                tools = ext.get_tools()
                print(f"    工具: {', '.join(tools.keys())}")
        
        print("=" * 50)
        input("\n按回车继续...")
    
    def show_history(self):
        """显示对话历史"""
        if not self.messages:
            TerminalUI.clear_screen()
            print("[系统] 暂无对话历史")
            input("\n按回车继续...")
            return
        
        TerminalUI.clear_screen()
        print("=" * 50)
        print("对话历史:")
        print("=" * 50)
        for i, msg in enumerate(self.messages, 1):
            role = "你" if msg['role'] == 'user' else "助手"
            content = msg['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"\n[{i}] {role}:")
            print(f"{content}")
        print("\n" + "=" * 50)
        input("\n按回车继续...")
    
    def export_history(self, filename: str):
        """导出对话历史"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 对话历史已导出到 {filename}")
        except Exception as e:
            print(f"\n[错误] 导出失败: {e}")
    
    def import_history(self, filename: str):
        """导入对话历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_messages = json.load(f)
            
            # 检查是否有system消息，如果没有则添加
            has_system = any(msg['role'] == 'system' for msg in imported_messages)
            if not has_system:
                imported_messages.insert(0, {
                    "role": "system",
                    "content": "请使用中文回复。不要使用任何特殊格式（如Markdown、代码块、加粗、斜体等），不要使用特殊字符。直接以纯文本形式回答问题。"
                })
            
            self.messages = imported_messages
            print(f"\n✓ 对话历史已从 {filename} 导入")
        except Exception as e:
            print(f"\n[错误] 导入失败: {e}")
    
    def clear_history(self):
        """清空对话历史"""
        # 保留system消息
        system_msg = None
        for msg in self.messages:
            if msg['role'] == 'system':
                system_msg = msg
                break
        self.messages = [system_msg] if system_msg else []
        self.current_conversation_name = None
        TerminalUI.clear_screen()
        print("[系统] 对话历史已清空")
        input("\n按回车继续...")
    
    def set_debug(self, enabled: bool):
        """设置调试模式"""
        self.debug_mode = enabled
        status = "开启" if enabled else "关闭"
        print(f"\n[系统] 调试模式已{status}")
        self._log(f"调试模式已{status}")
    
    def show_status_window(self):
        """显示状态窗口"""
        import tkinter as tk
        from tkinter import ttk
        
        self.status_window = tk.Tk()
        self.status_window.title("iFlow 状态")
        self.status_window.geometry("350x350")
        self.status_window.attributes('-topmost', True)
        
        # 计算屏幕尺寸，将窗口放在右上角
        screen_width = self.status_window.winfo_screenwidth()
        screen_height = self.status_window.winfo_screenheight()
        x = screen_width - 370
        y = 20
        self.status_window.geometry(f'+{x}+{y}')
        
        # 禁止调整窗口大小
        self.status_window.resizable(False, False)
        
        # 创建样式
        style = ttk.Style()
        style.configure('Status.TLabel', font=('Arial', 9))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Action.TLabel', font=('Arial', 9), foreground='blue')
        style.configure('Output.TLabel', font=('Consolas', 8))
        
        # 标题
        ttk.Label(self.status_window, text="iFlow 状态", style='Header.TLabel').pack(pady=5)
        
        # AI控制状态
        self.ai_control_label = ttk.Label(self.status_window, text="AI控制: 关闭", style='Status.TLabel')
        self.ai_control_label.pack(pady=2)
        
        # 当前操作
        self.action_label = ttk.Label(self.status_window, text="正在执行: 等待中...", style='Action.TLabel')
        self.action_label.pack(pady=2)
        
        # 调试模式状态
        self.debug_mode_label = ttk.Label(self.status_window, text=f"调试模式: {'开启' if self.debug_mode else '关闭'}", style='Status.TLabel')
        self.debug_mode_label.pack(pady=2)
        
        # 时间显示
        self.time_label = ttk.Label(self.status_window, text="", style='Status.TLabel')
        self.time_label.pack(pady=2)
        
        # 分隔线
        ttk.Separator(self.status_window, orient='horizontal').pack(fill='x', pady=5)
        
        # 控制台输出标签
        ttk.Label(self.status_window, text="控制台输出:", style='Status.TLabel').pack(anchor='w', padx=10)
        
        # 控制台输出文本框
        self.console_output_text = tk.Text(self.status_window, height=8, width=38, 
                                          font=('Consolas', 8), wrap='word',
                                          bg='#f5f5f5', relief='sunken', borderwidth=1)
        self.console_output_text.pack(padx=5, pady=2)
        
        # 初始化控制台输出
        self.console_output = ""
        
        self.status_running = True
        self.update_status_window()
        self.status_window.mainloop()
    
    def update_status_window(self):
        """更新状态窗口"""
        if not self.status_running or not self.status_window:
            return
        
        try:
            import tkinter as tk
            
            # 更新AI控制状态
            ai_control_text = f"AI控制: {'开启' if self.ai_control_enabled else '关闭'}"
            if hasattr(self, 'ai_control_label'):
                self.ai_control_label.config(text=ai_control_text)
            
            # 更新当前操作
            if self.current_action:
                action_text = f"正在执行: {self.current_action}"
            else:
                action_text = "正在执行: 等待中..."
            if hasattr(self, 'action_label'):
                self.action_label.config(text=action_text)
            
            # 更新调试模式状态
            debug_text = f"调试模式: {'开启' if self.debug_mode else '关闭'}"
            if hasattr(self, 'debug_mode_label'):
                self.debug_mode_label.config(text=debug_text)
            
            # 更新时间
            time_text = datetime.now().strftime("%H:%M:%S")
            if hasattr(self, 'time_label'):
                self.time_label.config(text=time_text)
            
            # 更新控制台输出
            if hasattr(self, 'console_output_text') and hasattr(self, 'console_output'):
                try:
                    self.console_output_text.config(state='normal')
                    self.console_output_text.delete('1.0', tk.END)
                    # 只显示最后500个字符
                    display_output = self.console_output[-500:] if len(self.console_output) > 500 else self.console_output
                    self.console_output_text.insert('1.0', display_output)
                    self.console_output_text.config(state='disabled')
                    # 自动滚动到底部
                    self.console_output_text.see(tk.END)
                except Exception:
                    pass
            
            # 1秒后再次更新
            self.status_window.after(1000, self.update_status_window)
        except Exception:
            self.status_running = False
    
    def close_status_window(self):
        """关闭状态窗口"""
        self.status_running = False
        if self.status_window:
            try:
                self.status_window.destroy()
            except Exception:
                pass
            self.status_window = None
    
    def start_status_window(self):
        """启动状态窗口"""
        if self.status_window is None:
            import threading
            self.status_thread = threading.Thread(target=self.show_status_window, daemon=True)
            self.status_thread.start()
    
    def _log(self, message: str):
        """记录日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass
    
    def _load_extensions(self):
        """加载扩展"""
        if not EXTENSIONS_AVAILABLE or extension_manager is None:
            print("扩展管理器不可用，跳过扩展加载")
            return
        
        try:
            # 加载所有扩展
            extension_manager.load_extensions()
            self.extensions = extension_manager.extensions
            
            # 收集所有扩展的工具和提示词
            for ext_name, ext in self.extensions.items():
                # 收集工具
                tools = ext.get_tools()
                for tool_name, tool_func in tools.items():
                    self.extension_tools[tool_name] = (ext, tool_func)
                
                # 收集提示词
                prompt = ext.get_prompt()
                if prompt:
                    self.extension_prompts += prompt + "\n\n"
            
            print(f"已加载 {len(self.extensions)} 个扩展")
            print(f"已加载 {len(self.extension_tools)} 个工具")
        except Exception as e:
            print(f"加载扩展失败: {e}")
    
    def set_model(self, model_name: str):
        """设置模型名称"""
        self.model = model_name
        print(f"\n[系统] 模型已设置为: {model_name}")
    
    def set_api_url(self, url: str):
        """设置API URL"""
        self.api_url = url
        print(f"\n[系统] API URL已设置为: {url}")
    
    def stop_output(self):
        """停止输出"""
        with self.lock:
            self.stop_flag = True
        print("\n[系统] 正在停止输出...")
    
    def save_current_conversation(self):
        """保存当前对话"""
        if self.auto_save and len([m for m in self.messages if m['role'] in ['user', 'assistant']]) > 0:
            # 如果没有标题，自动生成
            if not self.current_conversation_name:
                self.current_conversation_name = self.generate_conversation_title()
            self.key_manager.save_conversation(self.messages, self.current_conversation_name)
    
    def generate_conversation_title(self) -> str:
        """生成对话标题"""
        # 获取前几条用户消息作为上下文
        user_messages = [m['content'] for m in self.messages if m['role'] == 'user'][:3]
        if not user_messages:
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        
        context = "\n".join([f"用户: {msg}" for msg in user_messages])
        
        headers = {
            "Authorization": f"Bearer {self.key_manager.get_api_key()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个标题生成器。根据对话内容生成一个简短的中文标题（不超过10个字），不要使用任何标点符号或特殊字符。只返回标题内容，不要其他文字。"
                },
                {
                    "role": "user",
                    "content": f"请为以下对话生成一个标题：\n\n{context}"
                }
            ],
            "stream": False,
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    title = data['choices'][0]['message']['content'].strip()
                    # 清理标题，移除可能的引号和标点
                    title = title.replace('"', '').replace("'", '').replace('。', '').replace('，', '')
                    if title:
                        return title
        except Exception:
            pass
        
        # 如果生成失败，使用时间戳
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """执行系统命令（需要用户确认）"""
        print(f"\n[系统] AI请求执行命令: {command}")
        
        # 检查AI控制权限
        if self.ai_control_enabled:
            print("[AI控制] 自动执行命令")
            self._log(f"[AI控制] 自动执行命令: {command}")
        else:
            confirm = input("是否允许执行此命令？(y/n): ").strip().lower()
            if confirm != 'y':
                return False, "用户取消执行"
        
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n错误: {result.stderr}"
            
            # 保存到控制台输出
            self.console_output = f"$ {command}\n{output}"
            
            return True, output
        except subprocess.TimeoutExpired:
            error_msg = "命令执行超时"
            self.console_output = f"$ {command}\n{error_msg}"
            return False, error_msg
        except Exception as e:
            error_msg = f"执行失败: {str(e)}"
            self.console_output = f"$ {command}\n{error_msg}"
            return False, error_msg
    
    def handle_ai_tool_call(self, tool_name: str, tool_args: str) -> Tuple[bool, str]:
        """处理AI工具调用"""
        if tool_name == 'cmd':
            return self.execute_command(tool_args)
        elif tool_name == 'mouse_move':
            return self.mouse_move(tool_args)
        elif tool_name == 'mouse_click':
            return self.mouse_click(tool_args)
        elif tool_name == 'keyboard':
            return self.keyboard_input(tool_args)
        elif tool_name == 'screenshot':
            return self.take_screenshot()
        elif tool_name == 'view_screenshot':
            return self.view_screenshot(tool_args)
        elif tool_name == 'wait':
            return self.wait(tool_args)
        elif tool_name == 'request_control':
            return self.request_computer_control()
        elif tool_name in self.extension_tools:
            # 处理扩展工具
            ext, tool_func = self.extension_tools[tool_name]
            confirm_callback = lambda title, message: self._confirm_action(title, message)
            try:
                return tool_func(tool_args, confirm_callback)
            except Exception as e:
                return False, f"扩展工具执行失败: {str(e)}"
        else:
            return False, f"未知工具: {tool_name}"
    
    def _confirm_action(self, title: str, message: str) -> bool:
        """确认操作"""
        if self.ai_control_enabled:
            return True
        
        print(f"\n[{title}] {message}")
        confirm = input("是否允许？(y/n): ").strip().lower()
        return confirm == 'y'
    
    def request_computer_control(self) -> Tuple[bool, str]:
        """请求AI电脑操作权限"""
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.title("AI电脑操作权限请求")
        root.geometry("400x200")
        root.attributes('-topmost', True)  # 顶置窗口
        root.geometry('+0+0')  # 左上角
        
        label = tk.Label(root, text="AI请求获得电脑操作权限\n\n允许AI模拟鼠标、键盘操作\n并获取屏幕内容", 
                        font=('Arial', 12), justify='center')
        label.pack(pady=20)
        
        result = {'allowed': False}
        
        def allow():
            result['allowed'] = True
            root.destroy()
        
        def deny():
            result['allowed'] = False
            root.destroy()
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="允许", command=allow, width=10, bg='#4CAF50', fg='white').pack(side='left', padx=10)
        tk.Button(btn_frame, text="拒绝", command=deny, width=10, bg='#f44336', fg='white').pack(side='left', padx=10)
        
        root.mainloop()
        
        if result['allowed']:
            self.ai_control_enabled = True
            self._log("用户授予AI电脑操作权限")
            # 启动状态窗口
            self.start_status_window()
            return True, "已获得电脑操作权限"
        else:
            self._log("用户拒绝AI电脑操作权限")
            return False, "用户拒绝授予权限"
    
    def mouse_move(self, args: str) -> Tuple[bool, str]:
        """移动鼠标"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        try:
            parts = args.split(',')
            if len(parts) == 2:
                x, y = int(parts[0].strip()), int(parts[1].strip())
                self.current_action = f"移动鼠标到 ({x}, {y})"
                pyautogui.moveTo(x, y, duration=0.5)
                self._log(f"AI移动鼠标到 ({x}, {y})")
                self.current_action = None
                return True, f"鼠标已移动到 ({x}, {y})"
            else:
                return False, "参数格式错误，应为: x,y"
        except Exception as e:
            self.current_action = None
            return False, f"移动鼠标失败: {str(e)}"
    
    def mouse_click(self, args: str) -> Tuple[bool, str]:
        """鼠标点击"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行鼠标操作"
        try:
            button = args.strip() if args else 'left'
            self.current_action = f"点击鼠标 {button}"
            pyautogui.click(button=button)
            self._log(f"AI点击鼠标 {button}")
            self.current_action = None
            return True, f"已点击鼠标 {button}"
        except Exception as e:
            self.current_action = None
            return False, f"鼠标点击失败: {str(e)}"
    
    def keyboard_input(self, args: str) -> Tuple[bool, str]:
        """键盘输入
        支持两种模式：
        1. 文本输入：@keyboard(Hello World) - 输入文本
        2. 特殊按键：@keyboard(key:enter) - 按Enter键
        特殊按键包括：enter, space, tab, esc, shift, ctrl, alt, up, down, left, right, f1-f12 等
        """
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行键盘操作"
        try:
            # 检查是否是特殊按键
            if args.startswith('key:'):
                key_name = args[4:].strip().lower()
                self.current_action = f"按下按键: {key_name}"
                pyautogui.press(key_name)
                self._log(f"AI按下按键: {key_name}")
                self.current_action = None
                return True, f"已按下按键: {key_name}"
            else:
                # 普通文本输入
                self.current_action = f"输入文本: {args}"
                pyautogui.typewrite(args)
                self._log(f"AI输入文本: {args}")
                self.current_action = None
                return True, f"已输入文本: {args}"
        except Exception as e:
            self.current_action = None
            return False, f"键盘输入失败: {str(e)}"
    
    def take_screenshot(self) -> Tuple[bool, str]:
        """获取屏幕截图"""
        if pyautogui is None:
            return False, "pyautogui模块未安装，无法执行截图操作"
        try:
            self.current_action = "正在截图..."
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(APIKeyManager.SCREENSHOT_DIR, filename)
            screenshot.save(filepath)
            self._log(f"AI获取屏幕截图: {filepath}")
            
            # 使用图像识别分析截图内容
            try:
                self.current_action = None
                # 使用 image_read 工具让 AI 看到截图内容
                return True, f"屏幕截图已保存到: {filepath}\n截图尺寸: {screenshot.size}\n[图像数据已准备好，请分析屏幕内容]"
            except Exception as e:
                self.current_action = None
                return True, f"屏幕截图已保存到: {filepath}\n截图尺寸: {screenshot.size}"
                
        except Exception as e:
            self.current_action = None
            error_msg = str(e)
            if "pyscreeze" in error_msg or "Pillow" in error_msg:
                return False, f"获取屏幕截图失败: pyautogui依赖不兼容\n建议: pip install --upgrade pillow pyscreeze pyautogui\n错误详情: {error_msg}"
            else:
                return False, f"获取屏幕截图失败: {error_msg}"
    
    def view_screenshot(self, filename: str) -> Tuple[bool, str]:
        """查看屏幕截图（让 AI 分析截图内容）"""
        filepath = os.path.join(APIKeyManager.SCREENSHOT_DIR, filename)
        if not os.path.exists(filepath):
            return False, f"截图文件不存在: {filepath}"
        
        try:
            # 读取截图并让 AI 分析
            from PIL import Image
            
            # 将截图转换为 base64
            with open(filepath, 'rb') as f:
                img_data = f.read()
            
            import base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            self._log(f"AI分析截图: {filepath}")
            return True, f"[屏幕截图: {filename}]\n[图像数据: {img_base64[:500]}...]\n请分析这个截图的内容"
            
        except Exception as e:
            return False, f"读取截图失败: {str(e)}"
    
    def wait(self, args: str) -> Tuple[bool, str]:
        """等待指定秒数"""
        try:
            seconds = float(args.strip())
            if seconds <= 0:
                return False, "等待时间必须大于0"
            
            import time
            self.current_action = f"等待 {seconds} 秒..."
            self._log(f"AI等待 {seconds} 秒")
            time.sleep(seconds)
            self.current_action = None
            return True, f"已等待 {seconds} 秒"
        except ValueError:
            return False, "参数格式错误，应为秒数（数字）"
        except Exception as e:
            self.current_action = None
            return False, f"等待失败: {str(e)}"
    
    def history_manager(self):
        """对话历史管理界面"""
        while True:
            options = ["新建对话", "选择历史对话", "返回"]
            selected = TerminalUI.show_menu("对话历史管理", options)
            
            if selected == 0:
                # 新建对话
                self.current_conversation_name = None
                # 保留system消息
                system_msg = None
                for msg in self.messages:
                    if msg['role'] == 'system':
                        system_msg = msg
                        break
                self.messages = [system_msg] if system_msg else []
                TerminalUI.clear_screen()
                print("[系统] 已创建新对话")
                input("\n按回车继续...")
                return
            elif selected == 1:
                # 选择历史对话
                conversations = self.key_manager.list_conversations()
                if not conversations:
                    TerminalUI.clear_screen()
                    print("[系统] 暂无历史对话")
                    input("\n按回车继续...")
                    continue
                
                idx = TerminalUI.show_list("选择历史对话", conversations)
                if idx is not None:
                    selected = conversations[idx]
                    loaded = self.key_manager.load_conversation(selected[0])
                    if loaded:
                        # 显示历史对话内容
                        TerminalUI.clear_screen()
                        print("=" * 50)
                        print(f"历史对话: {selected[1]}")
                        print("=" * 50)
                        
                        history_text = ""
                        for msg in loaded:
                            role = "你" if msg['role'] == 'user' else ("系统" if msg['role'] == 'system' else "助手")
                            content = msg['content']
                            history_text += f"\n[{role}]:\n{content}\n"
                        
                        print(history_text)
                        print("=" * 50)
                        input("\n按回车继续加载...")
                        
                        # 以system身份发送历史对话内容
                        self.messages = loaded
                        self.current_conversation_name = selected[1]
                        self.messages.append({
                            "role": "system",
                            "content": f"以上是历史对话内容。请根据历史对话继续回复用户。"
                        })
                        TerminalUI.clear_screen()
                        print(f"[系统] 已加载对话: {selected[1]}")
                        input("\n按回车继续...")
                        return
            elif selected == 2:
                # 返回
                return
    
    def _continue_conversation(self):
        """继续对话，让AI处理执行结果"""
        headers = {
            "Authorization": f"Bearer {self.key_manager.get_api_key()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        }
        
        try:
            print("\n助手: ", end="", flush=True)
            assistant_response = ""
            
            with self.lock:
                self.stop_flag = False
                self.is_streaming = True
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            
            if self.debug_mode:
                print(f"[调试] 状态码: {response.status_code}", end="", flush=True)
            response.raise_for_status()
            
            # 处理SSE流
            line_count = 0
            for line in response.iter_lines(decode_unicode=True):
                with self.lock:
                    if self.stop_flag:
                        print("\n[系统] 输出已停止")
                        break
                
                if line:
                    line_count += 1
                    line_str = line.strip()
                    if self.debug_mode and line_count <= 5:
                        print(f"\n[调试行{line_count}] {line_str[:200]}", end="", flush=True)
                    
                    if line_str.startswith('data:'):
                        data_str = line_str[5:]
                        if data_str.startswith(' '):
                            data_str = data_str[1:]
                        if data_str == '[DONE]':
                            if self.debug_mode:
                                print(f"\n[调试] 收到DONE信号", end="", flush=True)
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'delta' in choice:
                                    delta = choice['delta']
                                    content = delta.get('content', '')
                                    if content:
                                        print(content, end="", flush=True)
                                        assistant_response += content
                        except json.JSONDecodeError as e:
                            if self.debug_mode:
                                print(f"\n[调试] JSON解析失败: {data_str[:100]}", end="", flush=True)
                            continue
            
            if self.debug_mode:
                print(f"\n[调试] 共接收{line_count}行数据", end="", flush=True)
            print()
            
            # 保存助手回复
            if assistant_response:
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                self.save_current_conversation()
                
                # 检查AI是否又调用了指令
                execution_results = self._execute_ai_commands(assistant_response)
                if execution_results:
                    print(f"\n{execution_results}")
                    self.messages.append({
                        "role": "user",
                        "content": f"指令执行结果：{execution_results}\n\n请根据执行结果继续回复。"
                    })
                    self.save_current_conversation()
                    # 递归继续对话
                    self._continue_conversation()
            else:
                print("[警告] 未收到任何回复内容")
                
        except requests.exceptions.HTTPError as e:
            print(f"\n[错误] HTTP错误: {e}")
            print(f"[调试] 响应内容: {response.text if 'response' in locals() else 'N/A'}")
        except requests.exceptions.RequestException as e:
            print(f"\n[错误] 请求失败: {e}")
        except Exception as e:
            print(f"\n[错误] 发生异常: {e}")
        finally:
            with self.lock:
                self.is_streaming = False
    
    def stream_chat(self, user_message: str):
        """流式对话"""
        if not user_message.strip():
            return
        
        # 记录用户输入
        self._log(f"用户: {user_message}")
        
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # 准备请求
        headers = {
            "Authorization": f"Bearer {self.key_manager.get_api_key()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        }
        
        try:
            print("\n助手: ", end="", flush=True)
            assistant_response = ""
            
            with self.lock:
                self.stop_flag = False
                self.is_streaming = True
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            
            # 打印响应状态
            if self.debug_mode:
                print(f"[调试] 状态码: {response.status_code}", end="", flush=True)
            response.raise_for_status()
            
            # 处理SSE流
            line_count = 0
            for line in response.iter_lines(decode_unicode=True):
                with self.lock:
                    if self.stop_flag:
                        print("\n[系统] 输出已停止")
                        break
                
                if line:
                    line_count += 1
                    line_str = line.strip()
                    # 打印前5行原始数据用于调试
                    if self.debug_mode and line_count <= 5:
                        print(f"\n[调试行{line_count}] {line_str[:200]}", end="", flush=True)
                    
                    # 支持 data: 和 data:{ 两种格式
                    if line_str.startswith('data:'):
                        data_str = line_str[5:]  # 去掉 "data:"
                        if data_str.startswith(' '):
                            data_str = data_str[1:]  # 去掉空格
                        if data_str == '[DONE]':
                            if self.debug_mode:
                                print(f"\n[调试] 收到DONE信号", end="", flush=True)
                            break
                        try:
                            data = json.loads(data_str)
                            # 检查choices
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                # 检查delta
                                if 'delta' in choice:
                                    delta = choice['delta']
                                    # 获取content
                                    content = delta.get('content', '')
                                    if content:
                                        print(content, end="", flush=True)
                                        assistant_response += content
                        except json.JSONDecodeError as e:
                            if self.debug_mode:
                                print(f"\n[调试] JSON解析失败: {data_str[:100]}", end="", flush=True)
                            continue
            
            if self.debug_mode:
                print(f"\n[调试] 共接收{line_count}行数据", end="", flush=True)
            print()  # 换行
            
            # 保存助手回复
            if assistant_response:
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                # 记录AI回复
                self._log(f"助手: {assistant_response}")
                # 自动保存对话
                self.save_current_conversation()
                
                # 检查并执行AI调用的指令，获取执行结果
                execution_results = self._execute_ai_commands(assistant_response)
                
                # 如果有执行结果，以用户身份发送给AI，让AI继续处理
                if execution_results:
                    print(f"\n{execution_results}")
                    # 添加用户消息（执行结果）
                    self.messages.append({
                        "role": "user",
                        "content": f"指令执行结果：{execution_results}\n\n请根据执行结果继续回复。"
                    })
                    # 自动保存
                    self.save_current_conversation()
                    
                    # 继续对话，让AI处理执行结果
                    self._continue_conversation()
            else:
                print("[警告] 未收到任何回复内容")
                
        except requests.exceptions.HTTPError as e:
            print(f"\n[错误] HTTP错误: {e}")
            print(f"[调试] 响应内容: {response.text if 'response' in locals() else 'N/A'}")
        except requests.exceptions.RequestException as e:
            print(f"\n[错误] 请求失败: {e}")
        except Exception as e:
            print(f"\n[错误] 发生异常: {e}")
        finally:
            with self.lock:
                self.is_streaming = False
    
    def check_user_input_during_stream(self):
        """在流式输出时检查用户输入"""
        if os.name == 'nt':
            # Windows平台使用msvcrt检测输入
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8', errors='ignore')
        else:
            # Linux/Unix平台使用select
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
        return None
    
    def _execute_ai_commands(self, response: str) -> str:
        """执行AI回复中的指令和工具调用，返回执行结果"""
        import re
        
        execution_results = []
        
        # 只提取回复末尾的指令（最后一个 @/ 或 @ 开头的指令）
        # 先找到所有可能的指令位置
        cmd_pattern = r'@/(\w+)(?:\s+(.*))?'
        tool_pattern = r'@(\w+)\((.*?)\)'
        
        # 找到所有指令匹配
        cmd_matches = list(re.finditer(cmd_pattern, response))
        tool_matches = list(re.finditer(tool_pattern, response))
        
        # 合并所有匹配并按位置排序
        all_matches = []
        for match in cmd_matches:
            all_matches.append((match.start(), 'cmd', match))
        for match in tool_matches:
            all_matches.append((match.start(), 'tool', match))
        
        all_matches.sort(key=lambda x: x[0])
        
        # 只处理最后一个指令（末尾的指令）
        if all_matches:
            last_match = all_matches[-1]
            match_type, match_obj = last_match[1], last_match[2]
            
            if match_type == 'cmd':
                cmd = match_obj.group(1)
                args = match_obj.group(2) if match_obj.group(2) else ""
                full_cmd = f"/{cmd}"
                if args:
                    full_cmd += f" {args}"
                
                # 退出指令需要特别确认
                if cmd.lower() == 'exit':
                    print(f"\n[系统] AI请求退出程序")
                    # 检查AI控制权限
                    if self.ai_control_enabled:
                        print("[AI控制] 自动允许退出")
                        self._log("[AI控制] AI退出程序")
                        print("[系统] 正在退出...")
                        sys.exit(0)
                    else:
                        confirm = input("是否允许AI退出程序？(y/n): ").strip().lower()
                        if confirm == 'y':
                            print("[系统] 正在退出...")
                            sys.exit(0)
                        else:
                            print("[系统] 已取消退出")
                            execution_results.append(f"[系统] 用户取消了退出指令")
                else:
                    # 其他指令需要用户确认
                    print(f"\n[系统] AI请求执行指令: {full_cmd}")
                    
                    # 检查AI控制权限
                    if self.ai_control_enabled:
                        print("[AI控制] 自动执行指令")
                        self._log(f"[AI控制] AI执行指令: {full_cmd}")
                    else:
                        confirm = input("是否允许执行？(y/n): ").strip().lower()
                        if confirm != 'y':
                            print(f"[系统] 已取消执行: {full_cmd}")
                            execution_results.append(f"[系统] 用户取消了指令 {full_cmd}")
                            if execution_results:
                                return "\n\n" + "\n".join(execution_results)
                            return ""
                    
                    result = self.handle_command(full_cmd)
                    
                    if result is not None and result is not True:
                        # 指令已执行
                        print(f"[系统] 指令执行完成: {full_cmd}")
                        execution_results.append(f"[系统] 指令 {full_cmd} 执行成功")
                    else:
                        execution_results.append(f"[系统] 指令 {full_cmd} 执行完成")
            
            elif match_type == 'tool':
                tool_name = match_obj.group(1)
                tool_args = match_obj.group(2) if match_obj.group(2) else ""
                
                print(f"\n[系统] AI请求调用工具: {tool_name}")
                self._log(f"AI请求调用工具: {tool_name}({tool_args})")
                
                # 检查是否需要确认（AI控制权限下自动允许所有工具）
                need_confirm = not self.ai_control_enabled
                
                if need_confirm:
                    confirm = input("是否允许调用此工具？(y/n): ").strip().lower()
                    if confirm != 'y':
                        print(f"[系统] 已取消调用工具: {tool_name}")
                        execution_results.append(f"[系统] 用户取消了工具 {tool_name}")
                        if execution_results:
                            return "\n\n" + "\n".join(execution_results)
                        return ""
                else:
                    print(f"[AI控制] 自动执行工具: {tool_name}")
                
                success, result = self.handle_ai_tool_call(tool_name, tool_args)
                
                if success:
                    print(f"[系统] 工具执行成功")
                    self._log(f"工具 {tool_name} 执行成功")
                    if result.strip():
                        # 只在调试模式下输出结果
                        if self.debug_mode:
                            print(f"输出:\n{result}")
                        execution_results.append(f"[工具 {tool_name} 输出]:\n{result}")
                        # 总是记录到日志
                        self._log(f"工具 {tool_name} 输出: {result}")
                    else:
                        execution_results.append(f"[工具 {tool_name}] 执行成功，无输出")
                        self._log(f"工具 {tool_name} 执行成功，无输出")
                else:
                    print(f"[系统] 工具执行失败: {result}")
                    execution_results.append(f"[工具 {tool_name}] 执行失败: {result}")
                    self._log(f"工具 {tool_name} 执行失败: {result}")
        
        # 返回执行结果
        if execution_results:
            return "\n\n" + "\n".join(execution_results)
        return ""
    
    def handle_command(self, cmd: str) -> bool:
        """处理指令，返回True表示已处理，False表示继续对话"""
        cmd = cmd.strip()
        
        if not cmd.startswith('/'):
            return False
        
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == '/help':
            self.show_help()
        elif command == '/extension':
            self.show_help()
        elif command == '/extension':
            if args:
                # 处理扩展子命令
                parts = args.split()
                sub_command = parts[0].lower() if parts else ""
                
                if sub_command == 'list':
                    self._list_extensions()
                    input("\n按回车继续...")
                elif sub_command == 'info':
                    if len(parts) > 1:
                        ext_name = parts[1]
                        if ext_name in self.extensions:
                            ext = self.extensions[ext_name]
                            print(f"\n扩展详情: {ext_name}")
                            print(f"  名称: {ext.name}")
                            print(f"  描述: {ext.description}")
                            print(f"  版本: {ext.version}")
                            print(f"  作者: {ext.author}")
                            tools = ext.get_tools()
                            print(f"  工具: {', '.join(tools.keys())}")
                        else:
                            print(f"\n错误: 扩展不存在: {ext_name}")
                    else:
                        print("\n[系统] 用法: /extension info <扩展名>")
                elif sub_command == 'import':
                    self._import_extension()
                    input("\n按回车继续...")
                elif sub_command == 'delete':
                    if len(parts) > 1:
                        ext_name = parts[1]
                        if ext_name in self.extensions:
                            print(f"\n确定要删除扩展 '{ext_name}' 吗？")
                            confirm = input("确认删除？(y/n): ").strip().lower()
                            if confirm == 'y':
                                ext_dir = os.path.join("iflow_extensions", ext_name)
                                if os.path.exists(ext_dir):
                                    import shutil
                                    shutil.rmtree(ext_dir)
                                    print(f"✓ 扩展 '{ext_name}' 删除成功！")
                                    print("请重启程序以生效。")
                                else:
                                    print(f"错误: 扩展目录不存在: {ext_dir}")
                        else:
                            print(f"\n错误: 扩展不存在: {ext_name}")
                    else:
                        print("\n[系统] 用法: /extension delete <扩展名>")
                else:
                    print("\n[系统] 未知子命令")
                    print("可用子命令: list, info, import, delete")
            else:
                # 显示扩展管理界面
                self.show_extension_manager()
        elif command == '/info':
            self.show_info()
        elif command == '/debug':
            if args.lower() == 'on':
                self.set_debug(True)
            elif args.lower() == 'off':
                self.set_debug(False)
            else:
                print("\n[系统] 用法: /debug on|off")
        elif command == '/api':
            if args:
                self.key_manager.set_api_key(args.strip())
                print("\n✓ API密钥已更新")
            else:
                print("\n[系统] 用法: /api <your_api_key>")
        elif command == '/model':
            if args:
                self.set_model(args.strip())
            else:
                print("\n[系统] 用法: /model <model_name>")
        elif command == '/url':
            if args:
                self.set_api_url(args.strip())
            else:
                print("\n[系统] 用法: /url <api_url>")
        elif command == '/history':
            self.history_manager()
        elif command == '/clear':
            self.clear_history()
        elif command == '/export':
            if args:
                self.export_history(args.strip())
            else:
                print("\n[系统] 用法: /export <filename>")
        elif command == '/import':
            if args:
                self.import_history(args.strip())
            else:
                print("\n[系统] 用法: /import <filename>")
        elif command == '/stop':
            self.stop_output()
        elif command == '/exit':
            print("\n[系统] 再见！")
            return 'exit'
        else:
            print(f"\n[系统] 未知指令: {command}")
            print("输入 /help 查看可用指令")
        
        return True
    
    def run(self):
        """运行主程序"""
        TerminalUI.clear_screen()
        print("=" * 50)
        print("      心流平台流式对话客户端")
        print(f"      模型: {self.model}")
        print("=" * 50)
        
        # 检查API密钥
        if not self.check_api_key():
            self.input_api_key()
        
        # 对话选择界面
        options = ["新建对话", "使用历史对话"]
        selected = TerminalUI.show_menu("请选择", options)
        
        if selected == 1:
            self.history_manager()
        
        TerminalUI.clear_screen()
        print("[提示] 输入消息开始对话，输入 /help 查看可用指令")
        if self.readline_available:
            print("[提示] 按 Tab 键自动补全指令，输入部分指令后按 ? 显示候选项")
        print("[提示] AI输出时按 Ctrl+C 可以停止输出")
        print()
        
        while True:
            try:
                user_input = input("你: ").strip()
                
                if not user_input:
                    continue
                
                # 检查是否请求显示候选项
                if user_input.endswith('?') and user_input.startswith('/'):
                    prefix = user_input[:-1].strip()
                    selected = self.show_completions(prefix)
                    if selected:
                        user_input = selected
                        print(f"你: {user_input}\n")
                    else:
                        continue
                
                # 处理指令
                result = self.handle_command(user_input)
                if result == 'exit':
                    self.close_status_window()
                    break
                elif result:
                    continue
                
                # 检查API密钥是否过期
                if not self.check_api_key():
                    self.input_api_key()
                
                # 进行对话
                self.stream_chat(user_input)
                
            except KeyboardInterrupt:
                print("\n\n[系统] 程序已中断")
                self.close_status_window()
                sys.exit(0)
            except Exception as e:
                print(f"\n[错误] {e}")


def main():
    """主函数"""
    client = IflowChatClient(model="qwen3-coder-plus")
    client.run()


if __name__ == "__main__":
    main()
