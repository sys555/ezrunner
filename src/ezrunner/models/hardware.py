"""Hardware specifications."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hardware:
    """Hardware specifications.

    Attributes:
        gpu_memory_gb: GPU memory in GB
        gpu_count: Number of GPUs
        cpu_cores: Number of CPU cores
        ram_gb: System RAM in GB
        gpu_vendor: GPU vendor ("nvidia", "amd", or "none")
    """

    gpu_memory_gb: float
    gpu_count: int
    cpu_cores: int
    ram_gb: float
    gpu_vendor: str

    def __post_init__(self) -> None:
        """Validate hardware specs."""
        if self.gpu_memory_gb < 0:
            raise ValueError(f"Invalid GPU memory: {self.gpu_memory_gb}")
        if self.gpu_count < 0:
            raise ValueError(f"Invalid GPU count: {self.gpu_count}")
        if self.cpu_cores <= 0:
            raise ValueError(f"Invalid CPU cores: {self.cpu_cores}")
        if self.ram_gb <= 0:
            raise ValueError(f"Invalid RAM: {self.ram_gb}")
        if self.gpu_vendor not in ("nvidia", "amd", "none"):
            raise ValueError(f"Unsupported GPU vendor: {self.gpu_vendor}")

    @property
    def has_gpu(self) -> bool:
        """Check if GPU is available."""
        return self.gpu_vendor != "none" and self.gpu_count > 0
