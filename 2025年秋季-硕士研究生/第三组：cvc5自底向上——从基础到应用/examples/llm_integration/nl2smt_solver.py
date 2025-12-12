#!/usr/bin/env python3
"""
自然语言转 SMT 约束求解器
Natural Language to SMT Constraint Solver

用法:
    python nl2smt_solver.py "找三个正整数,和为10"

    或交互模式:
    python nl2smt_solver.py
"""

import sys
import re
import os
from typing import Optional
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    load_dotenv(env_path)
except ImportError:
    # 如果没有安装 python-dotenv,直接使用环境变量
    pass


def call_llm(query: str, api_key: Optional[str] = None) -> str:
    """
    调用 LLM API 生成代码

    支持多种 LLM:
    1. OpenAI 兼容 API (从环境变量或.env文件读取配置)
    2. 本地 Ollama (免费,需要先安装 ollama)

    环境变量:
        OPENAI_API_KEY: API密钥
        OPENAI_BASE_URL: API地址 (可选,默认OpenAI官方)
        OPENAI_MODEL: 模型名称 (可选,默认gpt-4o-mini)

    Args:
        query: 用户的自然语言查询
        api_key: API Key (可选,优先级最高)

    Returns:
        生成的 Python 代码
    """

    # 方案1: 使用 OpenAI 兼容 API
    api_key_to_use = api_key or os.getenv('OPENAI_API_KEY')

    if api_key_to_use:
        try:
            from openai import OpenAI

            # 使用环境变量配置
            client = OpenAI(
                api_key=api_key_to_use,
                base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            )

            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(query=query)}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"API 调用失败: {e}")
            print("尝试使用本地 Ollama...")

    # 方案2: 使用本地 Ollama (免费)
    try:
        import requests

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5-coder:7b',  # 或 'codellama', 'deepseek-coder'
                'prompt': f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(query=query)}",
                'stream': False
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Ollama 返回错误: {response.status_code}")

    except Exception as e:
        print(f"本地 Ollama 调用失败: {e}")
        print("\n提示:")
        print("1. 安装依赖: pip install openai python-dotenv")
        print("2. 配置API: 复制 .env.example 为 .env 并填入你的API配置")
        print("或")
        print("1. 安装 Ollama: https://ollama.ai/")
        print("2. 运行模型: ollama run qwen2.5-coder:7b")
        return None


def extract_code(llm_response: str) -> Optional[str]:
    """
    从 LLM 响应中提取代码

    Args:
        llm_response: LLM 的完整响应

    Returns:
        提取出的 Python 代码
    """
    # 尝试匹配 ```python ... ``` 格式
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, llm_response, re.DOTALL)

    if match:
        return match.group(1).strip()

    # 尝试匹配 ``` ... ``` 格式
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, llm_response, re.DOTALL)

    if match:
        return match.group(1).strip()

    # 如果没有代码块标记,返回全部内容
    return llm_response.strip()


def execute_code(code: str) -> None:
    """
    执行生成的代码

    Args:
        code: 要执行的 Python 代码
    """
    try:
        # 移除 if __name__ == "__main__" 块,直接执行
        # 这样可以确保代码在 exec 环境中正常运行
        lines = code.split('\n')
        filtered_lines = []
        skip_next = False

        for i, line in enumerate(lines):
            # 跳过 if __name__ == "__main__": 及其缩进块
            if 'if __name__' in line and '__main__' in line:
                # 找到这一行之后的缩进内容并提取出来
                indent_level = len(line) - len(line.lstrip())
                # 收集该块下的内容
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    if next_line.strip():  # 非空行
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent > indent_level:
                            # 属于这个块,去掉缩进后添加
                            filtered_lines.append(next_line[indent_level + 4:])
                        else:
                            break
                break
            else:
                filtered_lines.append(line)

        cleaned_code = '\n'.join(filtered_lines)

        # 在独立的命名空间中执行
        namespace = {}
        exec(cleaned_code, namespace)
    except Exception as e:
        print(f"\n代码执行出错: {e}")
        print("\n生成的代码可能有问题,请检查:")
        print("-" * 60)
        print(code)
        print("-" * 60)


def solve_query(query: str, api_key: Optional[str] = None, verbose: bool = True) -> None:
    """
    完整的求解流程

    Args:
        query: 用户的自然语言查询
        api_key: OpenAI API Key (可选)
        verbose: 是否打印详细信息
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print(f"{'='*60}\n")
        print("正在生成代码...\n")

    # 1. 调用 LLM 生成代码
    llm_response = call_llm(query, api_key)

    if not llm_response:
        print("无法生成代码")
        return

    # 2. 提取代码
    code = extract_code(llm_response)

    if verbose:
        print("生成的代码:")
        print("-" * 60)
        print(code)
        print("-" * 60)
        print("\n执行结果:")
        print("-" * 60)

    # 3. 执行代码
    execute_code(code)

    if verbose:
        print("-" * 60)


def interactive_mode(api_key: Optional[str] = None):
    """
    交互式模式
    """
    print("\n" + "="*60)
    print("欢迎使用 自然语言约束求解器 (NL2SMT)")
    print("="*60)
    print("\n提示:")
    print("- 输入问题后按回车")
    print("- 输入 'exit' 或 'quit' 退出")
    print("- 输入 'examples' 查看示例问题")
    print("\n" + "="*60 + "\n")

    while True:
        try:
            query = input("请输入问题: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                print("\n再见!")
                break

            if query.lower() == 'examples':
                print("\n示例问题:")
                print("1. 找三个正整数,和为10,第一个数是偶数")
                print("2. 解方程 x^2 - 5*x + 6 = 0")
                print("3. 有三个人A、B、C,A比B年龄大,C比A小,B是25岁,问C可能多少岁")
                print("4. 数独:填一个3x3的格子,每行每列每个数字都不重复")
                print()
                continue

            solve_query(query, api_key)
            print()

        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")


def main():
    """主函数"""
    # 检查是否有 API Key
    api_key = os.getenv('OPENAI_API_KEY')

    if len(sys.argv) > 1:
        # 命令行模式
        query = ' '.join(sys.argv[1:])
        solve_query(query, api_key)
    else:
        # 交互模式
        interactive_mode(api_key)


if __name__ == "__main__":
    main()
