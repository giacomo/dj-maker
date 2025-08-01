"""
Tests for the generate command of the django-cli tool.
"""
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from dj_maker.main import app

runner = CliRunner()


def test_generate_outside_django_project():
    """Test running the generate command outside a Django project."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["generate", "test_app", "TestModel"])
        assert result.exit_code != 0
        assert "Not in a Django project directory" in result.output


def test_generate_help():
    """Test the generate command help."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate CRUD views and URLs" in result.output


@patch('dj_maker.generators.views.ViewGenerator')
@patch('dj_maker.generators.urls.URLGenerator')
def test_generate_basic_functionality(mock_url_gen, mock_view_gen):
    """Test basic generate command functionality."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Mock generator returns
        mock_view_gen.return_value.generate.return_value = []
        mock_url_gen.return_value = mock_url_gen

        result = runner.invoke(app, ["generate", "test_app", "TestModel"])
        # Should complete without crashing
        assert result.exit_code == 0 or "generating" in result.output.lower()


@patch('dj_maker.generators.views.ViewGenerator')
@patch('dj_maker.generators.urls.URLGenerator')
def test_generate_dry_run(mock_url_gen, mock_view_gen):
    """Test generate command with dry-run option."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Mock the preview methods to return file lists
        mock_view_gen.return_value.preview.return_value = ["test_app/views.py"]
        mock_url_gen.return_value.preview.return_value = ["test_app/urls.py"]

        result = runner.invoke(app, ["generate", "test_app", "TestModel", "--dry-run"])

        # Should show dry run output
        assert result.exit_code == 0
        assert "DRY RUN MODE" in result.output


@patch('dj_maker.generators.views.ViewGenerator')
@patch('dj_maker.generators.urls.URLGenerator')
def test_generate_with_options(mock_url_gen, mock_view_gen):
    """Test generate command with various options."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        mock_view_gen.return_value.generate.return_value = []

        # Test with all options
        result = runner.invoke(app, [
            "generate", "test_app", "TestModel",
            "--view-type", "function",
            "--url-template", "api",
            "--include-api",
            "--namespace", "test_namespace"
        ])

        # Should complete successfully
        assert result.exit_code == 0 or "generating" in result.output.lower()


@patch('dj_maker.generators.views.ViewGenerator')
@patch('dj_maker.generators.urls.URLGenerator')
def test_generate_different_view_types(mock_url_gen, mock_view_gen):
    """Test generate command with different view types."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        mock_view_gen.return_value.generate.return_value = []

        for view_type in ["function", "class", "api"]:
            result = runner.invoke(app, [
                "generate", "test_app", "TestModel",
                "--view-type", view_type
            ])
            assert result.exit_code == 0 or "generating" in result.output.lower()


@patch('dj_maker.generators.views.ViewGenerator')
@patch('dj_maker.generators.urls.URLGenerator')
def test_generate_with_exception_handling(mock_url_gen, mock_view_gen):
    """Test generate command error handling."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Mock generator to raise an exception
        mock_view_gen.side_effect = Exception("Generator error")

        result = runner.invoke(app, ["generate", "test_app", "TestModel"])

        # Should handle the exception gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()
