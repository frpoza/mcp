"""
Herramienta: FR_renombrar_mayusculas
Descripcion: Abre el Explorador de Windows para seleccionar un directorio, renombra a MAYÚSCULAS todos los archivos y carpetas (recursivo, incluyendo subdirectorios), y cierra el explorador al finalizar.
Generada automaticamente el 2026-02-12 18:31:45
Autor: Sistema de Generacion Automatica
"""

import os
import tkinter as tk
from tkinter import filedialog
from mcp.types import Tool, TextContent

# Definicion de la herramienta
HERRAMIENTA = Tool(
    name="FR_renombrar_mayusculas",
    description="Abre el Explorador de Windows para seleccionar un directorio, renombra a MAYÚSCULAS todos los archivos y carpetas (recursivo, incluyendo subdirectorios), y cierra el explorador al finalizar.",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

# Funcion de ejecucion
async def ejecutar(argumentos: dict) -> list[TextContent]:
    """Ejecuta la herramienta FR_renombrar_mayusculas"""

    # Ocultar ventana principal de tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Abrir explorador para seleccionar carpeta
    directorio = filedialog.askdirectory(
        title="Selecciona el directorio para renombrar a MAYÚSCULAS"
    )
    root.destroy()

    if not directorio:
        return [TextContent(type="text", text="❌ Operación cancelada: no se seleccionó ningún directorio.")]

    renombrados = 0
    errores = 0
    errores_detalle = []

    # Recorrer el árbol de directorios de abajo hacia arriba (bottom-up)
    # para evitar problemas al renombrar carpetas padre antes que hijos
    for raiz, carpetas, archivos in os.walk(directorio, topdown=False):
        # Renombrar archivos
        for nombre in archivos:
            nombre_nuevo = nombre.upper()
            if nombre != nombre_nuevo:
                ruta_original = os.path.join(raiz, nombre)
                ruta_nueva = os.path.join(raiz, nombre_nuevo)
                try:
                    os.rename(ruta_original, ruta_nueva)
                    renombrados += 1
                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"{ruta_original}: {str(e)}")

        # Renombrar subcarpetas
        for carpeta in carpetas:
            carpeta_nueva = carpeta.upper()
            if carpeta != carpeta_nueva:
                ruta_original = os.path.join(raiz, carpeta)
                ruta_nueva = os.path.join(raiz, carpeta_nueva)
                try:
                    os.rename(ruta_original, ruta_nueva)
                    renombrados += 1
                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"{ruta_original}: {str(e)}")

    # Construir mensaje de resultado
    resultado = f"✅ Proceso completado en: {directorio}\n"
    resultado += f"   📄 Elementos renombrados: {renombrados}\n"
    if errores > 0:
        resultado += f"   ⚠️ Errores: {errores}\n"
        for detalle in errores_detalle[:5]:  # Mostrar máximo 5 errores
            resultado += f"      - {detalle}\n"
    else:
        resultado += f"   ✔️ Sin errores."

    return [TextContent(type="text", text=resultado)]