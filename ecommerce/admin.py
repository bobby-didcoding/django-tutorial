from django.contrib import admin
from .models import Wallet, Cart, Item, CartItem, Source, Line, Invoice


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id','user')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','user' )

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ('id','created')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id',)
