import xlrd
import xlwt
from xlutils.copy import copy
import os

# Define la carpeta principal
UPLOAD_FOLDER = os.path.abspath("")

# Obtiene todas las subcarpetas dentro de "archivos_usuarios"
subcarpetas = [
    os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d) 
    for d in os.listdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios")) 
    if os.path.isdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d))
]

# Asegúrate de que hay subcarpetas disponibles
if not subcarpetas:
    raise ValueError("No se encontraron subcarpetas dentro de la carpeta 'archivos_usuarios'.")

# Procesar cada subcarpeta de forma independiente
for subcarpeta in subcarpetas:
    # Ruta del archivo "doc_importar.xls" en la subcarpeta actual
    file_path = os.path.join(subcarpeta, "doc_importar.xls")
    
    # Verifica si el archivo existe en la subcarpeta
    if not os.path.exists(file_path):
        print(f"El archivo 'doc_importar.xls' no se encontró en la subcarpeta: {subcarpeta}")
        continue

    # Abrir el archivo Excel
    workbook = xlrd.open_workbook(file_path, formatting_info=True)
    sheet = workbook.sheet_by_index(0)

    # Crear una copia del archivo para modificarlo
    workbook_copy = copy(workbook)
    sheet_copy = workbook_copy.get_sheet(0)

    # Obtener índices de las columnas
    header = sheet.row_values(0)
    index_mCuenta = header.index('mCuenta')
    index_mDebito = header.index('mDebito')
    index_mCredito = header.index('mCredito')
    index_dTercero = header.index('dTercero')

    # Función para redondear los valores basándose en los decimales
    def round_based_on_decimal(value):
        try:
            return round(float(value))
        except ValueError:
            return value  # Si no es un número, devolver el valor original

    # Recorrer las filas y rellenar las celdas según las condiciones especificadas
    for row_idx in range(1, sheet.nrows):  # Empezar desde la segunda fila para omitir el encabezado
        mCuenta = sheet.cell_value(row_idx, index_mCuenta)
        mDebito = sheet.cell_value(row_idx, index_mDebito)
        mCredito = sheet.cell_value(row_idx, index_mCredito)
        dTercero = sheet.cell_value(row_idx, index_dTercero)
        
        # Redondear los valores de mDebito y mCredito
        mDebito = round_based_on_decimal(mDebito)
        mCredito = round_based_on_decimal(mCredito)

        # Escribir los valores redondeados de mDebito y mCredito
        sheet_copy.write(row_idx, index_mDebito, mDebito)
        sheet_copy.write(row_idx, index_mCredito, mCredito)

        # Convertir dTercero a número entero si es posible
        try:
            dTercero_int = int(float(dTercero))
            sheet_copy.write(row_idx, index_dTercero, dTercero_int)
        except ValueError:
            pass  # Si no es un número válido, dejarlo como está

        # Condiciones para llenar con 0
        if mCuenta and mDebito == "":
            sheet_copy.write(row_idx, index_mDebito, 0)
        if mCuenta and mCredito == "":
            sheet_copy.write(row_idx, index_mCredito, 0)
        if mDebito and mCuenta == "":
            sheet_copy.write(row_idx, index_mCuenta, 0)
        if mCredito and mCuenta == "":
            sheet_copy.write(row_idx, index_mCuenta, 0)
        if mDebito == "" and mCredito == "" and mCuenta == "":
            # No se hace nada, las columnas siguen vacías
            continue

    # Guardar los cambios en el archivo dentro de la subcarpeta actual
    workbook_copy.save(file_path)

    # Mensaje de confirmación
    print(f"Procesamiento completo para la subcarpeta: {subcarpeta}")
