# -*- coding: utf-8 -*-
"""
扩展打包脚本
使用方法: python setup.py <扩展目录>
示例: python setup.py ../my_extension
"""

import os
import sys
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
        
        # 验证扩展目录
        if not self._validate_extension():
            raise ValueError(f"无效的扩展目录: {self.extension_dir}")
        
        # 获取扩展版本
        version = self._get_version()
        
        # 创建输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"{self.extension_name}_v{version}_{timestamp}.zip"
        )
        
        # 创建 zip 文件
        print(f"[打包] 正在打包扩展: {self.extension_name}")
        print(f"[打包] 版本: {version}")
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.extension_dir):
                # 跳过 __pycache__ 和 .pyc 文件
                dirs[:] = [d for d in dirs if d != '__pycache__']
                
                for file in files:
                    if file.endswith('.pyc') or file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.extension_dir)
                    
                    print(f"[打包] 添加文件: {arcname}")
                    zipf.write(file_path, arcname)
        
        # 显示打包信息
        file_size = os.path.getsize(output_file)
        print(f"\n[打包] 扩展已打包到: {output_file}")
        print(f"[打包] 文件大小: {file_size} 字节")
        
        return output_file
    
    def _validate_extension(self) -> bool:
        """
        验证扩展目录是否有效
        
        返回:
            bool: 是否有效
        """
        # 检查目录是否存在
        if not os.path.isdir(self.extension_dir):
            print(f"[错误] 目录不存在: {self.extension_dir}")
            return False
        
        # 检查是否包含 extension.py
        extension_file = os.path.join(self.extension_dir, 'extension.py')
        if not os.path.exists(extension_file):
            print(f"[错误] 找不到 extension.py 文件")
            return False
        
        # 检查是否定义了 Extension 变量
        try:
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            
            # 创建实例检查属性
            try:
                ext_instance = Extension()
                
                # 检查必要属性（实例属性）
                required_attrs = ['name', 'description', 'version', 'author']
                for attr in required_attrs:
                    if not hasattr(ext_instance, attr):
                        print(f"[错误] 缺少必要属性: {attr}")
                        return False
                    if not getattr(ext_instance, attr):
                        print(f"[错误] 属性 {attr} 为空")
                        return False
            except Exception as e:
                print(f"[错误] 无法创建扩展实例: {e}")
                return False
            
            # 检查必要方法
            required_methods = ['get_prompt', 'get_tools']
            for method in required_methods:
                if not hasattr(Extension, method):
                    print(f"[错误] 缺少必要方法: {method}")
                    return False
            
            return True
            
        except ImportError as e:
            print(f"[错误] 无法导入 extension.py: {e}")
            return False
        except Exception as e:
            print(f"[错误] 验证失败: {e}")
            return False
    
    def _get_version(self) -> str:
        """
        获取扩展版本
        
        返回:
            str: 版本号
        """
        try:
            import sys
            sys.path.insert(0, self.extension_dir)
            from extension import Extension
            return Extension.version
        except:
            return "1.0.0"


def print_usage():
    """打印使用说明"""
    print("=" * 60)
    print("iFlow 扩展打包工具")
    print("=" * 60)
    print()
    print("用法: python setup.py <扩展目录>")
    print()
    print("参数:")
    print("  扩展目录    要打包的扩展目录路径")
    print()
    print("示例:")
    print("  python setup.py ../my_extension")
    print("  python setup.py /path/to/my_extension")
    print()
    print("输出:")
    print("  生成一个 .zip 文件，包含扩展的所有文件")
    print("  文件名格式: <扩展名>_v<版本>_<时间戳>.zip")
    print()
    print("=" * 60)


def main():
    """主函数"""
    print()
    
    # 检查参数
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    extension_dir = sys.argv[1]
    
    # 显示帮助
    if extension_dir in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # 检查目录是否存在
    if not os.path.isdir(extension_dir):
        print(f"[错误] 目录不存在: {extension_dir}")
        print()
        print_usage()
        sys.exit(1)
    
    # 获取绝对路径
    extension_dir = os.path.abspath(extension_dir)
    
    print(f"[信息] 扩展目录: {extension_dir}")
    print()
    
    try:
        # 创建打包器
        packager = ExtensionPackager(extension_dir)
        
        # 打包扩展
        output_file = packager.pack()
        
        print()
        print("=" * 60)
        print("打包成功！")
        print("=" * 60)
        print()
        print(f"输出文件: {output_file}")
        print()
        print("使用方法:")
        print("  1. 将 .zip 文件复制到 iflow_extensions/ 目录")
        print("  2. 使用扩展管理功能导入")
        print()
        print("或手动解压:")
        print(f"  unzip {output_file} -d iflow_extensions/")
        print()
        
    except Exception as e:
        print()
        print(f"[错误] 打包失败: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()