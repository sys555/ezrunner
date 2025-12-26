# EZ Runner 代码规范

> **"Bad programmers worry about the code. Good programmers worry about data structures."**
> — Linus Torvalds

本规范基于 Linus 的"好品味"(Good Taste)原则。

---

## 核心原则

### 1. 简洁性 - 最高准则

```python
# ❌ 糟糕：特殊情况处理
def delete_node(head, target):
    if head == target:
        return head.next  # 特殊情况：头节点

    prev = head
    curr = head.next
    while curr:
        if curr == target:
            prev.next = curr.next  # 一般情况
            break
        prev = curr
        curr = curr.next
    return head

# ✅ 好品味：消除特殊情况
def delete_node(head, target):
    indirect = &head  # 指针的指针
    while *indirect:
        if *indirect == target:
            *indirect = (*indirect).next
            break
        indirect = &(*indirect).next
    return head
```

**关键：重新设计数据结构来消除特殊情况，而不是添加 if 判断。**

---

### 2. 缩进限制 - 铁律

```python
# ❌ 超过 3 层缩进 = 代码设计有问题
def process_model(model_id):
    if model_exists(model_id):
        if has_permission():
            if disk_space_enough():
                if download_model():
                    return True  # 第 5 层！
    return False

# ✅ 提前返回 (Early Return)
def process_model(model_id):
    if not model_exists(model_id):
        return False
    if not has_permission():
        return False
    if not disk_space_enough():
        return False
    return download_model()

# ✅✅ 更好：提取函数
def process_model(model_id):
    validate_model(model_id)
    ensure_resources()
    return download_model()
```

**规则：函数内部不超过 3 层缩进。如果需要更多，重构它。**

---

### 3. 函数设计 - 短小精悍

```python
# ❌ 函数做太多事情
def pack_model(model_id, output, engine, quantization, port):
    # 100 行代码：发现模型 + 分析硬件 + 生成 Dockerfile + 构建镜像 + 导出
    ...

# ✅ 单一职责
def pack_model(model_id: str, config: PackConfig) -> Path:
    """打包模型为 Docker 镜像"""
    model = discover_model(model_id)      # 10 行
    hardware = analyze_hardware(config)   # 5 行
    engine = select_engine(model, hardware)  # 8 行
    dockerfile = generate_dockerfile(model, engine)  # 3 行
    image = build_image(dockerfile)       # 5 行
    return export_image(image, config.output)  # 3 行
```

**规则：**
- 函数 ≤ 40 行（理想 ≤ 20 行）
- 只做一件事
- 可以用一句话描述

---

## 命名规范

### 基础规则

```python
# 模块/包: 小写 + 下划线
model_discovery.py
hardware_analyzer.py

# 类: PascalCase
class ModelDiscovery:
class HardwareAnalyzer:

# 函数/变量: snake_case
def discover_model():
gpu_memory_gb = 24.0

# 常量: 大写 + 下划线
MAX_RETRIES = 3
DEFAULT_PORT = 8080

# 私有成员: 单下划线前缀
def _validate_config():
self._cache = {}
```

### Linus 式命名

```python
# ❌ 冗长的匈牙利命名法
strModelIdentifier = "qwen"
intGpuMemoryInGigabytes = 24

# ✅ 简洁清晰
model_id = "qwen"
gpu_memory_gb = 24  # 单位在名称中，不需要注释

# ❌ 过度抽象
class AbstractModelDiscoveryStrategyFactory:
    ...

# ✅ 直接明了
class ModelDiscovery:
    ...

# ❌ 无意义的缩写
def proc_mdl(mid):  # 什么鬼？
    ...

# ✅ 清晰的名称
def discover_model(model_id: str):
    ...
```

**规则：**
- 局部变量可以短 (`i`, `n`, `fd`)
- 全局/公共接口必须清晰
- 不要为了缩短而缩写

---

## 类型注解 - 必需

```python
# ✅ 所有公共 API 必须有类型注解
def discover_model(model_id: str) -> ModelInfo:
    """发现模型元数据"""
    ...

def analyze_hardware(specs: dict[str, Any]) -> Hardware:
    """分析硬件能力"""
    ...

# ✅ dataclass 自带类型
@dataclass
class ModelInfo:
    model_id: str
    format: str
    size_gb: float
    repo_type: str
```

**规则：**
- 公共函数/方法：必须有类型注解
- 私有函数：可选（但推荐）
- 复杂类型：使用 `TypeAlias`

---

## 错误处理

### 1. 使用特定异常

```python
# ❌ 通用异常
raise Exception("Model not found")

# ✅ 自定义异常
class ModelNotFoundError(Exception):
    """模型不存在"""
    pass

raise ModelNotFoundError(f"Model {model_id} not found")
```

### 2. 提前失败 (Fail Fast)

