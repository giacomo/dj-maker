"""
Tests for basic functionality of the django-cli tool.
"""
from pathlib import Path
from typer.testing import CliRunner

from dj_maker.main import app, is_django_project, is_django_app, get_apps_list

runner = CliRunner()


def test_is_django_project():
    """Test is_django_project function."""
    with runner.isolated_filesystem():
        # Not a Django project initially
        assert not is_django_project()

        # Create manage.py to make it a Django project
        Path("manage.py").write_text("# Django manage.py")
        assert is_django_project()


def test_is_django_app():
    """Test is_django_app function."""
    with runner.isolated_filesystem():
        # Not a Django app
        Path("test_dir").mkdir()
        assert not is_django_app(Path("test_dir"))

        # Create Django app
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")
        assert is_django_app(Path("test_app"))


def test_get_apps_list():
    """Test get_apps_list function."""
    with runner.isolated_filesystem():
        # Not a Django project initially
        assert get_apps_list() == []

        # Create Django project with app
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        apps = get_apps_list()
        assert "test_app" in apps


def test_version_command():
    """Test the --version option."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Django CLI version:" in result.output


def test_main_command_outside_django_project():
    """Test running the main command outside a Django project."""
    with runner.isolated_filesystem():
        result = runner.invoke(app)
        assert result.exit_code != 0


def test_app_help():
    """Test the main app help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Django CLI" in result.output
    assert "Modern Django CLI tool" in result.output
