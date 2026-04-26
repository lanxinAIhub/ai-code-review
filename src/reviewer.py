#!/usr/bin/env python3
"""
AI Code Reviewer - 核心评审模块
使用 Claude/GPT API 自动分析代码
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# 支持的 API Provider
PROVIDERS = {
    "claude": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
    "minimax": "https://api.minimax.chat/v1/chat/completions",
}

DEFAULT_PROVIDER = "minimax"

def get_api_key(provider: str) -> str:
    """获取 API Key"""
    env_map = {
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "minimax": "MINIMAX_API_KEY",
    }
    key = os.environ.get(env_map.get(provider, "MINIMAX_API_KEY"), "")
    if not key:
        # 尝试从 shangshu 的 models.json 获取
        config_path = "/home/lanxin/.openclaw/agents/shangshu/agent/models.json"
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    for prov in config.get("providers", {}).values():
                        for model in prov.get("models", []):
                            if "minimax" in model.get("id", "").lower():
                                return prov.get("apiKey", "")
            except:
                pass
    return key

def get_file_extensions(path: str) -> list:
    """获取文件扩展名"""
    EXTENSIONS = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".c": "C",
        ".cpp": "C++",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".sh": "Shell",
        ".sql": "SQL",
    }
    _, ext = os.path.splitext(path)
    return EXTENSIONS.get(ext.lower(), "Unknown")

def read_file(path: str) -> str:
    """读取文件内容"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[读取失败: {e}]"

def build_review_prompt(file_path: str, content: str, lang: str) -> str:
    """构建评审 Prompt"""
    return f"""你是一位资深的 {lang} 工程师，负责代码评审。请分析以下代码，重点检查：

1. **Bug 和逻辑错误** - 潜在的运行时错误、空指针、边界条件
2. **安全漏洞** - SQL注入、XSS、敏感信息泄露、硬编码密码
3. **代码风格** - 命名规范、注释质量、函数长度
4. **性能问题** - 循环嵌套、重复计算、不必要的I/O
5. **可维护性** - 耦合度、重复代码、单一职责

文件：{file_path}
语言：{lang}

代码内容：
```{lang.lower()}
{content[:3000]}
```

请输出 JSON 格式的评审报告：
{{
  "file": "{file_path}",
  "language": "{lang}",
  "issues": [
    {{
      "severity": "high|medium|low",
      "category": "bug|security|style|performance|maintainability",
      "line": 行号或null,
      "description": "问题描述",
      "suggestion": "修复建议"
    }}
  ],
  "summary": "一句话总结",
  "score": 0-100
}}
"""

def review_with_claude(content: str, model: str = "claude-3-5-sonnet-20241022") -> dict:
    """使用 Claude API 评审"""
    import urllib.request
    
    key = get_api_key("claude")
    if not key:
        return {"error": "ANTHROPIC_API_KEY not set"}
    
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": content}]
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["content"][0]["text"]
            # 提取 JSON
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}

def review_with_openai(content: str, model: str = "gpt-4o") -> dict:
    """使用 OpenAI API 评审"""
    import urllib.request
    
    key = get_api_key("openai")
    if not key:
        return {"error": "OPENAI_API_KEY not set"}
    
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一位资深的代码评审专家，输出严格的JSON格式评审报告。"},
            {"role": "user", "content": content}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}

def review_with_minimax(content: str, model: str = "MiniMax-M2.7") -> dict:
    """使用 MiniMax API 评审（OpenAI兼容格式）"""
    import urllib.request
    
    key = get_api_key("minimax")
    if not key:
        return {"error": "MINIMAX_API_KEY not set"}
    
    url = "https://api.minimax.chat/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一位资深的代码评审专家，输出严格的JSON格式评审报告。"},
            {"role": "user", "content": content}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}

def review_file(file_path: str, provider: str = DEFAULT_PROVIDER) -> dict:
    """评审单个文件"""
    lang = get_file_extensions(file_path)
    content = read_file(file_path)
    
    if content.startswith("[读取失败"):
        return {"file": file_path, "error": content}
    
    prompt = build_review_prompt(file_path, content, lang)
    
    if provider == "claude":
        result = review_with_claude(prompt)
    elif provider == "openai":
        result = review_with_openai(prompt)
    else:
        result = review_with_minimax(prompt)
    
    result["file"] = file_path
    result["language"] = lang
    return result

