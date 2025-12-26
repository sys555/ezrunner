"""CLI interface for EZ Runner."""

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ezrunner.core.builder import ImageBuilder
from ezrunner.core.discovery import ModelDiscovery
from ezrunner.core.dockerfile import DockerfileGenerator
from ezrunner.core.engine import EngineSelector
from ezrunner.core.exporter import TarExporter
from ezrunner.core.hardware import HardwareAnalyzer
from ezrunner.exceptions import DockerError, ModelNotFoundError
from ezrunner.models.engine import Engine

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """EZ Runner - Run any LLM, anywhere, offline."""
    pass


@main.command()
@click.argument("model_id")
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=Path("model.tar"),
    help="Output tar file path",
)
@click.option(
    "--engine",
    type=click.Choice(["auto", "transformers", "vllm"]),
    default="auto",
    help="Inference engine",
)
@click.option(
    "--target-gpu",
    type=float,
    default=0.0,
    help="Target GPU memory in GB",
)
@click.option(
    "--port",
    type=int,
    default=8080,
    help="API port",
)
def pack(
    model_id: str,
    output: Path,
    engine: str,
    target_gpu: float,
    port: int,
) -> None:
    """Pack a model into offline-runnable Docker image.

    Example:
        ezrunner pack qwen/Qwen-7B-Chat -o qwen.tar
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: Discover model
            task = progress.add_task("[cyan]Discovering model...", total=None)
            discovery = ModelDiscovery()
            model = discovery.discover(model_id)
            progress.update(
                task,
                description=f"[green]✓[/green] Model: {model.model_id} "
                f"({model.size_gb} GB, {model.format})",
                completed=True,
            )

            # Step 2: Analyze hardware
            task = progress.add_task("[cyan]Analyzing hardware...", total=None)
            analyzer = HardwareAnalyzer()
            hardware = analyzer.analyze(gpu_memory_gb=target_gpu)
            progress.update(
                task,
                description=f"[green]✓[/green] Target: {hardware.gpu_memory_gb} GB GPU",
                completed=True,
            )

            # Step 3: Select engine
            task = progress.add_task("[cyan]Selecting engine...", total=None)
            selector = EngineSelector()
            force_engine = None if engine == "auto" else Engine(engine)
            selected_engine = selector.select(model, hardware, force_engine)
            progress.update(
                task,
                description=f"[green]✓[/green] Engine: {selected_engine.value}",
                completed=True,
            )

            # Step 4: Generate Dockerfile
            task = progress.add_task("[cyan]Generating Dockerfile...", total=None)
            generator = DockerfileGenerator()
            dockerfile = generator.generate(model, selected_engine, port)
            progress.update(
                task, description="[green]✓[/green] Dockerfile generated", completed=True
            )

            # Step 5: Build image
            task = progress.add_task("[cyan]Building Docker image...", total=None)
            builder = ImageBuilder()
            image_tag = f"ezrunner-{model_id.replace('/', '-').lower()}"
            image = builder.build(dockerfile, image_tag)
            progress.update(
                task,
                description=f"[green]✓[/green] Image built: {image_tag}",
                completed=True,
            )

            # Step 6: Export image
            task = progress.add_task("[cyan]Exporting image...", total=None)
            exporter = TarExporter()
            exporter.export(image, output)
            size_mb = output.stat().st_size / (1024 * 1024)
            progress.update(
                task,
                description=f"[green]✓[/green] Exported: {output} ({size_mb:.1f} MB)",
                completed=True,
            )

        console.print("\n[bold green]✅ Success![/bold green]")
        console.print(f"\nTo run on offline machine:")
        console.print(f"  ezrunner run {output}")

    except ModelNotFoundError as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        raise click.Abort()
    except DockerError as e:
        console.print(f"[red]❌ Docker Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]❌ Unexpected Error:[/red] {e}")
        raise


@main.command()
@click.argument("tar_path", type=click.Path(exists=True, path_type=Path))
@click.option("--port", type=int, default=8080, help="API port")
def run(tar_path: Path, port: int) -> None:
    """Run a packed model.

    Example:
        ezrunner run model.tar
    """
    import docker

    try:
        console.print(f"[cyan]Loading image from {tar_path}...[/cyan]")
        client = docker.from_env()

        # Load image
        with open(tar_path, "rb") as f:
            images = client.images.load(f.read())

        if not images:
            console.print("[red]❌ No images found in tar file[/red]")
            raise click.Abort()

        image = images[0]
        console.print(f"[green]✓ Image loaded: {image.tags[0]}[/green]")

        # Run container
        console.print(f"\n[cyan]Starting container on port {port}...[/cyan]")
        container = client.containers.run(
            image.tags[0],
            detach=True,
            ports={f"{port}/tcp": port},
            remove=True,
        )

        console.print(f"[bold green]✅ Container started![/bold green]")
        console.print(f"\nAPI: http://localhost:{port}")
        console.print(f"Container ID: {container.short_id}")

    except docker.errors.DockerException as e:
        console.print(f"[red]❌ Docker Error:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
