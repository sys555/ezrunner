"""Hardware analysis module."""

from ezrunner.models.hardware import Hardware


class HardwareAnalyzer:
    """Analyze target hardware specifications."""

    def analyze(
        self,
        gpu_memory_gb: float = 0.0,
        gpu_count: int = 0,
        cpu_cores: int = 8,
        ram_gb: float = 16.0,
        gpu_vendor: str = "none",
    ) -> Hardware:
        """Analyze hardware specifications.

        Args:
            gpu_memory_gb: GPU memory in GB (per GPU)
            gpu_count: Number of GPUs
            cpu_cores: Number of CPU cores
            ram_gb: System RAM in GB
            gpu_vendor: GPU vendor ("nvidia", "amd", or "none")

        Returns:
            Hardware object
        """
        # Auto-detect GPU vendor if not specified
        if gpu_memory_gb > 0 and gpu_vendor == "none":
            gpu_vendor = "nvidia"  # Default to nvidia if GPU is present

        # Ensure gpu_count is correct
        if gpu_memory_gb > 0 and gpu_count == 0:
            gpu_count = 1

        return Hardware(
            gpu_memory_gb=gpu_memory_gb,
            gpu_count=gpu_count,
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            gpu_vendor=gpu_vendor,
        )
