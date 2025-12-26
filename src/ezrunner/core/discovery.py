"""Model discovery module."""

import requests
from ezrunner.api.huggingface import HuggingFaceClient
from ezrunner.api.modelscope import ModelScopeClient
from ezrunner.exceptions import ModelNotFoundError
from ezrunner.models.model_info import ModelInfo
from ezrunner.utils.logger import get_logger

logger = get_logger(__name__)


class ModelDiscovery:
    """Discover model metadata from ModelScope or HuggingFace."""

    def __init__(self) -> None:
        """Initialize discovery service."""
        self.modelscope = ModelScopeClient()
        self.huggingface = HuggingFaceClient()

    def discover(self, model_id: str) -> ModelInfo:
        """Discover model information.

        Tries ModelScope first, falls back to HuggingFace.

        Args:
            model_id: Model identifier

        Returns:
            ModelInfo object

        Raises:
            ModelNotFoundError: Model not found in any repository
        """
        logger.info(f"Discovering model: {model_id}")

        # Try ModelScope first
        try:
            logger.debug("Trying ModelScope API...")
            return self._discover_modelscope(model_id)
        except requests.RequestException as e:
            logger.debug(f"ModelScope failed: {e}")

        # Fall back to HuggingFace
        try:
            logger.debug("Trying HuggingFace API...")
            return self._discover_huggingface(model_id)
        except requests.RequestException as e:
            logger.error(f"HuggingFace failed: {e}")
            raise ModelNotFoundError(
                f"Model {model_id} not found in ModelScope or HuggingFace"
            ) from e

    def _discover_modelscope(self, model_id: str) -> ModelInfo:
        """Discover from ModelScope."""
        info = self.modelscope.get_model_info(model_id)
        files = self.modelscope.get_model_files(model_id)

        # Determine format
        has_safetensors = any(f["path"].endswith(".safetensors") for f in files)
        model_format = "safetensors" if has_safetensors else "pytorch"

        # Calculate size
        total_size = sum(f.get("size", 0) for f in files)
        size_gb = total_size / (1024**3)

        # Get architecture from config
        architecture = info.get("model_type", "unknown")

        return ModelInfo(
            model_id=model_id,
            size_gb=round(size_gb, 2),
            format=model_format,
            repo_type="modelscope",
            architecture=architecture,
        )

    def _discover_huggingface(self, model_id: str) -> ModelInfo:
        """Discover from HuggingFace."""
        info = self.huggingface.get_model_info(model_id)
        files = self.huggingface.get_model_files(model_id)

        # Determine format
        has_safetensors = any(
            f.get("path", "").endswith(".safetensors") for f in files
        )
        model_format = "safetensors" if has_safetensors else "pytorch"

        # Calculate size
        total_size = sum(f.get("size", 0) for f in files)
        size_gb = total_size / (1024**3)

        # Get architecture
        architecture = info.get("pipeline_tag", "unknown")

        return ModelInfo(
            model_id=model_id,
            size_gb=round(size_gb, 2),
            format=model_format,
            repo_type="huggingface",
            architecture=architecture,
        )
