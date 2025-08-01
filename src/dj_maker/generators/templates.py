"""
HTML Template Generator for DJ Maker CLI
"""

from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader


class TemplateGenerator:
    """Generate HTML templates for Django views using Jinja2 templates"""

    def __init__(self, app_name: str, model_name: str):
        self.app_name = app_name
        self.model_name = model_name
        self.model_name_lower = model_name.lower()
        self.template_dir = Path(app_name) / "templates" / app_name

        # Setup Jinja2 environment
        template_dir: Path = Path(__file__).parent.parent / "templates"
        self.jinja_env: Environment = Environment(
            loader=FileSystemLoader(str(template_dir))
        )

    def preview(self) -> List[str]:
        """Preview what templates would be generated without creating them"""
        template_files = []
        templates = {
            f"{self.model_name_lower}_list.html": "html/list.html.j2",
            f"{self.model_name_lower}_detail.html": "html/detail.html.j2",
            f"{self.model_name_lower}_form.html": "html/form.html.j2",
            f"{self.model_name_lower}_confirm_delete.html": "html/confirm_delete.html.j2",
            "base.html": "html/base.html.j2"
        }

        for template_name in templates.keys():
            template_path = self.template_dir / template_name
            # Skip base.html if it already exists
            if template_name == "base.html" and template_path.exists():
                continue
            template_files.append(str(template_path))

        return template_files

    def generate(self) -> List[Path]:
        """Generate all HTML templates using Jinja2"""
        created_files = []

        # Ensure template directory exists
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Context for template rendering
        context: Dict[str, Any] = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_name_lower': self.model_name_lower,
        }

        # Generate base template first
        base_template_path = self.template_dir / "base.html"
        if not base_template_path.exists():
            try:
                base_template = self.jinja_env.get_template("html/base.html.j2")
                base_content = base_template.render(**context)
                base_template_path.write_text(base_content, encoding='utf-8')
                created_files.append(base_template_path)
            except Exception as e:
                print(f"Error generating base template: {e}")

        # Generate other templates
        templates = {
            f"{self.model_name_lower}_list.html": "html/list.html.j2",
            f"{self.model_name_lower}_detail.html": "html/detail.html.j2",
            f"{self.model_name_lower}_form.html": "html/form.html.j2",
            f"{self.model_name_lower}_confirm_delete.html": "html/confirm_delete.html.j2"
        }

        for template_name, j2_template in templates.items():
            template_path = self.template_dir / template_name

            try:
                # Load and render Jinja2 template
                template = self.jinja_env.get_template(j2_template)
                content = template.render(**context)

                # Write rendered content
                template_path.write_text(content, encoding='utf-8')
                created_files.append(template_path)
            except Exception as e:
                print(f"Error generating template {template_name}: {e}")

        return created_files
