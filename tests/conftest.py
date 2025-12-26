"""Pytest configuration and shared fixtures."""

import pytest

from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


@pytest.fixture
def sample_model() -> ModelInfo:
    """Sample model for testing."""
    return ModelInfo(
        model_id="qwen/Qwen-7B-Chat",
        size_gb=14.2,
        format="safetensors",
        repo_type="modelscope",
        architecture="qwen2",
    )


@pytest.fixture
def high_end_hardware() -> Hardware:
    """High-end hardware configuration."""
    return Hardware(
        gpu_memory_gb=80.0,
        gpu_count=2,
        cpu_cores=32,
        ram_gb=256.0,
        gpu_vendor="nvidia",
    )


@pytest.fixture
def low_end_hardware() -> Hardware:
    """Low-end hardware configuration."""
    return Hardware(
        gpu_memory_gb=8.0,
        gpu_count=1,
        cpu_cores=8,
        ram_gb=32.0,
        gpu_vendor="nvidia",
    )


@pytest.fixture
def cpu_only_hardware() -> Hardware:
    """CPU-only hardware configuration."""
    return Hardware(
        gpu_memory_gb=0.0,
        gpu_count=0,
        cpu_cores=16,
        ram_gb=64.0,
        gpu_vendor="none",
    )