def review_directory(dir_path: str, provider: str = DEFAULT_PROVIDER) -> dict:
    """评审整个目录"""
    results = {"files": [], "total_issues": 0, "high": 0, "medium": 0, "low": 0}
    
    for root, dirs, files in os.walk(dir_path):
        # 跳过 node_modules, __pycache__, .git 等
        dirs[:] = [d for d in dirs if d not in ["node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build"]]
        
        for file in files:
            # 跳过二进制文件
            if any(file.endswith(ext) for ext in [".pyc", ".class", ".o", ".so", ".dll", ".png", ".jpg", ".exe"]):
                continue
            
            file_path = os.path.join(root, file)
            try:
                result = review_file(file_path, provider)
                results["files"].append(result)
                
                if "issues" in result:
                    for issue in result["issues"]:
                        results["total_issues"] += 1
                        if issue.get("severity") == "high":
                            results["high"] += 1
                        elif issue.get("severity") == "medium":
                            results["medium"] += 1
                        else:
                            results["low"] += 1
            except Exception as e:
                results["files"].append({"file": file_path, "error": str(e)})
    
    return results

def generate_report(results: dict, output_path: str = "review-report.md"):
    """生成 Markdown 评审报告"""
    lines = [
        "# 🤖 AI Code Review Report",
        "",
        f"**评审时间**: {subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S']).decode().strip()}",
        f"**评审文件数**: {len(results['files'])}",
        f"**发现问题数**: {results['total_issues']} (🔴高:{results['high']} | 🟡中:{results['medium']} | 🟢低:{results['low']})",
        "",
        "---",
        "",
    ]
    
    for file_result in results["files"]:
        fname = file_result.get("file", "?")
        if "error" in file_result:
            lines.append(f"### ❌ {fname}")
            lines.append(f"```
{file_result['error']}
```")
            lines.append("")
            continue
        
        issues = file_result.get("issues", [])
        if not issues:
            lines.append(f"### ✅ {fname} （{file_result.get('language','?')}）")
            lines.append(f"> {file_result.get('summary', '无问题')}")
            lines.append("")
            continue
        
        lines.append(f"### ⚠️ {fname} （{file_result.get('language','?')}）")
        lines.append(f"> 评分: **{file_result.get('score', 'N/A')}/100** | {file_result.get('summary', '')}")
        lines.append("")
        
        for issue in issues:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get("severity", "low"), "⚪")
            cat = {"bug": "Bug", "security": "安全", "style": "风格", "performance": "性能", "maintainability": "可维护性"}.get(issue.get("category", ""), issue.get("category", ""))
            line_info = f"[L{issue.get('line', '?')}]" if issue.get("line") else ""
            lines.append(f"- {severity_icon} **{cat}** {line_info}: {issue.get('description', '')}")
            lines.append(f"  - 💡 建议: {issue.get('suggestion', '')}")
        lines.append("")
    
    report = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Code Reviewer")
    parser.add_argument("path", help="文件或目录路径")
    parser.add_argument("--provider", "-p", default=DEFAULT_PROVIDER, 
                        choices=["claude", "openai", "minimax"],
                        help="API Provider")
    parser.add_argument("--output", "-o", default="review-report.md",
                        help="输出报告路径")
    args = parser.parse_args()
    
    path = args.path
    if os.path.isdir(path):
        results = review_directory(path, args.provider)
    else:
        result = review_file(path, args.provider)
        results = {"files": [result], "total_issues": 0, "high": 0, "medium": 0, "low": 0}
        if "issues" in result:
            for issue in result.get("issues", []):
                results["total_issues"] += 1
                sev = issue.get("severity", "low")
                if sev == "high": results["high"] += 1
                elif sev == "medium": results["medium"] += 1
                else: results["low"] += 1
    
    report = generate_report(results, args.output)
    print(f"✅ 评审完成！报告已保存至: {args.output}")
    print(f"📊 发现 {results['total_issues']} 个问题 (🔴{results['high']} | 🟡{results['medium']} | 🟢{results['low']})")
