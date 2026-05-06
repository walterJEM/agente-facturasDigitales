import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from agent.tools import (
    total_gastado,
    gasto_por_categoria,
    top_proveedores,
    buscar_factura,
    detectar_duplicados,
    resumen_general,
    cargar_facturas,
)
from agent.extractor import procesar_carpeta, procesar_archivo
from agent.excel_export import exportar_excel

SYSTEM_PROMPT = """
Eres un asistente contable especializado en análisis de facturas peruanas.
Ayudas a los usuarios a entender sus gastos, identificar patrones y tomar 
decisiones financieras inteligentes.

Cuando el usuario te haga preguntas sobre sus facturas, usa las herramientas
disponibles para dar respuestas precisas y útiles.

Responde siempre en español, de forma clara y concisa.
Si el usuario pregunta algo que no está relacionado a las facturas cargadas,
recuérdale amablemente que tu especialidad es el análisis de sus comprobantes.
"""


def crear_agente():
    """Crea y retorna el agente configurado con todas las herramientas."""

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [
        total_gastado,
        gasto_por_categoria,
        top_proveedores,
        buscar_factura,
        detectar_duplicados,
        resumen_general,
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = create_openai_tools_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,  # Muestra el razonamiento del agente (útil para aprender)
        handle_parsing_errors=True,
    )

    return executor


class AgenteFacturas:
    """
    Clase principal que orquesta todo el flujo:
    1. Procesar archivos
    2. Exportar Excel
    3. Responder preguntas
    """

    def __init__(self):
        self.agente = crear_agente()
        self.facturas = []

    def cargar_archivos(self, ruta: str) -> int:
        """
        Carga y procesa facturas desde una carpeta o archivo individual.
        Retorna el número de facturas procesadas exitosamente.
        """
        import os
        if os.path.isdir(ruta):
            self.facturas = procesar_carpeta(ruta)
        else:
            factura = procesar_archivo(ruta)
            self.facturas = [factura] if factura else []

        # Cargar en el cache de las herramientas
        cargar_facturas(self.facturas)
        return len(self.facturas)

    def exportar(self, ruta_salida: str = "output/facturas.xlsx") -> str:
        """Exporta las facturas a Excel y retorna la ruta del archivo."""
        if not self.facturas:
            return "No hay facturas para exportar."
        return exportar_excel(self.facturas, ruta_salida)

    def preguntar(self, pregunta: str) -> str:
        """Envía una pregunta al agente y retorna la respuesta."""
        if not self.facturas:
            return "Primero debes cargar tus facturas."

        resultado = self.agente.invoke({"input": pregunta})
        return resultado["output"]