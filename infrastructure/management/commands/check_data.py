from django.core.management.base import BaseCommand
from infrastructure.models import ModeloTractor, CatalogoRepuestos


class Command(BaseCommand):
    help = "Verifica los datos cargados"

    def handle(self, *args, **options):
        for m in ModeloTractor.objects.all().order_by("nombre"):
            self.stdout.write(f"--- {m.nombre} ---")
            cats = CatalogoRepuestos.objects.filter(modelo=m).order_by("tipo_mantencion")
            for c in cats:
                codigos = [r.codigo for r in c.repuestos.all().order_by("codigo")]
                self.stdout.write(f"  {c.tipo_mantencion}: {c.repuestos.count()} repuestos -> {', '.join(codigos)}")
            self.stdout.write("")
