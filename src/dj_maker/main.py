#!/usr/bin/env python3
"""
DJ Maker CLI Tool - Modern CRUD and URL Generator with Typer
Basierend auf dem django-urls Generator
"""

import os
import sys
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Annotated

import typer
from rich.console import Console
from rich.table import Table

import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Initialize Rich console for beautiful output
console = Console()
app = typer.Typer(
    name="django-cli",
    help="🚀 Modern DJ Maker CLI tool for automatic views and URLs generation",
    rich_markup_mode="rich",
)


class ViewType(str, Enum):
    """Supported view types for generation"""
    function = "function"
    class_based = "class"
    api = "api"


class URLTemplate(str, Enum):
    """Supported URL templates"""
    basic = "basic"
    api = "api"
    advanced = "advanced"


def setup_django() -> None:
    """Setup Django environment if not already configured"""
    if not settings.configured:
        manage_py: Path = Path.cwd() / "manage.py"
        if manage_py.exists():
            sys.path.insert(0, str(Path.cwd()))

            with open(manage_py) as f:
                content: str = f.read()
                if 'DJANGO_SETTINGS_MODULE' in content:
                    import re
                    match: Optional[re.Match[str]] = re.search(
                        r'DJANGO_SETTINGS_MODULE.*?["\']([^"\']+)["\']', content
                    )
                    if match:
                        os.environ.setdefault('DJANGO_SETTINGS_MODULE', match.group(1))

            django.setup()
        else:
            console.print("❌ [red]Error: manage.py not found. Please run from Django project root.[/red]")
            raise typer.Exit(1)


def is_django_project() -> bool:
    """Check if current directory is a Django project"""
    return Path("manage.py").exists()


def is_django_app(app_path: Path) -> bool:
    """Check if directory is a Django app"""
    return (app_path / "apps.py").exists() or (app_path / "models.py").exists()


def get_apps_list() -> List[str]:
    """Get list of Django apps in the project"""
    if not is_django_project():
        return []

    apps: List[str] = []
    for item in Path(".").iterdir():
        if item.is_dir() and is_django_app(item):
            apps.append(item.name)
    return apps


def version_callback(value: bool) -> None:
    """Print version and exit"""
    if value:
        console.print("DJ Maker CLI version: [bold green]0.1.0[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, help="Show version and exit")
    ] = None,
    ctx: typer.Context = None,
) -> None:
    """
    🚀 DJ Maker CLI - Modern CRUD and URL Generator

    Generate Django views and URLs with best practices and modern patterns.
    """
    # Commands that don't require being in a Django project
    commands_without_django_requirement = {'init', 'help', '--help', '--version'}

    # Check if we're running a command that doesn't require Django project
    if ctx and ctx.invoked_subcommand in commands_without_django_requirement:
        return

    # Also check if no subcommand is invoked (help case)
    if ctx and ctx.invoked_subcommand is None:
        return

    # For other commands, check if we're in a Django project
    if not is_django_project():
        console.print("❌ [red]Error: Not in a Django project directory (manage.py not found)[/red]")
        raise typer.Exit(1)

    try:
        setup_django()
    except Exception:
        # Continue without Django setup for some commands
        pass


# URLs Commands Group
urls_app = typer.Typer(help="🔗 URL management commands")
app.add_typer(urls_app, name="urls")


@urls_app.command("create")
def create_urls(
    app_name: Annotated[str, typer.Argument(help="Django app name")],
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", "-f", help="Overwrite existing urls.py")
    ] = False,
    template: Annotated[
        URLTemplate,
        typer.Option("--template", "-t", help="Template type")
    ] = URLTemplate.basic,
) -> None:
    """🔗 Create urls.py file for a Django app"""

    if not is_django_project():
        console.print("❌ [red]Error: Not in a Django project directory (manage.py not found)[/red]")
        raise typer.Exit(1)

    app_path: Path = Path(app_name)

    if not app_path.exists():
        console.print(f"❌ [red]Error: App directory '{app_name}' does not exist[/red]")
        raise typer.Exit(1)

    if not is_django_app(app_path):
        console.print(f"❌ [red]Error: '{app_name}' is not a Django app (apps.py or models.py not found)[/red]")
        raise typer.Exit(1)

    urls_file: Path = app_path / "urls.py"

    if urls_file.exists() and not overwrite:
        console.print(f"❌ [red]Error: {urls_file} already exists. Use --overwrite to replace it[/red]")
        raise typer.Exit(1)

    # Generate URLs content based on template
    urls_content: str = ""

    if template == URLTemplate.api:
        urls_content = f'''from django.urls import path, include
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
    elif template == URLTemplate.advanced:
        urls_content = f'''from django.urls import path, include
