# EZ Runner 架构设计

## 设计哲学

### 核心原则

1. **简单至上** - 一条命令解决问题
2. **通用性优先** - 支持任意模型，不维护模型列表
3. **离线优先** - 所有依赖打包进镜像
4. **官方格式** - 使用 safetensors，不强制转换

### Linus 式设计检查

```c
// 三个关键问题
1. "这是真问题还是臆想？"
   → 真问题：离线环境运行新模型

2. "有更简单的方法吗？"
   → 已是最简：一条命令打包

3. "会破坏什么吗？"
   → 零破坏：完全自包含
```

---

## 系统架构

### 整体流程

```
┌────────────────────────────────────────────────────────┐
│                    CLI Layer                           │
│  ezrunner pack <model> → ezrunner run <tar>            │
└─────────────────┬──────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│                  Core Modules                           │
├─────────────────────────────────────────────────────────┤
│  ModelDiscovery  →  HardwareAnalyzer  →  EngineSelector │
│        ↓                                      ↓          │
│  DockerfileGenerator  →  ImageBuilder  →  TarExporter   │
└─────────────────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│                External Dependencies                    │
│  Docker Engine  |  ModelScope API  |  HuggingFace API   │
└─────────────────────────────────────────────────────────┘
```

---

## 核心模块设计

### 1. ModelDiscovery (模型发现)

**职责：** 查询模型元数据，判断是否存在及格式

```python
class ModelDiscovery:
    def discover(self, model_id: str) -> ModelInfo:
        """
        数据流:
        model_id → API 查询 → ModelInfo

        返回:
        - model_id: str
        - format: "safetensors" | "pytorch"
        - size_gb: float
        - repo_type: "modelscope" | "huggingface"
        - architecture: "qwen2" | "llama" | ...
        """
```

**实现策略：**
```
1. 尝试 ModelScope API
2. 失败则尝试 HuggingFace API
3. 解析 config.json 获取架构信息
4. 计算模型文件总大小
```

---

### 2. HardwareAnalyzer (硬件分析)

**职责：** 分析目标机器硬件能力

```python
class HardwareAnalyzer:
    def analyze(self, target_specs: dict) -> Hardware:
        """
        输入: 用户指定的目标硬件
        输出: Hardware 对象

        Hardware:
        - gpu_count: int
        - gpu_memory_gb: float
        - cpu_cores: int
        - ram_gb: float
        - gpu_vendor: "nvidia" | "amd" | "none"
        """
```

---

### 3. EngineSelector (引擎选择)

**职责：** 根据模型和硬件选择最优推理引擎

```python
class EngineSelector:
    def select(self, model: ModelInfo, hardware: Hardware) -> Engine:
        """
        决策树:

        if hardware.gpu_vendor != "nvidia":
            return Engine.TRANSFORMERS  # CPU fallback

        if hardware.gpu_memory_gb < model.size_gb * 1.5:
            return Engine.TRANSFORMERS  # 显存不足

        if hardware.gpu_memory_gb >= model.size_gb * 2.0:
            return Engine.VLLM  # 显存充足，高性能

        return Engine.TRANSFORMERS  # 默认
        """
```

**引擎对比：**

| 引擎 | 优势 | 劣势 | 使用场景 |
|------|------|------|---------|
| **Transformers** | 兼容性强、稳定 | 性能中等 | 默认选择 |
| **vLLM** | 吞吐量极高 | 显存要求高 | 高并发服务 |

---

### 4. DockerfileGenerator (Dockerfile 生成)

**职责：** 根据引擎生成对应的 Dockerfile

```python
class DockerfileGenerator:
    def generate(self, model: ModelInfo, engine: Engine) -> str:
        """
        模板选择:
        - Engine.TRANSFORMERS → transformers.dockerfile.j2
        - Engine.VLLM → vllm.dockerfile.j2

        变量替换:
        - {{ MODEL_ID }}
        - {{ MODEL_SIZE }}
        - {{ PORT }}
        """
```

**Dockerfile 结构：**

```dockerfile
# 多阶段构建
FROM python:3.11-slim as downloader
# Stage 1: 下载模型

FROM nvidia/cuda:12.1.0-runtime as runtime
# Stage 2: 运行环境

COPY --from=downloader /models /models
# 只复制模型，减小镜像体积
```

---

