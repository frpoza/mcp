"""
Herramienta: FR_renombrar_ficheros
Descripcion: Abre el Explorador de Windows para seleccionar un directorio. Renombra:
             - Directorios: TODAS LAS LETRAS EN MAYUSCULAS
             - Ficheros: Primera Letra Mayuscula, resto minusculas, extension en minusculas
             Recursivo incluyendo subdirectorios. Cierra el explorador al finalizar.
Generada automaticamente el 2026-02-27
Autor: Sistema de Generacion Automatica
"""

import os
import tkinter as tk
from tkinter import filedialog
from mcp.types import Tool, TextContent
from pathlib import Path

# Definicion de la herramienta
HERRAMIENTA = Tool(
    name="FR_renombrar_ficheros",
    description="Abre el Explorador de Windows para seleccionar un directorio. Renombra: Directorios en MAYUSCULAS, Ficheros con Primera Letra Mayuscula y extension en minusculas (recursivo, incluyendo subdirectorios), y cierra el explorador al finalizar.",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

def renombrar_fichero(nombre_original: str) -> str:
    """
    Renombra un fichero: Primera Letra Mayuscula, resto minusculas, extension en minusculas
    Ejemplo: "miARCHIVO.PDF" -> "Miarchivo.pdf"
    """
    ruta = Path(nombre_original)
    nombre_sin_ext = ruta.stem  # Nombre sin extension
    extension = ruta.suffix      # Extension con el punto
    
    # Primera letra mayuscula, resto minusculas
    nombre_formateado = nombre_sin_ext[0].upper() + nombre_sin_ext[1:].lower() if nombre_sin_ext else ""
    
    # Extension completamente en minusculas
    extension_minuscula = extension.lower()
    
    return nombre_formateado + extension_minuscula

def renombrar_directorio(nombre_original: str) -> str:
    """
    Renombra un directorio: TODAS LAS LETRAS EN MAYUSCULAS
    Ejemplo: "MiCarpeta" -> "MICARPETA"
    """
    return nombre_original.upper()

# Funcion de ejecucion
async def ejecutar(argumentos: dict) -> list[TextContent]:
    """Ejecuta la herramienta FR_renombrar_ficheros"""

    # Ocultar ventana principal de tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Abrir explorador para seleccionar carpeta
    directorio = filedialog.askdirectory(
        title="Selecciona el directorio para renombrar (Dirs: MAYUSCULAS, Ficheros: Primera Mayuscula + Extension minuscula)"
    )
    root.destroy()

    if not directorio:
        return [TextContent(type="text", text="❌ Operación cancelada: no se seleccionó ningún directorio.")]

    renombrados = 0
    errores = 0
    errores_detalle = []
    cambios_realizados = []

    # Recorrer el árbol de directorios de abajo hacia arriba (bottom-up)
    # para evitar problemas al renombrar carpetas padre antes que hijos
    for raiz, carpetas, archivos in os.walk(directorio, topdown=False):
        # Renombrar archivos
        for nombre in archivos:
            nombre_nuevo = renombrar_fichero(nombre)
            if nombre != nombre_nuevo:
                ruta_original = os.path.join(raiz, nombre)
                ruta_nueva = os.path.join(raiz, nombre_nuevo)
                try:
                    # Verificar que no exista ya el archivo con el nuevo nombre
                    if os.path.exists(ruta_nueva):
                        errores += 1
                        errores_detalle.append(f"{ruta_original}: Ya existe un archivo con el nombre '{nombre_nuevo}'")
                    else:
                        os.rename(ruta_original, ruta_nueva)
                        renombrados += 1
                        cambios_realizados.append(f"  📄 {nombre} → {nombre_nuevo}")
                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"{ruta_original}: {str(e)}")

        # Renombrar subdirectorios (de abajo hacia arriba)
        for carpeta in carpetas:
            carpeta_nueva = renombrar_directorio(carpeta)
            if carpeta != carpeta_nueva:
                ruta_original = os.path.join(raiz, carpeta)
                ruta_nueva = os.path.join(raiz, carpeta_nueva)
                try:
                    # Verificar que no exista ya el directorio con el nuevo nombre
                    if os.path.exists(ruta_nueva):
                        errores += 1
                        errores_detalle.append(f"{ruta_original}: Ya existe un directorio con el nombre '{carpeta_nueva}'")
                    else:
                        os.rename(ruta_original, ruta_nueva)
                        renombrados += 1
                        cambios_realizados.append(f"  📁 {carpeta} → {carpeta_nueva}")
                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"{ruta_original}: {str(e)}")

    # Construir mensaje de resultado
    resultado = f"✅ Proceso completado en: {directorio}\n"
    resultado += f"   📊 Elementos renombrados: {renombrados}\n"
    
    if cambios_realizados:
        resultado += f"\n📝 Cambios realizados (primeros 10):\n"
        for cambio in cambios_realizados[:10]:
            resultado += f"{cambio}\n"
        if len(cambios_realizados) > 10:
            resultado += f"   ... y {len(cambios_realizados) - 10} más\n"
    
    if errores > 0:
        resultado += f"\n   ⚠️ Errores encontrados: {errores}\n"
        for detalle in errores_detalle[:5]:  # Mostrar máximo 5 errores
            resultado += f"      - {detalle}\n"
    else:
        resultado += f"\n   ✔️ Sin errores."

    return [TextContent(type="text", text=resultado)]
