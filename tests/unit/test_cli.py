"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from ezrunner.cli import main
from ezrunner.exceptions import DockerError, ModelNotFoundError
from ezrunner.models.engine import Engine
from ezrunner.models.hardware import Hardware
from ezrunner.models.model_info import ModelInfo


class TestPackCommand:
    """Test pack command."""

    @patch("ezrunner.cli.TarExporter")
    @patch("ezrunner.cli.ImageBuilder")
    @patch("ezrunner.cli.DockerfileGenerator")
    @patch("ezrunner.cli.EngineSelector")
    @patch("ezrunner.cli.HardwareAnalyzer")
    @patch("ezrunner.cli.ModelDiscovery")
    def test_pack_success(
        self,
        mock_discovery_cls: Mock,
        mock_analyzer_cls: Mock,
        mock_selector_cls: Mock,
        mock_generator_cls: Mock,
        mock_builder_cls: Mock,
        mock_exporter_cls: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful pack command."""
        # Setup mocks
        mock_model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        mock_hardware = Hardware(
            gpu_memory_gb=24.0,
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )
        mock_image = Mock()
        mock_image.tags = ["ezrunner-qwen-7b:latest"]

        mock_discovery = Mock()
        mock_discovery.discover.return_value = mock_model
        mock_discovery_cls.return_value = mock_discovery

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_hardware
        mock_analyzer_cls.return_value = mock_analyzer

        mock_selector = Mock()
        mock_selector.select.return_value = Engine.VLLM
        mock_selector_cls.return_value = mock_selector

        mock_generator = Mock()
        mock_generator.generate.return_value = "FROM ubuntu"
        mock_generator_cls.return_value = mock_generator

        mock_builder = Mock()
        mock_builder.build.return_value = mock_image
        mock_builder_cls.return_value = mock_builder

        mock_exporter = Mock()
        mock_exporter_cls.return_value = mock_exporter

        # Run command
        runner = CliRunner()
        output_path = tmp_path / "test.tar"
        # Create the file so stat() works
        output_path.write_bytes(b"test")

        result = runner.invoke(
            main,
            ["pack", "qwen/Qwen-7B", "-o", str(output_path), "--target-gpu", "24"],
        )

        # Verify
        assert result.exit_code == 0
        assert "Success" in result.output

        mock_discovery.discover.assert_called_once_with("qwen/Qwen-7B")
        mock_analyzer.analyze.assert_called_once()
        mock_selector.select.assert_called_once()
        mock_generator.generate.assert_called_once()
        mock_builder.build.assert_called_once()
        mock_exporter.export.assert_called_once()

    @patch("ezrunner.cli.ModelDiscovery")
    def test_pack_model_not_found(self, mock_discovery_cls: Mock) -> None:
        """Test pack with non-existent model."""
        mock_discovery = Mock()
        mock_discovery.discover.side_effect = ModelNotFoundError("Model not found")
        mock_discovery_cls.return_value = mock_discovery

        runner = CliRunner()
        result = runner.invoke(main, ["pack", "nonexistent/model"])

        assert result.exit_code == 1
        assert "Error" in result.output

    @patch("ezrunner.cli.ModelDiscovery")
    @patch("ezrunner.cli.HardwareAnalyzer")
    @patch("ezrunner.cli.EngineSelector")
    @patch("ezrunner.cli.DockerfileGenerator")
    @patch("ezrunner.cli.ImageBuilder")
    def test_pack_docker_error(
        self,
        mock_builder_cls: Mock,
        mock_generator_cls: Mock,
        mock_selector_cls: Mock,
        mock_analyzer_cls: Mock,
        mock_discovery_cls: Mock,
    ) -> None:
        """Test pack with Docker error."""
        # Setup successful mocks until builder
        mock_model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        mock_hardware = Hardware(
            gpu_memory_gb=24.0,
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )

        mock_discovery = Mock()
        mock_discovery.discover.return_value = mock_model
        mock_discovery_cls.return_value = mock_discovery

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_hardware
        mock_analyzer_cls.return_value = mock_analyzer

        mock_selector = Mock()
        mock_selector.select.return_value = Engine.TRANSFORMERS
        mock_selector_cls.return_value = mock_selector

        mock_generator = Mock()
        mock_generator.generate.return_value = "FROM ubuntu"
        mock_generator_cls.return_value = mock_generator

        # Builder fails
        mock_builder = Mock()
        mock_builder.build.side_effect = DockerError("Build failed")
        mock_builder_cls.return_value = mock_builder

        runner = CliRunner()
        result = runner.invoke(main, ["pack", "qwen/Qwen-7B"])

        assert result.exit_code == 1
        assert "Docker Error" in result.output

    @patch("ezrunner.cli.TarExporter")
    @patch("ezrunner.cli.ImageBuilder")
    @patch("ezrunner.cli.DockerfileGenerator")
    @patch("ezrunner.cli.EngineSelector")
    @patch("ezrunner.cli.HardwareAnalyzer")
    @patch("ezrunner.cli.ModelDiscovery")
    def test_pack_with_engine_option(
        self,
        mock_discovery_cls: Mock,
        mock_analyzer_cls: Mock,
        mock_selector_cls: Mock,
        mock_generator_cls: Mock,
        mock_builder_cls: Mock,
        mock_exporter_cls: Mock,
        tmp_path: Path,
    ) -> None:
        """Test pack with explicit engine selection."""
        # Setup mocks
        mock_model = ModelInfo(
            model_id="qwen/Qwen-7B",
            size_gb=14.2,
            format="safetensors",
            repo_type="modelscope",
            architecture="qwen2",
        )
        mock_hardware = Hardware(
            gpu_memory_gb=24.0,
            gpu_count=1,
            cpu_cores=16,
            ram_gb=64.0,
            gpu_vendor="nvidia",
        )
        mock_image = Mock()
        mock_image.tags = ["test:latest"]

        mock_discovery = Mock()
        mock_discovery.discover.return_value = mock_model
        mock_discovery_cls.return_value = mock_discovery

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_hardware
        mock_analyzer_cls.return_value = mock_analyzer

        mock_selector = Mock()
        mock_selector.select.return_value = Engine.VLLM
        mock_selector_cls.return_value = mock_selector

        mock_generator = Mock()
        mock_generator.generate.return_value = "FROM ubuntu"
        mock_generator_cls.return_value = mock_generator

        mock_builder = Mock()
        mock_builder.build.return_value = mock_image
        mock_builder_cls.return_value = mock_builder

        mock_exporter = Mock()
        mock_exporter_cls.return_value = mock_exporter

        # Run with explicit engine
        runner = CliRunner()
        output_path = tmp_path / "test.tar"
        output_path.write_bytes(b"test")

        result = runner.invoke(
            main, ["pack", "qwen/Qwen-7B", "-o", str(output_path), "--engine", "vllm"]
        )

        assert result.exit_code == 0

        # Verify engine was passed
        call_args = mock_selector.select.call_args
        assert call_args.kwargs["force_engine"] == Engine.VLLM


class TestRunCommand:
    """Test run command."""

    @patch("ezrunner.cli.docker")
    def test_run_success(self, mock_docker: Mock, tmp_path: Path) -> None:
        """Test successful run command."""
        # Create a fake tar file
        tar_path = tmp_path / "test.tar"
        tar_path.write_bytes(b"fake tar content")

        # Mock Docker client
        mock_client = Mock()
        mock_docker.from_env.return_value = mock_client

        # Mock loaded image
        mock_image = Mock()
        mock_image.tags = ["ezrunner-test:latest"]
        mock_client.images.load.return_value = [mock_image]

        # Mock container
        mock_container = Mock()
        mock_container.short_id = "abc123"
        mock_client.containers.run.return_value = mock_container

        # Run command
        runner = CliRunner()
        result = runner.invoke(main, ["run", str(tar_path)])

        assert result.exit_code == 0
        assert "Container started" in result.output
        assert "abc123" in result.output

        mock_client.images.load.assert_called_once()
        mock_client.containers.run.assert_called_once()

    @patch("ezrunner.cli.docker")
    def test_run_no_images(self, mock_docker: Mock, tmp_path: Path) -> None:
        """Test run with tar containing no images."""
        # Create a fake tar file
        tar_path = tmp_path / "test.tar"
        tar_path.write_bytes(b"fake tar content")

        # Mock Docker client
        mock_client = Mock()
        mock_docker.from_env.return_value = mock_client

        # No images loaded
        mock_client.images.load.return_value = []

        # Run command
        runner = CliRunner()
        result = runner.invoke(main, ["run", str(tar_path)])

        assert result.exit_code == 1
        assert "No images found" in result.output

    def test_run_file_not_exists(self) -> None:
        """Test run with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["run", "/nonexistent/file.tar"])

        assert result.exit_code == 2  # Click exits with 2 for invalid args
        assert "does not exist" in result.output.lower()
