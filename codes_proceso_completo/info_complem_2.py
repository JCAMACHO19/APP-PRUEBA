import os
import pandas as pd
from xlrd import open_workbook
from xlutils.copy import copy

# Ruta base de la carpeta archivos_usuarios
UPLOAD_FOLDER = os.path.abspath("")
base_folder = os.path.join(UPLOAD_FOLDER, "archivos_usuarios")

# Obtiene todas las subcarpetas dentro de archivos_usuarios
subcarpetas = [f.path for f in os.scandir(base_folder) if f.is_dir()]

# Nombre de los archivos
file_name_importar = "doc_importar.xls"
file_name_datos = "datos_facturas.xlsx"

for subcarpeta in subcarpetas:
    # Ruta completa de los archivos
    file_path_importar = os.path.join(subcarpeta, file_name_importar)
    file_path_datos = os.path.join(subcarpeta, file_name_datos)

    # Verifica si ambos archivos existen en la subcarpeta
    if os.path.exists(file_path_importar) and os.path.exists(file_path_datos):
        # Carga los datos del archivo datos_facturas.xlsx
        df_datos = pd.read_excel(file_path_datos)
        
        # Asegúrate de que las columnas necesarias existan
        if "Nit del Emisor:" in df_datos.columns and "Razón Social:" in df_datos.columns:
            # Crear un diccionario con "Nit del Emisor:" como clave y "Razón Social:" como valor
            map_dict = df_datos.set_index("Nit del Emisor:")["Razón Social:"].to_dict()

            # Carga el archivo doc_importar.xls
            rb = open_workbook(file_path_importar, formatting_info=True)
            wb = copy(rb)
            sheet = wb.get_sheet(0)

            # Convierte el archivo importado a DataFrame
            df_importar = pd.read_excel(file_path_importar)

            # Verifica si la columna dTercero existe en doc_importar.xls
            if "dTercero" in df_importar.columns:
                # Crear nueva columna "NO INCLUIR" basada en coincidencias
                df_importar["NO INCLUIR"] = df_importar["dTercero"].map(map_dict)

                # Reemplazar errores con el valor de la celda superior
                last_valid_value = None
                for i in range(len(df_importar)):
                    if pd.isna(df_importar.at[i, "NO INCLUIR"]):
                        # Usar el último valor válido si la celda está vacía
                        df_importar.at[i, "NO INCLUIR"] = last_valid_value
                    else:
                        # Actualizar el último valor válido
                        last_valid_value = df_importar.at[i, "NO INCLUIR"]

                # Escribir los datos actualizados en la hoja de cálculo
                for row_idx, value in enumerate(df_importar["NO INCLUIR"], start=1):
                    sheet.write(row_idx, len(df_importar.columns) - 1, value)

                # Sobrescribir el archivo original
                wb.save(file_path_importar)

                print(f"Archivo original modificado: {file_path_importar}")
            else:
                print(f"La columna 'dTercero' no se encuentra en {file_path_importar}")
        else:
            print(f"Las columnas necesarias no se encuentran en {file_path_datos}")
    else:
        print(f"No se encontraron ambos archivos en {subcarpeta}")
