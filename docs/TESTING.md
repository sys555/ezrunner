# EZ Runner 测试策略

> **"Theory and practice sometimes clash. Theory loses. Every single time."**
> — Linus Torvalds

测试要服务于代码质量，不是为了达到某个覆盖率数字。

---

## 测试原则

### 1. 测试真实场景

```python
# ❌ 测试实现细节
def test_internal_cache_structure():
    discovery = ModelDiscovery()
    assert isinstance(discovery._cache, dict)  # 谁在乎？

# ✅ 测试行为
def test_model_discovery_caches_results():
    discovery = ModelDiscovery()
    model1 = discovery.discover("qwen/Qwen-7B")
    model2 = discovery.discover("qwen/Qwen-7B")
    # 第二次不应该调用 API（通过 mock 验证）
```

### 2. 不要过度测试

```python
# ❌ 测试标准库
def test_string_concatenation():
    assert "hello" + " " + "world" == "hello world"

# ❌ 测试 getter/setter
def test_model_id_setter():
    model = ModelInfo()
    model.model_id = "qwen"
    assert model.model_id == "qwen"

# ✅ 测试业务逻辑
def test_engine_selection_with_insufficient_memory():
    model = ModelInfo(size_gb=14.0)
    hardware = Hardware(gpu_memory_gb=16.0)  # 不足 2x
    engine = select_engine(model, hardware)
    assert engine == Engine.TRANSFORMERS
```

### 3. 快速失败

```python
# ✅ 测试要快速运行
# 单元测试: < 100ms
# 集成测试: < 5s
# 端到端测试: < 30s

# 慢测试要标记
@pytest.mark.slow
def test_full_model_download():
    ...
```

---

## 测试层次

### 1. 单元测试 (Unit Tests)

**目标：** 测试单个函数/类的逻辑

**位置：** `tests/unit/`

**原则：**
- 无外部依赖（网络、文件、Docker）
- 使用 Mock 替代外部服务
- 快速（< 100ms）

```python
# tests/unit/test_discovery.py
from unittest.mock import Mock, patch
from ezrunner.core.discovery import ModelDiscovery
from ezrunner.models.model_info import ModelInfo

def test_discover_model_from_modelscope():
    """测试从 ModelScope 发现模型"""
    discovery = ModelDiscovery()

    with patch("ezrunner.api.modelscope.get_model_info") as mock_api:
        mock_api.return_value = {
            "model_id": "qwen/Qwen-7B",
            "size": 14200000000,
            "format": "safetensors"
        }

        model = discovery.discover("qwen/Qwen-7B")

        assert model.model_id == "qwen/Qwen-7B"
        assert model.size_gb == 14.2
        assert model.format == "safetensors"
        mock_api.assert_called_once()

def test_discover_model_fallback_to_huggingface():
    """测试 ModelScope 失败后降级到 HuggingFace"""
    discovery = ModelDiscovery()

    with patch("ezrunner.api.modelscope.get_model_info") as mock_ms:
        with patch("ezrunner.api.huggingface.get_model_info") as mock_hf:
            mock_ms.side_effect = ConnectionError("ModelScope down")
            mock_hf.return_value = {"model_id": "meta-llama/Llama-2-7b"}

            model = discovery.discover("meta-llama/Llama-2-7b")

            assert model.repo_type == "huggingface"
            mock_ms.assert_called_once()
            mock_hf.assert_called_once()
```

---

### 2. 集成测试 (Integration Tests)

**目标：** 测试多个模块协作

**位置：** `tests/integration/`

**原则：**
- 可以有轻量级外部依赖（临时文件、小体积文件）
- 不依赖真实的模型下载
- 较快（< 5s）

```python
# tests/integration/test_dockerfile_generation.py
import tempfile
from pathlib import Path
from ezrunner.core.discovery import ModelDiscovery
from ezrunner.core.engine import EngineSelector
from ezrunner.core.dockerfile import DockerfileGenerator
from ezrunner.models.model_info import ModelInfo
from ezrunner.models.hardware import Hardware
from ezrunner.models.engine import Engine

def test_dockerfile_generation_pipeline():
    """测试从模型信息到 Dockerfile 的完整流程"""
    # 准备数据
    model = ModelInfo(
        model_id="qwen/Qwen-7B",
        size_gb=14.2,
        format="safetensors",
        repo_type="modelscope",
        architecture="qwen2"
    )
    hardware = Hardware(gpu_memory_gb=24.0, gpu_count=1)

    # 选择引擎
    selector = EngineSelector()
    engine = selector.select(model, hardware)
    assert engine == Engine.VLLM  # 显存充足

    # 生成 Dockerfile
    generator = DockerfileGenerator()
    dockerfile = generator.generate(model, engine)

    # 验证内容
    assert "FROM nvidia/cuda" in dockerfile
    assert "qwen/Qwen-7B" in dockerfile
    assert "vllm" in dockerfile.lower()

def test_full_pack_without_docker():
    """测试打包流程（不实际构建 Docker）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock Docker 客户端
        from unittest.mock import Mock
        mock_docker = Mock()

        # 执行打包（到 Dockerfile 生成为止）
        from ezrunner.cli import pack_model
        result = pack_model(
            model_id="qwen/Qwen-1.5B",
            output=Path(tmpdir) / "model.tar",
            dry_run=True  # 不实际构建
        )

        assert result.dockerfile_path.exists()
        assert "qwen/Qwen-1.5B" in result.dockerfile_path.read_text()
```

