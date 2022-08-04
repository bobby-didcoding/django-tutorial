# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/basics_part_2.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout admin
git pull origin admin
```


## Steps/Commands
>Note: Please 'cd' into the root directory and fire up your virtual environment!

1) Create a user - Open a terminal and use the following command to create our first user.
> Note: You'll be prompted to add a username, email and password. Please make a note of these.
```
python manage.py createsuperuser
```

2) Built in admin page - Django has a great built-in admin page for superusers. To access the built-in admin page, fire up your local server and visit [http://localhost:8000/admin](http://localhost:8000/admin)

3) Sign in - You can sign in using the credentials we used in step #1

4) Managing data - After signing in, you will be redirected to your main admin page. Get used to the layout of the admin pages as we will be using them a lot during this course.

5) Shell - We can also check database entires using Django's shell. The Django shell is a Python shell that gives you access to the database API included with Django. Lets go ahead and query our database using the Django shell.

```
python manage.py shell
```
You should see the following in your terminal log
```
Python 3.10.2 (tags/v3.10.2:a58ebcc, Jan 17 2022, 14:12:15) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> 
```
> Note: '>>>' means that the Django shell is working

Now type the following code into the Django shell
```
from django.contrib.auth.models import User
user = User.objects.first()
user.first_name
```
The response should be a '' as we have not set our first name in the database.

Let's add our first name. Add the following to the Django shell.
```
user.first_name = "Bobby"
user.save()
user.first_name
```
The response should be 'Bobby' as we have just committed it to the database by calling .save()

This change will be visible in the built-in admin page. Visit [http://127.0.0.1:8000/admin/auth/user/](http://127.0.0.1:8000/admin/auth/user/) and see for yourself.
> Note: Don't forget to fire up a local server, refresh your browser and sign in if necessary.

6) CRUD - Just like the Django shell, Django's built-in admin page allows you to Create, Read, Update and Delete (CRUD) database entires. To demonstrate this, lets add your last name in the built-in admin page [http://127.0.0.1:8000/admin/auth/user/1/change/](http://127.0.0.1:8000/admin/auth/user/1/change/).

Add your last name and click save or press enter.

You can see now that your name has change. 
Let's bookend this by double checking with the Django shell with the following command.
```
python manage.py shell
from django.contrib.auth.models import User
user = User.objects.first()
user.last_name
```
In my case, the response should be 'Stearman'.

7) Database API - Django's database API is great. We will explore some common features in this course. For now here are some little snippets to start you off. You can find Django's queryset documentation here [https://docs.djangoproject.com/en/4.0/ref/models/querysets/](https://docs.djangoproject.com/en/4.0/ref/models/querysets/) 
```
python manage.py shell
from django.contrib.auth.models import User
#get the first entry in the database table
user = User.objects.first()
#get the last entry in the database table
user = User.objects.last()
#gets a specific record by field(s)
user = User.objects.get(id = 1)
user = User.objects.get(first_name = 'Bobby')
user = User.objects.get(first_name = 'Bobby', last_name="Stearman")

```

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