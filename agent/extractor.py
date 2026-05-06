import base64
import json
import os
from pathlib import Path
from typing import Optional

import pdfplumber
from openai import OpenAI
from PIL import Image
import io

from agent.models import Factura


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_EXTRACCION = """
Eres un asistente especializado en contabilidad peruana.
Analiza esta factura o boleta y extrae los siguientes datos en formato JSON:

{
  "numero_factura": "...",
  "proveedor": "...",
  "ruc_proveedor": "...",
  "fecha": "DD/MM/AAAA",
  "descripcion": "...",
  "subtotal": 0.00,
  "igv": 0.00,
  "total": 0.00,
  "moneda": "PEN o USD",
  "categoria": "una de: Servicios, Suministros, Tecnología, Alimentación, Transporte, Otros"
}

Si no encuentras un campo, ponlo como null.
Responde SOLO con el JSON, sin explicaciones.
"""


def pdf_a_imagen(pdf_path: str) -> list[bytes]:
    """Convierte cada página de un PDF a imagen en bytes."""
    imagenes = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # Intentar extraer texto primero (PDF nativo)
            texto = pagina.extract_text()
            if texto and len(texto.strip()) > 50:
                imagenes.append(("texto", texto))
            else:
                # PDF escaneado: convertir a imagen
                img = pagina.to_image(resolution=200)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                imagenes.append(("imagen", buffer.getvalue()))
    return imagenes


def imagen_a_base64(imagen_bytes: bytes) -> str:
    """Convierte bytes de imagen a base64 para la API."""
    return base64.b64encode(imagen_bytes).decode("utf-8")


def extraer_con_texto(texto: str) -> dict:
    """Extrae datos de factura usando texto plano."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"{PROMPT_EXTRACCION}\n\nTexto de la factura:\n{texto}"
            }
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


def extraer_con_vision(imagen_bytes: bytes) -> dict:
    """Extrae datos de factura usando GPT-4o Vision (imágenes/escaneos)."""
    imagen_b64 = imagen_a_base64(imagen_bytes)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_EXTRACCION},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{imagen_b64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


def procesar_archivo(archivo_path: str) -> Optional[Factura]:
    """
    Procesa un archivo (PDF o imagen) y retorna una Factura estructurada.
    Maneja PDFs nativos, escaneados e imágenes JPG/PNG.
    """
    path = Path(archivo_path)
    extension = path.suffix.lower()

    try:
        if extension == ".pdf":
            paginas = pdf_a_imagen(archivo_path)
            # Procesar primera página (donde suele estar la info clave)
            tipo, contenido = paginas[0]
            if tipo == "texto":
                datos = extraer_con_texto(contenido)
            else:
                datos = extraer_con_vision(contenido)

        elif extension in [".jpg", ".jpeg", ".png"]:
            with open(archivo_path, "rb") as f:
                imagen_bytes = f.read()
            datos = extraer_con_vision(imagen_bytes)

        else:
            print(f"⚠️  Formato no soportado: {extension}")
            return None

        # Agregar nombre del archivo fuente
        datos["archivo"] = path.name
        return Factura(**datos)

    except Exception as e:
        print(f"❌ Error procesando {path.name}: {e}")
        return None


def procesar_carpeta(carpeta_path: str) -> list[Factura]:
    """Procesa todos los archivos de una carpeta y retorna lista de Facturas."""
    carpeta = Path(carpeta_path)
    extensiones = [".pdf", ".jpg", ".jpeg", ".png"]
    archivos = [f for f in carpeta.iterdir() if f.suffix.lower() in extensiones]

    facturas = []
    for archivo in archivos:
        print(f"📄 Procesando: {archivo.name}...")
        factura = procesar_archivo(str(archivo))
        if factura:
            facturas.append(factura)
            print(f"   ✅ {factura.proveedor} — S/ {factura.total}")

    return facturas