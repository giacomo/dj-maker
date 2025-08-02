# 🚀 DJ Maker - Supercharge Your Django Development

[![PyPI version](https://badge.fury.io/py/dj-maker.svg)](https://badge.fury.io/py/dj-maker)
[![Python Support](https://img.shields.io/pypi/pyversions/dj-maker.svg)](https://pypi.org/project/dj-maker/)
[![Django Support](https://img.shields.io/badge/Django-4.2%20|%205.1%20|%205.2-success.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/giacomo/dj-maker/graph/badge.svg?token=Y112TWO5EE)](https://codecov.io/github/giacomo/dj-maker)
[![Tests](https://img.shields.io/badge/tests-128%20passing-brightgreen.svg)](https://github.com/giacomo/dj-maker)

> **Rapidly generate Django apps, models, views, URLs, and templates with a single command.**

DJ Maker is a powerful code generation tool that accelerates Django development by automatically creating complete CRUD applications, API endpoints, and boilerplate code. Say goodbye to repetitive tasks and hello to productive development! ⚡

## ✨ Features

### 🏗️ **Complete App Generation**
- **Full CRUD Apps**: Generate complete Django applications with models, views, URLs, and templates
- **Multiple View Types**: Support for function-based views, class-based views, and DRF API views
- **Smart Templates**: Beautiful, responsive HTML templates with Bootstrap styling
- **Advanced URL Patterns**: Nested URLs, namespacing, and API versioning support

### 🎯 **Developer Experience**
- **Rich CLI Interface**: Beautiful, colored terminal output powered by Rich
- **Interactive Prompts**: Guided setup with intelligent defaults
- **Preview Mode**: See what will be generated before creating files
- **Type Safety**: Full type annotations and mypy support

### 🔧 **Flexibility & Power**
- **API-First Development**: Generate Django REST Framework endpoints automatically
- **Custom Namespacing**: Support for API versioning and modular architectures
- **Template Customization**: Jinja2-powered templates with extensibility
- **Project Integration**: Seamlessly integrates with existing Django projects

## 🚀 Quick Start

### Installation

```bash
pip install dj-maker
```

### Create Your First Project

```bash
# Create a new Django project with best practices
dj init myblog

# Navigate to your project
cd myblog
```

### Generate Your First App

```bash
# Create a complete blog app with CRUD operations
dj generate blog Post --view-type=class

# Generate an API-first app with DRF integration
dj generate api articles Article --view-type=api --namespace=v1

# Create function-based views for maximum control
dj generate shop Product --view-type=function
```

### Initialize Apps in Existing Projects

```bash
# Create a new Django app with URLs and tests
dj init-app users

# Create app with specific URL template
dj init-app api --url-template=api --include-tests
```

## 📖 Usage Examples

### 🎨 **Basic CRUD Generation**

Generate a complete blog application with class-based views:

```bash
dj generate blog Post --view-type=class
```

**Generated structure:**
```
blog/
├── __init__.py
├── admin.py              # Admin interface with list_display, filters
├── apps.py
├── models.py             # Post model with common fields (title, description, timestamps)
├── views.py              # Complete CRUD class-based views
├── urls.py               # RESTful URL patterns
├── templates/blog/       # Bootstrap-styled templates
│   ├── base.html
│   ├── post_list.html
│   ├── post_detail.html
│   ├── post_form.html
│   └── post_confirm_delete.html
└── migrations/
```

### 🔌 **API Development**

Create a REST API with Django REST Framework:

```bash
dj generate api products Product --view-type=api --namespace=v1
```

**Features:**
- ViewSets and Serializers
- Router-based URL configuration
- API versioning support
- Both API and web views

### 🎛️ **Advanced URL Patterns**

Generate nested URL structures:

```bash
dj generate articles Article --view-type=advanced
```

**Generated URLs:**
```python
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('<int:pk>/', include([
        path('', views.ArticleDetailView.as_view(), name='article-detail'),
        path('edit/', views.ArticleUpdateView.as_view(), name='article-update'),
        path('delete/', views.ArticleDeleteView.as_view(), name='article-delete'),
    ])),
    path('search/', views.ArticleSearchView.as_view(), name='article-search'),
    path('export/', views.ArticleExportView.as_view(), name='article-export'),
]
```

### 🌐 **API Versioning**

Create versioned APIs for scalable applications:

```bash
# Generate v1 API
dj generate api users User --namespace=api_v1 --view-type=api

# Generate v2 API (in separate app)
dj generate api_v2 users User --namespace=api_v2 --view-type=api
```

**URL Structure:**
```
/api/v1/users/          # api_v1:user-list
/api/v1/users/1/        # api_v1:user-detail
/api/v2/users/          # api_v2:user-list
/api/v2/users/1/        # api_v2:user-detail
```

## 🎨 **Generated Templates**

Django CLI creates beautiful, responsive templates using Bootstrap 5:

### 📝 **List View Template**
```html
<!-- Responsive table with search, pagination, and actions -->
<div class="container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Posts</h1>
        <a href="{% url 'blog:post-create' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> New Post
        </a>
    </div>
    <!-- ... responsive table with Bootstrap styling ... -->
</div>
```

### 📋 **Form Template**
```html
<!-- Modern form with validation and UX enhancements -->
<form method="post" class="needs-validation" novalidate>
    {% csrf_token %}
    {{ form }}
    <div class="mt-3">
        <button type="submit" class="btn btn-primary">Save</button>
        <a href="{% url 'blog:post-list' %}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
```

## 🔧 Command Reference

### Project Management
```bash
dj init <project_name>              # Create new Django project
dj init-app <app_name>              # Initialize new app
```

### Generation Commands
```bash
dj generate <app> <model> [options]

Options:
  --view-type    [function|class|api|advanced]  View type (default: class)
  --namespace    TEXT                           URL namespace for versioning
  --dry-run                                     Preview files without creating
  --no-templates                               Skip HTML template generation
  --help                                        Show help message
```

### URL Management
```bash
dj urls create <app_name>           # Create urls.py for an app
dj urls list                         # List apps and their URL status
dj urls check <app_name>            # Check specific app's URLs
```

### Utility Commands
```bash
dj list-models [app_name]           # List models in project/app
dj --version                         # Show version information
dj --help                            # Show all available commands
```

## 🛠️ Integration

### Add to Existing Projects

1. **Install dj-maker** in your project environment
2. **Generate new apps** directly in your existing project
3. **Update main URLs** manually or let dj suggest the integration:

```python
# Add to your main urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),        # Generated app
    path('api/v1/', include('api.urls')),       # Generated API
]
```

### Settings Integration

Django CLI works with your existing Django settings. For API apps, ensure you have DRF configured:

```python
# settings.py
INSTALLED_APPS = [
    # ... your apps
    'rest_framework',
    'blog',  # Generated app
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

## 🧪 **Quality Assurance**

- **🎯 92% Test Coverage** across all modules
- **✅ 128 Comprehensive Tests** covering all functionality
- **🔒 Type Safety** with full mypy support
- **🚀 Production Ready** with comprehensive error handling
- **📚 Well Documented** with extensive examples

### **Test Coverage by Module:**
- **URLs Generator: 100%** - Perfect coverage
- **Models Generator: 99%** - Near perfect
- **Views Generator: 92%** - Excellent
- **Templates Generator: 89%** - Very good
- **Main CLI: 89%** - Excellent
- **Core Package: 100%** - Perfect

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Run tests**: `pytest tests/ --cov=src/`
4. **Submit a pull request**

### Development Setup

```bash
git clone https://github.com/giacomo/dj-maker.git
cd dj-maker
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## 📋 Requirements

- **Python**: 3.10+
- **Django**: 4.2, 5.1, 5.2
- **Dependencies**: Automatically managed via pip

## 🗺️ Roadmap

- [ ] **Template Customization**: Custom template directories
- [ ] **Model Field Inference**: Smart field type detection
- [ ] **Migration Generation**: Automatic migration creation
- [ ] **Testing Generation**: Auto-generate test cases
- [ ] **Docker Integration**: Container-ready project setup
- [ ] **GraphQL Support**: Generate GraphQL schemas

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/giacomo/dj-maker/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/giacomo/dj-maker/discussions)
- **Documentation**: [Wiki](https://github.com/giacomo/dj-maker/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django** community for the amazing framework
- **Typer** for the excellent CLI framework
- **Rich** for beautiful terminal output
- **Jinja2** for powerful templating

---

<div align="center">

**Made with ❤️ by [Giacomo](https://giacomo.dev)**

[⭐ Star us on GitHub](https://github.com/giacomo/dj-maker) | [📦 View on PyPI](https://pypi.org/project/dj-maker/)

</div>
