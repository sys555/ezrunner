"""Docker image exporter module."""

from pathlib import Path

from docker.models.images import Image

from ezrunner.exceptions import DockerError


class TarExporter:
    """Export Docker images to tar files."""

    def export(self, image: Image, output_path: Path) -> None:
        """Export image to tar file.

        Args:
            image: Docker image
            output_path: Output tar file path

        Raises:
            DockerError: Export failed
        """
        try:
            # Get image data as generator
            image_data = image.save()

            # Write to file
            with open(output_path, "wb") as f:
                for chunk in image_data:
                    f.write(chunk)

        except Exception as e:
            raise DockerError(f"Failed to export image: {e}") from e
