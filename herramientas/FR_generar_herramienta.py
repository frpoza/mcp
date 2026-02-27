"""
Herramienta: FR_generar_herramienta
Descripcion: Genera automaticamente una nueva herramienta MCP o modifica una existente, 
             con validacion automatica de sintaxis Python. Reemplaza automaticamente 
             la herramienta modificada en el servidor.
Autor: Francisco Pozuelo
Mejorada: 2026-02-27
"""

import json
import ast
import sys
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
    RUTA_LOGS.mkdir(parents=True, exist_ok=True)
    archivo_log = RUTA_LOGS / f"servidor_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(archivo_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

def validar_sintaxis_python(codigo: str) -> tuple[bool, str]:
    """
    Valida que el codigo Python sea sintacticamente correcto.
    Retorna (es_valido, mensaje_error)
    """
    try:
        ast.parse(codigo)
        return True, "✓ Sintaxis válida"
    except SyntaxError as e:
        return False, f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"❌ Error al validar: {str(e)}"

def herramienta_existe(nombre_completo: str) -> bool:
    """Verifica si una herramienta ya existe"""
    nombre_archivo = f"{nombre_completo.lower()}.py"
    ruta_archivo = RUTA_HERRAMIENTAS / nombre_archivo
    return ruta_archivo.exists()

def obtener_ruta_herramienta(nombre_completo: str) -> Path:
    """Obtiene la ruta de una herramienta"""
    nombre_archivo = f"{nombre_completo.lower()}.py"
    return RUTA_HERRAMIENTAS / nombre_archivo

# Definicion de la herramienta
HERRAMIENTA = Tool(
    name="FR_generar_herramienta",
    description="Genera automaticamente una nueva herramienta MCP o modifica una existente, con validacion automatica de sintaxis Python",
    inputSchema={
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "Nombre de la herramienta (sin el prefijo FR_)"
            },
            "descripcion": {
                "type": "string",
                "description": "Descripcion de que hace la herramienta"
            },
            "parametros": {
                "type": "array",
                "description": "Lista de parametros que acepta la herramienta",
                "items": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"},
                        "tipo": {"type": "string", "enum": ["string", "number", "boolean", "array", "object"]},
                        "descripcion": {"type": "string"},
                        "requerido": {"type": "boolean"}
                    },
                    "required": ["nombre", "tipo", "descripcion"]
                }
            },
            "codigo_funcion": {
                "type": "string",
                "description": "Codigo Python de la funcion que ejecuta la herramienta"
            }
        },
        "required": ["nombre", "descripcion", "parametros", "codigo_funcion"]
    }
)

# Funcion de ejecucion
async def ejecutar(argumentos: dict) -> list[TextContent]:
    """Ejecuta la herramienta FR_generar_herramienta"""
    
    nombre = argumentos["nombre"].strip()
    descripcion = argumentos["descripcion"].strip()
    parametros = argumentos["parametros"]
    codigo_funcion = argumentos["codigo_funcion"].strip()
    
    # Nombre completo con prefijo
    nombre_completo = f"FR_{nombre}"
    
    # VALIDACION 1: Verificar si la herramienta ya existe
    existe = herramienta_existe(nombre_completo)
    ruta_archivo = obtener_ruta_herramienta(nombre_completo)
    accion = "MODIFICAR" if existe else "CREAR"
    
    # VALIDACION 2: Validar sintaxis del codigo Python
    es_valido, mensaje_validacion = validar_sintaxis_python(codigo_funcion)
    if not es_valido:
        return [TextContent(type="text", text=f"❌ NO SE PUEDE {accion} LA HERRAMIENTA\n\n{mensaje_validacion}\n\nVerifica la sintaxis de tu codigo Python.")]
    
    # VALIDACION 3: Validar que los parametros sean consistentes
    for param in parametros:
        if not param.get("nombre"):
            return [TextContent(type="text", text="❌ Error: Todos los parametros deben tener un nombre")]
        if param.get("tipo") not in ["string", "number", "boolean", "array", "object"]:
            return [TextContent(type="text", text=f"❌ Error: Tipo de parametro '{param['tipo']}' no valido")]
    
    # Generar el esquema de parametros
    propiedades = {}
    requeridos = []
    
    for param in parametros:
        propiedades[param["nombre"]] = {
            "type": param["tipo"],
            "description": param["descripcion"]
        }
        if param.get("requerido", False):
            requeridos.append(param["nombre"])
    
    esquema_parametros = {
        "type": "object",
        "properties": propiedades
    }
    if requeridos:
        esquema_parametros["required"] = requeridos
    
    # Serializar el esquema
    esquema_json = json.dumps(esquema_parametros, indent=8, ensure_ascii=False)
    
    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Plantilla del archivo de herramienta
    cabecera = f'"""\nHerramienta: {nombre_completo}\nDescripcion: {descripcion}\nGenerada automaticamente el {fecha_generacion}\nAutor: Sistema de Generacion Automatica\n"""\n\nfrom mcp.types import Tool, TextContent\n\n# Definicion de la herramienta\nHERRAMIENTA = Tool(\n    name="{nombre_completo}",\n    description="{descripcion}",\n    inputSchema={esquema_json}\n)\n\n# Funcion de ejecucion\nasync def ejecutar(argumentos: dict) -> list[TextContent]:\n    """Ejecuta la herramienta {nombre_completo}"""\n    \n'
    
    pie = '\n    \n    return [TextContent(type="text", text=resultado)]\n'
    
    contenido = cabecera + codigo_funcion + pie
    
    # VALIDACION 4: Validar el contenido completo antes de guardar
    es_valido_completo, mensaje_completo = validar_sintaxis_python(contenido)
    if not es_valido_completo:
        return [TextContent(type="text", text=f"❌ NO SE PUEDE {accion} LA HERRAMIENTA\n\nError en el archivo generado:\n{mensaje_completo}\n\nVerifica que la funcion retorne correctamente con 'return [TextContent(...)]'")]
    
    try:
        # Crear directorio si no existe
        RUTA_HERRAMIENTAS.mkdir(parents=True, exist_ok=True)
        
        # Guardar el archivo
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
        
        # Registrar en logs
        registrar_log(f"Herramienta {accion}A: {nombre_completo} -> {ruta_archivo}")
        
        resultado = f"""✅ Herramienta {accion}ADA exitosamente

Nombre: {nombre_completo}
Archivo: {ruta_archivo.name}
Ubicacion: {ruta_archivo}
Descripcion: {descripcion}
Parametros: {len(parametros)}

✓ Validaciones completadas:
  ✓ Sintaxis Python válida
  ✓ Esquema de parámetros válido
  ✓ Archivo generado correctamente

La herramienta ha sido guardada en el directorio de herramientas.
El servidor la cargara automaticamente en la proxima solicitud.

Tip: Puedes usar FR_listar_herramientas_creadas para verificar que se creo/modifico correctamente.
"""
        
        return [TextContent(type="text", text=resultado)]
        
    except Exception as e:
        registrar_log(f"Error al {accion.lower()} herramienta {nombre_completo}: {str(e)}")
        return [TextContent(type="text", text=f"❌ Error al guardar la herramienta: {str(e)}")]
