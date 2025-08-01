"""
Tests for the ViewGenerator class.
"""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from dj_maker.generators.views import ViewGenerator


def test_view_generator_init():
    """Test ViewGenerator initialization."""
    generator = ViewGenerator("test_app", "TestModel", "function")

    assert generator.app_name == "test_app"
    assert generator.model_name == "TestModel"
    assert generator.view_type == "function"
    assert generator.app_path == Path("test_app")


def test_view_generator_get_model_fields_with_exception():
    """Test get_model_fields when model cannot be found."""
    generator = ViewGenerator("test_app", "TestModel", "function")

    # This should return default fields when model is not found
    fields = generator.get_model_fields()

    assert len(fields) == 2
    assert fields[0]['name'] == 'id'
    assert fields[1]['name'] == 'created_at'


def test_view_generator_generate_function_views():
    """Test generating function-based views."""
    generator = ViewGenerator("test_app", "TestModel", "function")

    with patch.object(generator.jinja_env, 'get_template') as mock_template:
        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "# Function-based views"
        mock_template.return_value = mock_template_instance

        result = generator.generate_function_views()

        assert result == "# Function-based views"
        mock_template.assert_called_once_with("views/function_based.py.j2")


def test_view_generator_generate_class_views():
    """Test generating class-based views."""
    generator = ViewGenerator("test_app", "TestModel", "class")

    with patch.object(generator.jinja_env, 'get_template') as mock_template:
        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "# Class-based views"
        mock_template.return_value = mock_template_instance

        result = generator.generate_class_views()

        assert result == "# Class-based views"
        mock_template.assert_called_once_with("views/class_based.py.j2")


def test_view_generator_generate_api_views():
    """Test generating API views."""
    generator = ViewGenerator("test_app", "TestModel", "api")

    with patch.object(generator.jinja_env, 'get_template') as mock_template:
        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "# API views"
        mock_template.return_value = mock_template_instance

        result = generator.generate_api_views()

        assert result == "# API views"
        mock_template.assert_called_once_with("views/api_views.py.j2")


def test_view_generator_generate_serializers():
    """Test generating serializers."""
    generator = ViewGenerator("test_app", "TestModel", "api")

    with patch.object(generator.jinja_env, 'get_template') as mock_template:
        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "# Serializers"
        mock_template.return_value = mock_template_instance

        result = generator.generate_serializers()

        assert result == "# Serializers"
        mock_template.assert_called_once_with("serializers/model_serializer.py.j2")


def test_view_generator_preview():
    """Test preview method for different view types."""
    # Function views
    generator = ViewGenerator("test_app", "TestModel", "function")
    files = generator.preview()
    assert "test_app/views.py" in files

    # Class views
    generator = ViewGenerator("test_app", "TestModel", "class")
    files = generator.preview()
    assert "test_app/views.py" in files

    # API views
    generator = ViewGenerator("test_app", "TestModel", "api")
    files = generator.preview()
    assert "test_app/api_views.py" in files
    assert "test_app/serializers.py" in files


def test_view_generator_generate_function(tmp_path):
    """Test generate method for function views."""
    generator = ViewGenerator("test_app", "TestModel", "function")
    generator.app_path = tmp_path / "test_app"

    with patch.object(generator, 'generate_function_views') as mock_gen:
        mock_gen.return_value = "# Function views content"

        files = generator.generate()

        assert len(files) == 1
        assert files[0] == generator.app_path / "views.py"
        assert (generator.app_path / "views.py").exists()
        assert (generator.app_path / "views.py").read_text() == "# Function views content"


def test_view_generator_generate_class(tmp_path):
    """Test generate method for class views."""
    generator = ViewGenerator("test_app", "TestModel", "class")
    generator.app_path = tmp_path / "test_app"

    with patch.object(generator, 'generate_class_views') as mock_gen:
        mock_gen.return_value = "# Class views content"

        files = generator.generate()

        assert len(files) == 1
        assert files[0] == generator.app_path / "views.py"
        assert (generator.app_path / "views.py").exists()


def test_view_generator_generate_api(tmp_path):
    """Test generate method for API views."""
    generator = ViewGenerator("test_app", "TestModel", "api")
    generator.app_path = tmp_path / "test_app"

    with patch.object(generator, 'generate_api_views') as mock_api, \
         patch.object(generator, 'generate_serializers') as mock_serializers:

        mock_api.return_value = "# API views content"
        mock_serializers.return_value = "# Serializers content"

        files = generator.generate()

        assert len(files) == 2
        assert generator.app_path / "api_views.py" in files
        assert generator.app_path / "serializers.py" in files
        assert (generator.app_path / "api_views.py").exists()
        assert (generator.app_path / "serializers.py").exists()
