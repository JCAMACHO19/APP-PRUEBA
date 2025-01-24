import os
import pandas as pd
import xlrd
import xlwt
from xlutils.copy import copy

# Define la carpeta principal
UPLOAD_FOLDER = os.path.abspath("")
base_folder = os.path.join(UPLOAD_FOLDER, "archivos_usuarios")

# Obtiene todas las subcarpetas dentro de "archivos_usuarios"
subcarpetas = [
    os.path.join(base_folder, d) 
    for d in os.listdir(base_folder) 
    if os.path.isdir(os.path.join(base_folder, d))
]

# Asegúrate de que hay subcarpetas disponibles
if not subcarpetas:
    raise ValueError("No se encontraron subcarpetas dentro de la carpeta 'archivos_usuarios'.")

# Nombres de los archivos
file_name_importar = "doc_importar.xls"
file_name_datos = "datos_facturas.xlsx"

# Función para redondear valores
def round_based_on_decimal(value):
    try:
        return round(float(value))
    except ValueError:
        return value  # Si no es un número, devolver el valor original

# Procesar cada subcarpeta
for subcarpeta in subcarpetas:
    # Ruta completa de los archivos
    file_path_importar = os.path.join(subcarpeta, file_name_importar)
    file_path_datos = os.path.join(subcarpeta, file_name_datos)

    # Verifica si el archivo "doc_importar.xls" existe
    if not os.path.exists(file_path_importar):
        print(f"El archivo '{file_name_importar}' no se encontró en la subcarpeta: {subcarpeta}")
        continue

    # Carga el archivo "doc_importar.xls"
    rb = xlrd.open_workbook(file_path_importar, formatting_info=True)
    wb = copy(rb)
    sheet_copy = wb.get_sheet(0)

    # Carga el archivo como DataFrame
    df_importar = pd.read_excel(file_path_importar)

    # Obtener índices de las columnas
    header = rb.sheet_by_index(0).row_values(0)
    index_mCuenta = header.index('mCuenta')
    index_mDebito = header.index('mDebito')
    index_mCredito = header.index('mCredito')
    index_dTercero = header.index('dTercero')

    # Recorrer las filas y rellenar según las condiciones
    for row_idx in range(1, rb.sheet_by_index(0).nrows):
        mCuenta = rb.sheet_by_index(0).cell_value(row_idx, index_mCuenta)
        mDebito = rb.sheet_by_index(0).cell_value(row_idx, index_mDebito)
        mCredito = rb.sheet_by_index(0).cell_value(row_idx, index_mCredito)
        dTercero = rb.sheet_by_index(0).cell_value(row_idx, index_dTercero)

        # Redondear valores
        mDebito = round_based_on_decimal(mDebito)
        mCredito = round_based_on_decimal(mCredito)

        # Escribir valores redondeados
        sheet_copy.write(row_idx, index_mDebito, mDebito)
        sheet_copy.write(row_idx, index_mCredito, mCredito)

        # Convertir dTercero a número entero si es posible
        try:
            dTercero_int = int(float(dTercero))
            sheet_copy.write(row_idx, index_dTercero, dTercero_int)
        except ValueError:
            pass  # Si no es un número válido, dejarlo como está

        # Condiciones para rellenar con 0
        if mCuenta and mDebito == "":
            sheet_copy.write(row_idx, index_mDebito, 0)
        if mCuenta and mCredito == "":
            sheet_copy.write(row_idx, index_mCredito, 0)
        if mDebito and mCuenta == "":
            sheet_copy.write(row_idx, index_mCuenta, 0)
        if mCredito and mCuenta == "":
            sheet_copy.write(row_idx, index_mCuenta, 0)

    # Procesar "datos_facturas.xlsx" si existe
    if os.path.exists(file_path_datos):
        df_datos = pd.read_excel(file_path_datos)

        if "Nit del Emisor:" in df_datos.columns and "Razón Social:" in df_datos.columns:
            # Crear diccionario de mapeo
            map_dict = df_datos.set_index("Nit del Emisor:")["Razón Social:"].to_dict()

            # Agregar columna "NO INCLUIR" basada en coincidencias
            if "dTercero" in df_importar.columns:
                df_importar["NO INCLUIR"] = df_importar["dTercero"].map(map_dict)

                # Rellenar celdas vacías con el último valor válido
                last_valid_value = None
                for i in range(len(df_importar)):
                    if pd.isna(df_importar.at[i, "NO INCLUIR"]):
                        df_importar.at[i, "NO INCLUIR"] = last_valid_value
                    else:
                        last_valid_value = df_importar.at[i, "NO INCLUIR"]

                # Escribir columna "NO INCLUIR" en el archivo
                for row_idx, value in enumerate(df_importar["NO INCLUIR"], start=1):
                    sheet_copy.write(row_idx, len(header), value)

            else:
                print(f"La columna 'dTercero' no se encuentra en {file_path_importar}")

    # Guardar cambios en el archivo "doc_importar.xls"
    wb.save(file_path_importar)
    print(f"Procesamiento completo para la subcarpeta: {subcarpeta}")
