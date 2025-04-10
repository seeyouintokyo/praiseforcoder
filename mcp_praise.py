#!/usr/bin/env python3
import os
import json
import requests
from mcp.server.fastmcp import FastMCP, Context

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('praise.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PraiseBot')

# 创建MCP服务器
mcp = FastMCP("PraiseBot")

@mcp.tool()
async def praise(text: str, ctx: Context = None) -> str:
    """给用户一段话进行幽默夸赞，回复中包含emoji表情"""
    if ctx:
        ctx.info(f"收到夸赞请求: {text}")
    
    try:
        api_key = os.getenv("DEEPSEEK_KEY", "sk-27071d43402b4dfe9a26f79788671c13")
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个善于夸夸的程序员鼓励师，请用幽默风趣的语气夸赞用户，回复中一定要包含emoji表情。"},
                    {"role": "user", "content": f"请用20字内夸赞这句话: {text}"}
                ],
                "max_tokens": 50
            },
            timeout=10
        )
        
        if response.status_code != 200:
            if ctx:
                ctx.error(f"API错误: {response.status_code} {response.text}")
            return f"API调用失败: HTTP {response.status_code}"
        
        result = response.json()["choices"][0]["message"]["content"]
        if ctx:
            ctx.info(f"生成的夸赞: {result}")
        return result
        
    except Exception as e:
        if ctx:
            ctx.error(f"发生错误: {str(e)}")
        return "真棒！👍"

if __name__ == "__main__":
    logger.info("正在启动 PraiseBot...")
    mcp.run()
