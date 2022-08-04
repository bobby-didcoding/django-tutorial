# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/basics.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout basics_part_2
git pull origin basics_part_2
```


## Steps/Commands
>Note: Please 'cd' into the root directory and fire up your virtual environment!

1) Start application - Open a terminal and use the following command to start a new application
```
django-admin startapp core
```

2) Register application - Open django_course/settings.py and register the new application in INSTALLED_APPS.

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core' #this is our new application
]
```

3) Write a view - Open django_course/core/views.py and write a view to handle the user request/response logic.

```
from django.views import generic

class HomeView(generic.TemplateView):
	template_name = "core/index.html"
```

4) Configure template directory - Django is configured to find HTML files in registered app's. However, to help Django you will need to structure the template directory as follows:

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
                ...
                template go here
                ...
        >views.py
```

5) Create HTMl template - create an index.html file in core/templates/core:

```
<!DOCTYPE html>
<html lang="en">
<head>
</head>
<body>
    <h1>Welcome to our Django course</h1>
</body>
</html>
```

6) Wire up the url - Create a new url.py file to handle url's for the core application.

```
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
	path("", views.HomeView.as_view(), name="home"),
]
```

7) Register the core app url's - Open django_course/urls.py and wire up the core application urls

```
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace="core")), #our bespoke apps
]

```

8) Start a local server - Use the following command to start a local development server

```
python manage.py runserver
```
You should see this log.
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
August 04, 2022 - 12:18:44
Django version 4.0.6, using settings 'django_course.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

You should now be up and running!
>Note: Open an incognito browser when testing your project (Ctrl + Shift + N)

* Our django course project is accessible at [http://localhost:8000](http://localhost:8000)

***
***

## Root directory
>Note: If all went well, your root directory should now look like this
```
django_course\  <--This is the root directory
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
    steps\
        >basics.md
        >basics_part_2.md
    venv\
        include\
        Lib\
        Scripts\
    >.gitignore
    >manage.py
    >README.md
    >requirements.txt
```

***
***