# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/basics_part_2.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout debug
git pull origin debug
```


## Steps/Commands
>Note: Please 'cd' into the root directory and fire up your virtual environment!

1) Install Debug toolbar - Open a terminal and use the following command to install a fantastic package called django-debug-toolbar
```
pip install django-debug-toolbar
pip freeze > requirements.txt
```

2) Register Django debug toolbar - You will need to register the new package in django_course/settings.py. We also need to add some middleware and settings. Copy and paste the following code at the bottom of your settings file.
```
if DEBUG:
    INSTALLED_APPS += 'debug_toolbar', #this is to assist with debugging
    MIDDLEWARE += 'debug_toolbar.middleware.DebugToolbarMiddleware',#needed for django debug toolbar

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

    INTERNAL_IPS = ['127.0.0.1']
```

3) Static files - We will need change the static file settings. Add the following to the django_course/settings.py file
```
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"
```

4) Wire up the url's - Django debug toolbar needs to be added to the django_course/urls.py file.

```
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace="core")),
    path("__debug__/", include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

5) Static and Media - We now need to add new directories to our project to handle static and media files. We will talk more about these later in the course. Add a static and media directory to your root directory to look like this.

```
django_course\  
    core\
        migrations\
            >__init__.py
        >__init__.py
        >admin.py
        >apps.py
        >models.py
        >tests.py
        templates\
            core\
                >index.html
        >urls.py
        >views.py
    django_course\
        >__init__.py
        >asgi.py
        >settings.py
        >urls.py
        >wsgi.py
    media\ <--New directory
    static\ <--New directory
    steps\
        >basics.md
    venv\
        include\
        Lib\
        Scripts\
    >.gitignore
    >manage.py
    >README.md
    >requirements.txt
```

6) Migrations - Let's create some database tables. You can do this by running the following command.

```
python manage.py migrate
```

You should see this log.
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

7) Static - We can use a command called 'collectstatic' to consolidate our projects static files into a new directory. We have called this 'staticfiles' (see step 3). run the following command to collect static files.

```
python manage.py collectstatic
```

After typing 'yes', you should see this log.
```
You have requested to collect static files at the destination
location as specified in your settings:

    C:\Users\Bobby\Development\django_course\staticfiles

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes

135 static files copied to 'C:\Users\Bobby\Development\django_course\staticfiles'.
```

You should now have Django debug toolbar available in your browser!
>Note: Open an incognito browser when testing your project (Ctrl + Shift + N)

* Our django course project is accessible at [http://localhost:8000](http://localhost:8000)
***
***

## Root directory
>Note: If all went well, your root directory should now look like this
```
django_course\  <--This is the root directory
    core\
        __pycache__\
        migrations\
            >__init__.py
        >__init__.py
        >admin.py
        >apps.py
        >models.py
        >tests.py
        templates\
            core\
                >index.html
        >urls.py
        >views.py
    django_course\
        __pycache__\
        >__init__.py
        >asgi.py
        >settings.py
        >urls.py
        >wsgi.py
    media\ <--New directory
    static\ <--New directory
    staticfiles\ <--New directory
    steps\
        >basics.md
        >basics_part_2.md
        >debug.md
    venv\
        include\
        Lib\
        Scripts\
    >.gitignore
    >db.sqlite3
    >manage.py
    >README.md
    >requirements.txt
```

***
***