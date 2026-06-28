from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from infrastructure.views.auth_views import home_view, login_view, logout_view
from infrastructure.views.cliente_views import (
    registro_cliente, solicitar_mantencion, solicitud_exitosa,
    buscar_tractor_api, dias_disponibles_api, dashboard_cliente,
)
from infrastructure.views.mecanico_views import (
    dashboard, detalle_orden, lista_ordenes, lista_clientes,
    asignar_orden, iniciar_orden, completar_orden, cancelar_orden, eliminar_orden,
    reprogramar_orden, agregar_nota_interna, editar_nota_interna, eliminar_nota_interna,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("registro/", registro_cliente, name="registro_cliente"),
    path("logout/", logout_view, name="logout"),
    path("cliente/solicitar/", solicitar_mantencion, name="solicitar_mantencion"),
    path("cliente/solicitud/<uuid:orden_id>/", solicitud_exitosa, name="solicitud_exitosa"),
    path("api/buscar-tractor/", buscar_tractor_api, name="buscar_tractor_api"),
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
    path("mecanico/orden/<uuid:orden_id>/reprogramar/", reprogramar_orden, name="reprogramar_orden"),
    path("mecanico/orden/<uuid:orden_id>/nota/", agregar_nota_interna, name="agregar_nota_interna"),
    path("mecanico/nota/<uuid:nota_id>/editar/", editar_nota_interna, name="editar_nota_interna"),
    path("mecanico/nota/<uuid:nota_id>/eliminar/", eliminar_nota_interna, name="eliminar_nota_interna"),
    path("cliente/dashboard/", dashboard_cliente, name="dashboard_cliente"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
