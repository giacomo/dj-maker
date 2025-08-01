"""
Pytest configuration file with fixtures for django-cli tests.
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Generator, Dict, Any, Callable

import pytest
import django
from django.conf import settings
from typer.testing import CliRunner

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')

# Initialize Django once
if not settings.configured:
    django.setup()


@pytest.fixture
def runner() -> CliRunner:
    """Return a CLI runner for testing Typer apps."""
    return CliRunner()


@pytest.fixture
def temp_django_project(tmp_path: Path) -> Generator[Dict[str, Any], None, None]:
    """
    Create a temporary Django project structure for testing.

    Returns a dict with:
        - project_dir: Path to the project directory
        - manage_py_path: Path to manage.py
        - app_dir: Path to a sample Django app
    """
    # Create project directory
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create manage.py
    manage_py_path = project_dir / "manage.py"
    manage_py_content = '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    manage_py_path.write_text(manage_py_content)

    # Create a Django app
    app_dir = project_dir / "test_app"
    app_dir.mkdir()

    # Create apps.py
    apps_py_path = app_dir / "apps.py"
    apps_py_content = '''from django.apps import AppConfig

class TestAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_app'
'''
    apps_py_path.write_text(apps_py_content)

    # Create models.py
    models_py_path = app_dir / "models.py"
    models_py_content = '''from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
'''
    models_py_path.write_text(models_py_content)

    # Create __init__.py
    init_py_path = app_dir / "__init__.py"
    init_py_path.write_text("")

    # Create project directory
    project_module_dir = project_dir / "test_project"
    project_module_dir.mkdir()

    # Create settings.py
    settings_py_path = project_module_dir / "settings.py"
    settings_py_content = '''"""
Django settings for test_project.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-test-key'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'test_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'test_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''
    settings_py_path.write_text(settings_py_content)

    # Create __init__.py in project module
    project_init_py_path = project_module_dir / "__init__.py"
    project_init_py_path.write_text("")

    # Create urls.py in project module
    project_urls_py_path = project_module_dir / "urls.py"
    project_urls_py_content = '''from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
'''
    project_urls_py_path.write_text(project_urls_py_content)

    # Return paths
    yield {
        "project_dir": project_dir,
        "manage_py_path": manage_py_path,
        "app_dir": app_dir,
    }


@pytest.fixture
def mock_cwd(monkeypatch: pytest.MonkeyPatch) -> Callable[[Path], None]:
    """
    Fixture to mock Path.cwd() to return a custom path.

    Returns a function that accepts a path to set as the current working directory.
    This ensures any code using Path.cwd() will see our mocked path.
    """
    def _mock_cwd(path: Path) -> None:
        monkeypatch.setattr(Path, "cwd", lambda: path)
        # Also set the actual current working directory for processes
        os.chdir(path)

    # Store original directory to restore after test
    original_dir = os.getcwd()

    yield _mock_cwd

    # Restore original directory
    os.chdir(original_dir)
