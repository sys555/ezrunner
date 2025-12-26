"""Tests for EngineSelector."""

from ezrunner.core.engine import EngineSelector
from ezrunner.models.engine import Engine
from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


class TestEngineSelector:
    """Test EngineSelector."""

    def test_select_vllm_with_sufficient_memory(self) -> None:
        """Test selecting vLLM with sufficient GPU memory."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=32.0,  # 2x+ model size
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )

        selector = EngineSelector()
        engine = selector.select(model, hardware)

        assert engine == Engine.VLLM

    def test_select_transformers_with_insufficient_memory(self) -> None:
        """Test selecting Transformers with insufficient GPU memory."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=16.0,  # Less than 2x model size
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )

        selector = EngineSelector()
        engine = selector.select(model, hardware)

        assert engine == Engine.TRANSFORMERS

    def test_select_transformers_without_gpu(self) -> None:
        """Test selecting Transformers without GPU."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=0.0,
            gpu_count=0,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="none",
        )

        selector = EngineSelector()
        engine = selector.select(model, hardware)

        assert engine == Engine.TRANSFORMERS

    def test_force_engine(self) -> None:
        """Test forcing specific engine."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=32.0,
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )

        selector = EngineSelector()
        engine = selector.select(model, hardware, force_engine=Engine.TRANSFORMERS)

        assert engine == Engine.TRANSFORMERS
