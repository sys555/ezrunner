"""Tests for DockerfileGenerator."""

from ezrunner.core.dockerfile import DockerfileGenerator
from ezrunner.models.engine import Engine
from ezrunner.models.model_info import ModelInfo


class TestDockerfileGenerator:
    """Test DockerfileGenerator."""

    def test_generate_transformers_dockerfile(self) -> None:
        """Test generating Dockerfile for Transformers engine."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, Engine.TRANSFORMERS, port=8080)

        assert "FROM nvidia/cuda" in dockerfile
        assert "qwen/Qwen-7B" in dockerfile
        assert "transformers" in dockerfile
        assert "8080" in dockerfile

    def test_generate_vllm_dockerfile(self) -> None:
        """Test generating Dockerfile for vLLM engine."""
        model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, Engine.VLLM, port=9000)

        assert "FROM nvidia/cuda" in dockerfile
        assert "qwen/Qwen-7B" in dockerfile
        assert "vllm" in dockerfile.lower()
        assert "9000" in dockerfile

    def test_model_name_sanitization(self) -> None:
        """Test that model ID is sanitized for use in paths."""
        model = ModelInfo(
            model_id="ModelScope/Special-Model",
            size_gb=10.0,
            format="safetensors",
            repo_type="modelscope",
            architecture="test",
        )

        generator = DockerfileGenerator()
        dockerfile = generator.generate(model, Engine.TRANSFORMERS)

        # Should convert to lowercase and replace /
        assert "modelscope-special-model" in dockerfile
