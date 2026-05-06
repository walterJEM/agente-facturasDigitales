from langchain.tools import tool
from typing import TYPE_CHECKING

# Variable global donde el agente guarda las facturas procesadas
_facturas_cache: list = []


def cargar_facturas(facturas: list):
    """Carga las facturas procesadas en el cache del agente."""
    global _facturas_cache
    _facturas_cache = facturas


@tool
def total_gastado(periodo: str = "todo") -> str:
    """
    Calcula el total gastado en las facturas cargadas.
    Parámetro: 'todo' para el total general, o un mes como 'mayo', 'abril', etc.
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    facturas = _facturas_cache

    # Filtrar por mes si se especifica
    if periodo != "todo":
        meses = {
            "enero": "01", "febrero": "02", "marzo": "03",
            "abril": "04", "mayo": "05", "junio": "06",
            "julio": "07", "agosto": "08", "septiembre": "09",
            "octubre": "10", "noviembre": "11", "diciembre": "12"
        }
        mes_num = meses.get(periodo.lower())
        if mes_num:
            facturas = [
                f for f in _facturas_cache
                if f.fecha and f"/{mes_num}/" in f.fecha
            ]

    total = sum(f.total for f in facturas if f.total)
    igv_total = sum(f.igv for f in facturas if f.igv)

    return (
        f"📊 Total gastado: S/ {total:.2f}\n"
        f"   IGV incluido: S/ {igv_total:.2f}\n"
        f"   Número de facturas: {len(facturas)}"
    )


@tool
def gasto_por_categoria(categoria: str = "todas") -> str:
    """
    Muestra el gasto agrupado por categoría.
    Categorías disponibles: Servicios, Suministros, Tecnología, Alimentación, Transporte, Otros.
    Usa 'todas' para ver el resumen completo.
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    categorias: dict = {}
    for f in _facturas_cache:
        cat = f.categoria or "Sin categoría"
        categorias[cat] = categorias.get(cat, 0) + (f.total or 0)

    if categoria != "todas":
        monto = categorias.get(categoria, 0)
        return f"💰 {categoria}: S/ {monto:.2f}"

    resultado = "📂 Gasto por categoría:\n"
    for cat, monto in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        resultado += f"   • {cat}: S/ {monto:.2f}\n"
    return resultado


@tool
def top_proveedores(n: int = 5) -> str:
    """
    Muestra los N proveedores con mayor gasto total.
    Por defecto muestra los top 5.
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    proveedores: dict = {}
    for f in _facturas_cache:
        prov = f.proveedor or "Desconocido"
        proveedores[prov] = proveedores.get(prov, 0) + (f.total or 0)

    top = sorted(proveedores.items(), key=lambda x: x[1], reverse=True)[:n]
    resultado = f"🏆 Top {n} proveedores:\n"
    for i, (prov, monto) in enumerate(top, 1):
        resultado += f"   {i}. {prov}: S/ {monto:.2f}\n"
    return resultado


@tool
def buscar_factura(termino: str) -> str:
    """
    Busca facturas por proveedor, descripción o número de factura.
    Parámetro: texto a buscar (ej: 'Claro', 'internet', 'F001-123')
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    termino_lower = termino.lower()
    encontradas = [
        f for f in _facturas_cache
        if (f.proveedor and termino_lower in f.proveedor.lower()) or
           (f.descripcion and termino_lower in f.descripcion.lower()) or
           (f.numero_factura and termino_lower in f.numero_factura.lower())
    ]

    if not encontradas:
        return f"No se encontraron facturas con '{termino}'."

    resultado = f"🔍 Facturas encontradas ({len(encontradas)}):\n"
    for f in encontradas:
        resultado += (
            f"   • {f.proveedor} | {f.fecha} | "
            f"S/ {f.total:.2f} | {f.descripcion or 'Sin descripción'}\n"
        )
    return resultado


@tool
def detectar_duplicados() -> str:
    """
    Detecta posibles facturas duplicadas por monto y proveedor similares.
    Útil para evitar doble pago.
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    vistos = {}
    duplicados = []

    for f in _facturas_cache:
        clave = f"{f.proveedor}_{f.total}_{f.fecha}"
        if clave in vistos:
            duplicados.append((vistos[clave], f))
        else:
            vistos[clave] = f

    if not duplicados:
        return "✅ No se detectaron facturas duplicadas."

    resultado = f"⚠️  Se encontraron {len(duplicados)} posibles duplicados:\n"
    for f1, f2 in duplicados:
        resultado += f"   • {f1.archivo} y {f2.archivo} — {f1.proveedor} S/ {f1.total}\n"
    return resultado


@tool
def resumen_general() -> str:
    """
    Muestra un resumen ejecutivo completo de todas las facturas cargadas.
    """
    if not _facturas_cache:
        return "No hay facturas cargadas aún."

    total = sum(f.total for f in _facturas_cache if f.total)
    igv = sum(f.igv for f in _facturas_cache if f.igv)
    n = len(_facturas_cache)

    proveedores_unicos = len(set(f.proveedor for f in _facturas_cache if f.proveedor))

    return (
        f"📋 RESUMEN GENERAL\n"
        f"{'─'*30}\n"
        f"Total facturas:     {n}\n"
        f"Proveedores únicos: {proveedores_unicos}\n"
        f"Gasto total:        S/ {total:.2f}\n"
        f"IGV total:          S/ {igv:.2f}\n"
        f"Promedio/factura:   S/ {total/n:.2f}\n"
    )