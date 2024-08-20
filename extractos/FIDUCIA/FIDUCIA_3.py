import os
from collections import Counter

# Ruta del directorio base
directorio_base = os.path.abspath("extractos/FIDUCIA")

# Diccionario para mapear nombres de meses abreviados a números
meses = {
    'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
    'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
    'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12'
}

def convertir_fecha(fecha_str):
    """Convierte una fecha en formato 'DIA MES AÑO' a 'DIA/MES/AÑO'."""
    partes = fecha_str.split()
    dia = partes[0]
    mes = meses.get(partes[1].upper(), '00')
    año = f"20{partes[2]}"
    return f"{dia}/{mes}/{año}"

def procesar_archivo(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()

    lineas_numeros = []
    lineas_modificadas = []
    indices_modificados = set()

    # Separar las líneas que comienzan con números y las que no
    for i, linea in enumerate(lineas):
        linea = linea.strip()  # Limpiar espacios en blanco alrededor
        if linea[:2].isdigit():
            # Añadir los primeros 10 caracteres de las líneas que comienzan con números a la lista
            lineas_numeros.append(linea[:9])
        else:
            # Añadir las líneas que no comienzan con números para modificar
            lineas_modificadas.append((i, linea))  # Guardar índice y línea

    # Encontrar el valor moda de los primeros 10 caracteres
    contador = Counter(lineas_numeros)
    valor_moda = contador.most_common(1)[0][0] if contador else ''

    # Modificar las líneas que no comienzan con números
    for i, linea in lineas_modificadas:
        if linea:
            # Insertar el valor moda al inicio de la línea, seguido de un espacio y los datos originales
            # Agregar "; 0" al final de la línea
            lineas[i] = f"{valor_moda} ;{linea}; 0"

    # Convertir la fecha en la primera columna para todas las líneas
    for i, linea in enumerate(lineas):
        columnas = linea.split(';')
        if columnas[0].strip()[:2].isdigit():
            columnas[0] = convertir_fecha(columnas[0].strip())
            lineas[i] = ';'.join(columnas)

    # Filtrar y eliminar líneas vacías
    lineas = [linea for linea in lineas if linea.strip()]

    # Escribir las líneas modificadas en el archivo original
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write('\n'.join(lineas))

    print(f"Archivo modificado correctamente: {ruta_archivo}")

def procesar_archivos_en_directorio(directorio_base):
    for root, dirs, files in os.walk(directorio_base):
        for file in files:
            if file.endswith('.txt'):
                ruta_archivo = os.path.join(root, file)
                procesar_archivo(ruta_archivo)

# Procesar todos los archivos .txt en el directorio base y sus subcarpetas
try:
    procesar_archivos_en_directorio(directorio_base)
except Exception as e:
    print(f"Error durante el procesamiento: {e}")
