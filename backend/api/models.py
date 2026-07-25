from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    rating = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_open = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    category = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

# ✅ UPDATED CART MODEL
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    # ✅ Store item details for display
    item_name = models.CharField(max_length=200, blank=True, null=True)
    price = models.IntegerField(default=0)
    restaurant_name = models.CharField(max_length=200, blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.item_name or self.menu_item.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=100)
    items = models.JSONField()
    total = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ], default='Pending')
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


