from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import os
import tempfile
import subprocess
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="IDE Module Backend")

# 启用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应更改为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeSubmission(BaseModel):
    html: str
    css: Optional[str] = ""
    js: Optional[str] = ""

class AIMessage(BaseModel):
    message: str
    code: Optional[str] = None

@app.get("/")
async def read_root():
    return {"status": "active", "message": "IDE Module Backend is running"}

@app.post("/execute")
async def execute_code(code: CodeSubmission):
    """
    在沙箱环境中执行代码并返回结果
    """
    try:
        # 此处为临时实现，后续需集成到Docker沙箱
        # 创建临时HTML文件
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                {code.css}
                </style>
            </head>
            <body>
                {code.html}
                <script>
                {code.js}
                </script>
            </body>
            </html>
            """
            f.write(html_content.encode())
            temp_file = f.name
        
        # 这里只是返回文件路径，真实实现应该在Docker中运行并返回结果
        return {
            "status": "success",
            "file": os.path.basename(temp_file),
            "message": "代码已处理，此为临时实现"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/chat")
async def ai_chat(message: AIMessage):
    """
    与AI助手聊天的接口 (占位，需要后续集成实际的AI API)
    """
    try:
        # 此处为占位实现，后续需集成到实际的AI API
        return {
            "status": "success",
            "reply": "这是一个AI助手回复的占位文本。请在后续开发中集成实际的AI API。",
            "suggestions": ["尝试修复HTML结构", "检查CSS语法", "添加事件监听器"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/static-check")
async def static_check(code: CodeSubmission):
    """
    对代码进行静态检查 (占位，需要后续实现)
    """
    # 此处为占位实现，后续需集成实际的静态检查工具
    return {
        "status": "success",
        "errors": [],
        "warnings": [
            {"line": 5, "column": 10, "message": "示例警告：未闭合的标签", "severity": "warning"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)