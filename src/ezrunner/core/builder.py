"""Docker image builder module."""

import tempfile
from pathlib import Path
from typing import Any

import docker
from docker.models.images import Image

from ezrunner.exceptions import BuildError, DockerError


class ImageBuilder:
    """Build Docker images."""

    def __init__(self) -> None:
        """Initialize builder."""
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            raise DockerError("Docker is not running") from e

    def build(
        self, dockerfile: str, tag: str, buildargs: dict[str, str] | None = None
    ) -> Image:
        """Build Docker image.

        Args:
            dockerfile: Dockerfile content
            tag: Image tag
            buildargs: Build arguments

        Returns:
            Built image

        Raises:
            BuildError: Build failed
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write Dockerfile
            dockerfile_path = Path(tmpdir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile)

            # Build image
            try:
                image, logs = self.client.images.build(
                    path=tmpdir,
                    tag=tag,
                    rm=True,
                    buildargs=buildargs or {},
                )
                return image
            except docker.errors.BuildError as e:
                raise BuildError(f"Image build failed: {e}") from e
