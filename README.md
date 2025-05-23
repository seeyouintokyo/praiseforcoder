# 程序员鼓励师 🩷🌟阿星

一个基于 DeepSeek API 的简单 MCP 服务，用于生成简短可爱的赞美语句。

## 环境要求

- Python 3.10+
- DeepSeek API Key

## 配置

1. 确保 `.env` 文件中包含你的 DeepSeek API Key：
```
DEEPSEEK_API_KEY=your_api_key_here
```

## 启动服务

有两种方式可以启动服务：

1. 直接使用 Python 启动：
```bash
python main.py
```

2. 使用 MCP CLI 启动：
```bash
uv run mcp run main.py:server
```

## 注意事项

- 服务启动后会自动注册到 Cursor
- 无需额外配置，服务会自动在后台运行
- 如果需要重启服务，先用 `pkill -f "python main.py"` 停止旧服务，再重新启动

## 实现说明

服务使用 FastMCP 实现，主要特点：
- 使用 DeepSeek Chat 模型
- 限制回复为单句、15字以内
- 每句话都带 emoji
- 保持简短有趣的风格

## 功能特点

- 通过stdin接收JSON输入，调用DeepSeek-v3 API生成赞美回复
- 通过stdout返回JSON格式的夸夸内容
- 自动处理API错误并返回友好提示

## 安装依赖

```bash
pip install requests
```

## 输入输出格式

**输入（通过stdin）**:
```json
{
  "text": "用户输入内容",
  "api_key": "sk_yourDeepSeekKey" // 可选，也可通过环境变量传递
}
```

**输出（到stdout）**:
```json
{
  "praise": "生成的赞美文本",
  "error": "错误信息（如有）"
}
```

## 使用方法

### 命令行测试

```bash
# 测试运行
echo '{"text":"我学会用MCP开发了！"}' | python mcp_praise.py

# 带API密钥测试
echo '{"text":"今天代码一次通过","api_key":"sk_xxx"}' | python mcp_praise.py
```

### 环境变量配置

可以通过环境变量`DEEPSEEK_KEY`设置API密钥：

```bash
export DEEPSEEK_KEY="sk_yourKeyHere"
```

### Cursor配置

在Cursor中配置：

```json
{
  "praise-bot": {
    "command": "python",
    "args": ["/path/to/mcp_praise.py"],
    "env": {
      "DEEPSEEK_KEY": "sk_yourKeyHere"
    }
  }
}
```

## 注意事项

- API密钥优先使用输入参数，其次使用环境变量
- 超时设置为10秒，避免长时间阻塞
- 确保响应立即输出，使用`sys.stdout.flush()`进行刷新 