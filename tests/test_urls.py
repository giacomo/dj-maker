"""
Tests for URL management commands of the django-cli tool.
"""
from pathlib import Path
from typer.testing import CliRunner

from dj_maker.main import app

runner = CliRunner()


def test_urls_create_command():
    """Test the urls create command."""
    with runner.isolated_filesystem():
        # Create a simple Django project structure
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Create URLs file with basic template
        result = runner.invoke(app, ["urls", "create", "test_app"])
        assert result.exit_code == 0
        assert "Created" in result.output or "Overwrote" in result.output

        # Check that file exists
        urls_file = Path("test_app/urls.py")
        assert urls_file.exists()
        content = urls_file.read_text()
        assert "app_name = 'test_app'" in content
        assert "urlpatterns = [" in content

        # Try to create again without overwrite flag
        result = runner.invoke(app, ["urls", "create", "test_app"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_urls_create_with_templates():
    """Test urls create command with different templates."""
    with runner.isolated_filesystem():
        # Setup Django project
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Test API template
        result = runner.invoke(app, ["urls", "create", "test_app", "--template", "api"])
        assert result.exit_code == 0
        content = Path("test_app/urls.py").read_text()
        assert "from rest_framework.routers import DefaultRouter" in content

        # Test advanced template with overwrite
        result = runner.invoke(app, ["urls", "create", "test_app", "--overwrite", "--template", "advanced"])
        assert result.exit_code == 0
        content = Path("test_app/urls.py").read_text()
        assert "detail_patterns" in content


def test_urls_create_invalid_scenarios():
    """Test urls create command error scenarios."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        # Non-existent app
        result = runner.invoke(app, ["urls", "create", "nonexistent_app"])
        assert result.exit_code != 0
        assert "does not exist" in result.output

        # Invalid app (directory exists but not a Django app)
        Path("not_an_app").mkdir()
        result = runner.invoke(app, ["urls", "create", "not_an_app"])
        assert result.exit_code != 0
        assert "is not a Django app" in result.output


def test_urls_list_command():
    """Test the urls list command."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # List URLs before creating any
        result = runner.invoke(app, ["urls", "list"])
        assert result.exit_code == 0
        assert "test_app" in result.output

        # Create a urls.py file
        Path("test_app/urls.py").write_text("urlpatterns = []")

        # List URLs after creating one
        result = runner.invoke(app, ["urls", "list"])
        assert result.exit_code == 0
        assert "test_app" in result.output
        assert "Has urls.py" in result.output


def test_urls_list_no_apps():
    """Test urls list command when no apps are found."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        result = runner.invoke(app, ["urls", "list"])
        assert result.exit_code == 0
        assert "No Django apps found" in result.output


def test_urls_check_command():
    """Test the urls check command."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Check app without urls.py
        result = runner.invoke(app, ["urls", "check", "test_app"])
        assert result.exit_code == 0
        assert "does not have urls.py" in result.output

        # Create a urls.py file
        Path("test_app/urls.py").write_text("urlpatterns = []")

        # Check app with urls.py
        result = runner.invoke(app, ["urls", "check", "test_app"])
        assert result.exit_code == 0
        assert "has urls.py" in result.output


def test_urls_templates_command():
    """Test the urls templates command."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        result = runner.invoke(app, ["urls", "templates"])
        assert result.exit_code == 0
        assert "Available URL Templates" in result.output
        assert "basic" in result.output
        assert "api" in result.output
        assert "advanced" in result.output


def test_urls_outside_django_project():
    """Test URL commands outside Django project."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["urls", "list"])
        assert result.exit_code != 0
        assert "Not in a Django project directory" in result.output
