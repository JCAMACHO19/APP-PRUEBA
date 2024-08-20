import os

# Ruta del directorio base
directorio_base = os.path.abspath("extractos/FIDUCIA")

def eliminar_lineas_vacias_y_convertir_columna(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()

    lineas_procesadas = []

    for linea in lineas:
        linea = linea.strip()
        if linea:
            columnas = linea.split(';')
            if len(columnas) >= 3:
                # Convertir la tercera columna a formato general sin $
                columnas[2] = columnas[2].replace('$', '').replace('.', '').strip()
                # Cambiar la coma de miles a punto y el punto decimal a coma
                columnas[2] = columnas[2].replace(',', '.')
                partes = columnas[2].split('.')
                if len(partes) > 1:
                    columnas[2] = f"{partes[0]},{partes[1]}"
                else:
                    columnas[2] = partes[0]

            # Reunir las columnas en la línea procesada
            linea_procesada = ';'.join(columnas)
            lineas_procesadas.append(linea_procesada)

    # Escribir las líneas procesadas en el archivo original
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write('\n'.join(lineas_procesadas))

    print(f"Archivo procesado correctamente: {ruta_archivo}")

def procesar_archivos_en_directorio(directorio_base):
    for root, dirs, files in os.walk(directorio_base):
        for file in files:
            if file.endswith('.txt'):
                ruta_archivo = os.path.join(root, file)
                eliminar_lineas_vacias_y_convertir_columna(ruta_archivo)

# Procesar todos los archivos .txt en el directorio base y sus subcarpetas
try:
    procesar_archivos_en_directorio(directorio_base)
except Exception as e:
    print(f"Error durante el procesamiento: {e}")

