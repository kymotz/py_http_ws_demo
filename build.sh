#!/bin/bash

echo "===== 开始构建Ubuntu Linux可执行文件 ====="

# 检查并安装依赖
echo "正在检查并安装依赖..."
pip install fastapi uvicorn websockets pyinstaller --no-cache-dir

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build/ dist/

# 使用PyInstaller进行打包
echo "开始打包..."
pyinstaller demo.spec --clean

echo "===== 构建完成 ====="
echo "可执行文件位于: dist/demo"
echo "可使用以下命令运行: ./dist/demo"
