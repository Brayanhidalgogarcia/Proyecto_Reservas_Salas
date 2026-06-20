"""
Configuración WSGI para el proyecto.

Expone la aplicación WSGI como una variable a nivel de módulo llamada ``application``.
Es el estándar de Python para servidores web y aplicaciones web (síncronas).
Se utiliza típicamente en producción mediante servidores como Gunicorn o uWSGI
para manejar el tráfico HTTP tradicional de la API REST.
"""

import os
from django.core.wsgi import get_wsgi_application

# ==========================================
# 1. CONFIGURACIÓN DEL ENTORNO
# ==========================================
# Le indica a Django dónde encontrar la configuración principal (settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# ==========================================
# 2. INICIALIZACIÓN DE LA APLICACIÓN
# ==========================================
application = get_wsgi_application()