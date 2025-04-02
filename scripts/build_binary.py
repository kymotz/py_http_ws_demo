#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
构建二进制可执行文件的脚本，可通过 Poetry 调用。
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    print("正在清理构建目录...")
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"- 删除 {dir_name} 目录")
            shutil.rmtree(dir_name)

def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检测操作系统
    current_os = platform.system()
    print(f"检测到操作系统: {current_os}")
    
    # 使用 spec 文件还是命令行参数构建
    spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data-platform-agent.spec")
    if os.path.exists(spec_file):
        print(f"使用现有 spec 文件构建: {spec_file}")
        build_command = ["pyinstaller", "--clean", spec_file]
    else:
        print("未找到 spec 文件，使用命令行参数构建")
        
        # 设置隐藏导入模块
        hidden_imports = [
            "uvicorn.logging", 
            "uvicorn.protocols", 
            "uvicorn.lifespan", 
            "uvicorn.protocols.http", 
            "uvicorn.lifespan.on",
            "uvicorn.lifespan.off",
            "websockets"
        ]
        
        # 构建主要入口文件路径
        main_path = "agent.py"
        
        # 构建命令
        build_command = [
            "pyinstaller",
            "--clean",
            "--onefile",
            "--name", "data-platform-agent"
        ]
        
        # 添加隐藏导入
        for module in hidden_imports:
            build_command.extend(["--hidden-import", module])
        
        # 添加资源文件
        #data_separator = ";" if current_os == "Windows" else ":"
        #build_command.extend(["--add-data", f"agent{data_separator}agent"])
        
        # 添加主文件
        build_command.append(main_path)
    
    # 执行构建命令
    print(f"执行命令: {' '.join(build_command)}")
    try:
        subprocess.run(build_command, check=True)
        print("\n✅ 构建成功!")
        
        # 检查并显示输出位置
        executable_name = "data-platform-agent.exe" if current_os == "Windows" else "data-platform-agent"
        if not os.path.exists(os.path.join("dist", executable_name)):
            executable_name = "demo.exe" if current_os == "Windows" else "demo"
        
        executable_path = os.path.join("dist", executable_name)
        
        if os.path.exists(executable_path):
            print(f"可执行文件位置: {os.path.abspath(executable_path)}")
            size_bytes = os.path.getsize(executable_path)
            print(f"文件大小: {size_bytes / 1024 / 1024:.2f} MB")
        else:
            print("⚠️ 警告: 未找到预期的可执行文件")
            print(f"请检查 dist 目录")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 构建失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("======= Data Platform Agent 二进制构建工具 =======")
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建可执行文件
    build_executable()
    
    print("\n构建过程完成! 您可以在 dist 目录中找到可执行文件。")
    
if __name__ == "__main__":
    main()
