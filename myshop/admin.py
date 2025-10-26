from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from .models import Product, Cart, CartItem, Order, OrderItem, Review

AdminSite.site_header = "Administración de la Tienda 3D"
AdminSite.site_title = "Panel de Control - Tienda 3D"
AdminSite.index_title = "Bienvenido al Panel de Administración"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'rating_display')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')
    readonly_fields = ('average_rating', 'review_count')
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'price', 'image_url')
        }),
        ('Categorización', {
            'fields': ('category', 'is_active')
        }),
        ('Inventario', {
            'fields': ('stock',)
        }),
        ('Estadísticas', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )

    def rating_display(self, obj):
        if obj.review_count and obj.review_count > 0:
            stars = '★' * int(obj.average_rating) + '☆' * (5 - int(obj.average_rating))
            return format_html('<span style="color: #ffc107;">{}</span> ({} reseñas)', stars, obj.review_count)
        return 'Sin reseñas'
    rating_display.short_description = 'Valoración'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'shipping_address')
    readonly_fields = ('user', 'total', 'created_at')
    inlines = (OrderItemInline,)

    def save_model(self, request, obj, form, change):
        # Si el estado del pedido ha cambiado, enviar notificación
        if change and 'status' in form.changed_data:
            super().save_model(request, obj, form, change)
            from .utils import send_order_status_update
            try:
                send_order_status_update(obj)
            except Exception:
                # No bloquear el admin si el envío falla
                pass
        else:
            super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_price', 'created_at')
    search_fields = ('user__username',)
    inlines = (CartItemInline,)

    def item_count(self, obj):
        return obj.get_total_items()
    item_count.short_description = 'Cantidad de items'

    def total_price(self, obj):
        return f'${obj.get_total_price()}'
    total_price.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_cost')
    list_filter = ('product',)
    search_fields = ('cart__user__username', 'product__name')

