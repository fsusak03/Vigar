# Vigar - Django REST API Project

**Always follow these instructions first** and only fallback to additional search or context gathering if the information here is incomplete or found to be incorrect.

Vigar is a Django 5.2.5 web application with Django REST Framework, JWT authentication support, and PostgreSQL database integration. The project is in early development with minimal functionality implemented in the core app.

## Working Effectively

### Bootstrap and Setup (REQUIRED FIRST STEPS)
**ALWAYS use native Python setup - Docker build fails due to SSL certificate issues in this environment.**

```bash
# Create virtual environment (takes ~3 seconds)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (takes ~10 seconds in normal environments)
# NOTE: May fail in sandboxed environments due to network/SSL issues
# NEVER CANCEL - set timeout to 60+ seconds minimum
pip install --upgrade pip
pip install -r requirements.txt

# If pip install fails due to network issues, you may need to:
# - Check internet connectivity
# - Try: pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
# - Or install packages individually with --no-deps flag

# Create environment file (required for database config)
# Create .env file manually with the database settings shown below
```

### Environment Configuration
Create a `.env` file with these required variables:
```env
# Database configuration
POSTGRES_DB=vigar
POSTGRES_USER=vigar
POSTGRES_PASSWORD=vigarpass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django configuration  
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
DJANGO_TIME_ZONE=Europe/Sarajevo

# Use SQLite for development (set to True for local development)
USE_SQLITE=True
```

### Database Setup and Migrations
```bash
# Run migrations (takes ~0.4 seconds)
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
# Use: admin / admin@example.com / admin123 for development
```

### Running the Application
```bash
# Development server (starts immediately)
python manage.py runserver

# Server will be available at http://127.0.0.1:8000/
# Admin interface at http://127.0.0.1:8000/admin/
```

### Testing
```bash
# Run Django tests (takes ~0.4 seconds - currently 0 tests exist)
python manage.py test

# Run Django system check (instant)
python manage.py check
```

## Build and Deployment Timing
**Most operations are fast in this project (when network connectivity works):**
- Virtual environment creation: ~3 seconds
- Requirements installation: ~10 seconds (in normal environments) - NEVER CANCEL, set timeout to 60+ seconds minimum
- Database migrations: ~0.4 seconds  
- Test suite: ~0.4 seconds
- Server startup: Immediate
- System check: Instant

**Network issues may cause longer delays or failures during package installation.**

## Known Issues and Limitations

### Network and SSL Issues
**pip install may fail** in sandboxed environments due to:
- SSL certificate verification failures with pypi.org
- Network timeout issues
- Certificate chain validation problems

**If pip install fails, try these alternatives:**
```bash
# Option 1: Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Option 2: Install packages individually 
pip install Django==5.2.5
pip install djangorestframework==3.16.1
# ... continue with each package from requirements.txt

# Option 3: Use system package manager if available
apt-get update && apt-get install python3-django python3-djangorestframework
```

### Docker Setup
**DO NOT USE DOCKER** - The Docker setup fails due to SSL certificate issues with PyPI. The Makefile is also configured for Windows PowerShell and will not work on Linux systems.

### Missing Dependencies
- **PostgreSQL adapter missing**: `psycopg2` is not in requirements.txt. For PostgreSQL support, install with: `pip install psycopg2-binary`
- **Static files configuration**: `STATIC_ROOT` not configured - `collectstatic` command will fail

### Makefile Issues
The Makefile uses PowerShell and will fail on Linux systems:
```makefile
make dev    # FAILS - uses powershell.exe
make prod   # FAILS - uses powershell.exe  
```

Instead use direct commands:
```bash
# For development
source venv/bin/activate && python manage.py runserver

# For Docker (if SSL issues are resolved)
docker compose -f Docker-compose.yml up --build
```

## Validation and Testing

### ALWAYS Run These Validation Steps After Making Changes:
1. **System check**: `python manage.py check`
2. **Run migrations**: `python manage.py migrate` 
3. **Test startup**: `python manage.py runserver` and verify server starts
4. **Admin access**: Visit http://127.0.0.1:8000/admin/ and verify login page loads
5. **API endpoints**: Test any new API endpoints you create

### Manual Testing Scenarios
**ALWAYS test these user scenarios after making changes:**

1. **Admin Interface Test**:
   - Navigate to http://127.0.0.1:8000/admin/
   - Verify login page loads with CSRF token
   - Log in with admin credentials
   - Verify admin dashboard loads

2. **Basic Application Test**:
   - Navigate to http://127.0.0.1:8000/
   - Verify Django welcome page loads (until custom views are added)

3. **Database Connectivity Test**:
   - Run `python manage.py dbshell` (for PostgreSQL)
   - Or check `db.sqlite3` exists (for SQLite mode)

## Project Structure

### Key Locations
- **Main Django project**: `Vigar/` - contains settings, URLs, WSGI config
- **Core application**: `core/` - main app with models, views, tests (currently minimal)
- **Database models**: `core/models.py` (currently empty)
- **API views**: `core/views.py` (currently empty)
- **Tests**: `core/tests.py` (currently empty)
- **Admin config**: `core/admin.py` (currently empty)

### Settings Configuration
- **Database**: Supports both PostgreSQL and SQLite fallback via `USE_SQLITE` env var
- **Debug mode**: Controlled by `DJANGO_DEBUG` env var (default: True)
- **Authentication**: JWT authentication configured via `rest_framework_simplejwt`
- **API framework**: Django REST Framework with filtering and pagination

## Development Workflow

### Adding New Functionality
1. **Always start the server first**: Ensure base setup works
2. **Create/modify models in** `core/models.py`
3. **Run migrations**: `python manage.py makemigrations && python manage.py migrate`
4. **Add views to** `core/views.py`
5. **Update URLs in** `Vigar/urls.py` or create `core/urls.py`
6. **Test immediately**: Run server and test your changes
7. **Add tests to** `core/tests.py` (currently no test framework established)

### API Development
- **DRF configured**: Use Django REST Framework ViewSets and Serializers
- **JWT authentication available**: Configure JWT settings in `Vigar/settings.py`
- **Filtering enabled**: `django_filters` available for queryset filtering
- **Pagination**: Set to 20 items per page by default

## Available Management Commands
Standard Django commands are available:
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py runserver` - Start development server  
- `python manage.py test` - Run tests (currently none)
- `python manage.py check` - System check
- `python manage.py shell` - Django shell
- `python manage.py makemigrations` - Create new migrations

## Common Operations Summary
```bash
# Complete setup from scratch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export USE_SQLITE=True  # For development
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Development cycle
python manage.py check
python manage.py test
python manage.py runserver
# Test at http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/

# Adding new models
# 1. Edit core/models.py
python manage.py makemigrations
python manage.py migrate
# 2. Test immediately
python manage.py runserver
```

This project is in early development - most functionality needs to be implemented in the core app.