from django.db import migrations


def seed_tipos_mantencion(apps, schema_editor):
    TipoMantencion = apps.get_model("infrastructure", "TipoMantencion")
    tipos = [
        {"horas": 300, "nombre": "300 Horas", "codigo": "mant_300h"},
        {"horas": 600, "nombre": "600 Horas", "codigo": "mant_600h"},
        {"horas": 900, "nombre": "900 Horas", "codigo": "mant_900h"},
        {"horas": 1200, "nombre": "1200 Horas", "codigo": "mant_1200h"},
        {"horas": 0, "nombre": "Reparación General", "codigo": "reparacion_general"},
    ]
    for t in tipos:
        TipoMantencion.objects.get_or_create(
            horas=t["horas"],
            defaults={"nombre": t["nombre"], "codigo": t["codigo"]},
        )


def seed_marcas(apps, schema_editor):
    Marca = apps.get_model("infrastructure", "Marca")
    ModeloTractor = apps.get_model("infrastructure", "ModeloTractor")
    marcas_existentes = ModeloTractor.objects.values_list("marca", flat=True).distinct()
    for nombre in marcas_existentes:
        Marca.objects.get_or_create(nombre=nombre)


class Migration(migrations.Migration):

    dependencies = [
        ("infrastructure", "0010_marca_tipomantencion"),
    ]

    operations = [
        migrations.RunPython(seed_tipos_mantencion, migrations.RunPython.noop),
        migrations.RunPython(seed_marcas, migrations.RunPython.noop),
    ]
