# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/env.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout shop_part_1
git pull origin shop_part_1
```


## Steps/Commands

>Note: Please 'cd' into the root directory and fire up your virtual environment!

**Warning** we are about to swithc things up a little. This is probably intermediate level but I'll go nice and slowly!!

When putting this course together I was scrathcing my head to figure out what type of website I could use for demo purposes. The concensus I got when asking around was ecommerce! So thats what we're going to do.

It's always good practise to group similar logic into its own application. We have a core app that handles basic webpage logic. We have a users app to handle user specific data. We now need to create an app to handle everything todo with selling products.

> Note: We will be using [Stripe](https://stripe.com/) to handle payments. However, the code we work through can easily be adapted for other payment processing platforms i.e. Braintree. Please go ahead and create a Stripe account as you'll need it to follow along with this tutorial.

Lets get started.

1) New application - If we are grouping e-commerce functionality, I think we should call our app ecommerce. Run the following code to start a new app.
```
django-admin startapp ecommerce
```
Now register our new app in /django_course/settings.py. Update the INSTALLED_APPS variable with the following.

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'ecommerce', # This is our new app
    'users', 
    'django_extensions',
    'djmoney',
]  
```

Whilst you are in settings.py, add the following variables.
```
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE")
```

Now add the following to your .env file.
>Note: You will need your test API keys from [Stripe](https://dashboard.stripe.com/test/apikeys)
```
export STRIPE_PUBLISHABLE_KEY=pk_test_xxx
export STRIPE_SECRET_KEY=sk_test_xxx
```

2) Libraries - There are some great libraries that can help with an e-commerce application. django-money is one of them. Let's get it installed.
```
pip install django-money pycountry requests stripe
pip freeze > requirements.txt
```

3) UserProfile - We need to update our UserProfile model with a few new methods. This will help us with the Stripe integration. Open /users/models.py and replace the code with the following.

```
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import pycountry
from operator import itemgetter

#these are model abstracts from django extensions
from django_extensions.db.models import (
    TimeStampedModel,
	ActivatorModel 
)

country_list = sorted(
        [(country.name, country.name) 
        for country in list(pycountry.countries)], key=itemgetter(0))

country_list.insert(0, ("*Select Country", "*Select Country"))

#(('United Kingdom', 'United Kingdom'), ('France', 'France').....)
COUNTRIES = country_list

class UserProfile(TimeStampedModel,ActivatorModel,models.Model):
    '''
    Our UserProfile model extends the built-in Django User Model
    This is specific to the user! i.e. the individual that signs up
    '''
    class Meta:
        verbose_name_plural = 'User profiles'
        ordering = ["id"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(verbose_name="Contact telephone number", max_length=255, null=True, blank=True)
    address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True)
    town = models.CharField(verbose_name="Town/City",max_length=100, null=True, blank=True)
    county = models.CharField(verbose_name="County",max_length=100, null=True, blank=True)
    post_code = models.CharField(verbose_name="Zip/Post Code",max_length=8, null=True, blank=True)
    country = models.CharField(verbose_name="Country",max_length=100, null=True, blank=True, choices=COUNTRIES)

    longitude = models.CharField(verbose_name="Longitude",max_length=50, null=True, blank=True)
    latitude = models.CharField(verbose_name="Latitude",max_length=50, null=True, blank=True)

    avatar = models.ImageField(default='default_avatar.jpg', upload_to='avatar', null=True, blank=True)

    @property
    def country_alpha_2(self):
        if self.country:
            return pycountry.countries.get(name = self.country).alpha_2
        else:
            return None

    def full_name(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name.capitalize()} {self.user.last_name.capitalize()}'
        if self.user.email:
            return self.user.email
        return self.user.email

    def __str__(self):
        return self.full_name()
    
	
    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return self.user.email

```
Now open /users/forms.py and replace with the following.

```
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, COUNTRIES

class UserForm(UserCreationForm):
	'''
	Form that uses built-in UserCreationForm to handel user creation
	'''
	username = forms.CharField(max_length=150, required=True, widget=forms.TextInput())
	password1 = forms.CharField(required=True, widget=forms.PasswordInput())
	password2 = forms.CharField(required=True, widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'password1', 'password2')



class AuthForm(AuthenticationForm):
	'''
	Form that uses built-in AuthenticationForm to handel user auth
	'''
	username = forms.CharField(max_length=150, required=True, widget=forms.TextInput())
	password = forms.CharField(required=True, widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username','password')



class UserProfileForm(forms.ModelForm):
	'''
	Basic model-form for our user profile
	'''
	avatar = forms.ImageField(required=False)
	telephone = forms.CharField(max_length=255, required=False, widget=forms.TextInput())
	address = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
	town = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
	county = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
	post_code = forms.CharField(max_length=8, required=False, widget=forms.TextInput())
	country = forms.CharField(max_length=100, required=False, widget=forms.TextInput())
	country = forms.CharField(max_length=100, required=False, widget=forms.Select(choices=COUNTRIES))
	
	class Meta:
		model = UserProfile
		fields = ( 'avatar', 'telephone', 'address', 'town', 'county', 'post_code', 'country')


class UserAlterationForm(forms.ModelForm):
	'''
	Basic model-form for our user
	'''
	first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput())
	last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput())
	email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')

```

