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
        # Mock successful subprocess calls for uv and django-admin
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Change to tmp directory for test
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Run the init command
            result = runner.invoke(app, ['init', project_name])

            # Check command executed successfully
            assert result.exit_code == 0
            assert "Creating Django project" in result.stdout
            assert "Successfully created Django project!" in result.stdout

            # Verify the expected subprocess calls were made
            expected_calls = [
                call(['uv', 'init'], capture_output=True, text=True),
                call(['uv', 'add', 'django'], capture_output=True, text=True),
                call(['uv', 'run', 'django-admin', 'startproject', 'config', '.'], capture_output=True, text=True)
            ]
            mock_subprocess.assert_has_calls(expected_calls, any_order=False)

            # Check that project directory was created
            assert (tmp_path / project_name).exists()

        finally:
            os.chdir(original_cwd)


def test_init_command_with_template(tmp_path, runner):
    """Test project creation with custom template."""
    project_name = "test_project"
    template_url = "https://github.com/example/django-template"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Run init command with template
            result = runner.invoke(app, ['init', project_name, '--template', template_url])

            # Check command executed successfully
            assert result.exit_code == 0

            # Verify django-admin was called with template option
            expected_django_call = call(['uv', 'run', 'django-admin', 'startproject', 'config', '.', '--template', template_url], capture_output=True, text=True)
            mock_subprocess.assert_any_call(['uv', 'run', 'django-admin', 'startproject', 'config', '.', '--template', template_url], capture_output=True, text=True)

        finally:
            os.chdir(original_cwd)


def test_init_command_creates_additional_files(tmp_path, runner):
    """Test that init command creates additional files and directories."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Run the init command
            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            # Check that additional directories were created
            project_path = tmp_path / project_name
            assert (project_path / "static").exists()
            assert (project_path / "media").exists()
            assert (project_path / "templates").exists()

            # Check that configuration files were created
            assert (project_path / ".env.example").exists()
            assert (project_path / ".gitignore").exists()

        finally:
            os.chdir(original_cwd)


def test_init_command_shows_next_steps(tmp_path, runner):
    """Test that init command shows next steps."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0
            assert "Next steps:" in result.stdout
            assert "uv run python manage.py migrate" in result.stdout
            assert "uv run python manage.py runserver" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_database_option(tmp_path, runner):
    """Test init command with different database options."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Test with PostgreSQL database
            result = runner.invoke(app, ['init', project_name, '--database', 'postgresql'])
            assert result.exit_code == 0
            assert "Adding PostgreSQL support" in result.stdout

            # Verify psycopg2-binary was added
            mock_subprocess.assert_any_call(['uv', 'add', 'django', 'psycopg2-binary'], capture_output=True, text=True)

        finally:
            os.chdir(original_cwd)


def test_init_command_requirements_content(tmp_path, runner):
    """Test that init command creates proper project structure with uv."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            # Since the init command uses uv, it creates pyproject.toml instead of requirements.txt
            # The uv init call should have been made
            mock_subprocess.assert_any_call(['uv', 'init'], capture_output=True, text=True)

        finally:
            os.chdir(original_cwd)


def test_init_command_env_example_content(tmp_path, runner):
    """Test that .env.example is created with proper content."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            # Check .env.example content
            env_file = tmp_path / project_name / ".env.example"
            assert env_file.exists()
            content = env_file.read_text()
            assert "DEBUG=True" in content
            assert "SECRET_KEY=" in content
            assert "ALLOWED_HOSTS=" in content

        finally:
            os.chdir(original_cwd)


def test_init_command_gitignore_content(tmp_path, runner):
    """Test that .gitignore is created with proper content."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            # Check .gitignore content
            gitignore_file = tmp_path / project_name / ".gitignore"
            assert gitignore_file.exists()
            content = gitignore_file.read_text()
            assert "__pycache__/" in content
            assert "*.py[cod]" in content  # This pattern covers *.pyc, *.pyo, *.pyd
            assert ".env" in content
            assert "db.sqlite3" in content

        finally:
            os.chdir(original_cwd)


def test_init_command_directory_structure(tmp_path, runner):
    """Test that proper directory structure is created."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            project_path = tmp_path / project_name
            # Check main project directory exists
            assert project_path.exists()

            # Check additional directories
            assert (project_path / "static").exists()
            assert (project_path / "media").exists()
            assert (project_path / "templates").exists()

        finally:
            os.chdir(original_cwd)


def test_init_command_output_formatting(tmp_path, runner):
    """Test that init command has proper output formatting."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 0

            # Check for emoji and formatting in output
            assert "🚀" in result.stdout
            assert "✅" in result.stdout
            assert "📁" in result.stdout

        finally:
            os.chdir(original_cwd)


def test_init_command_directory_exists_error(tmp_path, runner):
    """Test init command when directory already exists."""
    project_name = "test_project"

    # Create the directory first
    (tmp_path / project_name).mkdir()

    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)

        result = runner.invoke(app, ['init', project_name])
        assert result.exit_code == 1
        assert "Directory test_project already exists" in result.stdout

    finally:
        os.chdir(original_cwd)


def test_init_command_uv_failure(tmp_path, runner):
    """Test init command when uv commands fail."""
    project_name = "test_project"

    with patch('subprocess.run') as mock_subprocess:
        # Mock failed uv init
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "uv init failed"
        mock_subprocess.return_value = mock_result

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            result = runner.invoke(app, ['init', project_name])
            assert result.exit_code == 1
            assert "Error initializing uv" in result.stdout

        finally:
            os.chdir(original_cwd)
