#!/usr/bin/env python3
"""
MCP server that provides a 'praise' tool to generate praise using DeepSeek API.
"""

import os
import json
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# 加载环境变量
load_dotenv()

# 获取API密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("警告: DEEPSEEK_API_KEY 未在环境变量或.env文件中设置")
    print("服务将启动，但没有API密钥时praise功能将无法使用")

# 创建MCP服务器
server = FastMCP("Praise Bot")

@server.tool()
async def praise(text: str, ctx: Context = None) -> str:
    """
    使用DeepSeek API生成赞美语句
    
    Args:
        text: 需要被赞美的内容
    
    Returns:
        生成的赞美语句
    """
    if ctx:
        ctx.info(f"正在生成赞美: {text}")
    
    if not DEEPSEEK_API_KEY:
        return "错误: DeepSeek API密钥未配置。请设置DEEPSEEK_API_KEY环境变量。"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "你是赞美助手。极其严格的要求：1. 回复必须限制在1句(包含emoji) 2. 必须带emoji 3. 语气可爱温暖 4. 禁止多句话 5. 禁止过度夸张"
                        },
                        {"role": "user", "content": f"请赞美：{text}"}
                    ],
                    "stream": False,
                    "max_tokens": 50,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                return f"DeepSeek API错误: {response.status_code} {response.text}"
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"连接DeepSeek API时出错: {str(e)}"

if __name__ == "__main__":
    # 运行服务器
    server.run() 