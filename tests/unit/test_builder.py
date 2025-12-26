"""Tests for ImageBuilder."""

from unittest.mock import Mock, patch

import docker
import pytest

from ezrunner.core.builder import ImageBuilder
from ezrunner.exceptions import BuildError, DockerError


class TestImageBuilder:
    """Test ImageBuilder."""

    @patch("docker.from_env")
    def test_init_success(self, mock_docker: Mock) -> None:
        """Test successful initialization."""
        mock_client = Mock()
        mock_docker.return_value = mock_client

        builder = ImageBuilder()

        assert builder.client == mock_client
        mock_docker.assert_called_once()

    @patch("docker.from_env")
    def test_init_docker_not_running(self, mock_docker: Mock) -> None:
        """Test initialization when Docker is not running."""
        mock_docker.side_effect = docker.errors.DockerException("Docker not running")

        with pytest.raises(DockerError, match="Docker is not running"):
            ImageBuilder()

    @patch("docker.from_env")
    def test_build_success(self, mock_docker: Mock) -> None:
        """Test successful image build."""
        # Mock Docker client
        mock_client = Mock()
        mock_docker.return_value = mock_client

        # Mock build result
        mock_image = Mock()
        mock_client.images.build.return_value = (mock_image, [])

        # Build image
        builder = ImageBuilder()
        dockerfile = "FROM ubuntu\nRUN echo test"
        image = builder.build(dockerfile, "test:latest")

        assert image == mock_image
        mock_client.images.build.assert_called_once()

        # Verify build was called with correct arguments
        call_args = mock_client.images.build.call_args
        assert call_args.kwargs["tag"] == "test:latest"
        assert call_args.kwargs["rm"] is True

    @patch("docker.from_env")
    def test_build_failure(self, mock_docker: Mock) -> None:
        """Test build failure."""
        # Mock Docker client
        mock_client = Mock()
        mock_docker.return_value = mock_client

        # Mock build error
        mock_client.images.build.side_effect = docker.errors.BuildError(
            "Build failed", ""
        )

        # Build should raise BuildError
        builder = ImageBuilder()
        with pytest.raises(BuildError, match="Image build failed"):
            builder.build("FROM ubuntu", "test:latest")

    @patch("docker.from_env")
    def test_build_with_buildargs(self, mock_docker: Mock) -> None:
        """Test build with build arguments."""
        # Mock Docker client
        mock_client = Mock()
        mock_docker.return_value = mock_client

        # Mock build result
        mock_image = Mock()
        mock_client.images.build.return_value = (mock_image, [])

        # Build with buildargs
        builder = ImageBuilder()
        buildargs = {"MODEL_ID": "qwen/Qwen-7B", "PORT": "8080"}
        builder.build("FROM ubuntu", "test:latest", buildargs=buildargs)

        # Verify buildargs were passed
        call_args = mock_client.images.build.call_args
        assert call_args.kwargs["buildargs"] == buildargs
