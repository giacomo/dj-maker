"""
Tests for the main entry point and CLI app functionality
"""
from typer.testing import CliRunner

from dj_maker.main import app

runner = CliRunner()


def test_app_help():
    """Test the main app help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Django CLI" in result.output
    assert "Modern Django CLI tool" in result.output


def test_app_version():
    """Test the version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Django CLI version:" in result.output


def test_urls_help():
    """Test the urls subcommand help."""
    with runner.isolated_filesystem():
        # Create a fake Django project structure for help to work
        with open("manage.py", "w") as f:
            f.write("# Django manage.py")

        result = runner.invoke(app, ["urls", "--help"])
        assert result.exit_code == 0
        assert "URL management commands" in result.output


def test_urls_templates_command():
    """Test the urls templates command."""
    # This command should work even outside a Django project
    with runner.isolated_filesystem():
        # Create a fake Django project structure
        with open("manage.py", "w") as f:
            f.write("# Django manage.py")

        result = runner.invoke(app, ["urls", "templates"])
        assert result.exit_code == 0
        assert "Available URL Templates" in result.output
        assert "basic" in result.output
        assert "api" in result.output
        assert "advanced" in result.output


def test_generate_help():
    """Test the generate command help."""
    with runner.isolated_filesystem():
        # Create a fake Django project structure for help to work
        with open("manage.py", "w") as f:
            f.write("# Django manage.py")

        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate CRUD views and URLs" in result.output


def test_app_outside_django_project():
    """Test running main app commands outside Django project."""
    with runner.isolated_filesystem():
        # Try to run a command that requires Django project
        result = runner.invoke(app, ["urls", "list"])
        assert result.exit_code != 0
        assert "Not in a Django project directory" in result.output
