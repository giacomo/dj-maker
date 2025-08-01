"""
View Generator with comprehensive type annotations
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Literal
from jinja2 import Environment, FileSystemLoader
import inspect
from django.apps import apps


ViewTypeOptions = Literal["function", "class", "api"]


class ViewGenerator:
    """Generate Django views with proper type annotations"""

    def __init__(
        self,
        app_name: str,
        model_name: str,
        view_type: ViewTypeOptions
    ) -> None:
        self.app_name: str = app_name
        self.model_name: str = model_name
        self.view_type: ViewTypeOptions = view_type
        self.app_path: Path = Path(app_name)

        # Setup Jinja2 environment
        template_dir: Path = Path(__file__).parent.parent / "templates"
        self.jinja_env: Environment = Environment(
            loader=FileSystemLoader(str(template_dir))
        )

    def get_model_fields(self) -> List[Dict[str, Any]]:
        """Get model fields with type information"""
        try:
            app_config = apps.get_app_config(self.app_name)
            model = app_config.get_model(self.model_name)

            fields: List[Dict[str, Any]] = []
            for field in model._meta.get_fields():
                if not field.many_to_many and not field.one_to_many:
                    fields.append({
                        'name': field.name,
                        'type': field.__class__.__name__,
                        'required': not field.null if hasattr(field, 'null') else True,
                    })
            return fields
        except Exception:
            # Return default fields if model not found
            return [
                {'name': 'id', 'type': 'AutoField', 'required': True},
                {'name': 'created_at', 'type': 'DateTimeField', 'required': False},
            ]

    def generate_function_views(self) -> str:
        """Generate function-based views"""
        template = self.jinja_env.get_template("views/function_based.py.j2")

        context: Dict[str, Any] = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_name_lower': self.model_name.lower(),
            'fields': self.get_model_fields(),
        }

        return template.render(**context)

    def generate_class_views(self) -> str:
        """Generate class-based views"""
        template = self.jinja_env.get_template("views/class_based.py.j2")

        context: Dict[str, Any] = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_name_lower': self.model_name.lower(),
            'fields': self.get_model_fields(),
        }

        return template.render(**context)

    def generate_api_views(self) -> str:
        """Generate API views"""
        template = self.jinja_env.get_template("views/api_views.py.j2")

        context: Dict[str, Any] = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'model_name_lower': self.model_name.lower(),
            'fields': self.get_model_fields(),
        }

        return template.render(**context)

    def preview(self) -> List[str]:
        """Preview files that would be generated"""
        files: List[str] = []

        if self.view_type == "function":
            files.append(f"{self.app_name}/views.py")
        elif self.view_type == "class":
            files.append(f"{self.app_name}/views.py")
        elif self.view_type == "api":
            files.append(f"{self.app_name}/api_views.py")
            files.append(f"{self.app_name}/serializers.py")

        return files

    def generate(self) -> List[Path]:
        """Generate view files"""
        created_files: List[Path] = []

        # Ensure app directory exists
        self.app_path.mkdir(exist_ok=True)

        if self.view_type == "function":
            content: str = self.generate_function_views()
            file_path: Path = self.app_path / "views.py"
            file_path.write_text(content, encoding='utf-8')
            created_files.append(file_path)

        elif self.view_type == "class":
            content = self.generate_class_views()
            file_path = self.app_path / "views.py"
            file_path.write_text(content, encoding='utf-8')
            created_files.append(file_path)

        elif self.view_type == "api":
            content = self.generate_api_views()
            file_path = self.app_path / "api_views.py"
            file_path.write_text(content, encoding='utf-8')
            created_files.append(file_path)

            # Also generate serializers
            serializer_content: str = self.generate_serializers()
            serializer_path: Path = self.app_path / "serializers.py"
            serializer_path.write_text(serializer_content, encoding='utf-8')
            created_files.append(serializer_path)

        return created_files

    def generate_serializers(self) -> str:
        """Generate DRF serializers"""
        template = self.jinja_env.get_template("serializers/model_serializer.py.j2")

        context: Dict[str, Any] = {
            'app_name': self.app_name,
            'model_name': self.model_name,
            'fields': self.get_model_fields(),
        }

        return template.render(**context)
