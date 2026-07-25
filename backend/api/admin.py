from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, MenuItem, Cart, Order

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cuisine', 'city', 'rating', 'image_preview', 'is_open']
    list_filter = ['city', 'cuisine', 'is_open']
    search_fields = ['name', 'city']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="border-radius:10px; object-fit:cover;" />', obj.image.url)
        return format_html('<span style="color:#999;">No Image</span>')
    image_preview.short_description = 'Image'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'restaurant', 'price', 'category', 'image_preview', 'is_available']
    list_filter = ['category', 'is_available', 'restaurant']
    search_fields = ['name', 'restaurant__name']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:10px; object-fit:cover;" />', obj.image.url)
        return format_html('<span style="color:#999;">No Image</span>')
    image_preview.short_description = 'Image'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'menu_item', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'restaurant_name', 'total', 'status', 'order_date']
    list_filter = ['status']