---

### 3. 端到端测试 (E2E Tests)

**目标：** 测试完整用户流程

**位置：** `tests/e2e/`

**原则：**
- 真实的外部依赖（Docker、小模型）
- 慢（< 30s），标记为 `@pytest.mark.e2e`
- CI 中可选运行

```python
# tests/e2e/test_full_pipeline.py
import pytest
import docker
from pathlib import Path
from ezrunner.cli import pack_model, run_model

@pytest.mark.e2e
@pytest.mark.slow
def test_pack_and_run_tiny_model(tmp_path):
    """
    端到端测试：打包并运行一个小模型

    使用 gpt2 (500MB) 而非真实的 7B 模型
    """
    # 1. 打包模型
    output = tmp_path / "gpt2.tar"
    pack_model(
        model_id="openai-community/gpt2",
        output=output,
        engine="transformers"
    )

    assert output.exists()
    assert output.stat().st_size > 100_000_000  # > 100MB

    # 2. 加载镜像
    client = docker.from_env()
    with open(output, "rb") as f:
        client.images.load(f)

    # 3. 运行容器
    container = client.containers.run(
        "ezrunner-gpt2:latest",
        detach=True,
        ports={"8080/tcp": 8080},
        remove=True
    )

    try:
        # 4. 等待服务启动
        import time
        time.sleep(5)

        # 5. 测试 API
        import requests
        response = requests.get("http://localhost:8080/v1/models")
        assert response.status_code == 200

        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json={
                "model": "gpt2",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            }
        )
        assert response.status_code == 200
        assert "choices" in response.json()

    finally:
        container.stop()
```

---

## 测试覆盖率

### 要求

- **整体覆盖率**: ≥ 80%
- **核心模块**: ≥ 90%
  - `core/discovery.py`
  - `core/engine.py`
  - `core/dockerfile.py`
- **CLI**: ≥ 70% (UI 代码难测试)

### 测量覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=ezrunner --cov-report=html --cov-report=term

# 查看报告
open htmlcov/index.html
```

### 配置

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=ezrunner",
    "--cov-report=term-missing",
]

# 标记
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "e2e: marks tests as end-to-end (deselect with '-m \"not e2e\"')",
]
```

---

## Mock 和 Fixtures

### 1. 使用 Fixtures 共享数据

```python
# tests/conftest.py
import pytest
from ezrunner.models.model_info import ModelInfo
from ezrunner.models.hardware import Hardware

@pytest.fixture
def sample_model():
    """标准测试模型"""
    return ModelInfo(
        model_id="qwen/Qwen-7B",
        size_gb=14.2,
        format="safetensors",
        repo_type="modelscope",
        architecture="qwen2"
    )

@pytest.fixture
def high_end_hardware():
    """高端硬件配置"""
    return Hardware(
        gpu_memory_gb=80.0,
        gpu_count=2,
        cpu_cores=32,
        ram_gb=256.0,
        gpu_vendor="nvidia"
    )

@pytest.fixture
def low_end_hardware():
    """低端硬件配置"""
    return Hardware(
        gpu_memory_gb=8.0,
        gpu_count=1,
        cpu_cores=8,
        ram_gb=32.0,
        gpu_vendor="nvidia"
    )

# 使用 fixture
def test_engine_selection_high_end(sample_model, high_end_hardware):
    selector = EngineSelector()
    engine = selector.select(sample_model, high_end_hardware)
    assert engine == Engine.VLLM

def test_engine_selection_low_end(sample_model, low_end_hardware):
    selector = EngineSelector()
    engine = selector.select(sample_model, low_end_hardware)
    assert engine == Engine.TRANSFORMERS
```

### 2. Mock 外部依赖

