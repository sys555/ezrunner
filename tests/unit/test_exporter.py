"""Tests for TarExporter."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from ezrunner.core.exporter import TarExporter
from ezrunner.exceptions import DockerError


class TestTarExporter:
    """Test TarExporter."""

    def test_export_success(self, tmp_path: Path) -> None:
        """Test successful image export."""
        # Mock image
        mock_image = Mock()
        mock_image.save.return_value = [b"chunk1", b"chunk2", b"chunk3"]

        # Export
        exporter = TarExporter()
        output_path = tmp_path / "test.tar"
        exporter.export(mock_image, output_path)

        # Verify file was created
        assert output_path.exists()

        # Verify content
        content = output_path.read_bytes()
        assert content == b"chunk1chunk2chunk3"

    def test_export_failure(self, tmp_path: Path) -> None:
        """Test export failure."""
        # Mock image that fails
        mock_image = Mock()
        mock_image.save.side_effect = Exception("Save failed")

        # Export should raise DockerError
        exporter = TarExporter()
        output_path = tmp_path / "test.tar"

        with pytest.raises(DockerError, match="Failed to export image"):
            exporter.export(mock_image, output_path)

    def test_export_large_chunks(self, tmp_path: Path) -> None:
        """Test exporting with large chunks."""
        # Mock image with large chunks
        mock_image = Mock()
        large_chunk = b"x" * 1024 * 1024  # 1MB
        mock_image.save.return_value = [large_chunk] * 10  # 10MB total

        # Export
        exporter = TarExporter()
        output_path = tmp_path / "large.tar"
        exporter.export(mock_image, output_path)

        # Verify file size
        assert output_path.stat().st_size == 10 * 1024 * 1024
