import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from infrastructure.models import ImagenOrden


class Command(BaseCommand):
    help = "Elimina imágenes de órdenes con más de 90 días de antigüedad"

    def handle(self, *args, **options):
        corte = timezone.now() - timedelta(days=90)
        imagenes = ImagenOrden.objects.filter(created_at__lt=corte)
        total = imagenes.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No hay imágenes antiguas que eliminar"))
            return

        for img in imagenes:
            if img.imagen and os.path.isfile(img.imagen.path):
                os.remove(img.imagen.path)

        eliminadas = imagenes.delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Se eliminaron {eliminadas} imágenes antiguas (>{90} días)"))
