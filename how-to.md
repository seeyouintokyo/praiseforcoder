# 阿星夸夸机器人项目技术实现指南 🌟

## 核心技术背景

### 1. 通信机制选择
本项目使用标准输入输出（stdin/stdout）进行通信，而不是常见的 HTTP/SSE，原因如下：

#### 为什么选择 stdin/stdout？
- MCP（Model-Controller-Peripheral）架构的标准通信方式
- Cursor IDE 原生支持的通信协议
- 无需额外的网络端口和服务器配置
- 更轻量级，启动速度更快
- 完美契合单一职责原则

#### 常见误区
❌ 错误实现：使用 SSE（Server-Sent Events）或 WebSocket
```python
from flask import Flask, Response
app = Flask(__name__)

@app.route('/praise')
def praise():
    def generate():
        while True:
            yield f"data: {generate_praise()}\n\n"
    return Response(generate(), mimetype='text/event-stream')
```

✅ 正确实现：使用 stdin/stdout
```python
import sys
import json

while True:
    try:
        # 从标准输入读取
        input_data = sys.stdin.readline()
        request = json.loads(input_data)
        
        # 处理请求
        result = generate_praise(request['text'])
        
        # 写入标准输出
        sys.stdout.write(json.dumps({"praise": result}) + '\n')
        sys.stdout.flush()  # 重要！确保立即输出
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.stderr.flush()
```

### 2. 数据流设计
```
[输入流]
stdin -> JSON解析 -> 业务处理 -> JSON序列化 -> stdout
```

关键点：
- 每行一个完整的 JSON
- 必须及时 flush 输出缓冲
- 错误信息写入 stderr

### 3. MCP 架构特性
```
Cursor IDE <-> MCP服务管理器 <-> 夸夸服务进程
     |              |               |
   用户交互     进程管理        stdin/stdout
```

#### MCP 服务生命周期
1. 服务注册：通过 mcp.json 配置
2. 进程启动：Cursor 调用指定命令
3. 通信建立：stdin/stdout 管道连接
4. 消息处理：JSON 格式数据交换
5. 错误处理：stderr 捕获异常

### 4. 实现注意事项

#### 输入输出处理
```python
# 1. 输入处理
def read_request():
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    except json.JSONDecodeError:
        return None

# 2. 输出处理
def write_response(data):
    response = json.dumps(data) + '\n'
    sys.stdout.write(response)
    sys.stdout.flush()  # 关键！

# 3. 错误处理
def write_error(error):
    sys.stderr.write(f"Error: {str(error)}\n")
    sys.stderr.flush()
```

#### 进程管理
- 不要后台运行或创建子进程
- 避免使用全局状态
- 保持单一事件循环

### 5. 调试技巧
```bash
# 1. 命令行测试
echo '{"text":"测试文本"}' | python simple_praise_service.py

# 2. 日志调试
python simple_praise_service.py > output.log 2> error.log

# 3. 进程监控
ps aux | grep simple_praise_service.py
```

### 6. 常见问题解决

#### 输出不显示
- 检查是否调用了 sys.stdout.flush()
- 确保输出是完整的 JSON 行
- 验证 stdout 缓冲区设置

#### 进程异常退出
- 检查异常处理是否完整
- 确保 JSON 解析安全
- 验证 API 调用超时设置

#### 通信中断
- 检查 stdin 是否正确读取
- 确保输出格式符合规范
- 验证进程权限设置

### 7. 性能优化
- 使用 ujson 替代 json 提升性能
- 实现请求队列避免阻塞
- 添加响应缓存机制
- 优化错误处理流程

### 8. 测试策略
```python
# 单元测试示例
def test_praise_service():
    # 模拟标准输入
    sys.stdin = io.StringIO('{"text":"测试文本"}\n')
    
    # 捕获标准输出
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    # 运行服务
    process_request()
    
    # 验证输出
    output = captured_output.getvalue()
    assert '"praise"' in output
    assert '\n' in output
```

### 9. 部署检查清单
- [ ] Python 环境配置正确
- [ ] DeepSeek API Key 设置
- [ ] MCP 配置文件路径正确
- [ ] 文件权限设置适当
- [ ] 日志记录功能启用
- [ ] 错误处理机制完整
- [ ] 进程监控方案就绪

## 项目概述
开发一个基于 DeepSeek API 的简单夸夸服务，能够生成温暖、简短、可爱的赞美语句。

## 技术栈选择
1. 开发语言：Python 3.10+ 
   - 原因：良好的异步支持和广泛的库生态
   - 注意：避免使用 3.12，因为部分依赖可能还未完全支持

2. API选择：DeepSeek API
   - 原因：相比其他大语言模型：
     * 响应速度快
     * 支持中文效果好
     * 价格相对合理
     * API调用简单稳定
   - 注意：需要提前申请 API Key

3. 项目框架：FastMCP
   - 原因：专为 Cursor IDE 设计的轻量级服务框架
   - 优势：
     * 零配置启动
     * 自动注册到 Cursor
     * 支持标准输入输出通信

## 核心实现要点

1. 提示词工程（最关键部分）：
```python
{
    "role": "system",
    "content": "你是赞美助手。极其严格的要求：
        1. 回复必须限制在10个字以内 
        2. 必须带emoji 
        3. 禁止多句话 
        4. 禁止过度夸张 
        5. 保持温暖真诚"
}
```

2. API 参数配置：
   - temperature: 0.3（保持输出稳定）
   - max_tokens: 20（控制输出长度）
   - timeout: 30.0（避免请求卡死）

3. 环境配置：
   - 创建 .env 文件存储 API Key
   - 设置合理的请求超时
   - 配置错误处理和重试机制

## 项目结构建议
```
project/
├── README.md           # 项目文档
├── .env               # 环境变量配置
├── requirements.txt   # 依赖管理
├── main.py           # 主服务入口
└── simple_praise_service.py  # 核心服务逻辑
```

## 关键依赖
```
requests>=2.31.0  # HTTP 请求库
python-dotenv    # 环境变量管理
```

## MCP 配置模板
```json
{
  "mcpServers": {
    "praise-bot": {
      "command": "python路径",
      "args": ["服务脚本路径"],
      "env": {
        "DEEPSEEK_API_KEY": "${DEEPSEEK_KEY}"
      }
    }
  }
}
```

## 常见坑点提醒
1. DeepSeek API 响应：
   - 注意处理 API 限流
   - 添加错误重试机制
   - 设置合理的超时时间

2. 提示词设计：
   - 严格控制输出长度
   - 保持语气可爱但不过度
   - 确保每次都带 emoji

3. 环境配置：
   - Python 版本兼容性检查
   - API Key 正确配置
   - MCP 服务注册路径正确

4. 开发建议：
   - 本地测试要充分
   - 添加日志记录
   - 做好异常处理
   - 考虑并发请求处理

## 测试验证
1. 本地测试命令：
```bash
echo '{"text":"测试文本"}' | python simple_praise_service.py
```

2. 验证要点：
   - 响应时间是否在1秒内
   - 输出是否符合字数限制
   - emoji 是否正确显示
   - 错误处理是否得当

## 扩展建议
1. 可以添加自定义词库
2. 实现多样化的情感风格
3. 添加响应缓存机制
4. 支持批量请求处理

记住：核心是保持输出简短、温暖、真诚，避免过度夸张的表达。这不仅是技术实现，更是产品体验的关键。 