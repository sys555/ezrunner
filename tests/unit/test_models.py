"""Tests for data models."""

import pytest

from ezrunner.models.engine import Engine
from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


class TestEngine:
    """Test Engine enum."""

    def test_engine_values(self) -> None:
        """Test engine enum values."""
        assert Engine.TRANSFORMERS.value == "transformers"
        assert Engine.VLLM.value == "vllm"

    def test_engine_string(self) -> None:
        """Test engine string representation."""
        assert str(Engine.TRANSFORMERS) == "transformers"
        assert str(Engine.VLLM) == "vllm"


class TestModelInfo:
    """Test ModelInfo dataclass."""

    def test_valid_model_info(self) -> None:
        """Test creating valid ModelInfo."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        assert model.model_id == "qwen/Qwen-7B"
        assert model.size_gb == 14.2
        assert model.format == "safetensors"

    def test_invalid_size(self) -> None:
        """Test ModelInfo with invalid size."""
        with pytest.raises(ValueError, match="Invalid model size"):
            ModelInfo(
                model_id="test",
                size_gb=-1.0,
                format="safetensors",
                repo_type="modelscope",
                architecture="qwen2",
            )

    def test_invalid_format(self) -> None:
        """Test ModelInfo with invalid format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            ModelInfo(
                model_id="test",
                size_gb=10.0,
                format="gguf",
                repo_type="modelscope",
                architecture="qwen2",
            )

    def test_frozen(self) -> None:
        """Test that ModelInfo is frozen."""
        model = ModelInfo(
            model_id="test",
            size_gb=10.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        with pytest.raises(AttributeError):
            model.size_gb = 20.0  # type: ignore


class TestHardware:
    """Test Hardware dataclass."""

    def test_valid_hardware(self) -> None:
        """Test creating valid Hardware."""
        hw = Hardware(
            gpu_memory_gb=24.0,
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )
        assert hw.gpu_memory_gb == 24.0
        assert hw.has_gpu is True

    def test_no_gpu(self) -> None:
        """Test Hardware without GPU."""
        hw = Hardware(
            gpu_memory_gb=0.0,
            gpu_count=0,
            cpu_cores=8,
            ram_gb=16.0,
            gpu_vendor="none",
        )
        assert hw.has_gpu is False

    def test_invalid_gpu_memory(self) -> None:
        """Test Hardware with invalid GPU memory."""
        with pytest.raises(ValueError, match="Invalid GPU memory"):
            Hardware(
                gpu_memory_gb=-1.0,
                gpu_count=1,
                cpu_cores=8,
                ram_gb=16.0,
                gpu_vendor="nvidia",
            )