```python
# ✅ Mock HTTP 请求
from unittest.mock import patch, Mock

@patch("requests.get")
def test_api_call(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {"model_id": "qwen"}
    )

    result = fetch_model_info("qwen")
    assert result["model_id"] == "qwen"

# ✅ Mock Docker 客户端
@patch("docker.from_env")
def test_image_build(mock_docker):
    mock_client = Mock()
    mock_docker.return_value = mock_client

    builder = ImageBuilder()
    builder.build("FROM ubuntu", "test:latest")

    mock_client.images.build.assert_called_once()
```

### 3. Fixture 作用域

```python
# 会话级 fixture (运行一次)
@pytest.fixture(scope="session")
def docker_client():
    """Docker 客户端（整个测试会话共享）"""
    return docker.from_env()

# 模块级 fixture
@pytest.fixture(scope="module")
def test_model_downloaded(tmp_path_factory):
    """下载测试模型（每个模块一次）"""
    path = tmp_path_factory.mktemp("models")
    # 下载小模型...
    return path

# 函数级 fixture (默认)
@pytest.fixture
def temp_dir(tmp_path):
    """临时目录（每个测试一次）"""
    return tmp_path
```

---

## 运行测试

### 基本用法

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/unit/test_discovery.py

# 运行特定测试
pytest tests/unit/test_discovery.py::test_discover_model

# 显示详细输出
pytest -v

# 显示 print 输出
pytest -s
```

### 选择性运行

```bash
# 只运行单元测试
pytest tests/unit/

# 跳过慢测试
pytest -m "not slow"

# 只运行快速测试（不包括 E2E）
pytest -m "not e2e and not slow"

# 失败后立即停止
pytest -x

# 失败后进入调试器
pytest --pdb
```

### 并行测试

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 自动使用多核
pytest -n auto

# 指定进程数
pytest -n 4
```

---

## CI/CD 配置

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=ezrunner --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  e2e:
    runs-on: ubuntu-latest
    needs: test  # 只有单元测试通过才运行 E2E

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker
        uses: docker/setup-buildx-action@v3

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v -m e2e
```

---

## 测试最佳实践

### 1. 测试命名

```python
# ✅ 描述性命名
def test_model_discovery_returns_correct_size():
    ...

def test_engine_selector_chooses_vllm_with_sufficient_memory():
    ...

def test_dockerfile_generator_includes_cuda_base_image():
    ...

# ❌ 无意义命名
def test_1():
    ...

def test_discovery():
    ...
```

### 2. AAA 模式 (Arrange-Act-Assert)

```python
def test_engine_selection():
    # Arrange (准备数据)
    model = ModelInfo(size_gb=14.2)
    hardware = Hardware(gpu_memory_gb=32.0)
    selector = EngineSelector()

    # Act (执行操作)
    engine = selector.select(model, hardware)

    # Assert (验证结果)
    assert engine == Engine.VLLM
```

### 3. 一个测试只测一件事

```python
# ❌ 测试多件事
def test_model_discovery_and_engine_selection_and_dockerfile():
    model = discover_model("qwen")
    engine = select_engine(model, hardware)
    dockerfile = generate_dockerfile(model, engine)
    assert model.size_gb > 0
    assert engine == Engine.VLLM
    assert "FROM" in dockerfile

# ✅ 拆分成多个测试
def test_model_discovery_returns_valid_size():
    model = discover_model("qwen")
    assert model.size_gb > 0

def test_engine_selection_with_high_memory():
    engine = select_engine(model, high_memory_hardware)
    assert engine == Engine.VLLM

def test_dockerfile_has_base_image():
    dockerfile = generate_dockerfile(model, engine)
    assert "FROM" in dockerfile
```

---

## 常见陷阱

### 1. 测试依赖外部状态

```python
# ❌ 依赖网络
def test_download_model():
    download_model("qwen/Qwen-7B")  # 慢且不可靠
    assert Path("qwen").exists()

# ✅ Mock 网络请求
@patch("requests.get")
def test_download_model(mock_get):
    mock_get.return_value = Mock(content=b"fake_model_data")
    download_model("qwen/Qwen-7B")
    assert Path("qwen").exists()
```

### 2. 测试顺序依赖

```python
# ❌ 测试顺序敏感
class TestPipeline:
    def test_1_discovery(self):
        self.model = discover_model("qwen")

    def test_2_selection(self):
        self.engine = select_engine(self.model)  # 依赖 test_1

# ✅ 每个测试独立
def test_discovery():
    model = discover_model("qwen")
    assert model.model_id == "qwen"

def test_selection():
    model = ModelInfo(...)  # 独立准备数据
    engine = select_engine(model)
    assert engine == Engine.VLLM
```

---

**"Testing shows the presence, not the absence of bugs."**
— Edsger W. Dijkstra

测试不是银弹，但能帮你早点发现问题。
