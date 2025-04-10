from django.contrib import admin
from .models import productListing, Message, ProductRequest, Order
# Register your models here.
admin.site.register(productListing)
admin.site.register(Message)
admin.site.register(ProductRequest)
admin.site.register(Order)