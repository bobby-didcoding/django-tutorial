# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/shop_part_one.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout shop_part_2
git pull origin shop_part_2
```


## Steps/Commands

>Note: Please 'cd' into the root directory and fire up your virtual environment!

Okay lets start where we left off in the last module. We have built our database tables and we're now ready to create some views.

Lets get started.

1) Views - We are going to need a few new views:
    - Product/item listing page (shop)
    - Product/Item detail page
    - Cart
    - Checkout
    - Payment page

    Open /ecommerce/views.py and add the following code.

```

from django.views import generic
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from . models import Item, CartItem, Source
from .utils import StripeManager
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class ItemsView(generic.ListView):

	model = Item
	template_name = "ecommerce/items.html"
	paginate_by: int = 10

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)

	def get_queryset(self):
		qs = Item.objects.active().filter(stock__gt=0)
		return qs

class ItemView(generic.DetailView):

	model = Item
	template_name = "ecommerce/item.html"

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)


def ajax_required(f):
    """
    AJAX request required decorator
    """
    def wrap(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponseBadRequest('Invalid request')
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


@login_required
@ajax_required
def add_or_remove_item(request):
    '''
    function used to handle the adding and removing of items to cart.
    This is also where we handle stock.
    '''
    data = {"result": "Error","message": "Something went wrong","redirect": False}
    try:
        obj_id = request.POST["object_id"]
    except (KeyError, ValueError):
        data["message"] = 'Invalid request'
        return JsonResponse(data)

    try:
        action = request.POST["action"]
    except (KeyError, ValueError):
        data["message"] = 'Invalid request'
        return JsonResponse(data)

    try:
        item = Item.objects.get(id = obj_id)
    except Item.DoesNotExist:
        data["message"] = 'Object does not exist'
        return JsonResponse(data)
    
    quantity = request.POST.get("object_quantity", 0)
    quantity = int(quantity)
    stock = item.stock
    cart_item, created = CartItem.objects.get_or_create(user = request.user, item = item)
    stripe_manager = StripeManager(request.user)
    cart = stripe_manager.cart_object()

    match action:
        case "remove":
            cart.add_or_remove(action, cart_item)
            qty = cart_item.quantity
            stock = stock + qty
            item.stock = stock
            item.save()
            cart_item.quantity = 0
            cart_item.save()
        case "add":
            if stock < quantity:
                data["message"] = 'Not enough stock'
                return JsonResponse(data)
            qty = cart_item.quantity
            cart.add_or_remove("add", cart_item)
            stock = stock - quantity
            item.stock = stock
            item.save()
            qty += quantity
            cart_item.quantity = qty
            cart_item.save()
    cart.save()

    item_count=cart.item_count()
    item_total_price=cart.amount()
    item_stock=stock
    data = {
            "result": "Success",
            "message": f'{item.content_object.title} has been {action}d to your cart',
            "redirect": False,
            "data": {
                "status": action,
                "item_count": item_count,
                "item_total_price": item_total_price,
                "stock": item_stock
            }
        }
    return JsonResponse(data)


class CartView(generic.TemplateView):
	'''
	View to display a users shopping cart
	'''
	template_name = "ecommerce/cart.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["stripe_key"] = settings.STRIPE_PUBLISHABLE_KEY
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)



class CheckoutView(generic.TemplateView):
    '''
    View to allow users to sign up to a subscription
    '''
    template_name = "ecommerce/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_key"] = settings.STRIPE_PUBLISHABLE_KEY
        stripe_manager = StripeManager(self.request.user)
        context["sources"] = stripe_manager.get_source_data()
        try:
            context["default_card"] = stripe_manager.wallet_object().sources.get(is_default=True)
        except Source.DoesNotExist:
            context["default_card"] = ""
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@login_required
@ajax_required
def stripe_payment(request):

	data = {"result": "Error","message": "Something went wrong","redirect": False}
	token = request.POST.get("stripeToken", None)
	source_id = request.POST.get("card_id", None)
	stripe_manager = StripeManager(request.user, token=token, source_id = source_id)
	invoice = stripe_manager.post_invoice()
	match invoice["status"]:
		case "200"|"201"|"202"|"203"|"204":
			data["redirect"] = "/"
			data["result"] = "Success"
			data["message"] = invoice["message"]
		case _:
			data["message"] = invoice["message"]
	return JsonResponse(data)