from . import views

app_name = '{app_name}'

# Detail patterns
detail_patterns = [
    path('', views.{app_name}_detail, name='detail'),
    path('edit/', views.{app_name}_edit, name='edit'),
    path('delete/', views.{app_name}_delete, name='delete'),
]

urlpatterns = [
    # List and create
    path('', views.{app_name}_list, name='list'),
    path('create/', views.{app_name}_create, name='create'),

    # Detail URLs
    path('<int:pk>/', include(detail_patterns)),

    # Additional URLs
    # path('search/', views.{app_name}_search, name='search'),
    # path('export/', views.{app_name}_export, name='export'),
]
'''
    else:  # basic template
        urls_content = f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    # Basic URL patterns
    path('', views.index, name='index'),
    # path('<int:pk>/', views.detail, name='detail'),
    # path('create/', views.create, name='create'),
    # path('<int:pk>/edit/', views.edit, name='edit'),
    # path('<int:pk>/delete/', views.delete, name='delete'),
]
'''

    # Write the file
    urls_file.write_text(urls_content)

    action: str = "Overwrote" if urls_file.exists() else "Created"
    console.print(f"✅ [green]{action} {urls_file} with {template.value} template[/green]")

    # Show next steps
    console.print("\n📝 [bold]Next steps:[/bold]")
    console.print("1. Add to your main urls.py:")
    console.print(f"   [cyan]path('{app_name}/', include('{app_name}.urls')),[/cyan]")
    console.print("2. Create the views referenced in the URLs")

    if template == URLTemplate.api:
        console.print("3. Install djangorestframework if not already installed:")
        console.print("   [cyan]uv add djangorestframework[/cyan]")


@urls_app.command("list")
def list_urls() -> None:
    """📋 List all Django apps in the project and their URLs status"""

    if not is_django_project():
        console.print("❌ [red]Error: Not in a Django project directory[/red]")
        raise typer.Exit(1)

    apps_list: List[str] = get_apps_list()

    if not apps_list:
        console.print("No Django apps found in this project")
        return

    # Create table for better visualization
    table = Table(title="📱 Django Apps and URLs Status")
    table.add_column("App Name", style="cyan")
    table.add_column("URLs Status", style="green")
    table.add_column("Action", style="dim")

    missing_urls: List[str] = []

    for app_name in sorted(apps_list):
        urls_file: Path = Path(app_name) / "urls.py"
        if urls_file.exists():
            table.add_row(app_name, "✅ Has urls.py", "")
        else:
            table.add_row(app_name, "❌ No urls.py", f"django-cli urls create {app_name}")
            missing_urls.append(app_name)

    console.print(table)

    if missing_urls:
        console.print(f"\n[yellow]{len(missing_urls)} app(s) missing urls.py[/yellow]")


@urls_app.command("check")
def check_urls(
    app_name: Annotated[str, typer.Argument(help="Django app name to check")]
) -> None:
    """🔍 Check if an app has urls.py and show its content"""

    if not is_django_project():
        console.print("❌ [red]Error: Not in a Django project directory[/red]")
        raise typer.Exit(1)

    app_path: Path = Path(app_name)

    if not app_path.exists():
        console.print(f"❌ [red]Error: App '{app_name}' does not exist[/red]")
        raise typer.Exit(1)

    if not is_django_app(app_path):
        console.print(f"❌ [red]Error: '{app_name}' is not a Django app[/red]")
        raise typer.Exit(1)

    urls_file: Path = app_path / "urls.py"

    if not urls_file.exists():
        console.print(f"❌ [red]{app_name} does not have urls.py[/red]")
        console.print(f"Create it with: [cyan]django-cli urls create {app_name}[/cyan]")
        return

    console.print(f"✅ [green]{app_name} has urls.py[/green]\n")
    console.print("📄 [bold]Content:[/bold]")
    console.print("-" * 40)

    try:
        content: str = urls_file.read_text()
        console.print(content)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")