Now open /users/views.py and replace the code with the following.

```
from django.views import generic
from django.shortcuts import redirect, reverse, render
from django.contrib.auth import logout, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import UserForm, AuthForm, UserProfileForm, UserAlterationForm
from .models import UserProfile

class SignUpView(generic.FormView):
    '''
    Basic view for user sign up
    '''
    template_name = "users/sign_up.html"
    form_class = UserForm
    success_url = '/account/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class SignInView(generic.FormView):
    '''
    Basic view for user sign in
    '''
    template_name = "users/sign_in.html"
    form_class = AuthForm
    success_url = '/account/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


def sign_out(request):
	'''
	Basic view for user sign out
	'''
	logout(request)
	return redirect(reverse('users:sign-in'))


@login_required
def AccountView(request):
    '''
    Basic view for user accounts
    '''
    up = request.user.userprofile
    up_form = UserProfileForm(instance = up)
    context = {'form': up_form}

    if request.method == "POST":
        form = UserProfileForm(instance = up, data = request.POST, files = request.FILES)
        if form.is_valid:
            form.save()
            return redirect('/account/')
    else:
        return render(request, 'users/account.html', context)

@login_required
def UserInfoView(request):
    '''
    Basic view for user info
    '''
    user = request.user
    u_form = UserAlterationForm(instance = user)
    context = {'form': u_form}

    if request.method == "POST":
        form = UserProfileForm(instance = user, data = request.POST)
        if form.is_valid:
            form.save()
            return redirect('/user-info/')
    else:
        return render(request, 'users/info.html', context)



```

Now open /users/urls.py and replace the code with the following.
```
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
	path('sign-up/', views.SignUpView.as_view(), name="sign-up"),
	path('sign-in/', views.SignInView.as_view(), name="sign-in"),
	path('sign-out/', views.sign_out, name="sign-out"),
	path('account/', views.AccountView, name="account"),
	path('user-info/', views.UserInfoView, name="user-info"),
	]
```

Now create a new html file in /templates/users called info.html and add the following code.

```
{% extends 'base/base.html' %}

{% block content %}
<h1>Sign in</h1>
<form method="POST">
    {% csrf_token %}
    {{form.as_p}}
    <button type="submit">Submit!</button>
</form>
{% endblock %}
```
Now open /templates/base/base.html and replace the code with the following.

```
<!DOCTYPE html>
{% load static %}
<html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- visit https://fonts.google.com/specimen/Courier+Prime?preview.text_type=custom to get script-->
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap" rel="stylesheet">

    <!--Bootstrap-->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    
    <!--Our own css-->
    <link rel="stylesheet" href="{% static 'main.css' %}">
    
    {% block extend_head %}<!-- This allows us to extend the head scripts in HTML docs that have special requirements-->{% endblock %}
    </head>
    <body>

    <!--Side nav-->
    {% if request.user.is_authenticated %}
    <ul class="sidenav">
        <li>---------Main menu---------</li>
        <li><a {% if 'account' in request.path %}class="active"{% endif %} href="{% url 'users:account' %}">User Account ({{request.user.username}})</a></li>
        <li><a {% if 'info' in request.path %}class="active"{% endif %}  href="{% url 'users:user-info' %}">User Info</a></li>
        <li><a href="{% url 'users:sign-out' %}">Sign Out</a></li>
    </ul>
    {% else %}
    <ul class="sidenav">
        <li>---------Main menu---------</li>
        <li><a {% if 'sign-in' in request.path %}class="active"{% endif %} href="{% url 'users:sign-in' %}">Sign in</a></li>
        <li><a {% if 'sign-up' in request.path %}class="active"{% endif %} href="{% url 'users:sign-up' %}">Sign up</a></li>
    </ul>
    {% endif %}

    <div class="div-container">
        {% block content %}<!--Used to add code to head-->{% endblock %}
    </div>

    <!--visit https://code.jquery.com/ for jquery script-->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <!--Bootstrap-->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

    {% block extend_foot %}<!-- This allows us to extend the foot scripts in HTML docs that have special requirements-->{% endblock %}

    </body>
</html>
```
Okay, that is everything updated in the users app. Let's crack on with the ecommerce app.

3) Database - We are going to need a whole bunch of new tables in our database. Go ahead and open /ecommerce/models.py and add the following code.

