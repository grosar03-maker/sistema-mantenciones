import json
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from application.use_cases.asignar_mecanico import AsignarMecanico
from application.use_cases.cancelar_mantencion import CancelarMantencion
from application.use_cases.iniciar_mantencion import IniciarMantencion
from application.use_cases.completar_mantencion import CompletarMantencion
from domain.value_objects.estado_orden import EstadoOrden
from infrastructure.mail_service.adapters.servicio_notificacion_email import ServicioNotificacionEmail
from infrastructure.models import Cliente, Mecanico, ModeloTractor, Repuesto, CatalogoRepuestos, ItemCatalogo, OrdenMantencion
from infrastructure.persistence.adapters.repositorio_mecanico_sql import RepositorioMecanicoSQL
from infrastructure.persistence.adapters.repositorio_orden_mantencion_sql import RepositorioOrdenMantencionSQL


def _mecanico_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name="mecanicos").exists():
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@login_required
@_mecanico_required
def dashboard(request):
    ordenes = OrdenMantencion.objects.select_related(
        "cliente", "tractor__modelo", "mecanico_asignado", "modelo"
    ).prefetch_related("repuestos").all()

    mecanico = Mecanico.objects.filter(email=request.user.email).first()

    pendientes = [o for o in ordenes if o.estado == "pendiente"]
    asignadas = [o for o in ordenes if o.estado == "asignada"]
    en_progreso = [o for o in ordenes if o.estado == "en_progreso"]

    dias_con_ordenes = (
        OrdenMantencion.objects.filter(
            fecha_programada__isnull=False,
        )
        .exclude(estado__in=("cancelada", "completada"))
        .values_list("fecha_programada", flat=True)
        .distinct()
    )
    dias_ocupados_json = json.dumps([d.isoformat() for d in dias_con_ordenes])

    ordenes_activas = [o for o in ordenes if o.estado in ("pendiente", "asignada", "en_progreso")]

    return render(request, "mecanico/dashboard.html", {
        "ordenes_pendientes": pendientes,
        "ordenes_asignadas": asignadas,
        "ordenes_en_progreso": en_progreso,
        "total_ordenes": len(ordenes_activas),
        "mecanico": mecanico,
        "dias_ocupados_json": dias_ocupados_json,
        "hoy_iso": date.today().isoformat(),
    })


@login_required
@_mecanico_required
def detalle_orden(request, orden_id):
    orden = get_object_or_404(
        OrdenMantencion.objects.select_related(
            "cliente", "tractor__modelo", "tractor__propietario", "mecanico_asignado", "modelo"
        ).prefetch_related("repuestos", "imagenes", "notas_internas__mecanico"),
        id=orden_id,
    )

    repuestos_agrupados = {
        "Filtros": [],
        "Lubricantes": [],
        "Otros": [],
    }
    for r in orden.repuestos.all():
        if "filtro" in r.tipo:
            repuestos_agrupados["Filtros"].append(r)
        elif "lubricante" in r.tipo:
            repuestos_agrupados["Lubricantes"].append(r)
        else:
            repuestos_agrupados["Otros"].append(r)

    mecanico_actual = Mecanico.objects.filter(email=request.user.email).first()
    mecanicos = Mecanico.objects.all()
    imagenes = orden.imagenes.all()
    notas_internas = orden.notas_internas.all().order_by("-created_at")

    return render(request, "mecanico/detalle_orden.html", {
        "orden": orden,
        "repuestos_agrupados": repuestos_agrupados,
        "mecanicos": mecanicos,
        "mecanico": mecanico_actual,
        "es_mi_orden": orden.mecanico_asignado == mecanico_actual if orden.mecanico_asignado else False,
        "imagenes": imagenes,
        "notas_internas": notas_internas,
    })


