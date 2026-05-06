🧾 Agente de Facturas con IA
Agente inteligente que procesa facturas y boletas peruanas (PDF o imagen), extrae sus datos automáticamente con GPT-4o Vision y permite consultarlas en lenguaje natural.
---
✨ Features
Feature	Descripción
📄 Extracción automática	Lee PDFs e imágenes con GPT-4o Vision
🤖 Chat en lenguaje natural	Pregúntale sobre tus gastos como si fuera un contador
📊 Export a Excel	Genera reporte profesional con gráficos automáticos
🔍 Detecta duplicados	Evita doble pago de facturas
🏷️ Categorización	Clasifica gastos por tipo automáticamente
🇵🇪 Adaptado a Perú	Reconoce RUC, IGV 18% y formato de comprobantes SUNAT
---
🏗️ Arquitectura
```
PDF / Imagen → extractor.py → GPT-4o Vision
                            │
                            └── Pydantic (models.py)
                            │
                    ┌───────┴────────┐
                 agent.py       excel_export.py
                (LangChain)     (openpyxl)
                    │
                 tools.py
        ┌───────────┼───────────┐
   total_gastado  top_proveedores  detectar_duplicados ...
                    │
                 app.py
               (Streamlit)
```
---
🛠️ Stack
IA: GPT-4o Vision + LangChain
Extracción: pdfplumber + Pillow
Datos: Pydantic v2
Excel: openpyxl
Interfaz: Streamlit
Config: python-dotenv
---
🚀 Quickstart
1. Clonar e instalar
```bash
git clone https://github.com/walterJEM/agente-facturasDigitales.git
cd agente-facturasDigitales
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Configurar API Key
```bash
cp .env.example .env
# Edita .env y agrega tu OPENAI_API_KEY
# Obtén tu key en: https://platform.openai.com
```
3. Correr la app
```bash
python -m streamlit run app.py
```
---
📁 Estructura del proyecto
```
agente-facturasDigitales/
├── app.py                  # Interfaz Streamlit
├── agent/
│   ├── agent.py            # Orquestador LangChain
│   ├── extractor.py        # Lectura de PDFs e imágenes con GPT-4o
│   ├── tools.py            # 6 herramientas de análisis
│   ├── excel_export.py     # Generación de Excel profesional
│   └── models.py           # Modelos Pydantic
├── data/
│   └── facturas_ejemplo/   # Facturas de prueba
├── output/                 # Excel generados
├── requirements.txt
└── .env.example
```
---
🤖 Herramientas del agente
Herramienta	¿Qué hace?
`total_gastado`	Calcula el gasto total o por mes
`gasto_por_categoria`	Desglosa por tipo de gasto
`top_proveedores`	Ranking de proveedores por monto
`buscar_factura`	Busca por nombre, RUC o descripción
`detectar_duplicados`	Compara montos y proveedores
`resumen_general`	Vista ejecutiva completa
---
💬 Ejemplo de uso
```
Usuario: ¿Cuánto gasté en servicios este mes?
Agente:  📊 Gasto en Servicios: S/ 850.00
         • Claro Perú - Internet: S/ 150.00
         • AWS - Cloud: S/ 420.00
         • Adobe - Licencia: S/ 280.00

Usuario: ¿Hay facturas duplicadas?
Agente:  ⚠️ Se encontró 1 posible duplicado:
         • claro_abril.pdf y claro_abril_2.pdf
           Claro Perú — S/ 150.00
```
---
📊 Excel generado
El agente exporta un Excel con 3 hojas:
Facturas — detalle completo con formato profesional
Resumen — gasto agrupado por categoría + gráfico de barras
Info — metadata del reporte
---
🗺️ Roadmap
[x] Extracción de datos con GPT-4o Vision
[x] Chat en lenguaje natural con LangChain
[x] Export a Excel con gráficos
[x] Detección de duplicados
[ ] Validación de RUC contra SUNAT API
[ ] Alertas por Telegram cuando detecta anomalías
[ ] Soporte para tickets y recibos informales
[ ] Deploy en Railway / Render
[ ] Versión API REST con FastAPI
---
📄 Licencia
MIT — úsalo, modifícalo, contribuye.
---
👤 Autor
Desarrollado por Walter Espino — Egresado de Ing. de Sistemas
