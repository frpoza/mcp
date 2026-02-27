"""
Herramienta: FR_listar_herramientas_creadas
Descripcion: Lista todas las herramientas que han sido creadas en el directorio
Autor: Francisco Pozuelo
"""

from datetime import datetime
from pathlib import Path
from mcp.types import Tool, TextContent

# Configuracion
RUTA_BASE = Path(__file__).parent.parent
RUTA_HERRAMIENTAS = RUTA_BASE / "herramientas"
RUTA_LOGS = RUTA_BASE / "logs"

def registrar_log(mensaje: str):
    """Registra mensajes en el archivo de logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archivo_log = RUTA_LOGS / f"servidor_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(archivo_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

# Definicion de la herramienta
HERRAMIENTA = Tool(
    name="FR_listar_herramientas_creadas",
    description="Lista todas las herramientas que han sido creadas en el directorio",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

def leer_metadatos_docstring(archivo: Path) -> dict:
    """
    Lee los metadatos SOLO del docstring inicial del archivo (entre las primeras triples comillas).
    Evita falsos positivos leyendo el resto del codigo.
    """
    metadatos = {
        "nombre": "",
        "descripcion": "",
        "fecha": "",
        "autor": ""
    }
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Extraer solo el primer docstring (entre las primeras triples comillas)
        if contenido.startswith('"""'):
            fin_docstring = contenido.find('"""', 3)
            if fin_docstring == -1:
                return metadatos
            docstring = contenido[3:fin_docstring]
        elif contenido.startswith("'''"):
            fin_docstring = contenido.find("'''", 3)
            if fin_docstring == -1:
                return metadatos
            docstring = contenido[3:fin_docstring]
        else:
            return metadatos
        
        # Parsear linea a linea SOLO dentro del docstring
        for linea in docstring.splitlines():
            linea = linea.strip()
            
            if linea.startswith("Herramienta:"):
                metadatos["nombre"] = linea.split("Herramienta:", 1)[1].strip()
            
            elif linea.startswith("Descripcion:"):
                metadatos["descripcion"] = linea.split("Descripcion:", 1)[1].strip()
            
            elif linea.startswith("Generada automaticamente el"):
                # Formato: "Generada automaticamente el YYYY-MM-DD HH:MM:SS"
                partes = linea.split("automaticamente el", 1)
                if len(partes) == 2:
                    metadatos["fecha"] = partes[1].strip()
            
            elif linea.startswith("Autor:"):
                metadatos["autor"] = linea.split("Autor:", 1)[1].strip()
    
    except Exception as e:
        metadatos["descripcion"] = f"ADVERTENCIA: Error leyendo archivo: {e}"
    
    return metadatos


# Funcion de ejecucion
async def ejecutar(argumentos: dict) -> list[TextContent]:
    """Ejecuta la herramienta FR_listar_herramientas_creadas"""
    
    archivos = list(RUTA_HERRAMIENTAS.glob("FR_*.py"))
    
    if not archivos:
        return [TextContent(
            type="text",
            text="No se han creado herramientas todavia.\n\nTip: Usa FR_generar_herramienta para crear tu primera herramienta."
        )]
    
    resultado = "Herramientas creadas:\n"
    resultado += "=" * 60 + "\n\n"
    
    for i, archivo in enumerate(sorted(archivos), 1):
        metadatos = leer_metadatos_docstring(archivo)
        
        resultado += f"{i}. {archivo.name}\n"
        
        if metadatos["nombre"]:
            resultado += f"   Nombre: {metadatos['nombre']}\n"
        
        if metadatos["descripcion"]:
            resultado += f"   Descripcion: {metadatos['descripcion']}\n"
        
        if metadatos["autor"]:
            resultado += f"   Autor: {metadatos['autor']}\n"
        
        if metadatos["fecha"]:
            resultado += f"   Generada: {metadatos['fecha']}\n"
        
        resultado += f"   Ubicacion: {archivo}\n"
        resultado += "\n"
    
    resultado += f"\nTotal: {len(archivos)} herramienta(s) encontrada(s)"
    
    registrar_log(f"Listadas {len(archivos)} herramientas")
    
    return [TextContent(type="text", text=resultado)]
