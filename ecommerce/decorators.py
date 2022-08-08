from functools import wraps
from django.shortcuts import redirect, reverse
from .utils import EcommerceManager

def empty_cart(function):
    """
    Decorator for views that checks if a user cart is empty.
    redirect user to /items/
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        ecommerce_manager = EcommerceManager(user = user)
        cart_obj = ecommerce_manager.cart_object()
        if cart_obj.items.all().count() == 0:
            return redirect(reverse('ecommerce:cart'))
        return function(request, *args, **kwargs)
    return wrap
