# Hy-MT2 Local Translator

Offline machine translation using **Tencent Hy-MT2** model with **llama.cpp** - fully local, no API keys needed.

## Features

- 🔒 **100% Offline** - No internet required after model download
- 🚀 **Fast** - Optimized with llama.cpp (Metal/Accelerate support)
- 🌍 **38 Languages** - Chinese, English, French, Spanish, Japanese, Korean, Arabic, Persian, etc.
- 🎯 **6 Translation Modes** - Basic, Terminology, Style, Delimiter, Structured (JSON/HTML/XML), Context-aware
- 💻 **macOS 12+ Intel (x64) Compatible** - Built specifically for older macOS

## Quick Start

### 1. Download Model

```bash
# Lightweight 1.25-bit quantized (440 MB) - Recommended
curl -L "https://huggingface.co/tencent/Hy-MT2-1.8B-1.25Bit-GGUF/resolve/main/Hy-MT2-1.8B-1.25Bit.gguf" -o ~/Hy-MT2-1.8B-1.25Bit.gguf

# Or Q4_K_M (1.1 GB) - Better quality, more compatible
curl -L "https://huggingface.co/tencent/Hy-MT2-1.8B-GGUF/resolve/main/Hy-MT2-1.8B-Q4_K_M.gguf" -o ~/Hy-MT2-1.8B-Q4_K_M.gguf
```

### 2. Build llama.cpp (macOS 12 Intel)

```bash
# One-command build
./build.sh ~/Hy-MT2-1.8B-Q4_K_M.gguf
```

### 3. Start Translation Server

```bash
./run_server.sh ~/Hy-MT2-1.8B-Q4_K_M.gguf
# Server runs on http://localhost:8081
```

### 4. Translate

```bash
# Using Python client
python3 translate.py -t "Hello world" -l Persian

# Or direct API
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hy-mt2","messages":[{"role":"user","content":"Translate to Persian: Hello world"}],"temperature":0.1}'
```

## Translation Modes

| Mode | Description | Example |
|------|-------------|---------|
| **Basic** | Standard translation | `-t "Hello" -l Persian` |
| **Terminology** | Custom term mapping | `--terminology "AI=هوش مصنوعی\nML=یادگیری ماشین"` |
| **Style** | Control tone/style | `--style "Formal academic"` |
| **Delimiter** | Preserve separators | `--preserve-delimiters` with `Hello@@World` |
| **Structured** | JSON/HTML/XML/MD/YAML | `--format-type JSON` |
| **Context** | Background context | `--context "Medical report"` |

## Supported Languages

Chinese (简体/繁体), English, French, Spanish, Portuguese, Japanese, Korean, Russian, Arabic, Turkish, Thai, Vietnamese, Indonesian, Malay, Filipino, Hindi, Persian, German, Italian, Dutch, Polish, Czech, Ukrainian, Hebrew, Bengali, Tamil, Kazakh, Mongolian, Uyghur, Cantonese, Khmer, Burmese, Gujarati, Urdu, Telugu, Marathi

## Requirements

- macOS 12+ (Intel x64)
- Xcode Command Line Tools: `xcode-select --install`
- ~2 GB disk space for build
- Model file (440 MB - 1.1 GB)

## Project Structure

```
hy-mt2-local-translator/
├── build.sh              # Build llama.cpp with macOS 12 compat
├── run_server.sh         # Start translation server
├── translate.py          # Python CLI client
├── hy_translate.py       # Advanced translation script (SkillHub)
├── .github/workflows/    # CI/CD for macOS 12 x64/arm64
└── README.md
```

## License

- Model: Apache 2.0 (Tencent/Hy-MT2)
- Code: MIT
- llama.cpp: MIT

## References

- [Tencent Hy-MT2](https://github.com/Tencent-Hunyuan/Hy-MT2)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [SkillHub Hy-MT2 Translator](https://skillhub.cn/skills/tencent-adm/hy-mt2-translator)
