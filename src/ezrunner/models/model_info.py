"""Model metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    """Model metadata.

    Attributes:
        model_id: Model identifier (e.g., "qwen/Qwen-7B-Chat")
        size_gb: Model size in GB
        format: Model format ("safetensors" or "pytorch")
        repo_type: Repository type ("modelscope" or "huggingface")
        architecture: Model architecture (e.g., "qwen2", "llama")
    """

    model_id: str
    size_gb: float
    format: str
    repo_type: str
    architecture: str

    def __post_init__(self) -> None:
        """Validate model info."""
        if self.size_gb <= 0:
            raise ValueError(f"Invalid model size: {self.size_gb}")
        if self.format not in ("safetensors", "pytorch"):
            raise ValueError(f"Unsupported format: {self.format}")
        if self.repo_type not in ("modelscope", "huggingface"):
            raise ValueError(f"Unsupported repo type: {self.repo_type}")