@urls_app.command("templates")
def show_templates() -> None:
    """📋 Show available URL templates"""

    table = Table(title="📋 Available URL Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Use Case", style="dim")

    templates_info: Dict[str, Dict[str, str]] = {
        "basic": {
            "description": "Simple URL patterns with common CRUD operations",
            "use_case": "Standard web apps"
        },
        "api": {
            "description": "REST API patterns with DRF router support",
            "use_case": "API-first applications"
        },
        "advanced": {
            "description": "Advanced patterns with nested URLs and detail views",
            "use_case": "Complex web applications"
        }
    }

    for template, info in templates_info.items():
        table.add_row(template, info["description"], info["use_case"])

    console.print(table)
    console.print("\n[dim]Usage: django-cli urls create myapp --template basic[/dim]")


# Original Generate Command (erweitert)
@app.command(rich_help_panel="Generation Commands")
def generate(
    app_name: Annotated[str, typer.Argument(help="Name of the Django app")],
    model_name: Annotated[str, typer.Argument(help="Name of the model to generate CRUD for")],
    view_type: Annotated[
        ViewType,
        typer.Option("--view-type", "-t", help="Type of views to generate")
    ] = ViewType.class_based,
    url_template: Annotated[
        URLTemplate,
        typer.Option("--url-template", help="URL template to use")
    ] = URLTemplate.basic,
    include_api: Annotated[
        bool,
        typer.Option("--include-api", "-a", help="Generate API views alongside regular views")
    ] = False,
    no_templates: Annotated[
        bool,
        typer.Option("--no-templates", help="Skip HTML template generation")
    ] = False,
    namespace: Annotated[
        Optional[str],
        typer.Option("--namespace", "-n", help="URL namespace for the app")
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-d", help="Show what would be generated without creating files")
    ] = False,
) -> None:
    """
    🔧 Generate CRUD views and URLs for a Django model.

    Combines view generation with automatic URL creation.

    Examples:
        [dim]django-cli generate blog Post[/dim]
        [dim]django-cli generate shop Product --view-type=api --url-template=api[/dim]
        [dim]django-cli generate users User --include-api --namespace=accounts[/dim]
        [dim]django-cli generate api-only ApiModel --view-type=api --no-templates[/dim]
    """
    from dj_maker.generators.views import ViewGenerator
    from dj_maker.generators.urls import URLGenerator
    from dj_maker.generators.templates import TemplateGenerator
    from dj_maker.generators.models import ModelGenerator

    console.print(f"🔧 Generating CRUD for [bold green]{model_name}[/bold green] in [bold blue]{app_name}[/bold blue] app...")

    try:
        # Generate model first
        model_gen: ModelGenerator = ModelGenerator(app_name, model_name)

        # Generate views
        view_gen: ViewGenerator = ViewGenerator(app_name, model_name, view_type.value)
        urls_gen: URLGenerator = URLGenerator(app_name, model_name, view_type.value, namespace)

        # Only create template generator if templates are needed
        template_gen = None if no_templates else TemplateGenerator(app_name, model_name)

        if dry_run:
            console.print("\n[yellow]--- DRY RUN MODE ---[/yellow]")

            # Create preview table
            table = Table(title="Files that would be generated")
            table.add_column("Type", style="cyan")
            table.add_column("File Path", style="green")
            table.add_column("Description", style="dim")

            # Add model files to preview
            model_files: List[str] = model_gen.preview()
            for file_path in model_files:
                table.add_row("Models", file_path, "Django model and admin")

            view_files: List[str] = view_gen.preview()
            url_files: List[str] = urls_gen.preview()

            for file_path in view_files:
                table.add_row("Views", file_path, f"{view_type.value} based views")

            for file_path in url_files:
                table.add_row("URLs", file_path, f"{url_template.value} URL patterns")

            # Only show templates if not skipped
            if not no_templates:
                template_files: List[str] = template_gen.preview()
                for file_path in template_files:
                    table.add_row("Templates", file_path, "Django templates")
            else:
                table.add_row("Templates", "[dim]Skipped[/dim]", "HTML templates disabled")

            if include_api:
                api_gen: ViewGenerator = ViewGenerator(app_name, model_name, 'api')
                api_files: List[str] = api_gen.preview()
                for file_path in api_files:
                    table.add_row("API", file_path, "REST API views")

            console.print(table)
            return

        # Create the files
        # 1. Generate model first
        model_files: List[Path] = model_gen.generate()
        console.print(f"   📊 Generated model and admin for {model_name}")

        # 2. Generate views
        views_created: List[Path] = view_gen.generate()

        # 3. Generate URLs
        urls_created: List[Path] = urls_gen.generate()

        # 4. Generate HTML templates only if not disabled
        template_files: List[Path] = []
        if not no_templates:
            template_files = template_gen.generate()

        console.print("✅ [bold green]Successfully generated:[/bold green]")

        for file_path in model_files + views_created + urls_created + template_files:
            console.print(f"   📁 {file_path}")

        if include_api:
            api_gen: ViewGenerator = ViewGenerator(app_name, model_name, 'api')
            api_files: List[Path] = api_gen.generate()
            console.print(f"   🔗 API views: [bold]{len(api_files)}[/bold] files")

        if no_templates:
            console.print("   🚫 [dim]HTML templates skipped[/dim]")

        # Show next steps
        console.print("\n📝 [bold]Next steps:[/bold]")
        console.print(f"1. Add '{app_name}' to INSTALLED_APPS in settings.py")

        if namespace:
            # Show versioned/namespaced URL structure
            console.print("2. Add to your main urls.py with namespace:")
            console.print(f"   [cyan]path('{namespace}/{app_name}/', include('{app_name}.urls')),[/cyan]")
            console.print(f"   [dim]This creates URLs like: {namespace}/{app_name}/{model_name.lower()}-list[/dim]")
        else:
            console.print("2. Add to your main urls.py:")
            console.print(f"   [cyan]path('{app_name}/', include('{app_name}.urls')),[/cyan]")

        console.print(f"3. Run migrations: [cyan]python manage.py makemigrations {app_name} && python manage.py migrate[/cyan]")

        if namespace:
            console.print("\n💡 [bold]URL Examples:[/bold]")
            console.print(f"   • List: [cyan]/{namespace}/{app_name}/[/cyan] → [dim]{namespace}:{model_name.lower()}-list[/dim]")
            console.print(f"   • Detail: [cyan]/{namespace}/{app_name}/1/[/cyan] → [dim]{namespace}:{model_name.lower()}-detail[/dim]")
            console.print(f"   • Create: [cyan]/{namespace}/{app_name}/create/[/cyan] → [dim]{namespace}:{model_name.lower()}-create[/dim]")

    except Exception as e:
        console.print(f"❌ [red]Error generating files: {e}[/red]")
        raise typer.Exit(1)


