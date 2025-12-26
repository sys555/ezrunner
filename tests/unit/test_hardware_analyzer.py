"""Tests for HardwareAnalyzer."""

from ezrunner.core.hardware import HardwareAnalyzer
from ezrunner.models.hardware import Hardware


class TestHardwareAnalyzer:
    """Test HardwareAnalyzer."""

    def test_analyze_with_gpu(self) -> None:
        """Test analyzing hardware with GPU."""
        analyzer = HardwareAnalyzer()
        hardware = analyzer.analyze(
            gpu_memory_gb=24.0, gpu_count=1, cpu_cores=16, ram_gb=64.0
        )

        assert hardware.gpu_memory_gb == 24.0
        assert hardware.gpu_count == 1
        assert hardware.gpu_vendor == "nvidia"  # Auto-detected
        assert hardware.has_gpu is True

    def test_analyze_without_gpu(self) -> None:
        """Test analyzing CPU-only hardware."""
        analyzer = HardwareAnalyzer()
        hardware = analyzer.analyze(cpu_cores=8, ram_gb=16.0)

        assert hardware.gpu_memory_gb == 0.0
        assert hardware.gpu_count == 0
        assert hardware.gpu_vendor == "none"
        assert hardware.has_gpu is False

    def test_analyze_auto_gpu_count(self) -> None:
        """Test auto-setting gpu_count when GPU memory specified."""
        analyzer = HardwareAnalyzer()
        hardware = analyzer.analyze(gpu_memory_gb=16.0)

        assert hardware.gpu_count == 1  # Auto-set to 1

    def test_analyze_explicit_gpu_vendor(self) -> None:
        """Test explicitly setting GPU vendor."""
        analyzer = HardwareAnalyzer()
        hardware = analyzer.analyze(
            gpu_memory_gb=16.0, gpu_vendor="amd"
        )

        assert hardware.gpu_vendor == "amd"
