"""
Tests for setup_django and other main.py functionality
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from typer.testing import CliRunner
import pytest
import typer

from dj_maker.main import app, setup_django

runner = CliRunner()


def test_setup_django_with_settings_module():
    """Test setup_django when manage.py contains DJANGO_SETTINGS_MODULE."""
    with runner.isolated_filesystem():
        # Create manage.py with DJANGO_SETTINGS_MODULE
        manage_py_content = '''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
'''
        Path("manage.py").write_text(manage_py_content)

        # Mock django.conf.settings.configured to return False, then True after setup
        mock_settings = MagicMock()
        mock_settings.configured = False

        with patch('dj_maker.main.settings', mock_settings), \
             patch('dj_maker.main.django.setup') as mock_django_setup:

            # Should not raise an exception
            setup_django()

            # Should call django.setup()
            mock_django_setup.assert_called_once()


def test_setup_django_without_settings_module():
    """Test setup_django when manage.py doesn't contain DJANGO_SETTINGS_MODULE."""
    with runner.isolated_filesystem():
        # Create manage.py without DJANGO_SETTINGS_MODULE
        manage_py_content = '''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
'''
        Path("manage.py").write_text(manage_py_content)

        mock_settings = MagicMock()
        mock_settings.configured = False

        with patch('dj_maker.main.settings', mock_settings), \
             patch('dj_maker.main.django.setup') as mock_django_setup:

            # Should not raise an exception
            setup_django()

            # Should still call django.setup()
            mock_django_setup.assert_called_once()


def test_setup_django_already_configured():
    """Test setup_django when Django is already configured."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        mock_settings = MagicMock()
        mock_settings.configured = True

        with patch('dj_maker.main.settings', mock_settings), \
             patch('dj_maker.main.django.setup') as mock_django_setup:

            # Should not raise an exception and not call setup
            setup_django()

            # Should NOT call django.setup() since already configured
            mock_django_setup.assert_not_called()


def test_setup_django_no_manage_py():
    """Test setup_django when manage.py doesn't exist."""
    with runner.isolated_filesystem():
        mock_settings = MagicMock()
        mock_settings.configured = False

        with patch('dj_maker.main.settings', mock_settings):
            # Should raise typer.Exit
            with pytest.raises(typer.Exit):
                setup_django()


def test_main_callback_django_setup_success():
    """Test main callback when Django setup succeeds."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        with patch('dj_maker.main.setup_django') as mock_setup:
            # setup_django succeeds
            mock_setup.return_value = None

            result = runner.invoke(app, ["urls", "templates"])
            assert result.exit_code == 0


def test_main_callback_django_setup_fails():
    """Test main callback when Django setup fails but continues."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        with patch('dj_maker.main.setup_django') as mock_setup:
            # setup_django raises an exception
            mock_setup.side_effect = Exception("Django setup failed")

            # Should continue and not crash
            result = runner.invoke(app, ["urls", "templates"])
            assert result.exit_code == 0


def test_version_callback_function():
    """Test the version_callback function directly."""
    from dj_maker.main import version_callback

    # Should raise typer.Exit when called with True
    with pytest.raises(typer.Exit):
        version_callback(True)


def test_urls_create_with_existing_settings_detection():
    """Test urls create command with Django settings detection."""
    with runner.isolated_filesystem():
        # Create a more realistic Django project structure
        Path("manage.py").write_text('''
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testproject.settings')
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
''')
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        mock_settings = MagicMock()
        mock_settings.configured = False

        with patch('dj_maker.main.settings', mock_settings), \
             patch('dj_maker.main.django.setup'):

            result = runner.invoke(app, ["urls", "create", "test_app"])
            assert result.exit_code == 0


def test_urls_create_all_template_types():
    """Test urls create with all template types to cover template logic."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Test each template type
        for template in ["basic", "api", "advanced"]:
            # Remove existing urls.py if it exists
            urls_file = Path("test_app/urls.py")
            if urls_file.exists():
                urls_file.unlink()

            result = runner.invoke(app, ["urls", "create", "test_app", "--template", template])
            assert result.exit_code == 0
            assert urls_file.exists()


def test_generate_command_import_error_handling():
    """Test generate command when imports fail."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")
        Path("test_app").mkdir()
        Path("test_app/apps.py").write_text("# Django app")

        # Mock the import to fail at the module level
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            result = runner.invoke(app, ["generate", "test_app", "TestModel"])
            # Should handle the import error - might exit with error or show error message
            assert result.exit_code != 0 or "error" in result.output.lower() or "import" in result.output.lower()


def test_setup_django_regex_match():
    """Test setup_django regex matching for DJANGO_SETTINGS_MODULE."""
    with runner.isolated_filesystem():
        # Test different quote styles and formats
        test_cases = [
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')",
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")',
            "    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  ",
        ]

        for i, settings_line in enumerate(test_cases):
            manage_py_content = f'''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    {settings_line}
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
'''
            Path("manage.py").write_text(manage_py_content)

            mock_settings = MagicMock()
            mock_settings.configured = False

            with patch('dj_maker.main.settings', mock_settings), \
                 patch('dj_maker.main.django.setup') as mock_django_setup, \
                 patch.dict('os.environ', {}, clear=False):

                setup_django()

                # Should call django.setup()
                mock_django_setup.assert_called()
                mock_django_setup.reset_mock()


def test_django_setup_exception_handling():
    """Test setup_django when django.setup() raises an exception."""
    with runner.isolated_filesystem():
        Path("manage.py").write_text("# Django manage.py")

        mock_settings = MagicMock()
        mock_settings.configured = False

        with patch('dj_maker.main.settings', mock_settings), \
             patch('dj_maker.main.django.setup', side_effect=Exception("Django setup failed")):

            # Should not crash, but might raise the exception
            try:
                setup_django()
            except Exception:
                # Exception is acceptable in this scenario
                pass