@app.command(rich_help_panel="Project Management")
def init(
    project_name: Annotated[str, typer.Argument(help="Name of the Django project to create")],
    template: Annotated[
        Optional[str],
        typer.Option("--template", help="Django project template to use")
    ] = None,
    database: Annotated[
        str,
        typer.Option("--database", help="Database backend to configure")
    ] = "sqlite3",
) -> None:
    """
    🚀 Create a new Django project with uv and best practices.

    Creates a new Django project using uv for dependency management.
    """
    try:
        console.print(f"🚀 Creating Django project: [bold blue]{project_name}[/bold blue]")

        # Create project directory
        current_dir = Path.cwd()
        project_path = current_dir / project_name

        if project_path.exists():
            console.print(f"❌ [red]Directory {project_name} already exists[/red]")
            raise typer.Exit(1)

        project_path.mkdir()
        console.print(f"📁 Created directory: [blue]{project_name}[/blue]")

        # Change to project directory
        os.chdir(project_path)
        console.print(f"📂 Changed to directory: [blue]{project_path}[/blue]")

        # Initialize uv project
        console.print("🔧 Initializing uv project...")
        result = subprocess.run(['uv', 'init'], capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"❌ [red]Error initializing uv: {result.stderr}[/red]")
            raise typer.Exit(1)

        # Add Django with uv
        console.print("📦 Adding Django...")
        django_deps = ['django']

        # Add database-specific dependencies
        if database == 'postgresql':
            django_deps.append('psycopg2-binary')
            console.print("📦 Adding PostgreSQL support...")
        elif database == 'mysql':
            django_deps.append('mysqlclient')
            console.print("📦 Adding MySQL support...")
        elif database == 'oracle':
            django_deps.append('cx_Oracle')
            console.print("📦 Adding Oracle support...")
        # sqlite3 is built into Python, no extra dependency needed

        result = subprocess.run(['uv', 'add'] + django_deps, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"❌ [red]Error adding Django dependencies: {result.stderr}[/red]")
            raise typer.Exit(1)

        # Create Django project in current directory
        console.print("🏗️ Creating Django project structure...")
        cmd = ['uv', 'run', 'django-admin', 'startproject', 'config', '.']
        if template:
            cmd.extend(['--template', template])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"❌ [red]Error creating Django project: {result.stderr}[/red]")
            raise typer.Exit(1)

        # Create additional directories
        console.print("📁 Creating additional directories...")
        Path("static").mkdir(exist_ok=True)
        Path("media").mkdir(exist_ok=True)
        Path("templates").mkdir(exist_ok=True)

        # Create .env.example
        console.print("🔒 Creating .env.example...")

        # Database configuration based on selected database
        db_config = ""
        if database == 'postgresql':
            db_config = f"""
# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/{project_name}
# Or use individual settings:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME={project_name}
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432"""
        elif database == 'mysql':
            db_config = f"""
# MySQL Database
DATABASE_URL=mysql://user:password@localhost:3306/{project_name}
# Or use individual settings:
# DB_ENGINE=django.db.backends.mysql
# DB_NAME={project_name}
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=3306"""
        elif database == 'oracle':
            db_config = f"""
# Oracle Database
# DB_ENGINE=django.db.backends.oracle
# DB_NAME=your_oracle_service
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=1521"""
        else:  # sqlite3
            db_config = f"""
# SQLite Database (default)
# DATABASE_URL=sqlite:///./db.sqlite3
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3"""

        env_example = f"""# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
{db_config}

# Static/Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
"""
        Path(".env.example").write_text(env_example, encoding='utf-8')

        # Create .gitignore
        console.print("🚫 Creating .gitignore...")
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
.Python
.venv/
env/
venv/

