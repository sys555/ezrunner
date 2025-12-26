"""Engine types for LLM inference."""

from enum import Enum


class Engine(Enum):
    """Supported inference engines."""

    TRANSFORMERS = "transformers"
    VLLM = "vllm"

    def __str__(self) -> str:
        return self.value
