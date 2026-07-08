from django.contrib import admin

from infrastructure.models import (
    Cliente,
    Mecanico,
    ModeloTractor,
    Tractor,
    Repuesto,
    CatalogoRepuestos,
    OrdenMantencion,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono")
    search_fields = ("nombre", "email")


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "especialidad")
    search_fields = ("nombre", "email")


@admin.register(ModeloTractor)
class ModeloTractorAdmin(admin.ModelAdmin):
    list_display = ("marca", "nombre", "tipo")
    list_filter = ("tipo", "marca")
    search_fields = ("nombre",)


@admin.register(Tractor)
class TractorAdmin(admin.ModelAdmin):
    list_display = ("numero_serie", "modelo", "propietario")
    search_fields = ("numero_serie",)


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo")
    list_filter = ("tipo",)
    search_fields = ("codigo", "nombre")


@admin.register(CatalogoRepuestos)
class CatalogoRepuestosAdmin(admin.ModelAdmin):
    list_display = ("modelo", "tipo_mantencion")
    list_filter = ("tipo_mantencion", "modelo")


@admin.register(OrdenMantencion)
class OrdenMantencionAdmin(admin.ModelAdmin):
    list_display = ("id_corto", "cliente", "tractor", "tipo_mantencion", "estado", "fecha_solicitud")
    list_filter = ("estado", "tipo_mantencion")
    filter_horizontal = ("repuestos",)
    date_hierarchy = "fecha_solicitud"

    def id_corto(self, obj):
        return str(obj.id)[:8]
    id_corto.short_description = "ID"
