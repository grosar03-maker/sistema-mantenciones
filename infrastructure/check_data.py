from infrastructure.models import ModeloTractor, CatalogoRepuestos
for m in ModeloTractor.objects.all().order_by('nombre'):
    print(f"--- {m.nombre} ---")
    cats = CatalogoRepuestos.objects.filter(modelo=m).order_by('tipo_mantencion')
    for c in cats:
        codigos = [r.codigo for r in c.repuestos.all().order_by('codigo')]
        print(f"  {c.tipo_mantencion}: {c.repuestos.count()} repuestos -> {', '.join(codigos)}")
    print()
