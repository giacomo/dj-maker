"""
Tests for the URLGenerator class.
"""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from dj_maker.generators.urls import URLGenerator


def test_url_generator_init():
    """Test URLGenerator initialization."""
    generator = URLGenerator("test_app", "TestModel", "function", "test_namespace")

    assert generator.app_name == "test_app"
    assert generator.model_name == "TestModel"
    assert generator.view_type == "function"
    assert generator.namespace == "test_namespace"
    assert generator.app_path == Path("test_app")


def test_url_generator_init_without_model():
    """Test URLGenerator initialization without model."""
    generator = URLGenerator("test_app", None, "function")

    assert generator.app_name == "test_app"
    assert generator.model_name is None
    assert generator.view_type == "function"
    assert generator.namespace is None


def test_url_generator_generate_basic_urls_no_model():
    """Test generating basic URLs without a model."""
    generator = URLGenerator("test_app", None, "function")

    urls = generator.generate_basic_urls()

    assert "app_name = 'test_app'" in urls
    assert "views.index" in urls
    assert "urlpatterns = [" in urls


def test_url_generator_generate_basic_urls_function_views():
    """Test generating basic URLs for function views."""
    generator = URLGenerator("test_app", "TestModel", "function")

    urls = generator.generate_basic_urls()

    assert "app_name = 'test_app'" in urls
    assert "views.testmodel_list" in urls
    assert "views.testmodel_detail" in urls
    assert "views.testmodel_create" in urls
    assert "views.testmodel_update" in urls
    assert "views.testmodel_delete" in urls


def test_url_generator_generate_basic_urls_class_views():
    """Test generating basic URLs for class views."""
    generator = URLGenerator("test_app", "TestModel", "class")

    urls = generator.generate_basic_urls()

    assert "app_name = 'test_app'" in urls
    assert "views.TestModelListView.as_view()" in urls
    assert "views.TestModelDetailView.as_view()" in urls
    assert "views.TestModelCreateView.as_view()" in urls
    assert "views.TestModelUpdateView.as_view()" in urls
    assert "views.TestModelDeleteView.as_view()" in urls


def test_url_generator_generate_api_urls_no_model():
    """Test generating API URLs without a model."""
    generator = URLGenerator("test_app", None, "api")

    urls = generator.generate_api_urls()

    assert "app_name = 'test_app'" in urls
    assert "from rest_framework.routers import DefaultRouter" in urls
    assert "path('api/', include(router.urls))" in urls


def test_url_generator_generate_api_urls_with_model():
    """Test generating API URLs with a model."""
    generator = URLGenerator("test_app", "TestModel", "api")

    urls = generator.generate_api_urls()

    assert "app_name = 'test_app'" in urls
    assert "router.register(r'testmodels', views.TestModelViewSet)" in urls
    assert "views.TestModelListView.as_view()" in urls
    assert "views.TestModelDetailView.as_view()" in urls
    assert "views.TestModelCreateView.as_view()" in urls
    assert "views.TestModelUpdateView.as_view()" in urls
    assert "views.TestModelDeleteView.as_view()" in urls


def test_url_generator_generate_advanced_urls_no_model():
    """Test generating advanced URLs without a model."""
    generator = URLGenerator("test_app", None, "advanced")

    urls = generator.generate_advanced_urls()

    assert "app_name = 'test_app'" in urls
    # When no model, advanced URLs fall back to basic URLs
    assert "views.index" in urls
    assert "path('', views.index, name='index')" in urls


def test_url_generator_generate_advanced_urls_with_model():
    """Test generating advanced URLs with a model."""
    generator = URLGenerator("test_app", "TestModel", "advanced")

    urls = generator.generate_advanced_urls()

    assert "app_name = 'test_app'" in urls
    assert "detail_patterns = [" in urls
    assert "views.TestModelDetailView.as_view()" in urls
    assert "views.TestModelUpdateView.as_view()" in urls
    assert "views.TestModelDeleteView.as_view()" in urls
    assert "views.TestModelSearchView.as_view()" in urls
    assert "views.TestModelExportView.as_view()" in urls
    assert "path('<int:pk>/', include(detail_patterns))" in urls


def test_url_generator_preview():
    """Test preview method for different URL types."""
    # Test basic preview
    generator = URLGenerator("test_app", "TestModel", "function")
    files = generator.preview()
    assert "test_app/urls.py" in files

    # Test API preview
    generator = URLGenerator("test_app", "TestModel", "api")
    files = generator.preview()
    assert "test_app/urls.py" in files

    # Test advanced preview
    generator = URLGenerator("test_app", "TestModel", "advanced")
    files = generator.preview()
    assert "test_app/urls.py" in files


