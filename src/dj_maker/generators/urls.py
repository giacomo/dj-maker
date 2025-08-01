"""
URL Generator with comprehensive type annotations
"""

from pathlib import Path
from typing import List, Optional, Literal
from jinja2 import Environment, FileSystemLoader


URLTypeOptions = Literal["standard", "api", "advanced"]


class URLGenerator:
    """Generate Django URLs with proper type annotations"""

    def __init__(
        self,
        app_name: str,
        model_name: Optional[str],
        view_type: str,
        namespace: Optional[str] = None
    ) -> None:
        self.app_name: str = app_name
        self.model_name: Optional[str] = model_name
        self.view_type: str = view_type
        self.namespace: Optional[str] = namespace
        self.app_path: Path = Path(app_name)

        # Setup Jinja2 environment
        template_dir: Path = Path(__file__).parent.parent / "templates"
        self.jinja_env: Environment = Environment(
            loader=FileSystemLoader(str(template_dir))
        )

    def generate_basic_urls(self) -> str:
        """Generate basic URL patterns"""
        app_name = self.namespace if self.namespace else self.app_name

        if not self.model_name:
            return f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
    # path('<int:pk>/', views.detail, name='detail'),
    # path('create/', views.create, name='create'),
    # path('<int:pk>/edit/', views.edit, name='edit'),
    # path('<int:pk>/delete/', views.delete, name='delete'),
]
'''

        model_lower: str = self.model_name.lower()

        if self.view_type == "function":
            return f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.{model_lower}_list, name='{model_lower}-list'),
    path('<int:pk>/', views.{model_lower}_detail, name='{model_lower}-detail'),
    path('create/', views.{model_lower}_create, name='{model_lower}-create'),
    path('<int:pk>/edit/', views.{model_lower}_update, name='{model_lower}-update'),
    path('<int:pk>/delete/', views.{model_lower}_delete, name='{model_lower}-delete'),
]
'''
        else:  # class-based views
            return f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.{self.model_name}ListView.as_view(), name='{model_lower}-list'),
    path('<int:pk>/', views.{self.model_name}DetailView.as_view(), name='{model_lower}-detail'),
    path('create/', views.{self.model_name}CreateView.as_view(), name='{model_lower}-create'),
    path('<int:pk>/edit/', views.{self.model_name}UpdateView.as_view(), name='{model_lower}-update'),
    path('<int:pk>/delete/', views.{self.model_name}DeleteView.as_view(), name='{model_lower}-delete'),
]
'''

    def generate_api_urls(self) -> str:
        """Generate API URL patterns"""
        app_name = self.namespace if self.namespace else self.app_name

        if not self.model_name:
            return f'''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = '{app_name}'

# REST API Router
router = DefaultRouter()
# router.register(r'items', views.ItemViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),

    # Custom API views
    # path('api/custom/', views.custom_api_view, name='custom-api'),

    # Regular views
    # path('', views.index, name='index'),
]
'''

        model_lower: str = self.model_name.lower()
        return f'''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = '{app_name}'

router = DefaultRouter()
router.register(r'{model_lower}s', views.{self.model_name}ViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.{self.model_name}ListView.as_view(), name='{model_lower}-list'),
    path('<int:pk>/', views.{self.model_name}DetailView.as_view(), name='{model_lower}-detail'),
    path('create/', views.{self.model_name}CreateView.as_view(), name='{model_lower}-create'),
    path('<int:pk>/update/', views.{self.model_name}UpdateView.as_view(), name='{model_lower}-update'),
    path('<int:pk>/delete/', views.{self.model_name}DeleteView.as_view(), name='{model_lower}-delete'),
]
'''

    def generate_advanced_urls(self) -> str:
        """Generate advanced URL patterns with nested routes"""
        app_name = self.namespace if self.namespace else self.app_name

        if not self.model_name:
            return self.generate_basic_urls()

        model_lower: str = self.model_name.lower()
        return f'''from django.urls import path, include
from . import views

app_name = '{app_name}'

# Detail patterns
detail_patterns = [
    path('', views.{self.model_name}DetailView.as_view(), name='{model_lower}-detail'),
    path('edit/', views.{self.model_name}UpdateView.as_view(), name='{model_lower}-update'),
    path('delete/', views.{self.model_name}DeleteView.as_view(), name='{model_lower}-delete'),
]

urlpatterns = [
    # List and create
    path('', views.{self.model_name}ListView.as_view(), name='{model_lower}-list'),
    path('create/', views.{self.model_name}CreateView.as_view(), name='{model_lower}-create'),

    # Detail URLs
    path('<int:pk>/', include(detail_patterns)),

    # Additional URLs
    path('search/', views.{self.model_name}SearchView.as_view(), name='{model_lower}-search'),
    path('export/', views.{self.model_name}ExportView.as_view(), name='{model_lower}-export'),
]
'''

    def preview(self) -> List[str]:
        """Preview files that would be generated"""
        files: List[str] = [f"{self.app_name}/urls.py"]
        return files

    def generate(self) -> List[Path]:
        """Generate URL files"""
        created_files: List[Path] = []

        # Ensure app directory exists
        self.app_path.mkdir(exist_ok=True)

        # Determine which URL pattern to generate
        if self.view_type == "api":
            content = self.generate_api_urls()
        elif self.view_type == "advanced":
            content = self.generate_advanced_urls()
        else:
            content = self.generate_basic_urls()

        # Write URLs file
        file_path: Path = self.app_path / "urls.py"
        file_path.write_text(content, encoding='utf-8')
        created_files.append(file_path)

        return created_files

    def generate_app_urls(self) -> List[Path]:
        """Generate basic app urls.py (for init-app command)"""
        created_files: List[Path] = []

        # Ensure app directory exists
        self.app_path.mkdir(exist_ok=True)

        content: str = f'''from django.urls import path
from . import views

app_name = '{self.app_name}'

urlpatterns = [
    path('', views.index, name='index'),
    # Add your URL patterns here
]
'''

        urls_file: Path = self.app_path / "urls.py"
        urls_file.write_text(content)
        created_files.append(urls_file)

        return created_files

    def update_main_urls(self, main_urls_path: Path) -> bool:
        """Update main project urls.py to include this app (optional helper)"""
        try:
            if not main_urls_path.exists():
                return False

            content: str = main_urls_path.read_text()

            # Check if app is already included
            if f"'{self.app_name}.urls'" in content:
                return True

            # Find urlpatterns and add new path
            include_line: str = f"    path('{self.app_name}/', include('{self.app_name}.urls')),"

            if "urlpatterns = [" in content:
                # Add to existing urlpatterns
                content = content.replace(
                    "urlpatterns = [",
                    f"urlpatterns = [\n{include_line}"
                )

            # Add import if not present
            if "from django.urls import include" not in content:
                content = content.replace(
                    "from django.urls import path",
                    "from django.urls import path, include"
                )

            main_urls_path.write_text(content)
            return True

        except Exception:
            return False
