import os

# Ruta del directorio base
directorio_base = os.path.abspath(os.path.join("extractos", "FIDUCIA"))

# Obtener la primera ruta de archivo .txt en cualquier subcarpeta
def obtener_archivos_txt(directorio_base):
    archivos_txt = []
    for root, dirs, files in os.walk(directorio_base):
        for file in files:
            if file.endswith('.txt'):
                archivos_txt.append(os.path.join(root, file))
    if archivos_txt:
        return archivos_txt
    else:
        raise FileNotFoundError("No se encontró ningún archivo .txt en el directorio especificado.")

# Procesar el archivo
def procesar_archivo(ruta):
    with open(ruta, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()

    lineas_ingresos = []
    lineas_egresos = []
    procesar_ingresos = False
    procesar_egresos = False

    for linea in lineas:
        if 'INGRESOS' in linea:
            procesar_ingresos = True
            procesar_egresos = False
            continue
        if 'EGRESOS' in linea:
            procesar_ingresos = False
            procesar_egresos = True
            continue
        if procesar_ingresos:
            if linea[:2].isdigit():
                if len(linea) > 10:
                    linea_modificada = linea[:10] + ';' + linea[10:].strip()
                else:
                    linea_modificada = linea.strip()
                lineas_ingresos.append(linea_modificada)
            else:
                lineas_ingresos.append(linea.strip())
        if procesar_egresos:
            if linea[:2].isdigit():
                if len(linea) > 10:
                    linea_modificada = linea[:10] + ';' + linea[10:].strip()
                else:
                    linea_modificada = linea.strip()
                lineas_egresos.append(linea_modificada)
            else:
                lineas_egresos.append(linea.strip())

    # Guardar las líneas de INGRESOS en un archivo
    ruta_ingresos = os.path.join(os.path.dirname(ruta), 'INGRESOS.txt')
    with open(ruta_ingresos, 'w', encoding='utf-8') as archivo_ingresos:
        for linea in lineas_ingresos:
            archivo_ingresos.write(linea + '\n')

    # Guardar las líneas de EGRESOS en un archivo
    ruta_egresos = os.path.join(os.path.dirname(ruta), 'EGRESOS.txt')
    with open(ruta_egresos, 'w', encoding='utf-8') as archivo_egresos:
        for linea in lineas_egresos:
            archivo_egresos.write(linea + '\n')

    print(f"Archivos procesados correctamente: {ruta_ingresos} y {ruta_egresos}")

# Obtener la ruta del archivo y procesarlo
try:
    archivos_txt = obtener_archivos_txt(directorio_base)
    for ruta_archivo in archivos_txt:
        procesar_archivo(ruta_archivo)
except FileNotFoundError as e:
    print(e)

