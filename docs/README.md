# EZ Runner

> **Run any LLM, anywhere, offline.**
> 一条命令，将任意大语言模型打包为离线可运行的 Docker 镜像。

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 核心理念

**问题：** 如何在离线环境运行最新的 LLM？

**答案：** EZ Runner - 在线机器打包，离线机器运行

```bash
# 在线机器
ezrunner pack qwen/Qwen-3-4B-Guard -o model.tar

# 传输到离线机器
scp model.tar offline-server:/data/

# 离线机器运行
ezrunner run model.tar
# ✅ API: http://localhost:8080
```

---

## ✨ 核心特性

### 🚀 支持任意模型

```bash
# 支持 HuggingFace 所有模型
ezrunner pack meta-llama/Llama-3.2-1B-Instruct

# 支持 ModelScope 所有模型
ezrunner pack qwen/Qwen2.5-7B-Instruct

# 刚发布的新模型？立即可用
ezrunner pack deepseek/DeepSeek-R1  # 发布 1 分钟后即可打包
```

### 📦 自包含镜像

```
Docker 镜像包含:
├── PyTorch + CUDA        (推理引擎)
├── 模型权重              (safetensors)
├── OpenAI 兼容 API       (即插即用)
└── 所有依赖              (零配置)
```

### 🎛️ 硬件自适应

```bash
# 自动检测目标硬件
ezrunner pack qwen/Qwen-7B --target-gpu 8   # 8GB 显存

# 输出：
# ✅ 检测到显存充足，使用 vLLM (高性能)
# ✅ 镜像大小: 15.2 GB
```

### 🔌 OpenAI 兼容 API

```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy",
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="qwen",
    messages=[{"role": "user", "content": "你好"}]
)
```

---

## 🚀 快速开始

### 安装

```bash
pip install ezrunner
```

### 5 分钟上手

#### **步骤 1: 在线机器打包**

```bash
# 打包模型
ezrunner pack qwen/Qwen-3-4B-Guard -o qwen3.tar

# 输出:
# [1/4] 发现模型: qwen/Qwen-3-4B-Guard
#   → 格式: safetensors, 大小: 4.2 GB
# [2/4] 选择引擎: PyTorch (Transformers)
# [3/4] 构建 Docker 镜像
#   → 下载模型...
#   → 安装依赖...
# [4/4] 导出镜像: qwen3.tar (12.5 GB)
# ✅ 完成！
```

#### **步骤 2: 传输到离线机器**

```bash
# U盘、内网传输、等
scp qwen3.tar offline-server:/data/
```

#### **步骤 3: 离线机器运行**

```bash
# 加载并运行
ezrunner run qwen3.tar

# 或手动
docker load < qwen3.tar
docker run -d --gpus all -p 8080:8080 ezrunner-qwen-3-4b-guard
```

#### **步骤 4: 测试**

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

---

## 📖 使用指南

### 基本用法

```bash
# 打包模型
ezrunner pack <model_id> [OPTIONS]

# 选项:
  -o, --output PATH          输出文件路径 (默认: model.tar)
  --engine [auto|transformers|vllm]
                             推理引擎 (默认: auto)
  --target-gpu INT           目标机器显存 (GB)
  --port INT                 API 端口 (默认: 8080)
  --quantization [4bit|8bit] 量化级别 (可选)
```

### 高级用法

#### **1. 指定推理引擎**

```bash
# 自动选择 (推荐)
ezrunner pack qwen/Qwen-7B --engine auto

# 强制使用 Transformers (兼容性最好)
ezrunner pack qwen/Qwen-7B --engine transformers

# 强制使用 vLLM (高性能，需要充足显存)
ezrunner pack qwen/Qwen-7B --engine vllm
```

#### **2. 量化支持**

```bash
# 4-bit 量化 (节省显存 75%)
ezrunner pack qwen/Qwen-7B --quantization 4bit

# 8-bit 量化 (节省显存 50%)
ezrunner pack qwen/Qwen-7B --quantization 8bit
```

#### **3. 多 GPU 支持**

```bash
# 指定目标有 2 张 GPU
ezrunner pack qwen/Qwen-72B \
  --target-gpu 40 \
  --target-gpu-count 2
```

#### **4. 自定义端口**

```bash
ezrunner pack qwen/Qwen-7B --port 8888
```

---

## 🏗️ 架构设计

详见 [ARCHITECTURE.md](ARCHITECTURE.md)

### 核心流程

```
┌─────────────────────────────────────────────┐
│  在线机器: ezrunner pack                     │
├─────────────────────────────────────────────┤
│  1. 模型发现 (ModelScope/HuggingFace API)   │
│  2. 硬件分析 (选择最优引擎)                  │
│  3. 生成 Dockerfile                          │
│  4. docker build (下载模型到镜像内)          │
│  5. docker save > model.tar                  │
└──────────────┬──────────────────────────────┘
               │
               ↓ (U盘/内网传输)
               │
┌──────────────┴──────────────────────────────┐
│  离线机器: ezrunner run                      │
├─────────────────────────────────────────────┤
│  1. docker load < model.tar                  │
│  2. docker run --gpus all -p 8080:8080       │
│  3. 访问 http://localhost:8080               │
└─────────────────────────────────────────────┘
```

---

## 📚 文档

- [架构设计](ARCHITECTURE.md)
- [API 文档](API.md)
- [贡献指南](CONTRIBUTING.md)

---

## 📊 与其他方案对比

| 方案 | 模型覆盖 | 离线支持 | 易用性 | 性能 |
|------|---------|---------|--------|------|
| **EZ Runner** | ✅ 所有模型 | ✅ 完全离线 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ollama** | ⚠️ 需要 GGUF | ✅ 离线 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **OpenLLM** | ⚠️ 预定义列表 | ⚠️ 运行时下载 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Xinference** | ⚠️ 预定义列表 | ⚠️ 运行时下载 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **vLLM** | ✅ 所有模型 | ❌ 需要在线 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🙏 致谢

- **PyTorch** - 强大的深度学习框架
- **HuggingFace Transformers** - 统一的模型接口
- **vLLM** - 高性能推理引擎
- **ModelScope** - 国内模型生态支持

---

**EZ Runner - Run any LLM, anywhere, offline. 🚀**
