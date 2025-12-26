"""Dockerfile generation module."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ezrunner.models.engine import Engine
from ezrunner.models.model_info import ModelInfo


class DockerfileGenerator:
    """Generate Dockerfile from template."""

    def __init__(self) -> None:
        """Initialize generator."""
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate(
        self, model: ModelInfo, engine: Engine, port: int = 8080
    ) -> str:
        """Generate Dockerfile content.

        Args:
            model: Model information
            engine: Selected inference engine
            port: API port

        Returns:
            Dockerfile content
        """
        template_name = f"{engine.value}.dockerfile"
        template = self.env.get_template(template_name)

        # Extract model name from model_id
        model_name = model.model_id.replace("/", "-").lower()

        return template.render(
            model_id=model.model_id, model_name=model_name, port=port
        )
