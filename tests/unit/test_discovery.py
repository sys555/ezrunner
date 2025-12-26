"""Tests for ModelDiscovery."""

from unittest.mock import Mock, patch

import pytest
import requests

from ezrunner.core.discovery import ModelDiscovery
from ezrunner.exceptions import ModelNotFoundError
from ezrunner.models.model_info import ModelInfo


class TestModelDiscovery:
    """Test ModelDiscovery."""

    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_info")
    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_files")
    def test_discover_from_modelscope(
        self, mock_get_files: Mock, mock_get_info: Mock
    ) -> None:
        """Test discovering model from ModelScope."""
        # Mock API responses
        mock_get_info.return_value = {"model_type": "qwen2"}
        mock_get_files.return_value = [
            {"path": "model-00001.safetensors", "size": 7_000_000_000},
            {"path": "model-00002.safetensors", "size": 7_000_000_000},
        ]

        discovery = ModelDiscovery()
        model = discovery.discover("qwen/Qwen-7B")

        assert model.model_id == "qwen/Qwen-7B"
        assert model.size_gb == 13.04  # 14GB / 1024^3
        assert model.format == "safetensors"
        assert model.repo_type == "modelscope"
        assert model.architecture == "qwen2"

    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_info")
    @patch("ezrunner.api.huggingface.HuggingFaceClient.get_model_info")
    @patch("ezrunner.api.huggingface.HuggingFaceClient.get_model_files")
    def test_discover_fallback_to_huggingface(
        self,
        mock_hf_files: Mock,
        mock_hf_info: Mock,
        mock_ms_info: Mock,
    ) -> None:
        """Test fallback to HuggingFace when ModelScope fails."""
        # ModelScope fails
        mock_ms_info.side_effect = requests.RequestException("Connection timeout")

        # HuggingFace succeeds
        mock_hf_info.return_value = {"pipeline_tag": "text-generation"}
        mock_hf_files.return_value = [
            {"path": "pytorch_model.bin", "size": 14_000_000_000}
        ]

        discovery = ModelDiscovery()
        model = discovery.discover("meta-llama/Llama-2-7b")

        assert model.repo_type == "huggingface"
        assert model.format == "pytorch"

    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_info")
    @patch("ezrunner.api.huggingface.HuggingFaceClient.get_model_info")
    def test_discover_model_not_found(
        self, mock_hf_info: Mock, mock_ms_info: Mock
    ) -> None:
        """Test discovering non-existent model."""
        # Both APIs fail
        mock_ms_info.side_effect = requests.RequestException("Not found")
        mock_hf_info.side_effect = requests.RequestException("Not found")

        discovery = ModelDiscovery()
        with pytest.raises(ModelNotFoundError, match="not found"):
            discovery.discover("nonexistent/model")

    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_info")
    @patch("ezrunner.api.modelscope.ModelScopeClient.get_model_files")
    def test_discover_pytorch_format(
        self, mock_get_files: Mock, mock_get_info: Mock
    ) -> None:
        """Test discovering PyTorch format model."""
        mock_get_info.return_value = {"model_type": "llama"}
        mock_get_files.return_value = [
            {"path": "pytorch_model.bin", "size": 14_000_000_000}
        ]

        discovery = ModelDiscovery()
        model = discovery.discover("test/pytorch-model")

        assert model.format == "pytorch"