def test_url_generator_generate_methods(tmp_path):
    """Test generate method for all URL types."""
    # Test standard generation
    generator = URLGenerator("test_app", "TestModel", "function")
    generator.app_path = tmp_path / "test_app"

    files = generator.generate()
    assert len(files) == 1
    assert files[0] == generator.app_path / "urls.py"
    assert (generator.app_path / "urls.py").exists()

    # Test API generation
    generator_api = URLGenerator("test_app", "TestModel", "api")
    generator_api.app_path = tmp_path / "test_app_api"

    files = generator_api.generate()
    assert len(files) == 1
    assert (generator_api.app_path / "urls.py").exists()

    # Test advanced generation
    generator_advanced = URLGenerator("test_app", "TestModel", "advanced")
    generator_advanced.app_path = tmp_path / "test_app_advanced"

    files = generator_advanced.generate()
    assert len(files) == 1
    assert (generator_advanced.app_path / "urls.py").exists()


def test_url_generator_generate_with_namespace(tmp_path):
    """Test generate method with namespace - should use namespace as app_name."""
    generator = URLGenerator("articles", "Article", "class", "v1")
    generator.app_path = tmp_path / "articles"

    files = generator.generate()
    content = files[0].read_text()

    # The namespace should replace the app_name in the generated urls.py
    assert "app_name = 'v1'" in content
    assert "app_name = 'articles'" not in content

    # URL patterns should still reference the model correctly
    assert "views.ArticleListView.as_view()" in content
    assert "name='article-list'" in content
    assert "name='article-detail'" in content


def test_url_structure_with_namespace():
    """Test explicit URL structure that would be created with namespace."""
    # This test documents the expected URL structure when using namespace

    # When you run: django-cli generate articles Article --namespace=v1
    # Generated articles/urls.py should have:
    app_name = "v1"  # namespace replaces app_name

    # In main project urls.py, user should add:
    project_url_pattern = "path('v1/articles/', include('articles.urls'))"

    # This creates URL structure like:
    expected_urls = {
        "list": "/v1/articles/",                    # v1:article-list
        "detail": "/v1/articles/1/",               # v1:article-detail
        "create": "/v1/articles/create/",          # v1:article-create
        "update": "/v1/articles/1/update/",        # v1:article-update
        "delete": "/v1/articles/1/delete/",        # v1:article-delete
    }

    # And reverse URL lookup would be:
    reverse_patterns = {
        "list": "reverse('v1:article-list')",
        "detail": "reverse('v1:article-detail', args=[1])",
        "create": "reverse('v1:article-create')",
        "update": "reverse('v1:article-update', args=[1])",
        "delete": "reverse('v1:article-delete', args=[1])",
    }

    # Test that our URL generator creates the right app_name
    generator = URLGenerator("articles", "Article", "class", "v1")
    content = generator.generate_basic_urls()

    assert f"app_name = '{app_name}'" in content
    assert "name='article-list'" in content
    assert "ArticleListView" in content


def test_url_structure_without_namespace():
    """Test URL structure without namespace (standard Django pattern)."""
    # When you run: django-cli generate articles Article
    # Generated articles/urls.py should have:
    app_name = "articles"  # uses actual app name

    # In main project urls.py, user should add:
    project_url_pattern = "path('articles/', include('articles.urls'))"

    # This creates URL structure like:
    expected_urls = {
        "list": "/articles/",                      # articles:article-list
        "detail": "/articles/1/",                 # articles:article-detail
        "create": "/articles/create/",            # articles:article-create
        "update": "/articles/1/update/",          # articles:article-update
        "delete": "/articles/1/delete/",          # articles:article-delete
    }

    # Test that our URL generator creates the right app_name
    generator = URLGenerator("articles", "Article", "class", None)
    content = generator.generate_basic_urls()

    assert f"app_name = '{app_name}'" in content
    assert "name='article-list'" in content
    assert "ArticleListView" in content


def test_api_versioning_url_structure():
    """Test API versioning URL structure with namespace."""
    # API versioning example: django-cli generate articles Article --namespace=api_v1 --view-type=api

    generator = URLGenerator("articles", "Article", "api", "api_v1")
    content = generator.generate_api_urls()

    # Generated articles/urls.py should have:
    assert "app_name = 'api_v1'" in content
    assert "router.register(r'articles', views.ArticleViewSet)" in content

    # In main project urls.py, user should add:
    # path('api/v1/articles/', include('articles.urls'))

    # This creates URL structure like:
    expected_api_urls = {
        "api_list": "/api/v1/articles/api/articles/",           # DRF router URLs
        "api_detail": "/api/v1/articles/api/articles/1/",       # DRF router URLs
        "web_list": "/api/v1/articles/",                        # api_v1:article-list
        "web_detail": "/api/v1/articles/1/",                    # api_v1:article-detail
    }

    # Reverse URL patterns would be:
    reverse_patterns = {
        "web_list": "reverse('api_v1:article-list')",
        "web_detail": "reverse('api_v1:article-detail', args=[1])",
    }


