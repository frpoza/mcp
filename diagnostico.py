import os
import sys
import json

def diagnosticar():
    print("=== DIAGNÓSTICO COMPLETO ===\n")
    
    # 1. Verificar Python
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}\n")
    
    # 2. Verificar openpyxl
    try:
        import openpyxl
        print(f"✅ openpyxl version: {openpyxl.__version__}")
    except ImportError:
        print("❌ openpyxl NO instalado")
    
    # 3. Verificar carpeta TEMP
    temp_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'revit_ext')
    json_path = os.path.join(temp_dir, 'revit_data.json')
    
    print(f"\nBuscando JSON en: {json_path}")
    print(f"¿Existe carpeta? {os.path.exists(temp_dir)}")
    
    if os.path.exists(temp_dir):
        print("Archivos en carpeta:")
        for f in os.listdir(temp_dir):
            print(f"  - {f}")
    
    print(f"¿Existe JSON? {os.path.exists(json_path)}")
    
    # 4. Verificar otras ubicaciones
    print("\nBuscando en otras ubicaciones:")
    otras = [
        os.path.join(os.getcwd(), 'revit_data.json'),
        os.path.join(os.path.expanduser('~'), 'revit_data.json'),
        'D:\\0-TRABAJOS\\2020\\02-20 C JODAR 15 UBEDA\\BIM\\revit_data.json'
    ]
    
    for loc in otras:
        if os.path.exists(loc):
            print(f"✅ Encontrado: {loc}")
    
    # 5. Verificar el archivo que intentas ejecutar
    print(f"\nDirectorio actual: {os.getcwd()}")
    print("Archivos en herramientas:")
    try:
        for f in os.listdir('herramientas'):
            if f.endswith('.py'):
                print(f"  - {f}")
    except:
        print("  No se puede acceder a la carpeta herramientas")

if __name__ == "__main__":
    diagnosticar()