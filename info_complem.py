import xlrd
import xlwt
from xlutils.copy import copy

# Ruta del archivo
file_path = 'C:\\Users\\jcamacho\\Desktop\\PRUEBA IMPORTE DE DOCUMENTOS\\doc_importar.xls'

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
    
    # Redondear los valores de mDebito y mCredito
    mDebito = round_based_on_decimal(mDebito)
    mCredito = round_based_on_decimal(mCredito)

    # Escribir los valores redondeados de mDebito y mCredito
    sheet_copy.write(row_idx, index_mDebito, mDebito)
    sheet_copy.write(row_idx, index_mCredito, mCredito)

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

# Guardar los cambios en el archivo
workbook_copy.save(file_path)
