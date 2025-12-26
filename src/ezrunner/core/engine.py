"""Engine selection module."""

from ezrunner.models.engine import Engine
from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


class EngineSelector:
    """Select optimal inference engine."""

    def select(
        self, model: ModelInfo, hardware: Hardware, force_engine: Engine | None = None
    ) -> Engine:
        """Select inference engine.

        Selection logic:
        1. If no GPU or insufficient memory -> Transformers
        2. If GPU memory >= 2x model size -> vLLM (high performance)
        3. Otherwise -> Transformers (compatibility)

        Args:
            model: Model information
            hardware: Hardware specifications
            force_engine: Force specific engine (optional)

        Returns:
            Selected engine
        """
        if force_engine:
            return force_engine

        # No GPU or non-NVIDIA -> Transformers
        if not hardware.has_gpu or hardware.gpu_vendor != "nvidia":
            return Engine.TRANSFORMERS

        # Insufficient memory -> Transformers
        if hardware.gpu_memory_gb < model.size_gb * 1.5:
            return Engine.TRANSFORMERS

        # Sufficient memory -> vLLM for high performance
        if hardware.gpu_memory_gb >= model.size_gb * 2.0:
            return Engine.VLLM

        # Default
        return Engine.TRANSFORMERS
