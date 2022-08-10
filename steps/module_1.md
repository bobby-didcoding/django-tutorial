# Django course - Module 1
This is my Django course. I hope you like it.

> These notes follow on from the README.md getting started instructions.
***
***

## Current root directory
Your root directory should look like the following.
```
django_course\  <--This is the root directory
    steps\
        ...
    >.gitignore
    >README.md
```
If in doubt, run the following git commands:
```
git checkout -b module_1
git pull origin module_1
```

## Steps/Commands
You should now have a directory called 'django_course' in your development directory. This will be known as your root directory.

In this module we will be start our project. To do this we will need to create a virtual environment.

1) Open a terminal and use the following command to create a virtual environment
```
python -m venv venv
venv\Scripts\activate.bat
pip install django
django-admin startproject django_course .
pip freeze > requirements.txt
```

***
***

## New Root directory
>Note: If all went well, your root directory should now look like this
```
django_course\  <--This is the root directory
    django_course\
        >__init__.py
        >asgi.py
        >settings.py
        >urls.py
        >wsgi.py
    steps\
        ...
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