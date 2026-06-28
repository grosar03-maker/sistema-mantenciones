import uuid

import os
from django.db import models
from django.conf import settings


def imagen_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    return f"ordenes/{instance.orden.id}/{uuid.uuid4()}.{ext}"


class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clientes"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.email})"


class Mecanico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mecánico"
        verbose_name_plural = "Mecánicos"
        db_table = "mecanicos"

    def __str__(self) -> str:
        return f"{self.nombre} - {self.especialidad}"


class ModeloTractor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100, default="Case")

    class Meta:
        verbose_name = "Modelo de Tractor"
        verbose_name_plural = "Modelos de Tractores"
        db_table = "modelos_tractor"

    def __str__(self) -> str:
        return f"{self.marca} {self.nombre}"


class Tractor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_serie = models.CharField(max_length=100, unique=True)
    modelo = models.ForeignKey(
        ModeloTractor, on_delete=models.CASCADE, related_name="tractores"
    )
    propietario = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="tractores"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tractor"
        verbose_name_plural = "Tractores"
        db_table = "tractores"

    def __str__(self) -> str:
        return f"{self.modelo} - S/N: {self.numero_serie}"


class Repuesto(models.Model):
    TIPOS_REPUESTO = [
        ("filtro_combustible", "Filtro de Combustible"),
        ("filtro_aceite", "Filtro de Aceite"),
        ("filtro_aire", "Filtro de Aire"),
        ("lubricante_motor", "Lubricante de Motor"),
        ("lubricante_transmision", "Lubricante de Transmisión"),
        ("lubricante_hidraulico", "Lubricante Hidráulico"),
        ("otro", "Otro"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPOS_REPUESTO)

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        db_table = "repuestos"

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.nombre}"


class ItemCatalogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogo = models.ForeignKey(
        "CatalogoRepuestos", on_delete=models.CASCADE, related_name="items"
    )
    repuesto = models.ForeignKey(
        "Repuesto", on_delete=models.CASCADE, related_name="items_catalogo"
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item del Catálogo"
        verbose_name_plural = "Items del Catálogo"
        db_table = "items_catalogo"
        unique_together = ("catalogo", "repuesto")

    def __str__(self) -> str:
        return f"{self.catalogo} - {self.repuesto.nombre} x{self.cantidad}"


class CatalogoRepuestos(models.Model):
    TIPOS_MANTENCION = [
        ("mant_300h", "300 Horas"),
        ("mant_600h", "600 Horas"),
        ("mant_900h", "900 Horas"),
        ("mant_1200h", "1200 Horas"),
        ("reparacion_general", "Reparación General"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modelo = models.ForeignKey(
        ModeloTractor, on_delete=models.CASCADE, related_name="catalogos"
    )
    tipo_mantencion = models.CharField(max_length=30, choices=TIPOS_MANTENCION)
    repuestos = models.ManyToManyField(Repuesto, through=ItemCatalogo, related_name="catalogos")

    class Meta:
        verbose_name = "Catálogo de Repuestos"
        verbose_name_plural = "Catálogos de Repuestos"
        db_table = "catalogo_repuestos"
        unique_together = ("modelo", "tipo_mantencion")

    def __str__(self) -> str:
        return f"{self.modelo} - {self.get_tipo_mantencion_display()}"


class OrdenMantencion(models.Model):
    TIPOS_MANTENCION = CatalogoRepuestos.TIPOS_MANTENCION

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("asignada", "Asignada"),
        ("en_progreso", "En Progreso"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="ordenes"
    )
    tractor = models.ForeignKey(
        Tractor, on_delete=models.CASCADE, related_name="ordenes"
    )
    mecanico_asignado = models.ForeignKey(
        Mecanico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes",
    )
    tipo_mantencion = models.CharField(max_length=30, choices=TIPOS_MANTENCION)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_solicitud = models.DateTimeField()
    fecha_programada = models.DateField(null=True, blank=True)
    nota_cliente = models.TextField(blank=True, default="")
    repuestos = models.ManyToManyField(Repuesto, related_name="ordenes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Orden de Mantención"
        verbose_name_plural = "Órdenes de Mantención"
        db_table = "ordenes_mantencion"
        ordering = ["-fecha_solicitud"]

    def __str__(self) -> str:
        return (
            f"ORD-{str(self.id)[:8]} - {self.cliente.nombre} - "
            f"{self.get_tipo_mantencion_display()}"
        )


class ImagenOrden(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(
        OrdenMantencion, on_delete=models.CASCADE, related_name="imagenes"
    )
    imagen = models.ImageField(upload_to=imagen_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de Orden"
        verbose_name_plural = "Imágenes de Órdenes"
        db_table = "imagenes_orden"

    def __str__(self) -> str:
        return f"Imagen {self.id} - Orden {self.orden.id}"


class NotaInterna(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(
        OrdenMantencion, on_delete=models.CASCADE, related_name="notas_internas"
    )
    mecanico = models.ForeignKey(
        Mecanico, on_delete=models.SET_NULL, null=True, blank=True
    )
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota Interna"
        verbose_name_plural = "Notas Internas"
        db_table = "notas_internas"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Nota {self.id} - Orden {self.orden.id}"
