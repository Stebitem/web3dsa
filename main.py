from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.product_list, name='product_list'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),
    path('carrito/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
]
