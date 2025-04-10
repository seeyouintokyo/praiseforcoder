import subprocess
import json
import sys
import os
import uuid

def test_mcp_tools_list():
    """测试MCP工具列表功能"""
    # 准备输入数据
    input_data = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "__listTools"
    }
    
    print(f"请求工具列表: {json.dumps(input_data, ensure_ascii=False)}")
    
    # 启动子进程
    proc = subprocess.Popen(
        ["python", "mcp_praise.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送输入并获取输出
    stdout, stderr = proc.communicate(json.dumps(input_data))
    
    # 输出调试信息
    if stderr:
        print(f"错误输出: {stderr}")
    
    # 解析输出
    try:
        result = json.loads(stdout.strip())
        print(f"工具列表: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始输出: {stdout}")
        return {"error": {"message": "解析响应失败"}}

def test_mcp_praise(text, api_key=None):
    """测试MCP夸夸服务"""
    # 准备输入数据
    input_data = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "praise",
        "params": {"text": text}
    }
    if api_key:
        input_data["params"]["api_key"] = api_key
    
    print(f"测试输入: {json.dumps(input_data, ensure_ascii=False)}")
    
    # 设置环境变量
    env = os.environ.copy()
    if api_key:
        env["DEEPSEEK_KEY"] = api_key
    
    # 启动子进程
    proc = subprocess.Popen(
        ["python", "mcp_praise.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # 发送输入并获取输出
    stdout, stderr = proc.communicate(json.dumps(input_data))
    
    # 输出调试信息
    if stderr:
        print(f"错误输出: {stderr}")
    
    # 解析输出
    try:
        result = json.loads(stdout.strip())
        return result
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始输出: {stdout}")
        return {"error": {"message": "解析响应失败"}}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        # 测试工具列表
        test_mcp_tools_list()
    else:
        # 获取命令行参数
        text = "今天代码一次通过" if len(sys.argv) < 2 else sys.argv[1]
        api_key = "sk-27071d43402b4dfe9a26f79788671c13" if len(sys.argv) < 3 else sys.argv[2]
        
        # 运行测试
        result = test_mcp_praise(text, api_key)
        
        # 输出结果
        print(f"测试文本: {text}")
        if "result" in result:
            print(f"赞美结果: {result['result'].get('praise')}")
        if "error" in result:
            print(f"错误信息: {result['error'].get('message')}") 