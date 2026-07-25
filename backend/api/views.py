from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Restaurant, MenuItem, Cart, Order
from .serializers import (
    UserSerializer,
    RestaurantSerializer, MenuItemSerializer,
    CartSerializer, OrderSerializer
)

# ==================== USER VIEWSET ====================
@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email', '')
            
            if not username or not password:
                return Response({'error': 'Username and password required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=400)
            
            user = User.objects.create_user(username=username, password=password, email=email)
            return Response(UserSerializer(user).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            print(f"🔐 Login attempt: username='{username}'")
            
            if not username or not password:
                return Response({'error': 'Username and password required'}, status=400)
            
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                print(f"✅ Login successful: {username}")
                return Response(UserSerializer(user).data)
            
            print(f"❌ Login failed: {username}")
            return Response({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            print(f"❌ Login error: {e}")
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logged out'})


# ==================== RESTAURANT VIEWSET ====================
@method_decorator(csrf_exempt, name='dispatch')
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'])
    def cities(self, request):
        cities = Restaurant.objects.values_list('city', flat=True).distinct()
        return Response(cities)
    
    @action(detail=False, methods=['get'])
    def cuisines(self, request):
        cuisines = Restaurant.objects.values_list('cuisine', flat=True).distinct()
        return Response(cuisines)


# ==================== MENU ITEM VIEWSET ====================
@method_decorator(csrf_exempt, name='dispatch')
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return self.queryset.filter(restaurant_id=restaurant_id)
        return self.queryset


# ==================== CART VIEWSET ====================
@method_decorator(csrf_exempt, name='dispatch')
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return self.queryset.all()
    
    def list(self, request, *args, **kwargs):
        try:
            print("🛒 Cart List Called")
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            print(f"📦 Cart Items Found: {len(serializer.data)}")
            return Response(serializer.data)
        except Exception as e:
            print(f"❌ Cart list error: {e}")
            return Response({'error': str(e)}, status=400)
    
    def create(self, request, *args, **kwargs):
        try:
            print("🛒 Cart Create Called")
            print("📦 Data:", request.data)
            
            data = request.data.copy()
            data['user'] = 1
            
            menu_item_id = data.get('menu_item')
            quantity = int(data.get('quantity', 1))
            
            # Get item details
            item_name = data.get('item_name', '')
            price = int(data.get('price', 0))
            restaurant_name = data.get('restaurant_name', '')
            image = data.get('image', '')
            
            existing = Cart.objects.filter(
                user_id=1,
                menu_item_id=menu_item_id
            ).first()
            
            if existing:
                existing.quantity += quantity
                if item_name:
                    existing.item_name = item_name
                if price:
                    existing.price = price
                if restaurant_name:
                    existing.restaurant_name = restaurant_name
                if image:
                    existing.image = image
                existing.save()
                serializer = self.get_serializer(existing)
                print(f"✅ Updated: {serializer.data}")
                return Response(serializer.data, status=200)
            
            cart_item = Cart.objects.create(
                user_id=1,
                menu_item_id=menu_item_id,
                quantity=quantity,
                item_name=item_name or f'Item {menu_item_id}',
                price=price,
                restaurant_name=restaurant_name or 'Restaurant',
                image=image or ''
            )
            serializer = self.get_serializer(cart_item)
            print(f"✅ Created: {serializer.data}")
            return Response(serializer.data, status=201)
                
        except Exception as e:
            print(f"❌ Cart create error: {e}")
            return Response({'error': str(e)}, status=400)
    
    # ✅ CLEAR CART API
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        try:
            count = Cart.objects.all().delete()
            return Response({'message': f'Cart cleared. {count[0]} items deleted.'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# ==================== ORDER VIEWSET ====================
@method_decorator(csrf_exempt, name='dispatch')
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return self.queryset.all()
    
    def list(self, request, *args, **kwargs):
        try:
            print("📦 Order List Called")
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            print(f"📦 Orders Found: {len(serializer.data)}")
            return Response(serializer.data)
        except Exception as e:
            print(f"❌ Order list error: {e}")
            return Response({'error': str(e)}, status=400)
    
    def create(self, request, *args, **kwargs):
        try:
            print("📦 Order Create Called")
            print("📦 Data:", request.data)
            
            data = request.data.copy()
            data['user'] = 1
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)
                
        except Exception as e:
            print(f"❌ Order create error: {e}")
            return Response({'error': str(e)}, status=400)
    
    def perform_create(self, serializer):
        serializer.save()
    
    # ✅ CANCEL ORDER - UPDATED
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        try:
            print(f"📦 Cancel Order Called for ID: {pk}")
            order = self.get_object()
            
            if order.status == 'Cancelled':
                return Response({'error': 'Order already cancelled'}, status=400)
            
            if order.status == 'Delivered':
                return Response({'error': 'Delivered orders cannot be cancelled'}, status=400)
            
            # ✅ Update status to Cancelled
            order.status = 'Cancelled'
            order.save()
            
            serializer = self.get_serializer(order)
            print(f"✅ Order {pk} cancelled successfully")
            return Response(serializer.data, status=200)
            
        except Exception as e:
            print(f"❌ Cancel order error: {e}")
            return Response({'error': str(e)}, status=400)