# Django
*.log
db.sqlite3
media/
staticfiles/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        Path(".gitignore").write_text(gitignore_content, encoding='utf-8')

        console.print("✅ [bold green]Successfully created Django project![/bold green]")
        console.print(f"\n📁 [bold]Project created in:[/bold] {project_path.absolute()}")
        console.print("\n📝 [bold]Next steps:[/bold]")
        console.print(f"1. [cyan]cd {project_name}[/cyan]")
        console.print("2. [cyan]uv run python manage.py migrate[/cyan]")
        console.print("3. [cyan]uv run python manage.py createsuperuser[/cyan]")
        console.print("4. [cyan]uv run python manage.py runserver[/cyan]")
        console.print("\n💡 [dim]Use 'uv add package-name' to add more dependencies[/dim]")

    except KeyboardInterrupt:
        console.print("\n❌ [red]Operation cancelled by user[/red]")
        raise typer.Exit(1)
    except Exception as e:
            console.print(f"❌ [red]Error creating project: {e}[/red]")
            raise typer.Exit(1)


@app.command(rich_help_panel="App Management")
def init_app(
    app_name: Annotated[str, typer.Argument(help="Name of the Django app to create")],
    include_urls: Annotated[
        bool,
        typer.Option("--include-urls/--no-include-urls", "-u", help="Also generate urls.py")
    ] = True,
    url_template: Annotated[
        URLTemplate,
        typer.Option("--url-template", help="URL template to use")
    ] = URLTemplate.basic,
    include_tests: Annotated[
        bool,
        typer.Option("--include-tests/--no-include-tests", help="Generate test files")
    ] = True,
) -> None:
    """
    🆕 Initialize a new Django app with standard structure.

    Creates the app and optionally adds urls.py and test files.
    """
    try:
        console.print(f"🆕 Creating Django app: [bold blue]{app_name}[/bold blue]")

        # Use Django's startapp command
        execute_from_command_line(['manage.py', 'startapp', app_name])

        if include_urls:
            # Use the integrated URL creation
            create_urls(app_name, overwrite=True, template=url_template)

        if include_tests:
            # Generate additional test files
            test_dir: Path = Path(app_name) / "tests"
            test_dir.mkdir(exist_ok=True)

            (test_dir / "__init__.py").touch()
            (test_dir / "test_models.py").write_text(
                f'"""Tests for {app_name} models"""\n\nfrom django.test import TestCase\n\n# Add your model tests here\n'
            )
            (test_dir / "test_views.py").write_text(
                f'"""Tests for {app_name} views"""\n\nfrom django.test import TestCase\n\n# Add your view tests here\n'
            )
            console.print("   🧪 Generated test files")

        console.print(f"✅ [bold green]Successfully created app {app_name}[/bold green]")

    except Exception as e:
        console.print(f"❌ [red]Error creating app: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-models", rich_help_panel="Utility Commands")
