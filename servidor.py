#!/usr/bin/env python3
"""
Servidor MCP Modular - Sistema de Generacion de Herramientas
Autor: Francisco de la Poza
Version: 2.0 (Modular)

Este servidor carga herramientas dinamicamente desde el directorio 'herramientas/'
"""

import asyncio
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Configuracion de rutas
RUTA_BASE = Path(__file__).parent
RUTA_HERRAMIENTAS = RUTA_BASE / "herramientas"
RUTA_LOGS = RUTA_BASE / "logs"

# Crear directorios si no existen
RUTA_HERRAMIENTAS.mkdir(exist_ok=True)
RUTA_LOGS.mkdir(exist_ok=True)

# Inicializar servidor
servidor = Server("generador-herramientas")

# Diccionario para almacenar herramientas cargadas
herramientas_cargadas = {}

def registrar_log(mensaje: str):
    """Registra mensajes en el archivo de logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archivo_log = RUTA_LOGS / f"servidor_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(archivo_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

def cargar_herramienta(ruta_archivo: Path) -> dict:
    """
    Carga una herramienta desde un archivo Python
    
    El archivo debe contener:
    - HERRAMIENTA: objeto Tool con la definicion
    - ejecutar(): funcion async que ejecuta la herramienta
    """
    try:
        # Cargar el modulo dinamicamente
        spec = importlib.util.spec_from_file_location(ruta_archivo.stem, ruta_archivo)
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[ruta_archivo.stem] = modulo
        spec.loader.exec_module(modulo)
        
        # Verificar que tenga los componentes necesarios
        if not hasattr(modulo, 'HERRAMIENTA'):
            registrar_log(f"ADVERTENCIA: {ruta_archivo.name} no tiene HERRAMIENTA")
            return None
        
        if not hasattr(modulo, 'ejecutar'):
            registrar_log(f"ADVERTENCIA: {ruta_archivo.name} no tiene funcion ejecutar()")
            return None
        
        herramienta_def = modulo.HERRAMIENTA
        
        registrar_log(f"Herramienta cargada: {herramienta_def.name}")
        
        return {
            'definicion': herramienta_def,
            'ejecutar': modulo.ejecutar
        }
        
    except Exception as e:
        registrar_log(f"ERROR cargando {ruta_archivo.name}: {e}")
        return None

def cargar_todas_las_herramientas():
    """Carga todas las herramientas desde el directorio"""
    global herramientas_cargadas
    herramientas_cargadas.clear()
    
    archivos_herramientas = list(RUTA_HERRAMIENTAS.glob("FR_*.py"))
    
    registrar_log(f"Buscando herramientas en: {RUTA_HERRAMIENTAS}")
    registrar_log(f"Encontrados {len(archivos_herramientas)} archivos")
    
    for archivo in archivos_herramientas:
        herramienta = cargar_herramienta(archivo)
        if herramienta:
            nombre = herramienta['definicion'].name
            herramientas_cargadas[nombre] = herramienta
    
    registrar_log(f"Cargadas {len(herramientas_cargadas)} herramientas exitosamente")

@servidor.list_tools()
async def listar_herramientas() -> list[Tool]:
    """Lista todas las herramientas disponibles (cargadas dinamicamente)"""
    # Recargar herramientas cada vez que se listen (para detectar cambios)
    cargar_todas_las_herramientas()
    
    herramientas = [h['definicion'] for h in herramientas_cargadas.values()]
    
    registrar_log(f"Listando {len(herramientas)} herramientas")
    
    return herramientas

@servidor.call_tool()
async def ejecutar_herramienta(nombre: str, argumentos: dict) -> list[TextContent]:
    """Ejecuta la herramienta solicitada"""
    
    if nombre not in herramientas_cargadas:
        error_msg = f"ERROR: Herramienta no encontrada: {nombre}\n\nHerramientas disponibles:\n"
        error_msg += "\n".join([f"  - {h}" for h in herramientas_cargadas.keys()])
        registrar_log(f"ERROR: Intento de ejecutar herramienta inexistente: {nombre}")
        return [TextContent(type="text", text=error_msg)]
    
    try:
        registrar_log(f"Ejecutando: {nombre} con args: {argumentos}")
        resultado = await herramientas_cargadas[nombre]['ejecutar'](argumentos)
        registrar_log(f"Ejecucion exitosa: {nombre}")
        return resultado
    except Exception as e:
        error_msg = f"ERROR ejecutando {nombre}: {str(e)}"
        registrar_log(error_msg)
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Funcion principal para ejecutar el servidor"""
    registrar_log("=" * 60)
    registrar_log("Servidor MCP Modular iniciado")
    registrar_log(f"Directorio de herramientas: {RUTA_HERRAMIENTAS}")
    registrar_log(f"Directorio de logs: {RUTA_LOGS}")
    
    # Cargar herramientas iniciales
    cargar_todas_las_herramientas()
    
    registrar_log(f"Total herramientas cargadas: {len(herramientas_cargadas)}")
    for nombre in herramientas_cargadas.keys():
        registrar_log(f"  - {nombre}")
    
    # NO usar print() aqui - interfiere con la comunicacion stdio JSON
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await servidor.run(
            read_stream,
            write_stream,
            servidor.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())