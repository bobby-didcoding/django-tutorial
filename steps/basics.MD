# Django course
This is my Django course. I hope you like it.

> These notes follow on from the README.md getting started instructions.
***
***


## Steps/Commands
>Note: The first 'cd' command will assume your terminal is already in the root directory. In my case that would be C:\Users\Bobby\Development\django_course
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

## Root directory
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

***
***