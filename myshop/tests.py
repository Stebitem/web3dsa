from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from myshop.models import Product, Cart, CartItem, Order, OrderItem, Review


User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ShopIntegrationTests(TestCase):
    def setUp(self):
        # crear usuario
        self.user = User.objects.create_user(username='buyer', password='pass123', email='buyer@example.com')
        # crear productos
        self.p1 = Product.objects.create(name='Figura A', price=15.00, stock=10, category='figure')
        self.p2 = Product.objects.create(name='Repuesto B', price=7.50, stock=5, category='spare')
        self.client = Client()

    def test_product_listing_and_detail(self):
        resp = self.client.get(reverse('myshop:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Figura A')

        # detalle
        resp = self.client.get(reverse('myshop:product_detail', kwargs={'product_id': self.p1.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.p1.name)

    def test_add_to_cart_and_view(self):
        self.client.login(username='buyer', password='pass123')
        add_url = reverse('myshop:add_to_cart', kwargs={'product_id': self.p1.id})
        resp = self.client.post(add_url, follow=True)
        # add_to_cart returns JsonResponse; after posting we still can fetch cart
        self.assertEqual(resp.status_code, 200)

        cart_url = reverse('myshop:cart')
        resp = self.client.get(cart_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Figura A')

    def test_checkout_creates_order_and_sends_email_and_decrements_stock(self):
        self.client.login(username='buyer', password='pass123')
        # poblar carrito
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.p1, quantity=2)

        checkout_url = reverse('myshop:checkout')
        data = {
            'shipping_address': 'Calle Test 123',
            'phone': '555-1234'
        }
        resp = self.client.post(checkout_url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        # verificar order creada
        orders = Order.objects.filter(user=self.user)
        self.assertTrue(orders.exists())
        order = orders.first()
        self.assertEqual(order.items.count(), 1)

        # stock decrementado
        p = Product.objects.get(id=self.p1.id)
        self.assertEqual(p.stock, 8)

        # carrito vacío
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0)

        # email enviado
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)

    def test_review_submission_updates_product_rating(self):
        self.client.login(username='buyer', password='pass123')
        url = reverse('myshop:product_detail', kwargs={'product_id': self.p1.id})
        resp = self.client.post(url, {'rating': 5, 'comment': 'Excelente'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # review creada
        self.assertTrue(Review.objects.filter(product=self.p1, user=self.user).exists())
        p = Product.objects.get(id=self.p1.id)
        self.assertEqual(p.review_count, 1)
        self.assertGreater(float(p.average_rating), 0)

    def test_checkout_insufficient_stock(self):
        """Si no hay suficiente stock no debe crearse el pedido y mostrar mensaje."""
        self.client.login(username='buyer', password='pass123')
        cart, _ = Cart.objects.get_or_create(user=self.user)
        # p2 tiene stock=5 en setUp
        CartItem.objects.create(cart=cart, product=self.p2, quantity=10)

        checkout_url = reverse('myshop:checkout')
        resp = self.client.post(checkout_url, {'shipping_address': 'Calle X', 'phone': '000'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # No se creó orden
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        # El carrito debe mantenerse con items
        cart.refresh_from_db()
        self.assertGreater(cart.items.count(), 0)

    def test_checkout_missing_fields(self):
        """Si faltan campos en checkout, no crear order y mostrar error."""
        self.client.login(username='buyer', password='pass123')
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.p1, quantity=1)

        checkout_url = reverse('myshop:checkout')
        resp = self.client.post(checkout_url, {'shipping_address': '', 'phone': ''}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.filter(user=self.user).exists())
