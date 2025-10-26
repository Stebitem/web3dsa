"""
settings_local.example.py

Copiar este archivo como `settings_local.py` y ajustar valores sensibles.
No commitear `settings_local.py` con credenciales reales.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Seguridad
SECRET_KEY = 'replace-this-in-production'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Email (ejemplo para desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

# Database override (opcional)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
