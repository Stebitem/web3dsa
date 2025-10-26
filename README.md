# Proyecto Django - Tienda (myshop)

Este repositorio contiene una aplicación Django simple de e-commerce (tienda) con carrito, checkout, órdenes y valoraciones.

## Requisitos

- Python 3.10+ (usar el intérprete del proyecto si corresponde)
- Crear un virtualenv e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración rápida

- Copiar `settings_local.example.py` (si existe) o exportar variables de entorno para las credenciales.
- Recomendado: no almacenar contraseñas en el repositorio. Use variables de entorno:

```powershell
$env:EMAIL_HOST_USER = 'tu_email@dominio.com'
$env:EMAIL_HOST_PASSWORD = 'tu_contraseña'
$env:EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # opcional
$env:DJANGO_DEBUG = 'True' # si quieres forzar console backend en dev
```

Si `EMAIL_BACKEND` no está definido y `DJANGO_DEBUG` está en `'True'`, el sistema usará por defecto `django.core.mail.backends.console.EmailBackend`.

## Migraciones y ejecución

```powershell
# Crear migraciones (si se requiriera)
python manage.py makemigrations
python manage.py migrate
# Crear superusuario
python manage.py createsuperuser
# Ejecutar servidor
python manage.py runserver
```

## Tests

```powershell
python manage.py test
```

## Cambio rápido de backend de email

- Para desarrollo local es útil usar `console` o `locmem` backend. Puede exportar:

```powershell
$env:EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

o modificar `shopproject/settings.py` mediante un `settings_local.py` (no versionar) y ajustar `EMAIL_BACKEND`, `EMAIL_HOST`, etc.

## Notas de seguridad

- El archivo `shopproject/settings.py` fue actualizado para leer credenciales desde variables de entorno. Asegúrate de no commitear secretos.

## Siguientes pasos sugeridos

- Integrar un gateway de pago (Stripe/PayPal) para completar el checkout real.
- Añadir tests de concurrencia y CI.# Tienda de impresión 3D — integración rápida

Archivos añadidos:

- `templates/index.html`: plantilla principal con Bootstrap.
- `myshop/views.py`: vista `index` que pasa una lista de productos de ejemplo.
- `myshop/urls.py`: rutas de la app.

Cómo integrar en tu proyecto Django existente:

1. Asegúrate de tener una app llamada `myshop` o mover `myshop/` al lugar apropiado.
2. En `settings.py` añade `myshop` a `INSTALLED_APPS` si quieres usar modelos o traducciones.
3. Configura plantillas: en `settings.py` confirma que `TEMPLATES` incluye la ruta a `templates/` o usa `BASE_DIR / 'templates'`.

Ejemplo mínimo de `TEMPLATES` (en `settings.py`):

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

4. Incluir las URLs de la app en `urls.py` del proyecto principal:

    from django.urls import path, include

    urlpatterns = [
        path('', include('myshop.urls')),
        path('admin/', admin.site.urls),
    ]

5. Asegúrate de tener las URLs de autenticación (login/logout/signup). Puedes usar `django.contrib.auth` o una app de terceros.

Comandos PowerShell para crear entorno y ejecutar servidor (ejecutar desde la carpeta del proyecto donde está `manage.py`):

```powershell
python -m venv .venv
; .\.venv\Scripts\Activate.ps1
; pip install django
; python manage.py migrate
; python manage.py runserver
```

Notas:
- `myshop/views.py` usa datos de ejemplo en memoria; para una tienda real crea modelos en `myshop/models.py` y administra productos vía admin o panel.
- Si quieres que genere todos los archivos para una app completa (models, formularios, autenticación lista), dime y lo genero.

## Despliegue en Render (guía rápida)

Render es una opción sencilla para desplegar apps Django. Resumen de pasos:

1. Entra en https://render.com y conecta tu repositorio de GitHub.
2. Crea un "Web Service" y elige el repo.
3. Configura:
     - Runtime: Python
     - Build Command: pip install -r requirements.txt
     - Start Command: gunicorn shopproject.wsgi
     - Environment: agrega variables de entorno necesarias:
         - DJANGO_SETTINGS_MODULE=shopproject.settings
         - SECRET_KEY (valor seguro)
         - DATABASE_URL (si usas Postgres en Render)
         - EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_BACKEND (opcional)
     - Asegúrate de ejecutar `python manage.py collectstatic --noinput` durante el build o desde la sección de comandos de build.

4. Activa una base de datos Postgres en Render si la necesitas y pega `DATABASE_URL` en las variables de entorno.
5. Ejecuta migraciones desde la consola de Render:

```powershell
python manage.py migrate
```

Notas:
- Añadimos `whitenoise` y configuración en `shopproject/settings.py` para servir archivos estáticos en despliegues simples.
- `Procfile` fue añadido con `web: gunicorn shopproject.wsgi`.
- Los paquetes necesarios se añadieron a `requirements.txt` (gunicorn, whitenoise, dj-database-url, psycopg2-binary).
