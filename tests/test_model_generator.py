"""
Tests for the ModelGenerator class.
"""
import pytest
from pathlib import Path
from dj_maker.generators.models import ModelGenerator


def test_model_generator_init():
    """Test ModelGenerator initialization."""
    generator = ModelGenerator("test_app", "TestModel")

    assert generator.app_name == "test_app"
    assert generator.model_name == "TestModel"
    assert generator.app_path == Path("test_app")


def test_generate_basic_model():
    """Test basic model generation."""
    generator = ModelGenerator("blog", "Post")
    model_code = generator.generate_basic_model()

    # Check model structure
    assert "class Post(models.Model):" in model_code
    assert "title = models.CharField(max_length=200)" in model_code
    assert "description = models.TextField(blank=True)" in model_code
    assert "created_at = models.DateTimeField(auto_now_add=True)" in model_code
    assert "updated_at = models.DateTimeField(auto_now=True)" in model_code
    assert "is_active = models.BooleanField(default=True)" in model_code

    # Check methods
    assert "def __str__(self):" in model_code
    assert "def get_absolute_url(self):" in model_code

    # Check Meta class
    assert "class Meta:" in model_code
    assert "ordering = ['-created_at']" in model_code
    assert "verbose_name = 'Post'" in model_code
    assert "verbose_name_plural = 'Posts'" in model_code

    # Check imports
    assert "from django.db import models" in model_code
    assert "from django.urls import reverse" in model_code
    assert "from django.contrib.auth.models import User" in model_code


def test_generate_admin_registration():
    """Test admin registration generation."""
    generator = ModelGenerator("blog", "Post")
    admin_code = generator.generate_admin_registration()

    # Check admin class structure
    assert "@admin.register(Post)" in admin_code
    assert "class PostAdmin(admin.ModelAdmin):" in admin_code
    assert "list_display = ['title', 'created_at', 'updated_at', 'is_active']" in admin_code
    assert "list_filter = ['is_active', 'created_at', 'updated_at']" in admin_code
    assert "search_fields = ['title', 'description']" in admin_code
    assert "readonly_fields = ['created_at', 'updated_at']" in admin_code
    assert "fieldsets = (" in admin_code

    # Check imports
    assert "from django.contrib import admin" in admin_code
    assert "from .models import Post" in admin_code


def test_update_models_file_new(tmp_path):
    """Test creating new models.py file."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    models_file = generator.update_models_file()

    assert models_file.exists()
    assert models_file.name == "models.py"

    content = models_file.read_text()
    assert "class TestModel(models.Model):" in content
    assert "from django.db import models" in content


def test_update_models_file_existing_empty(tmp_path):
    """Test updating existing empty models.py file."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create existing empty models.py
    models_file = generator.app_path / "models.py"
    models_file.write_text("from django.db import models\n\n# Create your models here.\n")

    updated_file = generator.update_models_file()

    assert updated_file.exists()
    content = updated_file.read_text()

    # Should contain the new model
    assert "class TestModel(models.Model):" in content
    assert "from django.db import models" in content  # Should not duplicate imports


