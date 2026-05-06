from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Factura(BaseModel):
    """Estructura de datos de una factura peruana."""

    numero_factura: Optional[str] = Field(None, description="Número de factura o boleta")
    proveedor: Optional[str] = Field(None, description="Nombre del emisor")
    ruc_proveedor: Optional[str] = Field(None, description="RUC del emisor (11 dígitos)")
    fecha: Optional[str] = Field(None, description="Fecha de emisión DD/MM/AAAA")
    descripcion: Optional[str] = Field(None, description="Descripción del bien o servicio")
    subtotal: Optional[float] = Field(None, description="Monto sin IGV")
    igv: Optional[float] = Field(None, description="IGV (18%)")
    total: Optional[float] = Field(None, description="Monto total con IGV")
    moneda: Optional[str] = Field("PEN", description="PEN o USD")
    categoria: Optional[str] = Field(None, description="Categoría del gasto")
    archivo: Optional[str] = Field(None, description="Nombre del archivo fuente")

    class Config:
        # Permite crear el objeto aunque falten campos
        populate_by_name = True