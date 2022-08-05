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