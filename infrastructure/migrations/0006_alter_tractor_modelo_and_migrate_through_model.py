import uuid

from django.db import migrations, models
import django.db.models.deletion


def copy_m2m_data(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='catalogo_repuestos_repuestos'"
        )
        if not cursor.fetchone():
            return
        cursor.execute(
            "SELECT catalogorepuestos_id, repuesto_id FROM catalogo_repuestos_repuestos"
        )
        rows = cursor.fetchall()
        if rows:
            values = []
            for cat_id, rep_id in rows:
                uid = str(uuid.uuid4())
                values.append(f"('{uid}', 1, '{cat_id}', '{rep_id}')")
            cursor.execute(
                "INSERT INTO items_catalogo (id, cantidad, catalogo_id, repuesto_id) VALUES "
                + ",".join(values)
            )
        cursor.execute("DROP TABLE catalogo_repuestos_repuestos")


def reverse_copy(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='items_catalogo'"
        )
        if not cursor.fetchone():
            return
        cursor.execute(
            "CREATE TABLE catalogo_repuestos_repuestos ("
            "    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
            "    catalogorepuestos_id char(32) NOT NULL,"
            "    repuesto_id char(32) NOT NULL"
            ")"
        )
        cursor.execute(
            "SELECT catalogo_id, repuesto_id FROM items_catalogo"
        )
        rows = cursor.fetchall()
        if rows:
            values = []
            for cat_id, rep_id in rows:
                values.append(f"('{cat_id}', '{rep_id}')")
            cursor.execute(
                "INSERT INTO catalogo_repuestos_repuestos (catalogorepuestos_id, repuesto_id) VALUES "
                + ",".join(values)
            )


class Migration(migrations.Migration):

    dependencies = [
        ("infrastructure", "0005_ordenmantencion_nota_cliente_imagenorden_notainterna"),
    ]

    operations = [
        migrations.AlterField(
            model_name="repuesto",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("filtro_combustible", "Filtro de Combustible"),
                    ("filtro_aceite", "Filtro de Aceite"),
                    ("filtro_aire", "Filtro de Aire"),
                    ("lubricante_motor", "Lubricante de Motor"),
                    ("lubricante_transmision", "Lubricante de Transmisión"),
                    ("lubricante_hidraulico", "Lubricante Hidráulico"),
                    ("motor", "Motor"),
                    ("transmision", "Transmisión"),
                    ("cabina", "Cabina"),
                    ("accesorios", "Accesorios"),
                    ("otro", "Otro"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="tractor",
            name="modelo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tractores",
                to="infrastructure.modelotractor",
            ),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE TABLE IF NOT EXISTS items_catalogo ("
                    "    id TEXT NOT NULL PRIMARY KEY,"
                    "    cantidad INTEGER NOT NULL DEFAULT 1,"
                    "    catalogo_id TEXT NOT NULL REFERENCES catalogo_repuestos(id),"
                    "    repuesto_id TEXT NOT NULL REFERENCES repuestos(id)"
                    ")",
                    reverse_sql="DROP TABLE IF EXISTS items_catalogo",
                ),
                migrations.RunPython(copy_m2m_data, reverse_copy),
                migrations.RunSQL(
                    [
                        "CREATE UNIQUE INDEX IF NOT EXISTS items_catalogo_uniq "
                        "ON items_catalogo(catalogo_id, repuesto_id)",
                    ],
                    reverse_sql="DROP INDEX IF EXISTS items_catalogo_uniq",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="ItemCatalogo",
                    fields=[
                        (
                            "id",
                            models.UUIDField(
                                default=uuid.uuid4,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        ("cantidad", models.PositiveIntegerField(default=1)),
                        (
                            "catalogo",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="items",
                                to="infrastructure.catalogorepuestos",
                            ),
                        ),
                        (
                            "repuesto",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="items_catalogo",
                                to="infrastructure.repuesto",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "Item del Catálogo",
                        "verbose_name_plural": "Items del Catálogo",
                        "db_table": "items_catalogo",
                        "unique_together": {("catalogo", "repuesto")},
                    },
                ),
                migrations.AlterField(
                    model_name="catalogorepuestos",
                    name="repuestos",
                    field=models.ManyToManyField(
                        related_name="catalogos",
                        through="infrastructure.ItemCatalogo",
                        to="infrastructure.repuesto",
                    ),
                ),
            ],
        ),
    ]
