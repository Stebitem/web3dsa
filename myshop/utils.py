from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_order_confirmation(order):
    """Envía un correo de confirmación al cliente cuando se realiza un pedido."""
    subject = f'Confirmación de pedido #{order.id}'
    html_message = render_to_string('emails/order_confirmation.html', {
        'order': order,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        fail_silently=False,
    )


def send_order_status_update(order):
    """Envía una notificación cuando el estado del pedido cambia."""
    subject = f'Actualización de pedido #{order.id}'
    html_message = render_to_string('emails/order_status_update.html', {
        'order': order,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        fail_silently=False,
    )


def send_welcome_email(user):
    """Envía un correo de bienvenida cuando un usuario se registra."""
    subject = '¡Bienvenido a nuestra tienda!'
    html_message = render_to_string('emails/welcome.html', {
        'user': user,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )