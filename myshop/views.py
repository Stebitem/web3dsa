from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Product, Cart, CartItem, Review, Order, OrderItem
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import reverse


def index(request):
    # Sistema de búsqueda y filtrado
    query = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort', '-created_at')
    
    # Obtener todos los productos
    products = Product.objects.all()
    
    # Filtrado por búsqueda
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Filtrado por categoría
    if category:
        products = products.filter(category=category)
    
    # Ordenamiento
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(products, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "products": page_obj,
        "query": query,
        "sort": sort,
        "category": category,
        "year": datetime.now().year,
    }
    return render(request, "index.html", context)


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            
            # Enviar correo de bienvenida
            from .utils import send_welcome_email
            send_welcome_email(user)
            
            return redirect('myshop:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'year': datetime.now().year})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Inicio de sesión exitoso!')
                return redirect('myshop:index')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'year': datetime.now().year})


def logout_view(request):
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('myshop:index')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    user_review = None
    
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            messages.success(request, '¡Gracias por tu valoración!')
            return redirect('myshop:product_detail', product_id=product_id)
        else:
            messages.error(request, 'Por favor completa todos los campos')
    
    context = {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'year': datetime.now().year,
    }
    return render(request, 'product_detail.html', context)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {
        'cart': cart,
        'year': datetime.now().year
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} agregado al carrito')
    return JsonResponse({
        'message': 'Producto agregado al carrito',
        'cart_items': cart.get_total_items()
    })


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('myshop:cart')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return JsonResponse({
        'message': 'Carrito actualizado',
        'subtotal': cart_item.get_cost() if quantity > 0 else 0,
        'cart_total': cart_item.cart.get_total_price() if quantity > 0 else 0
    })


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        if not cart.items.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('myshop:cart')
            
        shipping_address = request.POST.get('shipping_address')
        phone = request.POST.get('phone')
        
        if not shipping_address or not phone:
            messages.error(request, 'Por favor complete todos los campos')
            return redirect('myshop:checkout')
        # Usar una transacción para asegurar atomicidad
        try:
            with transaction.atomic():
                # Verificar stock y calcular total preciso
                total = 0
                items = list(cart.items.select_related('product').all())
                for item in items:
                    if item.product.stock < item.quantity:
                        messages.error(request, f'No hay suficiente stock para {item.product.name}')
                        return redirect('myshop:cart')
                    total += float(item.product.price) * item.quantity

                # Crear el pedido
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    phone=phone,
                    total=total
                )

                # Crear items del pedido y decrementar stock
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    # Decrementar stock
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

                # Limpiar el carrito
                cart.items.all().delete()

            # Enviar correo de confirmación (fuera de la transacción)
            from .utils import send_order_confirmation
            try:
                send_order_confirmation(order)
            except Exception:
                # No bloquear el flujo si falla el envío de correo
                pass

            messages.success(request, '¡Tu pedido ha sido procesado con éxito!')
            return redirect(reverse('myshop:order_detail', kwargs={'order_id': order.id}))
        except Exception as e:
            messages.error(request, 'Ocurrió un error al procesar tu pedido. Intenta nuevamente.')
            return redirect('myshop:checkout')
    
    return render(request, 'checkout.html', {
        'cart': cart,
        'year': datetime.now().year
    })


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {
        'orders': orders,
        'year': datetime.now().year
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {
        'order': order,
        'year': datetime.now().year
    })