### 5. ImageBuilder (镜像构建)

**职责：** 调用 Docker API 构建镜像

```python
class ImageBuilder:
    def build(self, dockerfile: str, tag: str) -> Image:
        """
        流程:
        1. 创建临时目录
        2. 写入 Dockerfile
        3. docker build
        4. 返回 Image 对象

        优化:
        - 使用 BuildKit (并行构建)
        - 缓存层复用
        - 显示构建进度
        """
```

---

### 6. TarExporter (镜像导出)

**职责：** 将 Docker 镜像导出为 .tar 文件

```python
class TarExporter:
    def export(self, image: Image, output_path: str):
        """
        docker save <image> > output.tar

        压缩选项:
        - 不压缩 (默认，兼容性好)
        - gzip (可选，体积小但加载慢)
        """
```

---

## 数据结构设计

### ModelInfo

```python
@dataclass
class ModelInfo:
    model_id: str           # "qwen/Qwen-7B-Chat"
    format: str             # "safetensors"
    size_gb: float          # 14.2
    repo_type: str          # "modelscope"
    architecture: str       # "qwen2"
    files: List[str]        # ["model-00001.safetensors", ...]
```

### Hardware

```python
@dataclass
class Hardware:
    gpu_count: int          # 1
    gpu_memory_gb: float    # 24.0
    cpu_cores: int          # 16
    ram_gb: float           # 64.0
    gpu_vendor: str         # "nvidia"
```

### Engine

```python
class Engine(Enum):
    TRANSFORMERS = "transformers"
    VLLM = "vllm"
```

---

## 错误处理策略

### 1. 模型不存在

```python
try:
    model = discovery.discover(model_id)
except ModelNotFoundError:
    print(f"❌ 模型 {model_id} 不存在")
    print("提示：检查模型名称是否正确")
    sys.exit(1)
```

### 2. 显存不足

```python
if hardware.gpu_memory_gb < model.size_gb:
    print(f"⚠️  警告：目标显存可能不足")
    print(f"   模型需要: {model.size_gb:.1f} GB")
    print(f"   目标显存: {hardware.gpu_memory_gb:.1f} GB")
    print(f"   建议：使用 --quantization 4bit 减少显存需求")
```

### 3. Docker 未运行

```python
try:
    client = docker.from_env()
except DockerException:
    print("❌ Docker 未运行")
    print("请先启动 Docker")
    sys.exit(1)
```

---

## 性能优化

### 1. 构建缓存

```dockerfile
# 分层优化
RUN pip install torch transformers  # 缓存依赖层
COPY server.py /app/                # 代码变化不重装依赖
RUN download_model()                # 模型层独立
```

### 2. 多阶段构建

```dockerfile
FROM python:3.11 as downloader
RUN download_model()  # 大镜像，包含下载工具

FROM nvidia/cuda:12.1-runtime
COPY --from=downloader /models /models  # 小镜像，只要模型
```

### 3. 并行构建

```python
# 使用 BuildKit
os.environ["DOCKER_BUILDKIT"] = "1"
```

---

## 安全考虑

### 1. 模型来源验证

```python
def verify_model_source(model_id: str):
    """验证模型来自可信源"""
    allowed_domains = ["modelscope.cn", "huggingface.co"]
    # 检查模型仓库域名
```

### 2. 容器安全

```dockerfile
# 非 root 用户运行
USER 1000:1000

# 只读文件系统
FROM nvidia/cuda:12.1-runtime
RUN chmod -R a-w /models
```

---

## 扩展性设计

### 1. 插件化引擎

```python
# 未来可以轻松添加新引擎
class TensorRTEngine(Engine):
    def generate_dockerfile(self):
        ...
```

### 2. 多模态支持

```python
# 预留接口
class ModelInfo:
    modality: str  # "text" | "vision" | "multimodal"
```

---

## 测试策略

### 单元测试

```python
def test_model_discovery():
    discovery = ModelDiscovery()
    model = discovery.discover("qwen/Qwen-7B-Chat")
    assert model.format == "safetensors"
    assert model.size_gb > 10
```

### 集成测试

```python
def test_full_pipeline():
    # 端到端测试
    ezrunner pack qwen/Qwen-1.5B -o test.tar
    assert Path("test.tar").exists()
```

---

**架构原则：Keep It Simple, Make It Work.**