def test_multiple_version_url_structure():
    """Test multiple API versions URL structure."""
    # Example: Supporting both v1 and v2 APIs

    # Version 1
    v1_generator = URLGenerator("articles", "Article", "api", "v1")
    v1_content = v1_generator.generate_api_urls()
    assert "app_name = 'v1'" in v1_content

    # Version 2
    v2_generator = URLGenerator("articles", "Article", "api", "v2")
    v2_content = v2_generator.generate_api_urls()
    assert "app_name = 'v2'" in v2_content

    # In main project urls.py, user would add:
    project_url_patterns = [
        "path('v1/articles/', include('articles.urls'))",  # Same app, different namespace
        "path('v2/articles/', include('articles.urls'))",  # Would need separate apps in practice
    ]

    # This creates URL structure like:
    expected_v1_urls = {
        "list": "/v1/articles/",           # v1:article-list
        "detail": "/v1/articles/1/",       # v1:article-detail
    }

    expected_v2_urls = {
        "list": "/v2/articles/",           # v2:article-list
        "detail": "/v2/articles/1/",       # v2:article-detail
    }


def test_namespace_vs_app_name_precedence():
    """Test that namespace takes precedence over app_name when provided."""

    # Test with namespace provided
    generator_with_namespace = URLGenerator("my_app", "MyModel", "class", "custom_namespace")
    content_with_namespace = generator_with_namespace.generate_basic_urls()

    assert "app_name = 'custom_namespace'" in content_with_namespace
    assert "app_name = 'my_app'" not in content_with_namespace

    # Test without namespace
    generator_without_namespace = URLGenerator("my_app", "MyModel", "class", None)
    content_without_namespace = generator_without_namespace.generate_basic_urls()

    assert "app_name = 'my_app'" in content_without_namespace
    assert "app_name = 'custom_namespace'" not in content_without_namespace


def test_url_patterns_remain_consistent_regardless_of_namespace():
    """Test that URL patterns themselves don't change, only the app_name."""

    # Generate with and without namespace
    generator_with_ns = URLGenerator("shop", "Product", "class", "v1")
    generator_without_ns = URLGenerator("shop", "Product", "class", None)

    content_with_ns = generator_with_ns.generate_basic_urls()
    content_without_ns = generator_without_ns.generate_basic_urls()

    # Both should have the same URL patterns
    common_patterns = [
        "path('', views.ProductListView.as_view(), name='product-list')",
        "path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail')",
        "path('create/', views.ProductCreateView.as_view(), name='product-create')",
        "path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-update')",
        "path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete')",
    ]

    for pattern in common_patterns:
        assert pattern in content_with_ns
        assert pattern in content_without_ns

    # Only the app_name should differ
    assert "app_name = 'v1'" in content_with_ns
    assert "app_name = 'shop'" in content_without_ns


def test_generate_app_urls(tmp_path):
    """Test generate_app_urls method."""
    generator = URLGenerator("test_app", "TestModel", "class")
    generator.app_path = tmp_path / "test_app"

    files = generator.generate_app_urls()

    assert len(files) == 1
    assert files[0] == generator.app_path / "urls.py"
    assert (generator.app_path / "urls.py").exists()

    # Check content - generate_app_urls creates basic app structure, not model-specific URLs
    content = files[0].read_text()
    assert "app_name = 'test_app'" in content
    assert "views.index" in content
    assert "# Add your URL patterns here" in content


def test_update_main_urls_file_not_exists():
    """Test update_main_urls when main urls.py doesn't exist."""
    generator = URLGenerator("test_app", "TestModel", "class")
    non_existent_path = Path("/non/existent/urls.py")

    result = generator.update_main_urls(non_existent_path)
    assert result is False


def test_update_main_urls_success(tmp_path):
    """Test update_main_urls when it successfully updates the file."""
    generator = URLGenerator("test_app", "TestModel", "class")

    # Create a main urls.py file
    main_urls_path = tmp_path / "urls.py"
    main_urls_path.write_text("""from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
""")

    result = generator.update_main_urls(main_urls_path)
    assert result is True

    # Check that the file was updated
    content = main_urls_path.read_text()
    assert "path('test_app/', include('test_app.urls'))" in content


def test_update_main_urls_already_included(tmp_path):
    """Test update_main_urls when app is already included."""
    generator = URLGenerator("test_app", "TestModel", "class")

    # Create a main urls.py file that already includes the app
    main_urls_path = tmp_path / "urls.py"
    main_urls_path.write_text("""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test_app/', include('test_app.urls')),
]
""")

    result = generator.update_main_urls(main_urls_path)
    assert result is True  # Should return True since it's already included


