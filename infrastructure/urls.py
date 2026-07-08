from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from infrastructure.views.auth_views import home_view, login_view, logout_view
from infrastructure.views.cliente_views import (
    registro_cliente, solicitar_mantencion, solicitud_exitosa,
    dias_disponibles_api, dashboard_cliente,
)
from infrastructure.views.mecanico_views import (
    dashboard, detalle_orden, lista_ordenes, lista_clientes,
    asignar_orden, iniciar_orden, completar_orden, cancelar_orden, eliminar_orden,
    reprogramar_orden, agregar_nota_interna, editar_nota_interna, eliminar_nota_interna,
    listar_modelos, crear_modelo, editar_modelo, eliminar_modelo,
    eliminar_cliente, eliminar_clientes_masivo,
    listar_repuestos, crear_repuesto, editar_repuesto, eliminar_repuesto,
    listar_catalogos, crear_catalogo, eliminar_catalogo,
    agregar_item_catalogo, editar_item_catalogo, eliminar_item_catalogo,
    detalle_mecanico,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("registro/", registro_cliente, name="registro_cliente"),
    path("logout/", logout_view, name="logout"),
    path("cliente/solicitar/", solicitar_mantencion, name="solicitar_mantencion"),
    path("cliente/solicitud/<uuid:orden_id>/", solicitud_exitosa, name="solicitud_exitosa"),
    path("api/dias-disponibles/", dias_disponibles_api, name="dias_disponibles_api"),
    path("mecanico/dashboard/", dashboard, name="dashboard_mecanico"),
    path("mecanico/orden/<uuid:orden_id>/", detalle_orden, name="detalle_orden"),
    path("mecanico/orden/<uuid:orden_id>/asignar/", asignar_orden, name="asignar_orden"),
    path("mecanico/orden/<uuid:orden_id>/iniciar/", iniciar_orden, name="iniciar_orden"),
    path("mecanico/orden/<uuid:orden_id>/completar/", completar_orden, name="completar_orden"),
    path("mecanico/orden/<uuid:orden_id>/cancelar/", cancelar_orden, name="cancelar_orden"),
    path("mecanico/orden/<uuid:orden_id>/eliminar/", eliminar_orden, name="eliminar_orden"),
    path("mecanico/ordenes/", lista_ordenes, name="lista_ordenes"),
    path("mecanico/clientes/", lista_clientes, name="lista_clientes"),
    path("mecanico/clientes/<uuid:cliente_id>/eliminar/", eliminar_cliente, name="eliminar_cliente"),
    path("mecanico/clientes/eliminar-masivo/", eliminar_clientes_masivo, name="eliminar_clientes_masivo"),
    path("mecanico/orden/<uuid:orden_id>/reprogramar/", reprogramar_orden, name="reprogramar_orden"),
    path("mecanico/orden/<uuid:orden_id>/nota/", agregar_nota_interna, name="agregar_nota_interna"),
    path("mecanico/nota/<uuid:nota_id>/editar/", editar_nota_interna, name="editar_nota_interna"),
    path("mecanico/nota/<uuid:nota_id>/eliminar/", eliminar_nota_interna, name="eliminar_nota_interna"),
    path("cliente/dashboard/", dashboard_cliente, name="dashboard_cliente"),
    path("mecanico/modelos/", listar_modelos, name="listar_modelos"),
    path("mecanico/modelos/crear/", crear_modelo, name="crear_modelo"),
    path("mecanico/modelos/<uuid:modelo_id>/editar/", editar_modelo, name="editar_modelo"),
    path("mecanico/modelos/<uuid:modelo_id>/eliminar/", eliminar_modelo, name="eliminar_modelo"),
    path("mecanico/repuestos/", listar_repuestos, name="listar_repuestos"),
    path("mecanico/repuestos/crear/", crear_repuesto, name="crear_repuesto"),
    path("mecanico/repuestos/<uuid:repuesto_id>/editar/", editar_repuesto, name="editar_repuesto"),
    path("mecanico/repuestos/<uuid:repuesto_id>/eliminar/", eliminar_repuesto, name="eliminar_repuesto"),
    path("mecanico/catalogos/", listar_catalogos, name="listar_catalogos"),
    path("mecanico/catalogos/crear/", crear_catalogo, name="crear_catalogo"),
    path("mecanico/catalogos/<uuid:catalogo_id>/eliminar/", eliminar_catalogo, name="eliminar_catalogo"),
    path("mecanico/catalogos/<uuid:catalogo_id>/agregar-item/", agregar_item_catalogo, name="agregar_item_catalogo"),
    path("mecanico/items/<uuid:item_id>/editar/", editar_item_catalogo, name="editar_item_catalogo"),
    path("mecanico/items/<uuid:item_id>/eliminar/", eliminar_item_catalogo, name="eliminar_item_catalogo"),
    path("mecanico/mi-cuenta/", detalle_mecanico, name="detalle_mecanico"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