def test_update_models_file_existing_with_models(tmp_path):
    """Test updating models.py file that already has models."""
    generator = ModelGenerator("test_app", "NewModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create existing models.py with existing model
    existing_content = """from django.db import models

class ExistingModel(models.Model):
    name = models.CharField(max_length=100)
"""
    models_file = generator.app_path / "models.py"
    models_file.write_text(existing_content)

    updated_file = generator.update_models_file()

    content = updated_file.read_text()

    # Should contain both models
    assert "class ExistingModel(models.Model):" in content
    assert "class NewModel(models.Model):" in content
    # Should not duplicate imports
    assert content.count("from django.db import models") == 1


def test_update_models_file_model_already_exists(tmp_path):
    """Test updating models.py when model already exists."""
    generator = ModelGenerator("test_app", "ExistingModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create models.py with the same model name
    existing_content = """from django.db import models

class ExistingModel(models.Model):
    name = models.CharField(max_length=100)
"""
    models_file = generator.app_path / "models.py"
    models_file.write_text(existing_content)

    updated_file = generator.update_models_file()

    content = updated_file.read_text()

    # Should not add duplicate model
    assert content.count("class ExistingModel(models.Model):") == 1
    assert content == existing_content  # Content should remain unchanged


def test_update_admin_file_new(tmp_path):
    """Test creating new admin.py file."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    admin_file = generator.update_admin_file()

    assert admin_file.exists()
    assert admin_file.name == "admin.py"

    content = admin_file.read_text()
    assert "@admin.register(TestModel)" in content
    assert "class TestModelAdmin(admin.ModelAdmin):" in content


def test_update_admin_file_existing_empty(tmp_path):
    """Test updating existing empty admin.py file."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create existing admin.py
    admin_file = generator.app_path / "admin.py"
    admin_file.write_text("from django.contrib import admin\n\n# Register your models here.\n")

    updated_file = generator.update_admin_file()

    content = updated_file.read_text()

    assert "@admin.register(TestModel)" in content
    assert "class TestModelAdmin(admin.ModelAdmin):" in content
    assert "from .models import TestModel" in content


def test_update_admin_file_existing_with_models(tmp_path):
    """Test updating admin.py that already has model registrations."""
    generator = ModelGenerator("test_app", "NewModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create existing admin.py with existing registrations
    existing_content = """from django.contrib import admin
from .models import ExistingModel

@admin.register(ExistingModel)
class ExistingModelAdmin(admin.ModelAdmin):
    list_display = ['name']
"""
    admin_file = generator.app_path / "admin.py"
    admin_file.write_text(existing_content)

    updated_file = generator.update_admin_file()

    content = updated_file.read_text()

    # Should contain both admin classes
    assert "ExistingModelAdmin" in content
    assert "NewModelAdmin" in content
    assert "from .models import NewModel," in content


def test_update_admin_file_already_exists(tmp_path):
    """Test updating admin.py when admin registration already exists."""
    generator = ModelGenerator("test_app", "ExistingModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create admin.py with the same model admin
    existing_content = """from django.contrib import admin
from .models import ExistingModel

@admin.register(ExistingModel)
class ExistingModelAdmin(admin.ModelAdmin):
    list_display = ['name']
"""
    admin_file = generator.app_path / "admin.py"
    admin_file.write_text(existing_content)

    updated_file = generator.update_admin_file()

    content = updated_file.read_text()

    # Should not add duplicate admin registration
    assert content.count("ExistingModelAdmin") == 1
    assert content == existing_content  # Content should remain unchanged


def test_preview():
    """Test preview method."""
    generator = ModelGenerator("test_app", "TestModel")
    files = generator.preview()

    expected_files = [
        "test_app/models.py",
        "test_app/admin.py"
    ]

    assert files == expected_files


def test_generate(tmp_path):
    """Test complete generation process."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"

    created_files = generator.generate()

    assert len(created_files) == 2

    # Check that files were created
    models_file = tmp_path / "test_app" / "models.py"
    admin_file = tmp_path / "test_app" / "admin.py"

    assert models_file.exists()
    assert admin_file.exists()
    assert models_file in created_files
    assert admin_file in created_files

    # Check content
    models_content = models_file.read_text()
    admin_content = admin_file.read_text()

    assert "class TestModel(models.Model):" in models_content
    assert "class TestModelAdmin(admin.ModelAdmin):" in admin_content


def test_generate_app_directory_creation(tmp_path):
    """Test that app directory is created if it doesn't exist."""
    generator = ModelGenerator("new_app", "TestModel")
    generator.app_path = tmp_path / "new_app"

    # Directory doesn't exist initially
    assert not generator.app_path.exists()

    created_files = generator.generate()

    # Directory should be created
    assert generator.app_path.exists()
    assert generator.app_path.is_dir()
    assert len(created_files) == 2


def test_model_with_special_characters():
    """Test model generation with special characters in names."""
    generator = ModelGenerator("my_app", "MyModel_Name")
    model_code = generator.generate_basic_model()

    assert "class MyModel_Name(models.Model):" in model_code
    assert "verbose_name = 'MyModel_Name'" in model_code
    assert "verbose_name_plural = 'MyModel_Names'" in model_code


def test_different_app_names():
    """Test model generation with different app name patterns."""
    # Test with underscores
    generator1 = ModelGenerator("my_blog_app", "Post")
    model_code1 = generator1.generate_basic_model()
    assert "reverse('my_blog_app:post-detail'" in model_code1

    # Test with dashes (though not recommended)
    generator2 = ModelGenerator("api", "User")
    model_code2 = generator2.generate_basic_model()
    assert "reverse('api:user-detail'" in model_code2


def test_admin_fieldsets_structure():
    """Test that admin fieldsets are properly structured."""
    generator = ModelGenerator("shop", "Product")
    admin_code = generator.generate_admin_registration()

    # Check fieldsets structure
    assert "fieldsets = (" in admin_code
    assert "(None, {" in admin_code
    assert "'fields': ('title', 'description', 'is_active')" in admin_code
    assert "('Timestamps', {" in admin_code
    assert "'classes': ('collapse',)" in admin_code


def test_update_admin_file_no_admin_import(tmp_path):
    """Test updating admin.py file without existing admin import."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create admin.py without admin import
    admin_file = generator.app_path / "admin.py"
    admin_file.write_text("# No imports yet\n")

    updated_file = generator.update_admin_file()

    content = updated_file.read_text()

    # Should add both imports
    assert "from django.contrib import admin" in content
    assert "from .models import TestModel" in content
    assert "@admin.register(TestModel)" in content


def test_update_models_file_import_edge_cases(tmp_path):
    """Test models.py update with various import scenarios."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create models.py with partial imports
    existing_content = """from django.db import models
# Missing other imports

class ExistingModel(models.Model):
    name = models.CharField(max_length=100)
"""
    models_file = generator.app_path / "models.py"
    models_file.write_text(existing_content)

    updated_file = generator.update_models_file()
    content = updated_file.read_text()

    # Should add missing imports
    assert "from django.urls import reverse" in content
    assert "from django.contrib.auth.models import User" in content
    # Should not duplicate existing import
    assert content.count("from django.db import models") == 1


def test_update_models_file_user_import_only(tmp_path):
    """Test models.py update when only User import is missing."""
    generator = ModelGenerator("test_app", "TestModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create models.py with models and reverse imports but missing User import
    existing_content = """from django.db import models
from django.urls import reverse

class ExistingModel(models.Model):
    name = models.CharField(max_length=100)
"""
    models_file = generator.app_path / "models.py"
    models_file.write_text(existing_content)

    updated_file = generator.update_models_file()
    content = updated_file.read_text()

    # Should add the missing User import specifically (line 78)
    assert "from django.contrib.auth.models import User" in content
    # Should not duplicate existing imports
    assert content.count("from django.db import models") == 1
    assert content.count("from django.urls import reverse") == 1


def test_update_models_file_with_user_import_missing_specific(tmp_path):
    """Test the specific edge case that covers line 78 - User import condition."""
    generator = ModelGenerator("test_app", "NewModel")
    generator.app_path = tmp_path / "test_app"
    generator.app_path.mkdir()

    # Create a models.py file that has all imports except User import
    # This will specifically trigger line 78: if 'from django.contrib.auth.models import User' not in content:
    existing_content = """from django.db import models
from django.urls import reverse
# User import is missing

class ExistingModel(models.Model):
    title = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse('test_app:existing-detail', kwargs={'pk': self.pk})
"""
    models_file = generator.app_path / "models.py"
    models_file.write_text(existing_content)

    # Update the file - this should trigger the User import check on line 78
    updated_file = generator.update_models_file()
    content = updated_file.read_text()

    # Verify that the User import was added (this is line 78 being executed)
    assert "from django.contrib.auth.models import User" in content
    # Verify existing imports weren't duplicated
    assert content.count("from django.db import models") == 1
    assert content.count("from django.urls import reverse") == 1
    # Verify new model was added
    assert "class NewModel(models.Model):" in content
