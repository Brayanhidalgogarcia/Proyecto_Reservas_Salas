from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Reserva  # Asegúrate de importar tu modelo correctamente

# Esta función se ejecuta CADA VEZ que se guarda (crea o edita) una reserva
@receiver(post_save, sender=Reserva)
def notificar_cambio_reserva(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    
    # Mensaje que enviaremos
    accion = "creada" if created else "actualizada"
    mensaje = f"La sala {instance.sala} ha sido {accion}."

    # Enviamos el mensaje al grupo "reservas_updates" (el mismo nombre que en consumers.py)
    async_to_sync(channel_layer.group_send)(
        "reservas_updates",
        {
            "type": "reserva_update", # Esto debe coincidir con el nombre del método en consumers.py
            "message": mensaje
        }
    )

# Esta función se ejecuta cuando se ELIMINA una reserva
@receiver(post_delete, sender=Reserva)
def notificar_borrado_reserva(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        "reservas_updates",
        {
            "type": "reserva_update",
            "message": f"La reserva de la sala {instance.sala} ha sido eliminada."
        }
    )