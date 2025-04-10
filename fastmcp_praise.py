#!/usr/bin/env python3
"""
MCP服务，提供一个'praise'工具，使用DeepSeek模型生成带emoji的幽默夸赞。
"""

import os
import json
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_KEY")
if not DEEPSEEK_API_KEY:
    print("警告: DEEPSEEK_KEY未在环境变量或.env文件中设置。")
    print("服务器会启动，但没有API密钥夸赞工具将会失败。")

# 创建MCP服务器
mcp = FastMCP("DeepSeek夸夸服务")


@mcp.tool()
async def praise(text: str, ctx: Context = None) -> str:
    """
    给用户一段话进行幽默夸赞，回复中包含emoji表情
    
    Args:
        text: 需要被夸赞的文本内容
    
    Returns:
        生成的幽默夸赞内容，包含emoji表情
    """
    if ctx:
        ctx.info(f"收到夸赞请求: {text}")
    
    if not DEEPSEEK_API_KEY:
        return "错误: DeepSeek API密钥未配置。请设置DEEPSEEK_KEY环境变量。"
    
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
                        {"role": "user", "content": f"请用20字内幽默夸赞这句话，回复中一定要包含emoji表情: {text}"}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 50
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return f"DeepSeek API错误: {response.status_code} {response.text}"
            
            data = response.json()
            
            # 从响应中提取夸赞内容
            praise_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not praise_text:
                return "你说的太棒了！👍"
                
            return praise_text
    
    except Exception as e:
        return f"连接DeepSeek API时出错: {str(e)}"


if __name__ == "__main__":
    # 运行服务器
    mcp.run() 