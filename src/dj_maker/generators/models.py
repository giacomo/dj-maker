"""
Model Generator for DJ Maker CLI
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader


class ModelGenerator:
    """Generate Django models with common fields and patterns"""

    def __init__(self, app_name: str, model_name: str) -> None:
        self.app_name: str = app_name
        self.model_name: str = model_name
        self.app_path: Path = Path(app_name)

        # Setup Jinja2 environment
        template_dir: Path = Path(__file__).parent.parent / "templates"
        self.jinja_env: Environment = Environment(
            loader=FileSystemLoader(str(template_dir))
        )

    def generate_basic_model(self) -> str:
        """Generate a basic model with common fields"""
        model_lower = self.model_name.lower()

        return f'''from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class {self.model_name}(models.Model):
    """
    {self.model_name} model with common fields.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Optional: Add user relationship
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{model_lower}_created')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '{self.model_name}'
        verbose_name_plural = '{self.model_name}s'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('{self.app_name}:{model_lower}-detail', kwargs={{'pk': self.pk}})
'''

    def update_models_file(self) -> Path:
        """Update or create models.py file"""
        models_file = self.app_path / "models.py"

        if models_file.exists():
            # Read existing content
            content = models_file.read_text()

            # Check if model already exists
            if f"class {self.model_name}(" in content:
                return models_file  # Model already exists

            # Add new model to existing file
            model_code = self.generate_basic_model()

            # Remove the imports if they already exist
            lines_to_add = []
            for line in model_code.split('\n'):
                if line.startswith('from django.db import models'):
                    if 'from django.db import models' not in content:
                        lines_to_add.append(line)
                elif line.startswith('from django.urls import reverse'):
                    if 'from django.urls import reverse' not in content:
                        lines_to_add.append(line)
                elif line.startswith('from django.contrib.auth.models import User'):
                    if 'from django.contrib.auth.models import User' not in content:
                        lines_to_add.append(line)
                elif line.strip() and not line.startswith('from '):
                    lines_to_add.append(line)

            # Append the new model
            updated_content = content.rstrip() + '\n\n\n' + '\n'.join(lines_to_add)
            models_file.write_text(updated_content)
        else:
            # Create new models.py file
            content = self.generate_basic_model()
            models_file.write_text(content)

        return models_file

    def generate_admin_registration(self) -> str:
        """Generate admin.py registration for the model"""
        return f'''from django.contrib import admin
from .models import {self.model_name}


@admin.register({self.model_name})
class {self.model_name}Admin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {{
            'fields': ('title', 'description', 'is_active')
        }}),
        ('Timestamps', {{
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }}),
    )
'''

    def update_admin_file(self) -> Path:
        """Update or create admin.py file"""
        admin_file = self.app_path / "admin.py"

        if admin_file.exists():
            content = admin_file.read_text()

            # Check if admin registration already exists
            if f"{self.model_name}Admin" in content:
                return admin_file

            # Add import if not exists
            if f"from .models import {self.model_name}" not in content:
                if "from .models import" in content:
                    # Add to existing import
                    content = content.replace(
                        "from .models import",
                        f"from .models import {self.model_name},"
                    )
                else:
                    # Add new import
                    if "from django.contrib import admin" in content:
                        content = content.replace(
                            "from django.contrib import admin",
                            f"from django.contrib import admin\nfrom .models import {self.model_name}"
                        )
                    else:
                        content = f"from django.contrib import admin\nfrom .models import {self.model_name}\n\n" + content

            # Add admin class
            admin_class = f'''

@admin.register({self.model_name})
class {self.model_name}Admin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {{
            'fields': ('title', 'description', 'is_active')
        }}),
        ('Timestamps', {{
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }}),
    )
'''

            content += admin_class
            admin_file.write_text(content)
        else:
            # Create new admin.py file
            content = self.generate_admin_registration()
            admin_file.write_text(content)

        return admin_file

    def preview(self) -> List[str]:
        """Preview files that would be created/updated"""
        files = [
            f"{self.app_name}/models.py",
            f"{self.app_name}/admin.py"
        ]
        return files

    def generate(self) -> List[Path]:
        """Generate model and admin files"""
        created_files = []

        # Ensure app directory exists
        self.app_path.mkdir(exist_ok=True)

        # Generate model
        models_file = self.update_models_file()
        created_files.append(models_file)

        # Generate admin registration
        admin_file = self.update_admin_file()
        created_files.append(admin_file)

        return created_files
