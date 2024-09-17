import pandas as pd
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
import re
import os
import shutil

UPLOAD_FOLDER = os.path.abspath("")

# Define la ruta base de la carpeta archivos_usuarios
base_folder = os.path.join(UPLOAD_FOLDER, "archivos_usuarios")

# Obtiene todas las subcarpetas dentro de archivos_usuarios
subcarpetas = [f.path for f in os.scandir(base_folder) if f.is_dir()]

# Nombre del archivo de referencia que se debe copiar
file_name_importar = "doc_importar.xls"
file_name_datos = "datos_facturas.xlsx"
file_name_cuenta_contable = "Cuenta_contable.xlsx"

# Ruta del archivo de referencia (no modificar)
file_path_importar_referencia = os.path.join(base_folder, file_name_importar)

# Itera sobre cada subcarpeta para realizar el procesamiento
for subcarpeta in subcarpetas:
    # Define las rutas de los archivos en la subcarpeta actual
    file_path_datos = os.path.join(subcarpeta, file_name_datos)
    file_path_cuenta_contable = os.path.join(subcarpeta, file_name_cuenta_contable)
    file_path_importar_subcarpeta = os.path.join(subcarpeta, file_name_importar)
    
    # Verifica si los archivos de datos existen antes de continuar
    if not os.path.exists(file_path_datos) or not os.path.exists(file_path_cuenta_contable):
        print(f"Archivos de datos faltantes en: {subcarpeta}")
        continue
    
    # Copia el archivo doc_importar.xls desde la carpeta principal a la subcarpeta actual
    shutil.copy(file_path_importar_referencia, file_path_importar_subcarpeta)

    # Lee los archivos Excel con los datos a rellenar
    df_datos = pd.read_excel(file_path_datos)
    df_cuenta_contable = pd.read_excel(file_path_cuenta_contable, dtype={'Centro Costos': str, 'IVA': str})

    # Asegúrate de que los valores de NIT y Nit del Emisor: estén en formato de texto
    df_datos['Nit del Emisor:'] = df_datos['Nit del Emisor:'].astype(str)
    df_cuenta_contable['NIT'] = df_cuenta_contable['NIT'].astype(str)

    # Reemplazar NaN en 'Fecha de Vencimiento:' con los valores de 'Fecha de Emisión:'
    df_datos['Fecha de Vencimiento:'] = df_datos['Fecha de Vencimiento:'].fillna(df_datos['Fecha de Emisión:'])

    # Función para limpiar números de factura eliminando espacios, guiones, comas y puntos
    def clean_number(number):
        return re.sub(r'[\s\-,.]', '', str(number))

    # Obtener un conjunto de valores limpios de 'Ref. Factura'
    ref_facturas_set = set(df_datos['Ref. Factura'].dropna().apply(clean_number))

    # Abre el archivo .xls para leer y copiar
    rb = open_workbook(file_path_importar_subcarpeta, formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)

    # Fila destino en el archivo de importación
    dest_row = 1  # Comienza desde la segunda fila en el archivo de importación

    # Calcula el valor más frecuente (moda) de la columna 'Centro Costos'
    centro_costos_mas_frecuente = df_cuenta_contable['Centro Costos'].mode()[0] if not df_cuenta_contable['Centro Costos'].empty else None

    # Itera sobre todas las filas del archivo datos_facturas.xlsx
    for i, row in df_datos.iterrows():
        # Verifica si el tipo de documento es "Nota Crédito"
        tipo_doc = row['Tipo de doc']
        if (tipo_doc == "Nota Crédito"):
            continue  # Omite esta fila y pasa a la siguiente iteración
        
        # Limpia los números de factura y de referencia
        numero_factura = clean_number(row['Número de Factura:'])
        
        # Verifica si el tipo de documento es "FACTURA ELECTRÓNICA DE VENTA" y si coincide "Número de Factura:" con "Ref. Factura"
        if (tipo_doc == "FACTURA ELECTRÓNICA DE VENTA") and (numero_factura in ref_facturas_set):
            continue  # Omite esta fila y pasa a la siguiente iteración

        nit_del_emisor = str(row['Nit del Emisor:'])
        descripcion = str(row['descripcion'])
        fecha_emision = str(row['Fecha de Emisión:'])
        fecha_vencimiento = str(row['Fecha de Vencimiento:'])
        
        # Valores de las columnas para la verificación
        total_bruto_factura = row.get('Total Bruto Factura', 0)
        total_factura = row.get('Total factura (=)', 0)
        iva = row.get('IVA', 0)
        inc = row.get('INC', 0)
        
        # Asegurarse de que los valores son numéricos
        def to_float(value):
            try:
                return float(value)
            except ValueError:
                return 0

        total_bruto_factura = to_float(total_bruto_factura)
        total_factura = to_float(total_factura)
        iva = to_float(iva)
        inc = to_float(inc)
        
        # Definir los valores para la columna mCuenta
        cuenta_iva = df_cuenta_contable.loc[df_cuenta_contable['NIT'] == nit_del_emisor, 'IVA']
        
        mcuenta_values = {
            'IVA': cuenta_iva.values[0] if not cuenta_iva.empty else '24081001',
            'Total factura (=)': '23359505',
            'INC': '51159801',
            'Fallback': '53959501'  # Valor predeterminado cuando no se encuentra un NIT
        }
        
        # Contar cuántas columnas tienen valores mayores a cero
        columnas_mayores_cero = [
            (total_bruto_factura, 'mDebito', 'Total Bruto Factura'), 
            (iva, 'mDebito', 'IVA'), 
            (inc, 'mDebito', 'INC'), 
            (total_factura, 'mCredito', 'Total factura (=)')
        ]
        
        # Escribe los datos en el archivo de importación
        sheet.write(dest_row, 0, 'CP')  # dTipoDocumento
        sheet.write(dest_row, 1, None)  # dConsecutivo
        sheet.write(dest_row, 2, nit_del_emisor)  # dTercero
        sheet.write(dest_row, 3, f"{numero_factura} {descripcion}")  # dDescripcion
        sheet.write(dest_row, 4, fecha_emision)  # dFecha
        sheet.write(dest_row, 5, fecha_vencimiento)  # dVencimiento
        sheet.write(dest_row, 6, numero_factura)  # dReferencia
        sheet.write(dest_row, 7, None)  # mCuenta (vacío por ahora)

        # Incrementa la fila destino considerando las filas vacías
        dest_row += 1
        
        # Rellena las filas vacías
        for value, col_name, mcuenta_key in columnas_mayores_cero:
            if value > 0:
                # Deja una fila vacía
                sheet.write(dest_row, 0, None)  # dTipoDocumento
                sheet.write(dest_row, 1, None)  # dConsecutivo
                
                if col_name == 'mDebito':
                    sheet.write(dest_row, 8, value)  # mDebito
                elif col_name == 'mCredito':
                    sheet.write(dest_row, 9, value)  # mCredito
                
                # Rellena mCuenta según el tipo de dato
                if mcuenta_key and mcuenta_key != 'Total Bruto Factura':
                    sheet.write(dest_row, 7, mcuenta_values[mcuenta_key])  # mCuenta
                elif mcuenta_key == 'Total Bruto Factura':
                    # Busca el valor correspondiente en Cuenta_contable.xlsx
                    cuenta_contable = df_cuenta_contable.loc[df_cuenta_contable['NIT'] == nit_del_emisor, 'Cuenta Contable Moda']
                    if not cuenta_contable.empty:
                        sheet.write(dest_row, 7, str(cuenta_contable.values[0]))  # mCuenta (convertido a cadena)
                    else:
                        sheet.write(dest_row, 7, mcuenta_values['Fallback'])  # Usa el valor predeterminado si no se encuentra el NIT
                
                # Rellenar mDescripcion, mNit, mBase, mCentroC, mSegmento
                sheet.write(dest_row, 10, descripcion)  # mDescripcion
                sheet.write(dest_row, 11, nit_del_emisor)  # mNit
                
                # Aquí agregamos la lógica para calcular mBase cuando es IVA
                if mcuenta_key == 'IVA':
                    mBase_value = round((value * 100) / 19, 2)
                    sheet.write(dest_row, 12, mBase_value)  # mBase
                else:
                    sheet.write(dest_row, 12, None)  # mBase
                
                sheet.write(dest_row, 13, centro_costos_mas_frecuente)  # mCentroC
                sheet.write(dest_row, 14, None)  # mSegmento
                
                dest_row += 1

    # Guardar el archivo modificado
    wb.save(file_path_importar_subcarpeta)
    print(f"Procesamiento completado para la subcarpeta: {subcarpeta}")