```
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from djmoney.models.fields import MoneyField
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)


class Item(
    TimeStampedModel,
    ActivatorModel ,
    TitleSlugDescriptionModel,
    models.Model):

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ["id"]

    stock = models.IntegerField(default=1.0)
    variable_price = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency='GBP', 
        null=True, 
        blank=True)

    def amount(self):
        amount = int(self.variable_price.amount * 100)
        return amount

class CartItemManager(models.Manager):
    """
    A Manager for Cart item objects
    """
    def get_query_set(self):
        return self.get_queryset()

    def clear_items(self, user):

        qs = self.get_query_set().filter(
            user = user
        )

        for q in qs:
            q.delete()



class CartItem(
    TimeStampedModel,
    ActivatorModel ,
    models.Model):

    class Meta:
        verbose_name = 'Item for cart'
        verbose_name_plural = 'Item for cart'
        ordering = ["id"]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)

    def amount(self):
        amount = self.item.amount() * self.quantity
        return amount

    objects = CartItemManager()


class Cart(
    TimeStampedModel,
    ActivatorModel ,
    models.Model):

    class Meta:
        verbose_name = 'User cart'
        verbose_name_plural = 'User cart'
        ordering = ["id"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)   
    items = models.ManyToManyField(CartItem, blank=True)

    def item_count(self):
        count = 0
        for obj in self.items.all():
            count += obj.quantity
        return count

    def amount(self):
        count = 0
        for obj in self.items.all():
            count += obj.amount()
        return int(count)

    def add_or_remove(self, action, object):
        '''
        Used to easily add or remove users to the cart model
        '''
        match action:
            case "add":
                if object not in self.items.all():
                    self.items.add(object)
            case "remove":
                self.items.remove(object)
        self.save()

    def item_check(self, item):
        cartitems = [i.item  for i in self.items.all()]
        if item in cartitems:
            return True
        return False

    def qty_check(self, item):
        try:
            cart_item = CartItem.objects.get(item = item, user = self.user)
            return cart_item.quantity
        except CartItem.DoesNotExist:
            return 0.0




class Source(
    TimeStampedModel,
    ActivatorModel ,
    models.Model):

    stripe_id = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)



class Line(
    TimeStampedModel,
    ActivatorModel ,
    models.Model):

    class Meta:
        verbose_name = 'Invoice Line'
        verbose_name_plural = 'Invoice Lines'
        ordering = ["id"]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)   
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='GBP', null=True, blank=True)
    stripe_id = models.CharField(max_length=100)
    quantity = models.FloatField(default=1.0, blank=True,null=True)


class Invoice(
    TimeStampedModel,
    ActivatorModel ,
    models.Model):

    class Meta:
        verbose_name = 'User Invoice'
        verbose_name_plural = 'User Invoices'
        ordering = ["id"]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)   
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True) 
    stripe_id = models.CharField(max_length=100)

    lines = models.ManyToManyField(Line, blank=True)

    def item_count(self):
        count = 0
        for obj in self.lines.all():
            count += obj.quantity
        return count

    def amount(self):
        count = 0
        for obj in self.lines.all():
            count += obj.buy_amount * obj.quantity
        return count

    def wallet(self):
        wallet = Wallet.objects.for_source(self.source)
        return wallet

class WalletManager(models.Manager):
    """
    A Manager for Wallet objects
    """
    def get_query_set(self):
        return self.get_queryset()

    def for_source(self, source):
        """
        Returns a Wallet objects queryset for a given source model.
        Usage:
            Source = Source.objects.first()
            Wallet.objects.for_source(Source)
        """
        qs = self.get_query_set().filter(
            sources=source
        )

        return qs

class Wallet(TimeStampedModel, ActivatorModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    invoices = models.ManyToManyField(Invoice, blank=True)
    sources = models.ManyToManyField(Source, blank=True)

    objects = WalletManager()

```

Now commit these changes to the database with the following commands.
```
python manage.py makemigrations
python manage.py migrate
```

***
***

## Root directory
>Note: If all went well, your root directory should now look like this
```
django_course\  <--This is the root directory
    core\
        __pycache__\
        migrations\
            __pycache__\
            >__init__.py
        >__init__.py
        >admin.py
        >apps.py
        >models.py
        >tests.py
        >urls.py
        >views.py
    django_course\
        __pycache__\
        >__init__.py
        >asgi.py
        >settings.py
        >urls.py
        >wsgi.py
    media\
    mediafiles\ 
    static\
        >main.css
    staticfiles\
    steps\
        >account.md
        >admin.md
        >basics.md
        >basics_part_2.md
        >debug.md
        >env.md
        >shop_part_one.md
        >style.md
        >user_app_part_2.md
        >user_app.md
    templates\
        base\
            >base.html
        core\
            >index.html
        users\
            >account.html
            >info.html
            >sign_in.html
            >sign_up.html
    users\
        __pycache__\
        migrations\
            __pycache__\
            >__init__.py
            >0001_initial.py
        >__init__.py
        >admin.py
        >apps.py
        >forms.py
        >models.py
        >signals.py
        >tests.py
        >urls.py
        >views.py
    venv\
        include\
        Lib\
        Scripts\
    .env
    >.gitignore
    >db.sqlite3
    >manage.py
    >README.md
    >requirements.txt
```

***
***