"""
Tests for the init command functionality in main.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess
from typer.testing import CliRunner

from dj_maker.main import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


def test_init_command_success(tmp_path, runner):
    """Test successful project creation with init command."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:

        # Mock successful django-admin call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Change to tmp directory for test
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path = tmp_path / project_name
            project_path.mkdir(exist_ok=True)

            # Run the init command
            result = runner.invoke(app, ['init', project_name])

            # Check command executed successfully
            assert result.exit_code == 0
            assert "Creating Django project" in result.stdout
            assert "Successfully created Django project!" in result.stdout

            # Verify django-admin was called correctly
            mock_subprocess.assert_called_once_with(
                ['django-admin', 'startproject', project_name],
                capture_output=True,
                text=True
            )

        finally:
            os.chdir(original_cwd)


def test_init_command_with_template(tmp_path, runner):
    """Test project creation with custom template."""
    project_name = "test_project"
    template_url = "https://github.com/example/django-template"

    with patch('subprocess.run') as mock_subprocess:

        # Mock successful django-admin call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path = tmp_path / project_name
            project_path.mkdir(exist_ok=True)

            # Run init command with template
            result = runner.invoke(app, ['init', project_name, '--template', template_url])

            # Check command executed successfully
            assert result.exit_code == 0

            # Verify django-admin was called with template option
            mock_subprocess.assert_called_once_with(
                ['django-admin', 'startproject', project_name, '--template', template_url],
                capture_output=True,
                text=True
            )

        finally:
            os.chdir(original_cwd)


def test_init_command_django_admin_failure(tmp_path, runner):
    """Test handling of django-admin command failure."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:

        # Mock failed django-admin call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Project already exists"
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Run the init command
            result = runner.invoke(app, ['init', project_name])

            # Check command failed appropriately
            assert result.exit_code == 1
            assert "Error creating project" in result.stdout
            assert "Project already exists" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_creates_additional_files(tmp_path, runner):
    """Test that init command creates additional project files."""
    project_name = "test_project"
    project_path = tmp_path / project_name

    with patch('subprocess.run') as mock_subprocess:

        # Mock successful django-admin call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path.mkdir(exist_ok=True)

            # Run the init command
            result = runner.invoke(app, ['init', project_name])

            # Check that additional directories were created
            assert (project_path / "static").exists()
            assert (project_path / "media").exists()
            assert (project_path / "templates").exists()

            # Check that additional files were created
            assert (project_path / "requirements.txt").exists()
            assert (project_path / ".env.example").exists()
            assert (project_path / ".gitignore").exists()

            # Verify file contents
            requirements = (project_path / "requirements.txt").read_text()
            assert "Django>=4.2,<6.0" in requirements
            assert "djangorestframework>=3.14.0" in requirements

            env_example = (project_path / ".env.example").read_text()
            assert "DEBUG=True" in env_example
            assert "SECRET_KEY=" in env_example

            gitignore = (project_path / ".gitignore").read_text()
            assert "__pycache__/" in gitignore
            assert "db.sqlite3" in gitignore
            assert ".env" in gitignore

        finally:
            os.chdir(original_cwd)


def test_init_command_shows_next_steps(tmp_path, runner):
    """Test that init command shows helpful next steps."""
    project_name = "my_project"

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path = tmp_path / project_name
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check that helpful next steps are shown
            assert "Next steps:" in result.stdout
            assert f"cd {project_name}" in result.stdout
            assert "python -m venv .venv" in result.stdout
            assert "pip install -r requirements.txt" in result.stdout
            assert "python manage.py migrate" in result.stdout
            assert "python manage.py createsuperuser" in result.stdout
            assert "python manage.py runserver" in result.stdout
            assert "django-cli generate" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_database_option(tmp_path, runner):
    """Test init command with database option."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path = tmp_path / project_name
            project_path.mkdir(exist_ok=True)

            # Test with postgresql database option
            result = runner.invoke(app, ['init', project_name, '--database', 'postgresql'])

            assert result.exit_code == 0
            assert "Creating Django project" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_exception_handling(tmp_path, runner):
    """Test init command exception handling."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:

        # Mock subprocess to raise an exception
        mock_subprocess.side_effect = Exception("Unexpected error")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])

            # Should handle exception gracefully
            assert result.exit_code == 1
            assert "Error creating project" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_requirements_content(tmp_path, runner):
    """Test that requirements.txt has correct content."""
    project_name = "test_project"
    project_path = tmp_path / project_name

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check requirements.txt content
            requirements_file = project_path / "requirements.txt"
            assert requirements_file.exists()

            content = requirements_file.read_text()
            expected_packages = [
                "Django>=4.2,<6.0",
                "djangorestframework>=3.14.0",
                "python-decouple>=3.8",
                "Pillow>=10.0.0"
            ]

            for package in expected_packages:
                assert package in content

        finally:
            os.chdir(original_cwd)


def test_init_command_env_example_content(tmp_path, runner):
    """Test that .env.example has correct content."""
    project_name = "my_awesome_project"
    project_path = tmp_path / project_name

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check .env.example content
            env_file = project_path / ".env.example"
            assert env_file.exists()

            content = env_file.read_text()

            # Check for essential environment variables
            assert "DEBUG=True" in content
            assert "SECRET_KEY=" in content
            assert "ALLOWED_HOSTS=" in content
            assert f"postgresql://user:password@localhost:5432/{project_name}" in content
            assert "STATIC_URL=/static/" in content
            assert "MEDIA_URL=/media/" in content

        finally:
            os.chdir(original_cwd)


def test_init_command_gitignore_content(tmp_path, runner):
    """Test that .gitignore has correct content."""
    project_name = "test_project"
    project_path = tmp_path / project_name

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check .gitignore content
            gitignore_file = project_path / ".gitignore"
            assert gitignore_file.exists()

            content = gitignore_file.read_text()

            # Check for essential gitignore patterns
            essential_patterns = [
                "__pycache__/",
                "*.py[cod]",
                ".Python",
                "venv/",
                ".venv/",
                "*.log",
                "db.sqlite3",
                "media/",
                ".env",
                ".vscode/",
                ".idea/",
                ".DS_Store"
            ]

            for pattern in essential_patterns:
                assert pattern in content

        finally:
            os.chdir(original_cwd)


def test_init_command_directory_structure(tmp_path, runner):
    """Test that init command creates proper directory structure."""
    project_name = "test_project"
    project_path = tmp_path / project_name

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check that all expected directories exist
            expected_dirs = ["static", "media", "templates"]

            for dir_name in expected_dirs:
                dir_path = project_path / dir_name
                assert dir_path.exists()
                assert dir_path.is_dir()

        finally:
            os.chdir(original_cwd)


def test_init_command_output_formatting(tmp_path, runner):
    """Test that init command has proper output formatting."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create the project directory that django-admin would normally create
            project_path = tmp_path / project_name
            project_path.mkdir(exist_ok=True)

            result = runner.invoke(app, ['init', project_name])

            # Check for proper emoji and formatting in output
            assert "🚀 Creating Django project" in result.stdout
            assert "✅" in result.stdout  # Success emoji
            assert "📝" in result.stdout  # Next steps emoji
            assert "💡" in result.stdout  # Tip emoji

            # Check that project name is highlighted in output
            assert project_name in result.stdout

        finally:
            os.chdir(original_cwd)