@login_required
@_mecanico_required
def lista_ordenes(request):
    qs = OrdenMantencion.objects.select_related(
        "cliente", "tractor__modelo", "mecanico_asignado", "modelo"
    ).prefetch_related("repuestos").all()

    numero_serie = request.GET.get("numero_serie", "").strip()
    cliente_nombre = request.GET.get("cliente", "").strip()
    fecha_desde = request.GET.get("fecha_desde", "").strip()
    fecha_hasta = request.GET.get("fecha_hasta", "").strip()
    estado = request.GET.get("estado", "").strip()

    if numero_serie:
        qs = qs.filter(
            Q(tractor__numero_serie__icontains=numero_serie)
            | Q(numero_serie_cliente__icontains=numero_serie)
        )
    if cliente_nombre:
        qs = qs.filter(cliente__nombre__icontains=cliente_nombre)
    if fecha_desde:
        qs = qs.filter(fecha_programada__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_programada__lte=fecha_hasta)
    if estado:
        qs = qs.filter(estado=estado)

    ordenes = qs

    mecanico = Mecanico.objects.filter(email=request.user.email).first()

    estados_opciones = [
        ("pendiente", "Pendiente"),
        ("asignada", "Asignada"),
        ("en_progreso", "En Progreso"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    ]

    return render(request, "mecanico/lista_ordenes.html", {
        "ordenes": ordenes,
        "mecanico": mecanico,
        "filtros": {
            "numero_serie": numero_serie,
            "cliente": cliente_nombre,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "estado": estado,
        },
        "estados": estados_opciones,
    })


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def asignar_orden(request, orden_id):
    mecanico_id = request.POST.get("mecanico_id")
    if not mecanico_id:
        messages.error(request, "Debe seleccionar un mecánico")
        return redirect("detalle_orden", orden_id=orden_id)

    repo_mecanico = RepositorioMecanicoSQL()
    mecanico = repo_mecanico.obtener_por_id(mecanico_id)
    if not mecanico:
        messages.error(request, "Mecánico no encontrado")
        return redirect("detalle_orden", orden_id=orden_id)

    caso_uso = AsignarMecanico(
        repo_orden=RepositorioOrdenMantencionSQL(),
        notificador=ServicioNotificacionEmail(),
    )

    try:
        caso_uso.ejecutar(orden_id, mecanico)
        messages.success(request, f"Orden asignada a {mecanico.nombre}")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def iniciar_orden(request, orden_id):
    caso_uso = IniciarMantencion(
        repo_orden=RepositorioOrdenMantencionSQL(),
    )

    try:
        caso_uso.ejecutar(orden_id)
        messages.success(request, "Mantención iniciada")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def completar_orden(request, orden_id):
    caso_uso = CompletarMantencion(
        repo_orden=RepositorioOrdenMantencionSQL(),
    )

    try:
        caso_uso.ejecutar(orden_id)
        messages.success(request, "Mantención completada")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def cancelar_orden(request, orden_id):
    caso_uso = CancelarMantencion(
        repo_orden=RepositorioOrdenMantencionSQL(),
    )

    try:
        caso_uso.ejecutar(orden_id)
        messages.success(request, "Mantención cancelada")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("dashboard_mecanico")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_orden(request, orden_id):
    orden = get_object_or_404(OrdenMantencion, id=orden_id)
    orden.delete()
    messages.success(request, "Orden eliminada correctamente")
    return redirect("dashboard_mecanico")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def reprogramar_orden(request, orden_id):
    orden = get_object_or_404(OrdenMantencion, id=orden_id)
    if orden.estado not in ("pendiente", "asignada"):
        messages.error(request, "Solo se puede reprogramar órdenes pendientes o asignadas")
        return redirect("detalle_orden", orden_id=orden_id)
    fecha_str = request.POST.get("fecha_programada", "").strip()
    if not fecha_str:
        messages.error(request, "Debe seleccionar una fecha")
        return redirect("detalle_orden", orden_id=orden_id)
    try:
        nueva_fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Formato de fecha inválido")
        return redirect("detalle_orden", orden_id=orden_id)
    if orden.fecha_programada and nueva_fecha == orden.fecha_programada:
        messages.warning(request, "La fecha seleccionada es la misma que la actual. No se reprogramó.")
        return redirect("detalle_orden", orden_id=orden_id)
    fecha_anterior = orden.fecha_programada.strftime("%d/%m/%Y") if orden.fecha_programada else "Sin fecha"
    orden.fecha_programada = nueva_fecha
    orden.save()
    from infrastructure.mail_service.adapters.servicio_notificacion_email import ServicioNotificacionEmail
    notificador = ServicioNotificacionEmail()
    notificador.notificar_reprogramacion_cliente(orden, fecha_anterior, nueva_fecha.strftime("%d/%m/%Y"))
    messages.success(request, f"Orden reprogramada para el {nueva_fecha} — correo enviado al cliente")
    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def agregar_nota_interna(request, orden_id):
    orden = get_object_or_404(OrdenMantencion, id=orden_id)
    contenido = request.POST.get("contenido", "").strip()
    if not contenido:
        messages.error(request, "La nota no puede estar vacía")
        return redirect("detalle_orden", orden_id=orden_id)
    mecanico = Mecanico.objects.filter(email=request.user.email).first()
    from infrastructure.models import NotaInterna
    NotaInterna.objects.create(
        orden=orden,
        mecanico=mecanico,
        contenido=contenido,
    )
    messages.success(request, "Nota agregada")
    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def editar_nota_interna(request, nota_id):
    from infrastructure.models import NotaInterna
    nota = get_object_or_404(NotaInterna, id=nota_id)
    contenido = request.POST.get("contenido", "").strip()
    if not contenido:
        messages.error(request, "La nota no puede estar vacía")
    else:
        nota.contenido = contenido
        nota.save()
        messages.success(request, "Nota actualizada")
    return redirect("detalle_orden", orden_id=nota.orden.id)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_nota_interna(request, nota_id):
    from infrastructure.models import NotaInterna
    nota = get_object_or_404(NotaInterna, id=nota_id)
    orden_id = nota.orden.id
    nota.delete()
    messages.success(request, "Nota eliminada")
    return redirect("detalle_orden", orden_id=orden_id)


@login_required
@_mecanico_required
def lista_clientes(request):
    clientes = Cliente.objects.prefetch_related(
        "tractores__modelo",
        "tractores__ordenes__mecanico_asignado",
    ).all()

    mecanico = Mecanico.objects.filter(email=request.user.email).first()

    return render(request, "mecanico/lista_clientes.html", {
        "clientes": clientes,
        "mecanico": mecanico,
    })


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    ref = str(cliente)
    cliente.delete()
    messages.success(request, f"Cliente {ref} eliminado")
    return redirect("lista_clientes")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_clientes_masivo(request):
    ids = request.POST.getlist("cliente_ids")
    if not ids:
        messages.warning(request, "No seleccionaste ningún cliente")
        return redirect("lista_clientes")
    count = Cliente.objects.filter(id__in=ids).count()
    Cliente.objects.filter(id__in=ids).delete()
    messages.success(request, f"{count} cliente(s) eliminado(s)")
    return redirect("lista_clientes")

# ─── Catálogo CRUD ────────────────────────────────────────────────

@login_required
@_mecanico_required
def listar_modelos(request):
    modelos = ModeloTractor.objects.all().order_by("tipo", "marca", "nombre")
    mecanico = Mecanico.objects.filter(email=request.user.email).first()
    # Group by tipo then marca
    grupos = {}
    for m in modelos:
        grupos.setdefault(m.tipo, {}).setdefault(m.marca, []).append(m)
    return render(request, "mecanico/gestionar_modelos.html", {
        "modelos": modelos,
        "grupos": grupos,
        "mecanico": mecanico,
        "tipos": ModeloTractor.TIPOS,
    })


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def crear_modelo(request):
    nombre = request.POST.get("nombre", "").strip()
    marca = request.POST.get("marca", "Case").strip()
    tipo = request.POST.get("tipo", "tractor")
    if not nombre:
        messages.error(request, "El nombre del modelo es obligatorio")
        return redirect("listar_modelos")
    ModeloTractor.objects.create(nombre=nombre, marca=marca, tipo=tipo)
    messages.success(request, f"Modelo {marca} {nombre} creado")
    return redirect("listar_modelos")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def editar_modelo(request, modelo_id):
    modelo = get_object_or_404(ModeloTractor, id=modelo_id)
    nombre = request.POST.get("nombre", "").strip()
    marca = request.POST.get("marca", "Case").strip()
    tipo = request.POST.get("tipo", "tractor")
    if not nombre:
        messages.error(request, "El nombre del modelo es obligatorio")
        return redirect("listar_modelos")
    modelo.nombre = nombre
    modelo.marca = marca
    modelo.tipo = tipo
    modelo.save()
    messages.success(request, f"Modelo actualizado: {marca} {nombre}")
    return redirect("listar_modelos")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_modelo(request, modelo_id):
    modelo = get_object_or_404(ModeloTractor, id=modelo_id)
    nombre = str(modelo)
    modelo.delete()
    messages.success(request, f"Modelo {nombre} eliminado")
    return redirect("listar_modelos")


@login_required
@_mecanico_required
def listar_repuestos(request):
    repuestos = Repuesto.objects.all()
    mecanico = Mecanico.objects.filter(email=request.user.email).first()
    return render(request, "mecanico/gestionar_repuestos.html", {
        "repuestos": repuestos,
        "mecanico": mecanico,
        "tipos_repuesto": Repuesto.TIPOS_REPUESTO,
    })


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def crear_repuesto(request):
    codigo = request.POST.get("codigo", "").strip()
    nombre = request.POST.get("nombre", "").strip()
    tipo = request.POST.get("tipo", "").strip()
    if not codigo or not nombre or not tipo:
        messages.error(request, "Todos los campos son obligatorios")
        return redirect("listar_repuestos")
    if Repuesto.objects.filter(codigo=codigo).exists():
        messages.error(request, f"Ya existe un repuesto con el código {codigo}")
        return redirect("listar_repuestos")
    Repuesto.objects.create(codigo=codigo, nombre=nombre, tipo=tipo)
    messages.success(request, f"Repuesto {codigo} - {nombre} creado")
    return redirect("listar_repuestos")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def editar_repuesto(request, repuesto_id):
    repuesto = get_object_or_404(Repuesto, id=repuesto_id)
    codigo = request.POST.get("codigo", "").strip()
    nombre = request.POST.get("nombre", "").strip()
    tipo = request.POST.get("tipo", "").strip()
    if not codigo or not nombre or not tipo:
        messages.error(request, "Todos los campos son obligatorios")
        return redirect("listar_repuestos")
    if Repuesto.objects.filter(codigo=codigo).exclude(id=repuesto.id).exists():
        messages.error(request, f"Ya existe otro repuesto con el código {codigo}")
        return redirect("listar_repuestos")
    repuesto.codigo = codigo
    repuesto.nombre = nombre
    repuesto.tipo = tipo
    repuesto.save()
    messages.success(request, f"Repuesto {codigo} actualizado")
    return redirect("listar_repuestos")


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_repuesto(request, repuesto_id):
    repuesto = get_object_or_404(Repuesto, id=repuesto_id)
    ref = str(repuesto)
    repuesto.delete()
    messages.success(request, f"Repuesto {ref} eliminado")
    return redirect("listar_repuestos")


@login_required
@_mecanico_required
def listar_catalogos(request):
    modelos = ModeloTractor.objects.prefetch_related(
        "catalogos__items__repuesto"
    ).all().order_by("tipo", "marca", "nombre")
    repuestos = Repuesto.objects.all()
    mecanico = Mecanico.objects.filter(email=request.user.email).first()
    grupos = {}
    for m in modelos:
        grupos.setdefault(m.tipo, {}).setdefault(m.marca, []).append(m)
    return render(request, "mecanico/gestionar_catalogos.html", {
        "modelos": modelos,
        "grupos": grupos,
        "repuestos": repuestos,
        "mecanico": mecanico,
        "tipos_mantencion": CatalogoRepuestos.TIPOS_MANTENCION,
        "tipos": ModeloTractor.TIPOS,
    })


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def crear_catalogo(request):
    modelo_id = request.POST.get("modelo_id", "").strip()
    tipo_mantencion = request.POST.get("tipo_mantencion", "").strip()
    hash_ref = "#modelo-" + modelo_id if modelo_id else ""
    if not modelo_id or not tipo_mantencion:
        messages.error(request, "Debe seleccionar modelo y tipo de mantención")
        return redirect("listar_catalogos")
    catalogo, created = CatalogoRepuestos.objects.get_or_create(
        modelo_id=modelo_id, tipo_mantencion=tipo_mantencion
    )
    if created:
        messages.success(request, "Catálogo creado")
    else:
        messages.info(request, "El catálogo ya existe")
    return redirect(reverse("listar_catalogos") + hash_ref)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_catalogo(request, catalogo_id):
    catalogo = get_object_or_404(CatalogoRepuestos, id=catalogo_id)
    modelo_id = catalogo.modelo_id
    catalogo.delete()
    messages.success(request, "Catálogo eliminado")
    return redirect(reverse("listar_catalogos") + "#modelo-" + str(modelo_id))


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def agregar_item_catalogo(request, catalogo_id):
    catalogo = get_object_or_404(CatalogoRepuestos, id=catalogo_id)
    repuesto_id = request.POST.get("repuesto_id", "").strip()
    cantidad = request.POST.get("cantidad", "1").strip()
    hash_ref = "#modelo-" + str(catalogo.modelo_id)
    if not repuesto_id:
        messages.error(request, "Debe seleccionar un repuesto")
        return redirect(reverse("listar_catalogos") + hash_ref)
    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1
    if ItemCatalogo.objects.filter(catalogo=catalogo, repuesto_id=repuesto_id).exists():
        messages.warning(request, "Ese repuesto ya está en el catálogo")
        return redirect(reverse("listar_catalogos") + hash_ref)
    ItemCatalogo.objects.create(catalogo=catalogo, repuesto_id=repuesto_id, cantidad=cantidad)
    messages.success(request, "Repuesto agregado al catálogo")
    return redirect(reverse("listar_catalogos") + hash_ref)


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def editar_item_catalogo(request, item_id):
    item = get_object_or_404(ItemCatalogo, id=item_id)
    cantidad = request.POST.get("cantidad", "1").strip()
    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1
    item.cantidad = cantidad
    item.save()
    messages.success(request, "Cantidad actualizada")
    return redirect(reverse("listar_catalogos") + "#modelo-" + str(item.catalogo.modelo_id))


@login_required
@_mecanico_required
@require_http_methods(["POST"])
def eliminar_item_catalogo(request, item_id):
    item = get_object_or_404(ItemCatalogo, id=item_id)
    modelo_id = item.catalogo.modelo_id
    item.delete()
    messages.success(request, "Repuesto eliminado del catálogo")
    return redirect(reverse("listar_catalogos") + "#modelo-" + str(modelo_id))


@login_required
@_mecanico_required
def detalle_mecanico(request):
    mecanico = Mecanico.objects.filter(email=request.user.email).first()
    if not mecanico:
        messages.error(request, "No se encontraron datos del mecánico")
        return redirect("dashboard_mecanico")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        if email:
            duplicado = Mecanico.objects.filter(email=email).exclude(id=mecanico.id).first()
            if duplicado:
                messages.error(request, "El correo electrónico ya está en uso por otro mecánico")
            else:
                mecanico.email = email
                mecanico.telefono = telefono
                mecanico.save()
                request.user.email = email
                request.user.save()
                messages.success(request, "Datos actualizados correctamente")
        else:
            messages.error(request, "El correo electrónico es obligatorio")
        return redirect("detalle_mecanico")

    return render(request, "mecanico/detalle_mecanico.html", {
        "mecanico": mecanico,
    })