def list_models(
    app_name: Annotated[Optional[str], typer.Argument(help="App name to list models for")] = None,
) -> None:
    """
    📋 List all models in the project or specific app.
    """

    if not is_django_project():
        console.print("❌ [red]Error: Not in a Django project directory[/red]")
        raise typer.Exit(1)

    # Get apps using the same method as urls list (filesystem-based)
    if app_name:
        # Check if specific app exists
        app_path = Path(app_name)
        if not app_path.exists():
            console.print(f"❌ [red]Error: App '{app_name}' does not exist[/red]")
            return
        if not is_django_app(app_path):
            console.print(f"❌ [red]Error: '{app_name}' is not a Django app[/red]")
            return
        apps_to_check = [app_name]
    else:
        # Get all apps using the working filesystem method
        apps_to_check = get_apps_list()

    if not apps_to_check:
        console.print("No Django apps found in this project")
        return

    table = Table(title="📱 Django Apps and Models")
    table.add_column("App", style="cyan")
    table.add_column("Models File", style="green")
    table.add_column("Status", style="dim")

    for app in sorted(apps_to_check):
        app_path = Path(app)
        models_file = app_path / "models.py"

        if models_file.exists():
            try:
                # Read models.py and look for class definitions
                content = models_file.read_text(encoding='utf-8')

                # Simple regex to find model classes
                import re
                model_matches = re.findall(r'class\s+(\w+)\s*\([^)]*Model[^)]*\)', content)

                if model_matches:
                    models_info = ", ".join(model_matches[:3])
                    if len(model_matches) > 3:
                        models_info += f" (+{len(model_matches) - 3} more)"
                    table.add_row(app, "✅ Has models.py", f"{len(model_matches)} models: {models_info}")
                else:
                    table.add_row(app, "✅ Has models.py", "No Model classes found")

            except Exception as e:
                table.add_row(app, "❌ Error reading", f"Error: {str(e)}")
        else:
            table.add_row(app, "❌ No models.py", "Create models.py file")

    console.print(table)
    console.print(f"\n[dim]💡 Tip: Use 'uv run django-cli generate {apps_to_check[0] if apps_to_check else 'myapp'} MyModel' to generate CRUD for a model[/dim]")