```python
# ❌ 嵌套 try-except
def process():
    try:
        result = step1()
        try:
            result = step2(result)
            try:
                return step3(result)
            except Error3:
                ...
        except Error2:
            ...
    except Error1:
        ...

# ✅ 让异常向上传播
def process():
    result = step1()  # 失败就让它抛出
    result = step2(result)
    return step3(result)
```

### 3. 不要吞掉异常

```python
# ❌ 吞掉异常
try:
    download_model()
except Exception:
    pass  # 静默失败，用户不知道发生了什么

# ✅ 记录并重新抛出
try:
    download_model()
except DownloadError as e:
    logger.error(f"Failed to download model: {e}")
    raise  # 让调用者处理
```

---

## 注释规范

### 1. 代码要自解释

```python
# ❌ 注释说"是什么"
i = i + 1  # 增加 i

# ✅ 代码说明一切
retry_count += 1

# ❌ 无意义的文档字符串
def add(a, b):
    """
    Adds two numbers.
    Args:
        a: first number
        b: second number
    Returns:
        sum of a and b
    """
    return a + b  # 废话！

# ✅ 解释"为什么"
def add(a, b):
    # 不需要注释，代码已经够清楚了
    return a + b
```

### 2. 注释解释"为什么"

```python
# ✅ 解释非显而易见的逻辑
def select_engine(model: ModelInfo, hardware: Hardware) -> Engine:
    # vLLM 需要 2x 模型大小的显存用于 KV cache
    if hardware.gpu_memory_gb < model.size_gb * 2.0:
        return Engine.TRANSFORMERS
    return Engine.VLLM

# ✅ 解释 Workaround
def build_image(dockerfile: str):
    # BuildKit 有时会卡住，添加超时
    # See: https://github.com/moby/buildkit/issues/1234
    client.images.build(..., timeout=3600)
```

### 3. 文档字符串规范

```python
# ✅ 简洁的文档字符串
def discover_model(model_id: str) -> ModelInfo:
    """
    查询模型元数据。

    先尝试 ModelScope，失败则尝试 HuggingFace。

    Raises:
        ModelNotFoundError: 模型不存在
    """
    ...
```

---

## 数据结构设计

### 1. 使用 dataclass

```python
# ❌ 字典传来传去
def process(config):
    model_id = config["model_id"]
    gpu_memory = config["hardware"]["gpu"]["memory"]  # 容易出错
    ...

# ✅ 强类型数据类
@dataclass
class ModelInfo:
    model_id: str
    size_gb: float
    format: str

@dataclass
class Hardware:
    gpu_memory_gb: float
    gpu_count: int

def process(model: ModelInfo, hardware: Hardware):
    # IDE 自动补全，类型安全
    if hardware.gpu_memory_gb < model.size_gb:
        ...
```

### 2. 不可变性

```python
# ✅ 使用 frozen dataclass
@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    size_gb: float

model = ModelInfo("qwen", 14.2)
# model.size_gb = 20  # ❌ 抛出异常
```

---

## Import 规范

```python
# 分组顺序：标准库 → 第三方库 → 本地模块
import os
import sys
from pathlib import Path

import click
import requests
from docker import DockerClient

from ezrunner.core.discovery import ModelDiscovery
from ezrunner.models.model_info import ModelInfo
```

---

## 自动化工具

### 格式化

```bash
# Black - 无需配置的格式化工具
black src/ tests/

# 配置 (pyproject.toml)
[tool.black]
line-length = 88
target-version = ["py311"]
```

### Linting

```bash
# Ruff - 极速 Linter (替代 flake8 + isort + pylint)
ruff check src/ tests/
ruff check --fix src/ tests/  # 自动修复

# 配置 (pyproject.toml)
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # 行长度由 black 处理
```

### 类型检查

```bash
# Mypy
mypy src/

# 配置 (pyproject.toml)
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
```

---

## Git Commit 规范

```bash
# 格式: <type>: <subject>
#
# type:
#   feat:     新功能
#   fix:      Bug 修复
#   refactor: 重构
#   docs:     文档
#   test:     测试
#   chore:    构建/工具

# ✅ 好的 commit
feat: implement ModelDiscovery with ModelScope API
fix: handle network timeout in image builder
refactor: simplify engine selection logic

# ❌ 差的 commit
update code
fix bug
wip
```

---

## 检查清单

提交代码前，确保：

- [ ] `black src/ tests/` - 格式化通过
- [ ] `ruff check src/ tests/` - Linting 通过
- [ ] `mypy src/` - 类型检查通过
- [ ] `pytest` - 所有测试通过
- [ ] 没有超过 3 层缩进
- [ ] 函数 ≤ 40 行
- [ ] 所有公共 API 有类型注解
- [ ] 注释解释"为什么"，不是"是什么"

---

**"Talk is cheap. Show me the code."**
— Linus Torvalds
