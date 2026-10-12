#!/usr/bin/env python3
"""
Hy-MT2 Local Translation Client
Usage: python3 translate.py -t "text" -l target_language [options]
"""

import sys
import json
import argparse
import requests

SUPPORTED_LANGUAGES = {
    "zh": "中文", "en": "英语", "fr": "法语", "pt": "葡萄牙语",
    "es": "西班牙语", "ja": "日语", "tr": "土耳其语", "ru": "俄语",
    "ar": "阿拉伯语", "ko": "韩语", "th": "泰语", "it": "意大利语",
    "de": "德语", "vi": "越南语", "ms": "马来语", "id": "印尼语",
    "tl": "菲律宾语", "hi": "印地语", "zh-Hant": "繁体中文",
    "pl": "波兰语", "cs": "捷克语", "nl": "荷兰语", "km": "高棉语",
    "my": "缅甸语", "fa": "波斯语", "gu": "古吉拉特语", "ur": "乌尔都语",
    "te": "泰卢固语", "mr": "马拉地语", "he": "希伯来语", "bn": "孟加拉语",
    "ta": "泰米尔语", "uk": "乌克兰语", "bo": "藏语", "kk": "哈萨克语",
    "mn": "蒙古语", "ug": "维吾尔语", "yue": "粤语",
}

def resolve_lang(lang: str) -> str:
    if lang in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang]
    rev = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
    if lang in rev:
        return lang
    raise ValueError(f"Unsupported language: {lang}")

def build_prompt(text: str, target_lang: str, mode: str = "basic", **kwargs) -> str:
    if mode == "basic":
        return f"将以下文本翻译为{target_lang}，注意只需要输出翻译后的结果，不要额外解释：\n\n{text}"
    elif mode == "terminology":
        terms = kwargs.get("terminology", "")
        return f"参考下面的翻译：\n{terms}\n将以下文本翻译为{target_lang}，注意只需要输出翻译后的结果，不要额外解释：\n\n{text}"
    elif mode == "style":
        style = kwargs.get("style", "日常口语化风格")
        return f"请将以下文本翻译为{target_lang}。注意翻译的风格要严格符合【{style}】\n\n{text}"
    elif mode == "delimiter":
        return f"请将以下文本准确翻译为{target_lang}。你必须在译文中保留等量的分隔符，绝对不可遗漏、转义或翻译该符号，并注意分隔符的位置。\n\n{text}"
    elif mode == "structured":
        fmt = kwargs.get("format_type", "JSON")
        return f"请将以下{fmt}结构化数据翻译为{target_lang}。绝对保持原有的{fmt}数据结构、缩进和层级完全不变。仅翻译面向用户展示的可见文本内容。禁止翻译代码标签、键名、变量占位符或任何代码属性。\n\n\n{text}"
    elif mode == "context":
        ctx = kwargs.get("context", "")
        return f"【背景信息】\n{ctx}\n\n请结合背景信息将以下文本翻译为{target_lang}。\n\n【待翻译文本】\n{text}"
    else:
        raise ValueError(f"Unknown mode: {mode}")

def translate(text: str, target_lang: str, url: str = "http://localhost:8081/v1/chat/completions",
              mode: str = "basic", **kwargs) -> str:
    target = resolve_lang(target_lang)
    prompt = build_prompt(text, target, mode=mode, **kwargs)
    
    payload = {
        "model": "hy-mt2",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
        "stream": False,
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=300)
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"].get("content", "")
            return content.strip()
        else:
            return f"ERROR: HTTP {resp.status_code} - {resp.text[:200]}"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    parser = argparse.ArgumentParser(description="Hy-MT2 Local Translator")
    parser.add_argument("--text", "-t", help="Text to translate")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--target-lang", "-l", required=True, help="Target language (e.g., zh, en, 中文, 英语, Persian)")
    parser.add_argument("--url", default="http://localhost:8081/v1/chat/completions", help="Server URL")
    parser.add_argument("--mode", choices=["basic", "terminology", "style", "delimiter", "structured", "context"],
                        default="basic", help="Translation mode")
    parser.add_argument("--terminology", help='Term pairs: "src1=tgt1\nsrc2=tgt2"')
    parser.add_argument("--style", help="Translation style (e.g., Formal academic, Casual)")
    parser.add_argument("--format-type", help="Structured format: JSON/HTML/Markdown/XML/YAML")
    parser.add_argument("--context", help="Background context for disambiguation")
    parser.add_argument("--preserve-delimiters", action="store_true")
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.terminology: kwargs["terminology"] = args.terminology
    if args.style: kwargs["style"] = args.style
    if args.format_type: kwargs["format_type"] = args.format_type
    if args.context: kwargs["context"] = args.context
    if args.preserve_delimiters: kwargs["preserve_delimiters"] = True
    
    text = args.text
    if not text and args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    
    if not text:
        parser.error("Provide --text or --file")
        sys.exit(1)
    
    result = translate(text, args.target_lang, args.url, args.mode, **kwargs)
    print(result)

if __name__ == "__main__":
    main()
