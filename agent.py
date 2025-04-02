# 程序启动文件
import os
import sys
import subprocess
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, Response, StreamingResponse, HTMLResponse
import uvicorn
import io
from util.mytest import plus

# 获取应用所在目录（针对PyInstaller打包后的情况）
def get_application_path():
    # 检查是否在PyInstaller环境中
    if getattr(sys, 'frozen', False):
        # 如果是打包后的程序，则app_path为可执行文件所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，则app_path为脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

# 创建FastAPI应用实例
app = FastAPI(title="Python Demo Service")

# WebSocket 连接处理
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.lower() == "hi":
                await websocket.send_text("hello")
            else:
                await websocket.send_text(f"收到消息: {data}")
    except WebSocketDisconnect:
        print("客户端断开连接")
    except Exception as e:
        print(f"WebSocket错误: {str(e)}")

# 1. /hello 向接口返回 hello world 字符串
@app.get("/hello", response_class=PlainTextResponse)
async def hello_world():
    return "hello world"

# 3. /cat?path=xxx 获取指定路径下的文件内容
@app.get("/cat")
async def cat_file(path: str):
    if not path:
        raise HTTPException(status_code=400, detail="缺少path参数")
    
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 尝试以不同的编码读取文件，优先使用utf-8
        encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
        content = None
        encoding_used = None
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as file:
                    content = file.read()
                encoding_used = encoding
                break  # 如果成功读取，跳出循环
            except UnicodeDecodeError:
                continue  # 尝试下一个编码
        
        if content is None:
            # 如果所有文本编码都失败，以二进制模式读取
            def file_iterator():
                with open(path, 'rb') as f:
                    yield from f
            
            # 尝试猜测文件类型
            file_extension = os.path.splitext(path)[1].lower()
            content_type = {
                '.html': 'text/html',
                '.txt': 'text/plain',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.xml': 'application/xml',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.pdf': 'application/pdf',
            }.get(file_extension, 'application/octet-stream')
            
            return StreamingResponse(file_iterator(), media_type=content_type)
        else:
            return PlainTextResponse(content, media_type=f"text/plain; charset={encoding_used}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"读取文件出错: {str(e)}")

# 4. /run?cmd=xxx 执行指定的命令
@app.get("/run", response_class=PlainTextResponse)
async def run_command(cmd: str):
    if not cmd:
        raise HTTPException(status_code=400, detail="缺少cmd参数")
    
    try:
        # 指定环境变量使命令输出使用UTF-8编码
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            env=env
        )
        return f"命令输出:\n{result.stdout}\n错误输出:\n{result.stderr}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行命令失败: {str(e)}")

# 添加版本信息接口
@app.get("/version", response_class=PlainTextResponse)
async def version():
    return "Python Demo API v1.0.0"

# 增加一个HTML页面用于测试WebSocket
@app.get("/", response_class=HTMLResponse)
async def websocket_test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket测试</title>
            <meta charset="utf-8" />
        </head>
        <body>
            <h1>WebSocket测试页面</h1>
            <div>
                <input type="text" id="messageText" placeholder="输入消息">
                <button onclick="sendMessage()">发送</button>
            </div>
            <div>
                <h2>接收到的消息:</h2>
                <ul id="messages">
                </ul>
            </div>
            <script>
                let ws = null;
                
                function connectWebSocket() {
                    ws = new WebSocket("ws://" + window.location.host + "/ws");
                    
                    ws.onopen = function(event) {
                        console.log("连接已建立");
                        addMessage("系统: WebSocket连接已建立");
                    };
                    
                    ws.onmessage = function(event) {
                        addMessage("收到: " + event.data);
                    };
                    
                    ws.onclose = function(event) {
                        console.log("连接已关闭");
                        addMessage("系统: WebSocket连接已关闭");
                        // 尝试重连
                        setTimeout(connectWebSocket, 2000);
                    };
                    
                    ws.onerror = function(event) {
                        console.error("WebSocket错误:", event);
                        addMessage("系统: WebSocket连接错误");
                    };
                }
                
                function addMessage(text) {
                    let messages = document.getElementById('messages');
                    let message = document.createElement('li');
                    let content = document.createTextNode(text);
                    message.appendChild(content);
                    messages.appendChild(message);
                }
                
                function sendMessage() {
                    let input = document.getElementById("messageText");
                    if (!input.value) return;
                    
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(input.value);
                        addMessage("发送: " + input.value);
                        input.value = '';
                    } else {
                        addMessage("系统: WebSocket未连接，无法发送消息");
                    }
                }
                
                // 页面加载后连接WebSocket
                window.onload = function() {
                    connectWebSocket();
                    
                    // 回车键发送消息
                    document.getElementById("messageText").addEventListener("keyup", function(event) {
                        if (event.key === "Enter") {
                            sendMessage();
                        }
                    });
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 主函数
def main():
    # 设置工作目录为应用目录（PyInstaller打包后很重要）
    os.chdir(get_application_path())

    print("正在启动服务，请确保已安装WebSocket依赖...")
    
    # 启动FastAPI应用，使用标准Uvicorn配置
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )

# 如果直接运行此模块，则调用main函数
if __name__ == '__main__':
    print("plus:" + str(plus(1, 2)))
    main()