@login_required
@ajax_required
def update_source(request):

	data = {"result": "Error","message": "Something went wrong","redirect": False}
	card_id = request.POST.get("card_id", None)
	stripe_manager = StripeManager(request.user)
	stripe_manager.put_source(card_id)
	data["redirect"] = "/checkout/"
	data["result"] = "Success"
	data["message"] = "Your source has been updated"

	return JsonResponse(data)

```
2) URL's - Like always, when we adjust our views we should then make sure we check our url's. In this case we need to create a new file called urls.py in /ecommerce. Create the file and user the following code.

```
from django.urls import path
from . import views

app_name = "ecommerce"

urlpatterns = [

    path('items/', views.ItemsView.as_view(), name='items'),
    path('item/<slug:slug>/', views.ItemView.as_view(), name='item'),
	path('items/add-or-remove/', views.add_or_remove_item, name='add_or_remove'),
	path('checkout/', views.CheckoutView.as_view(), name="checkout"),
	path('pay/', views.stripe_payment, name="pay"),
	path('cart/', views.CartView.as_view(), name="cart"),
	path('update-source/', views.update_source, name="update-source"),
	]
```
You can now register the ecommerce app to the /django_course/urls.py file. use the following code.

```
"""django_course URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace="core")),
    path('', include('ecommerce.urls', namespace="ecommerce")),
    path('', include('users.urls', namespace="users")),
    path("__debug__/", include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
3) Utilities - You will have noticed that the views.py file reference a 'StripeManger'. This is a key piece of the puzzle. It it this manager that we will use to handle the flow of data between the frontend and [Stripes API](https://stripe.com/docs/api?lang=python). Go ahead and create a new file in /ecommerce and call it utils.py. Use the following code.

```
from datetime import datetime
from django.conf import settings
from .models import Wallet, Source, Invoice, Line, CartItem, Cart
from django.contrib.contenttypes.models import ContentType
import pycountry
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeManager:
    '''
    This manager allows us to call a few of Stripe's endpoints. 
    '''
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.up = self.user.userprofile
        self.token = kwargs.get("token")
        self.source_id = kwargs.get("source_id")
        self.invoice_id = kwargs.get("invoice_id")
        self.invoice_item_id = kwargs.get("invoice_item_id")
        self.currency = 'GBP' 
        self.description = 'Django demo'
        

    def stripe_id(self):
        wallet = self.wallet_object()
        if not wallet.stripe_id:
            self.post_profile()			
        return wallet.stripe_id

    def cart_object(self):
        cart, created = Cart.objects.get_or_create(user = self.user)
        return cart

    def wallet_object(self):
        wallet, created = Wallet.objects.get_or_create(user = self.user)
        return wallet

    def source_object(self, id):
        source, created = Source.objects.get_or_create(stripe_id = id)
        if self.token:
            source.is_default = True
            source.save()
        wallet = self.wallet_object()
        wallet.sources.add(source)
        wallet.save()
        return source

    def line_object(self, id, item_obj):
        line, created = Line.objects.get_or_create(stripe_id = id)
        line.item = item_obj.item
        line.user = self.user
        line.quantity = item_obj.quantity
        line.sell_amount = item_obj.amount() / 100
        line.buy_amount = item_obj.amount() / 100
        line.amount_currency = self.wallet_object().currency
        line.save()
        return line

    def invoice_object(self, id, items, source_id):
        invoice, created = Invoice.objects.get_or_create(stripe_id = id)
        for item in items:
            invoice.lines.add(item)
            invoice.save()
        invoice.user = self.user
        invoice.source = Source.objects.get(stripe_id = source_id)
        invoice.save()
        wallet = self.wallet_object()
        wallet.invoices.add(invoice)
        wallet.save()
        return invoice

    def create_stripe_address(self):
        address={
            "line1":self.up.address,
            "city":self.up.town,
            "state":self.up.county,
            "postal_code": self.up.post_code,
            "country": self.up.country_alpha_2
            }
        return address

    def post_profile(self):
        stripe_customer = stripe.Customer.create(
            email = self.user.email, 
            name = self.up.full_name(),
            address = self.create_stripe_address()
            )
        wallet = self.wallet_object()
        wallet.stripe_id = stripe_customer["id"]
        wallet.save()
        return stripe_customer

    def put_profile(self):
        stripe_customer = stripe.Customer.modify(
            self.stripe_id(),
            email = self.up.email(), 
            name = self.up.full_name(),
            address = self.create_stripe_address()
            )
        return stripe_customer

    def get_profile(self):
        stripe_customer = stripe.Customer.retrieve(
            self.stripe_id(),
            )
        return stripe_customer

    def list_sources(self):
        try:
            sources = stripe.Customer.list_sources(self.stripe_id(),limit=3,object='card')
        except TypeError:
            sources = []
        return sources

    def get_source(self):
        source = stripe.Customer.retrieve_source(self.stripe_id(),self.source_id)
        return source

    def put_source(self, source_id):
        source = stripe.Customer.retrieve_source(self.stripe_id(),source_id)
        put_source = stripe.Customer.modify(
                    self.stripe_id(), 
                    default_source=source["id"],
                    )
        source_obj = self.source_object(source["id"])
        source_obj.is_default = True
        source_obj.save()
        return put_source

    def post_source(self):
        stripe_id = self.stripe_id()
        source = stripe.Customer.create_source(
            stripe_id,
            source=self.token
            )
        self.put_source(source["id"])
        return source

    def get_invoice_item(self):
        invoice_item = stripe.InvoiceItem.retrieve(self.invoice_item_id)
        return invoice_item

    def put_invoice_item(self):
        invoice_item = stripe.InvoiceItem.modify(self.invoice_item_id)
        return invoice_item

    def post_invoice_item(self, item):
        quantity = int(item.quantity)
        amount = int(item.amount())
        unit_amount = int(amount / quantity)
        line = stripe.InvoiceItem.create(
            customer= self.stripe_id(),
            unit_amount= unit_amount,
            quantity = int(item.quantity),
            currency=self.currency.lower(),
            description= item.item.content_object.title
            )
        line = self.line_object(line["id"], item)

        invoice_item = stripe.InvoiceItem.create(
                customer= self.stripe_id(),
                unit_amount= unit_amount,
                quantity = int(item.quantity),
                currency=self.currency.lower(),
                description= self.description
            )
        return line

    def list_invoices(self):
        invoices = stripe.Invoice.list(self.stripe_id())
        return invoices

    def get_source_data(self):

        source_data = {"sources":{},"has_sources":False}
        try:
            sources = self.list_sources()
            customer = self.get_profile()
            default_source = customer["default_source"]
            source_obj = self.source_object(default_source)
            source_obj.is_default = True
            source_obj.save()
            exclude_id = [source_obj.id]
            #manage default
            user_sources = self.wallet_object().sources.exclude(id__in=exclude_id)
            for source in user_sources:
                source.is_default = False
                source.save()
            source_list = []
            for source in sources["data"]:
                source_info = {"id": "", "stripe_id": "", "type": "", "card": "", "exp": "", "default": ""}
                date = datetime.strptime(f'{source["exp_month"]}/{source["exp_year"]}', '%m/%Y')
                date2 = date + relativedelta(months=+1)
                exp_date = date2 + relativedelta(days=-1)
                today = date.today()

                source_obj = self.source_object(source["id"])
                if today <= exp_date:
                    source_info["id"] = source_obj.id
                    source_info["stripe_id"] = source["id"]
                    source_info["type"] = source["brand"]
                    source_info["default"] = source_obj.is_default
                    source_info["card"] = f'**** {source["last4"]}'

                    if source["exp_month"] < 9:
                        mnt = f'0{source["exp_month"]}'
                    else:
                        mnt = source["exp_month"]

                    year = source["exp_year"] - 2000
                    source_info["exp"] = f'{mnt}/{year}'
                    
                source_list.append(source_info)
            source_data["has_sources"] = True
            source_data["sources"] = source_list
        except:
            return source_data
        return source_data
        
    def get_invoice_data(self):

        invoice_data = {"invoices":{},"has_invoices":False}
        try:
            invoices = self.list_invoices()
            invoice_list = []
            for invoice in invoices["data"]:
                invoice_info = {
                    "invoice_id": invoice["id"], 
                    "invoice_url": invoice["hosted_invoice_url"], 
                    "invoice_pdf": invoice["invoice_pdf"], 
                    "invoice_description": invoice["lines"]["data"][0]["description"],
                    "invoice_total": invoice["amount_paid"]/100,
                    "invoice_paid": invoice["paid"],
                    "invoice_date": datetime.fromtimestamp(int(invoice["created"])).strftime('%d-%m-%Y'),
                    }

                invoice_list.append(invoice_info)
            invoice_data["has_invoices"] = True
            invoice_data["invoices"] = invoice_list

        except:
            return invoice_data
        return invoice_data

    def get_invoice(self):
        invoice = stripe.Invoice.retrieve(self.invoice_id)
        invoice_info = {
                    "invoice_id": invoice["id"], 
                    "invoice_url": invoice["hosted_invoice_url"], 
                    "invoice_pdf": invoice["invoice_pdf"], 
                    "invoice_description": invoice["lines"]["data"][0]["description"],
                    "invoice_total": invoice["amount_paid"]/100,
                    "invoice_paid": invoice["paid"],
                    "invoice_date": datetime.fromtimestamp(int(invoice["created"])).strftime('%d-%m-%Y'),
                    }
        return invoice_info

    def post_invoice(self):

        cart = self.cart_object()
        amount = cart.amount

        if self.token:
            source = self.post_source()
            self.source_id = source["id"]
        
        #create invoice items
        items = []
        for item in cart.items.all():
            items.append(self.post_invoice_item(item))
        
        #created invoice items will automatically be added to this invoice
        new_invoice = stripe.Invoice.create(
            customer=self.stripe_id(),
            collection_method="charge_automatically",
        )

        #manually finalize the invoice before making a payment request
        invoice = stripe.Invoice.finalize_invoice(new_invoice.id)

        try:
            #pay the invoice
            stripe.Invoice.pay(
                invoice.id,
                source=self.source_id,
                )

            invoice = self.invoice_object(invoice.id, items, self.source_id)

            
        except stripe.error.CardError as e:
            message = "Card Error"
            status = "500"
            return {"status": status, "message": message}

        except stripe.error.RateLimitError as e:
            message = "Rate limit error"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.InvalidRequestError as e:
            message = "Invalid parameter"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.AuthenticationError as e:
            message = "Not authenticated"
            status = "500"
            return {"status": status, "message": message}

        except stripe.error.APIConnectionError as e:
            message = "Network error"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.StripeError as e:
            message = "Something went wrong, you were not charged"
            status = "500"
            return {"status": status, "message": message}
        
        except Exception as e:
            message = "Serious error, we have been notified"
            status = "500"
            return {"status": status, "message": message}

        #clear carts
        CartItem.objects.clear_items(self.user)
        
        message = "Success! Your payment was successful"
        status = "200"
        return {"status": status, "message": message, "id":invoice.id}

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
    ecommerce\
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
        >utils.py
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