"""ModelScope API client."""

import requests
from typing import Any


class ModelScopeClient:
    """Client for ModelScope API."""

    BASE_URL = "https://www.modelscope.cn/api/v1"

    def __init__(self, timeout: int = 30) -> None:
        """Initialize client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def get_model_info(self, model_id: str) -> dict[str, Any]:
        """Get model information.

        Args:
            model_id: Model identifier (e.g., "qwen/Qwen-7B-Chat")

        Returns:
            Model metadata dictionary

        Raises:
            requests.RequestException: API request failed
        """
        url = f"{self.BASE_URL}/models/{model_id}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_model_files(self, model_id: str) -> list[dict[str, Any]]:
        """Get list of model files.

        Args:
            model_id: Model identifier

        Returns:
            List of file metadata

        Raises:
            requests.RequestException: API request failed
        """
        url = f"{self.BASE_URL}/models/{model_id}/repo/files"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("files", [])
