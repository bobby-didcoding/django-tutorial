
from dateutil.relativedelta import *
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


