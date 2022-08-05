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



class Wallet(TimeStampedModel, ActivatorModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    invoices = models.ManyToManyField(Invoice, blank=True)
    sources = models.ManyToManyField(Source, blank=True)