def test_update_main_urls_no_urlpatterns(tmp_path):
    """Test update_main_urls when no urlpatterns list exists."""
    generator = URLGenerator("test_app", "TestModel", "class")

    # Create a main urls.py file without urlpatterns
    main_urls_path = tmp_path / "urls.py"
    main_urls_path.write_text("""from django.contrib import admin
from django.urls import path

# No urlpatterns defined yet
""")

    result = generator.update_main_urls(main_urls_path)
    assert result is True

    # Should still add the import even if no urlpatterns
    content = main_urls_path.read_text()
    assert "from django.urls import path, include" in content


def test_update_main_urls_exception_handling(tmp_path):
    """Test update_main_urls exception handling."""
    generator = URLGenerator("test_app", "TestModel", "class")

    # Create a file with no write permissions to trigger an exception
    main_urls_path = tmp_path / "readonly_urls.py"
    main_urls_path.write_text("# test file")
    main_urls_path.chmod(0o444)  # Read-only

    try:
        result = generator.update_main_urls(main_urls_path)
        # Should return False due to permission error
        assert result is False
    finally:
        # Restore write permissions for cleanup
        main_urls_path.chmod(0o666)
def test_jinja_environment_setup():
    """Test that Jinja2 environment is properly set up."""
    generator = URLGenerator("test_app", "TestModel", "class")

    # Check that jinja_env is properly initialized
    assert generator.jinja_env is not None
    assert hasattr(generator.jinja_env, 'loader')


def test_edge_case_empty_model_name():
    """Test edge case with empty string model name."""
    generator = URLGenerator("test_app", "", "function")

    # Should treat empty string similar to None
    urls = generator.generate_basic_urls()
    assert "app_name = 'test_app'" in urls
    assert "views.index" in urls


def test_edge_case_special_characters_in_names():
    """Test edge cases with special characters in app/model names."""
    # Test with underscore in model name
    generator = URLGenerator("test_app", "TestModel_Name", "class")
    urls = generator.generate_basic_urls()

    assert "TestModel_NameListView" in urls
    assert "name='testmodel_name-list'" in urls


def test_view_type_case_insensitive():
    """Test that view_type handling works with different cases."""
    # Test with uppercase
    generator = URLGenerator("test_app", "TestModel", "CLASS")
    urls = generator.generate_basic_urls()

    # Should still generate class-based views (the else branch)
    assert "TestModelListView.as_view()" in urls


def test_namespace_priority_over_app_name():
    """Test that namespace always takes priority over app_name in all methods."""
    generator = URLGenerator("articles", "Article", "class", "v1")

    # Test all URL generation methods
    basic_urls = generator.generate_basic_urls()
    api_urls = generator.generate_api_urls()
    advanced_urls = generator.generate_advanced_urls()

    # All should use namespace as app_name
    assert "app_name = 'v1'" in basic_urls
    assert "app_name = 'articles'" not in basic_urls

    assert "app_name = 'v1'" in api_urls
    assert "app_name = 'articles'" not in api_urls

    assert "app_name = 'v1'" in advanced_urls
    assert "app_name = 'articles'" not in advanced_urls


def test_complete_workflow_integration(tmp_path):
    """Test complete workflow from initialization to file generation."""
    # Test the complete workflow
    generator = URLGenerator("blog", "Post", "api", "v1")
    generator.app_path = tmp_path / "blog"

    # Preview first
    preview_files = generator.preview()
    assert "blog/urls.py" in preview_files

    # Generate files
    generated_files = generator.generate()
    assert len(generated_files) == 1
    assert generated_files[0].exists()

    # Check content
    content = generated_files[0].read_text()
    assert "app_name = 'v1'" in content
    assert "router.register(r'posts', views.PostViewSet)" in content
    assert "PostListView" in content


def test_url_pattern_correctness():
    """Test that generated URL patterns follow Django conventions."""
    generator = URLGenerator("products", "Product", "class")
    urls = generator.generate_basic_urls()

    # Check URL pattern structure
    assert "path('', views.ProductListView.as_view(), name='product-list')" in urls
    assert "path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail')" in urls
    assert "path('create/', views.ProductCreateView.as_view(), name='product-create')" in urls
    assert "path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-update')" in urls
    assert "path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete')" in urls


def test_advanced_urls_additional_patterns():
    """Test that advanced URLs include search and export patterns."""
    generator = URLGenerator("articles", "Article", "advanced")
    urls = generator.generate_advanced_urls()

    # Check for additional advanced patterns
    assert "views.ArticleSearchView.as_view()" in urls
    assert "views.ArticleExportView.as_view()" in urls
    assert "name='article-search'" in urls
    assert "name='article-export'" in urls
    assert "detail_patterns = [" in urls
    assert "path('<int:pk>/', include(detail_patterns))" in urls

