# EZ Runner 开发指南

> **规范先行** - 本文档定义项目结构、开发环境、工作流程

---

## 项目结构

```
ezrunner/
├── src/
│   └── ezrunner/
│       ├── __init__.py
│       ├── cli.py              # CLI 入口
│       ├── core/               # 核心模块
│       │   ├── __init__.py
│       │   ├── discovery.py    # ModelDiscovery
│       │   ├── hardware.py     # HardwareAnalyzer
│       │   ├── engine.py       # EngineSelector
│       │   ├── dockerfile.py   # DockerfileGenerator
│       │   ├── builder.py      # ImageBuilder
│       │   └── exporter.py     # TarExporter
│       ├── models/             # 数据模型
│       │   ├── __init__.py
│       │   ├── model_info.py
│       │   ├── hardware.py
│       │   └── engine.py
│       ├── api/                # API 客户端
│       │   ├── __init__.py
│       │   ├── modelscope.py
│       │   └── huggingface.py
│       ├── templates/          # Dockerfile 模板
│       │   ├── transformers.dockerfile
│       │   └── vllm.dockerfile
│       └── utils/              # 工具函数
│           ├── __init__.py
│           ├── docker.py
│           └── logger.py
├── tests/
│   ├── unit/                   # 单元测试
│   │   ├── test_discovery.py
│   │   ├── test_hardware.py
│   │   └── ...
│   ├── integration/            # 集成测试
│   │   └── test_full_pipeline.py
│   └── fixtures/               # 测试数据
│       └── mock_models/
├── docs/                       # 文档
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md          # 本文档
│   ├── CODE_STYLE.md
│   ├── TESTING.md
│   └── CONTRIBUTING.md
├── pyproject.toml              # 项目配置
├── setup.py                    # 安装脚本
├── requirements.txt            # 依赖
├── requirements-dev.txt        # 开发依赖
└── README.md
```

---

## 技术栈

### 核心依赖

- **Python**: 3.11+ (使用 dataclass, pattern matching 等新特性)
- **Docker**: 20.10+ (用于构建和导出镜像)
- **Click**: CLI 框架
- **Requests**: HTTP 客户端 (调用 ModelScope/HuggingFace API)
- **Docker SDK**: Python Docker 客户端
- **Jinja2**: Dockerfile 模板引擎

### 开发依赖

- **pytest**: 测试框架
- **black**: 代码格式化
- **ruff**: Linter (替代 flake8 + isort)
- **mypy**: 类型检查
- **pytest-cov**: 测试覆盖率

---

## 开发环境搭建

### 1. 前置要求

```bash
# 检查版本
python --version  # 需要 >= 3.11
docker --version  # 需要 >= 20.10
```

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/ezrunner.git
cd ezrunner
```

### 3. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 或使用 uv (推荐，速度快)
pip install uv
uv venv
source .venv/bin/activate
```

### 4. 安装依赖

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 或使用 uv
uv pip install -e ".[dev]"
```

### 5. 验证安装

```bash
# 运行 CLI
ezrunner --help

# 运行测试
pytest

# 检查代码格式
black --check src/ tests/
ruff check src/ tests/
mypy src/
```

---

## 开发工作流

### 日常开发

```bash
# 1. 创建功能分支
git checkout -b feature/model-discovery

# 2. 编写代码
vim src/ezrunner/core/discovery.py

# 3. 编写测试
vim tests/unit/test_discovery.py

# 4. 运行测试
pytest tests/unit/test_discovery.py -v

# 5. 检查代码质量
black src/ tests/
ruff check --fix src/ tests/
mypy src/

# 6. 提交
git add .
git commit -m "feat: implement ModelDiscovery"
```

### 本地测试完整流程

```bash
# 测试打包命令
ezrunner pack qwen/Qwen-1.5B-Chat -o test.tar

# 验证生成的镜像
docker load < test.tar
docker images | grep ezrunner

# 测试运行
docker run --rm -p 8080:8080 ezrunner-qwen-1.5b-chat

# 测试 API
curl http://localhost:8080/v1/models
```

---

## 调试技巧

### 1. 使用 IPython 调试

```python
# 在代码中插入断点
import IPython; IPython.embed()
```

### 2. 查看 Docker 构建日志

```bash
# 启用 BuildKit 详细日志
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

ezrunner pack qwen/Qwen-1.5B-Chat
```

### 3. 测试 Dockerfile 生成

```python
# 单独测试生成逻辑
from ezrunner.core.dockerfile import DockerfileGenerator
from ezrunner.models.engine import Engine

gen = DockerfileGenerator()
dockerfile = gen.generate(model_info, Engine.TRANSFORMERS)
print(dockerfile)
```

---

## 常见问题

### Q1: Docker 权限错误

```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### Q2: 模型下载失败

```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com

# 设置 ModelScope 镜像
export MODELSCOPE_DOWNLOAD_ENDPOINT=https://modelscope.cn
```

### Q3: 内存不足

```bash
# 限制 Docker 构建并发
export DOCKER_BUILDKIT_STEP_LOG_MAX_SIZE=10000000
docker system prune -a  # 清理缓存
```

---

## 性能优化

### 1. 加速依赖安装

```bash
# 使用 uv (比 pip 快 10-100x)
pip install uv
uv pip install -r requirements.txt
```

### 2. 缓存 Docker 层

```dockerfile
# 先安装依赖，再复制代码
COPY requirements.txt .
RUN pip install -r requirements.txt  # ← 缓存层
COPY src/ .                          # ← 代码变化不重装依赖
```

### 3. 并行测试

```bash
# 使用 pytest-xdist
pip install pytest-xdist
pytest -n auto  # 自动使用多核
```

---

## 下一步

1. 阅读 [CODE_STYLE.md](CODE_STYLE.md) - 代码规范
2. 阅读 [TESTING.md](TESTING.md) - 测试策略
3. 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献流程

---

**Keep it simple. Make it work.**
