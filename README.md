# Crowdfunding Project

A Django-based crowdfunding platform built with Tailwind CSS, HTMX, and modern tooling.

## Project Structure

```
crowdfunding-project/
├── CrowdfundingProject/       # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   ├── views.py              # Project-level views
│   ├── asgi.py               # ASGI configuration
│   └── wsgi.py               # WSGI configuration
│
├── user/                     # User app
│   ├── __init__.py
│   ├── admin.py              # Admin configuration
│   ├── apps.py               # App configuration
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── urls.py               # App-specific URL patterns
│   ├── tests.py              # Unit tests
│   ├── migrations/           # Database migrations
│   └── templates/            # App-specific templates
│       └── user/
│           └── hello.html
│
├── theme/                    # Tailwind CSS theme app
│   ├── __init__.py
│   ├── apps.py
│   ├── static/               # Compiled static files
│   │   └── css/
│   ├── static_src/           # Source files for Tailwind
│   │   ├── package.json      # Node.js dependencies
│   │   ├── postcss.config.js # PostCSS configuration
│   │   └── src/
│   │       └── styles.css    # Tailwind CSS source
│   └── templates/
│       └── base.html         # Base template
│
├── templates/                # Project-level templates
│   └── home.html
│
├── manage.py                 # Django management script
├── db.sqlite3                # SQLite database
├── pyproject.toml            # Python project metadata and dependencies
├── requirements.txt          # Frozen dependencies (auto-generated)
├── uv.lock                   # UV lock file
├── Procfile.tailwind         # Process file for running Tailwind
└── README.md                 # This file
```

## Technology Stack

- **Django 5.2.8** - Web framework
- **django-tailwind 4.4.1** - Tailwind CSS integration
- **django-htmx 1.26.0** - HTMX support for dynamic interactions
- **django-browser-reload 1.21.0** - Live reload during development
- **UV** - Fast Python package manager

## Setup Instructions

### Prerequisites

- Python 3.13 or higher
- Node.js and npm (for Tailwind CSS)

### Option 1: Using UV (Recommended)

UV is a fast Python package manager. If you don't have it installed:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then set up the project:

```bash
# Clone the repository
git clone <repository-url>
cd crowdfunding-project

# Sync dependencies with UV
uv sync

# Install Tailwind CSS dependencies
cd theme/static_src
npm install
cd ../..

# Run migrations
uv run python manage.py migrate
```

### Option 2: Using pip and requirements.txt

```bash
# Clone the repository
git clone <repository-url>
cd crowdfunding-project

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tailwind CSS dependencies
cd theme/static_src
npm install
cd ../..

# Run migrations
python manage.py migrate
```

## Running the Development Server

This project uses **Tailwind CSS** which requires running two processes simultaneously:

### Using Honcho (Recommended)

The project includes a `Procfile.tailwind` for running both Django and Tailwind:

```bash
# With UV
uv run honcho -f Procfile.tailwind start

# Or with pip
honcho -f Procfile.tailwind start
```

### Manual Method

Run these commands in separate terminal windows:

**Terminal 1 - Django development server:**

```bash
# With UV
uv run python manage.py runserver

# Or with pip
python manage.py runserver
```

**Terminal 2 - Tailwind CSS compiler:**

```bash
# With UV
uv run python manage.py tailwind start

# Or with pip
python manage.py tailwind start
```

The application will be available at `http://localhost:8000/`

## Adding Code to the Project

### Creating a New App

```bash
# With UV
uv run python manage.py startapp app_name

# Or with pip
python manage.py startapp app_name
```

Then add the app to `INSTALLED_APPS` in `CrowdfundingProject/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    "app_name",
]
```

### Adding a New View

1. **Create a view function** in `your_app/views.py`:

```python
from django.shortcuts import render

def my_view(request):
    context = {'message': 'Hello World'}
    return render(request, 'your_app/template.html', context)
```

2. **Create a template** in `your_app/templates/your_app/template.html`:

```html
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>My Page</title>
    {% tailwind_css %}
  </head>
  <body>
    <h1>{{ message }}</h1>
  </body>
</html>
```

3. **Add URL pattern** in `your_app/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'your_app'

urlpatterns = [
    path('my-route/', views.my_view, name='my_view'),
]
```

4. **Include app URLs** in `CrowdfundingProject/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('your_app.urls')),
    # ... other patterns
]
```

### Creating Database Models

1. **Define models** in `your_app/models.py`:

```python
from django.db import models

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

2. **Create and apply migrations**:

```bash
# With UV
uv run python manage.py makemigrations
uv run python manage.py migrate

# Or with pip
python manage.py makemigrations
python manage.py migrate
```

3. **Register in admin** (optional) in `your_app/admin.py`:

```python
from django.contrib import admin
from .models import MyModel

admin.site.register(MyModel)
```

### Using Tailwind CSS Classes

All templates have access to Tailwind CSS. Simply use Tailwind classes in your HTML:

```html
<div class="container mx-auto">
  <h1 class="text-4xl font-bold text-blue-600">Hello!</h1>
  <button
    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
  >
    Click Me
  </button>
</div>
```

### Adding HTMX Interactions

HTMX is already configured. Add `hx-` attributes to enable dynamic behavior:

```html
<button hx-get="/api/data/" hx-target="#result">Load Data</button>
<div id="result"></div>
```

## Common Django Commands

```bash
# Create a superuser for admin panel
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files for production
python manage.py collectstatic

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## Development Workflow

1. Make changes to Python code (views, models, etc.)
2. Browser auto-reloads thanks to `django-browser-reload`
3. Make changes to templates with Tailwind classes
4. Tailwind compiler automatically rebuilds CSS
5. Browser reflects changes immediately

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [HTMX Documentation](https://htmx.org/docs/)
- [UV Documentation](https://docs.astral.sh/uv/)

## Disclaimer

This project was scaffolded with the assistance of LLMs.
