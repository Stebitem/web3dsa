import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','shopproject.settings')
django.setup()
from django.contrib.auth import get_user_model
from myshop.models import Product, Cart, CartItem, Order, OrderItem
User = get_user_model()
# Crear usuario de prueba si no existe
user, created = User.objects.get_or_create(username='testbuyer', defaults={'email':'test@example.com'})
# Crear producto con stock
product, _ = Product.objects.get_or_create(name='Prueba', defaults={'price':10.00, 'stock':5})
# Crear carrito y item
from myshop.models import Cart
cart, _ = Cart.objects.get_or_create(user=user)
cart.items.all().delete()
item = CartItem.objects.create(cart=cart, product=product, quantity=2)
# Simular checkout
items = list(cart.items.select_related('product').all())
total = 0
for it in items:
    if it.product.stock < it.quantity:
        print('Insuficiente stock')
        raise SystemExit(1)
    total += float(it.product.price) * it.quantity
order = Order.objects.create(user=user, shipping_address='Calle Falsa 123', phone='12345678', total=total)
for it in items:
    OrderItem.objects.create(order=order, product=it.product, quantity=it.quantity, price=it.product.price)
    it.product.stock = max(0, it.product.stock - it.quantity)
    it.product.save()
cart.items.all().delete()
print('Checkout simulado OK, order id:', order.id)
