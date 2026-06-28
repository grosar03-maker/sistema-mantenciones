import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from infrastructure.models import ModeloTractor, Repuesto, CatalogoRepuestos, ItemCatalogo


def _clasificar_tipo(nombre):
    n = nombre.lower().replace("ó", "o").replace("í", "i").replace("á", "a").replace("é", "e").replace("ú", "u")
    if "aceite motor" in n:
        return "lubricante_motor"
    if "aceite" in n and ("transmision" in n or "cvx" in n):
        return "lubricante_transmision"
    if "hidraulico" in n:
        return "lubricante_hidraulico"
    if "aceite" in n:
        return "lubricante_motor"
    if "combustible" in n:
        return "filtro_combustible"
    if "aire" in n:
        return "filtro_aire"
    return "otro"


MANT_COLUMNS = {
    "Mant_300h": "mant_300h",
    "Mant_600h": "mant_600h",
    "Mant_900h": "mant_900h",
    "Mant_1200h": "mant_1200h",
}


class Command(BaseCommand):
    help = "Carga catálogo de repuestos desde archivo CSV de Case CNH"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="?", type=str, default="catalogo_case.csv")

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.is_absolute():
            csv_path = Path(__file__).resolve().parent.parent.parent / csv_path
        if not csv_path.exists():
            self.stderr.write(f"Archivo no encontrado: {csv_path}")
            return

        modelos_vistos = {}
        repuestos_vistos = {}
        catalogo_rows = {}  # (modelo_nombre, tipo_mant) -> set of repuesto_ids

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                modelo_nombre = row["Modelo_Tractor"].strip()

                if modelo_nombre not in modelos_vistos:
                    modelo, _ = ModeloTractor.objects.get_or_create(
                        nombre=modelo_nombre, defaults={"marca": "Case"}
                    )
                    modelos_vistos[modelo_nombre] = modelo

                codigo = row["Codigo_CNH"].strip()
                nombre_parte = row["Tipo_Filtro"].strip()
                tipo_repuesto = _clasificar_tipo(nombre_parte)

                if codigo not in repuestos_vistos:
                    repuesto, _ = Repuesto.objects.get_or_create(
                        codigo=codigo,
                        defaults={"nombre": nombre_parte, "tipo": tipo_repuesto},
                    )
                    repuestos_vistos[codigo] = repuesto

                for col_mant, tipo_mant in MANT_COLUMNS.items():
                    accion = row[col_mant].strip()
                    if accion == "No Tocar":
                        continue
                    key = (modelo_nombre, tipo_mant)
                    if key not in catalogo_rows:
                        catalogo_rows[key] = set()
                    catalogo_rows[key].add(codigo)

        count_modelos = len(modelos_vistos)
        count_repuestos = len(repuestos_vistos)

        for (modelo_nombre, tipo_mant), codigos in catalogo_rows.items():
            modelo = modelos_vistos[modelo_nombre]
            catalogo, created = CatalogoRepuestos.objects.get_or_create(
                modelo=modelo, tipo_mantencion=tipo_mant
            )
            existing = {it.repuesto_id for it in ItemCatalogo.objects.filter(catalogo=catalogo)}
            for c in codigos:
                repuesto = repuestos_vistos[c]
                if repuesto.id not in existing:
                    ItemCatalogo.objects.create(catalogo=catalogo, repuesto=repuesto, cantidad=1)

        count_catalogos = len(catalogo_rows)

        self.stdout.write(self.style.SUCCESS(
            f"OK: {count_modelos} modelos, {count_repuestos} repuestos, "
            f"{count_catalogos} catálogos creados/actualizados"
        ))
