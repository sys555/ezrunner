"""Integration tests for Dockerfile generation pipeline."""

from ezrunner.core.dockerfile import DockerfileGenerator
from ezrunner.core.engine import EngineSelector
from ezrunner.models.engine import Engine
from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


class TestDockerfilePipeline:
    """Test the complete Dockerfile generation pipeline."""

    def test_full_pipeline_high_end_hardware(self) -> None:
        """Test full pipeline with high-end hardware."""
        # Arrange: Create model and hardware
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=40.0,
            gpu_count=1,
            cpu_cores=32,
            ram_gb=128.0,
            gpu_vendor="nvidia",
        )

        # Act: Select engine and generate Dockerfile
        selector = EngineSelector()
        engine = selector.select(model, hardware)

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, engine)

        # Assert: Should use vLLM for high-end hardware
        assert engine == Engine.VLLM
        assert "vllm" in dockerfile.lower()
        assert "qwen/Qwen-7B" in dockerfile

    def test_full_pipeline_low_end_hardware(self) -> None:
        """Test full pipeline with low-end hardware."""
        # Arrange: Low-end hardware
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        hardware = Hardware(
            gpu_memory_gb=8.0,
            gpu_count=1,
            cpu_cores=8,
            ram_gb=16.0,
            gpu_vendor="nvidia",
        )

        # Act
        selector = EngineSelector()
        engine = selector.select(model, hardware)

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, engine)

        # Assert: Should use Transformers for low-end hardware
        assert engine == Engine.TRANSFORMERS
        assert "transformers" in dockerfile.lower()

    def test_full_pipeline_cpu_only(self) -> None:
        """Test full pipeline with CPU-only hardware."""
        # Arrange: CPU-only
        model = ModelInfo(
            model_id="openai-community/gpt2",
            size_gb=0.5,
            format="safetensors",
            repo_type="huggingface",
            architecture="gpt2",
        )
        hardware = Hardware(
            gpu_memory_gb=0.0,
            gpu_count=0,
            cpu_cores=16,
            ram_gb=32.0,
            gpu_vendor="none",
        )

        # Act
        selector = EngineSelector()
        engine = selector.select(model, hardware)

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, engine)

        # Assert
        assert engine == Engine.TRANSFORMERS
        assert "openai-community/gpt2" in dockerfile
