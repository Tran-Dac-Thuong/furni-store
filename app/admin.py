from django.contrib import admin
from . models import Product, Cart, Contact, Order, Blog
# Register your models here.
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display=['id', 'title', 'price', 'description', 'category', 'image']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display=['id', 'user', 'product', 'quantity']


@admin.register(Contact)
class ContactModelAdmin(admin.ModelAdmin):
    list_display=['id', 'firstname', 'lastname', 'email', 'message', 'created_at']

@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display=['id', 'payment_method', 'quantity', 'total_cost', 'status', 'product_id', 'user_id', 'date']


@admin.register(Blog)
class BlogModelAdmin(admin.ModelAdmin):
    list_display=['id', 'title', 'author', 'content', 'image', 'created_at']