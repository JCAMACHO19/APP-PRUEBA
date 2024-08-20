import pandas as pd
import os

UPLOAD_FOLDER = os.path.abspath("")

def trasladar_datos_a_excel(directorio_base):
    # Recorrer todas las subcarpetas y archivos
    for root, dirs, files in os.walk(directorio_base):
        if 'INGRESOS.txt' in files and 'EGRESOS.txt' in files:
            # Rutas de los archivos
            ruta_ingresos = os.path.join(root, 'INGRESOS.txt')
            ruta_egresos = os.path.join(root, 'EGRESOS.txt')
            ruta_excel = os.path.join(root, "Extracto_Fiducia.xlsx")

            # Leer y procesar el archivo INGRESOS.txt
            with open(ruta_ingresos, 'r', encoding='utf-8') as archivo:
                lineas_ingresos = archivo.readlines()

            fechas_ingresos = []
            descripciones_ingresos = []
            debitos_ingresos = []

            for linea in lineas_ingresos:
                columnas = linea.strip().split(';')
                if len(columnas) >= 3:
                    fechas_ingresos.append(columnas[0])
                    descripciones_ingresos.append(columnas[1])
                    debitos_ingresos.append(columnas[2].replace('.', '').replace(',', '.'))

            # Crear DataFrame para INGRESOS
            df_ingresos = pd.DataFrame({
                'Fecha': fechas_ingresos,
                'Descripcion': descripciones_ingresos,
                'Debitos': debitos_ingresos,
                'Creditos': [''] * len(fechas_ingresos)  # Columna Créditos vacía
            })

            # Leer y procesar el archivo EGRESOS.txt
            with open(ruta_egresos, 'r', encoding='utf-8') as archivo:
                lineas_egresos = archivo.readlines()

            fechas_egresos = []
            descripciones_egresos = []
            creditos_egresos = []

            for linea in lineas_egresos:
                columnas = linea.strip().split(';')
                if len(columnas) >= 3:
                    fechas_egresos.append(columnas[0])
                    descripciones_egresos.append(columnas[1])
                    creditos_egresos.append(columnas[2].replace('.', '').replace(',', '.'))

            # Crear DataFrame para EGRESOS
            df_egresos = pd.DataFrame({
                'Fecha': fechas_egresos,
                'Descripcion': descripciones_egresos,
                'Creditos': creditos_egresos,
                'Debitos': [''] * len(fechas_egresos)  # Columna Débitos vacía
            })

            # Convertir las columnas de débitos y créditos a números con dos decimales
            df_ingresos['Debitos'] = pd.to_numeric(df_ingresos['Debitos'], errors='coerce').round(2)
            df_egresos['Creditos'] = pd.to_numeric(df_egresos['Creditos'], errors='coerce').round(2)

            # Cargar el archivo Excel existente si ya existe
            if os.path.exists(ruta_excel):
                excel_df = pd.read_excel(ruta_excel)
            else:
                excel_df = pd.DataFrame(columns=['Fecha', 'No_Operacion', 'Descripcion', 'Creditos', 'Debitos'])

            # Combinar los datos de INGRESOS y EGRESOS con los datos existentes
            excel_df = pd.concat([excel_df, df_ingresos, df_egresos], ignore_index=True)

            # Convertir las columnas 'Creditos' y 'Debitos' a formato numérico con dos decimales
            excel_df['Creditos'] = pd.to_numeric(excel_df['Creditos'], errors='coerce').round(2)
            excel_df['Debitos'] = pd.to_numeric(excel_df['Debitos'], errors='coerce').round(2)

            # Reemplazar caracteres especiales en la columna 'Descripcion'
            excel_df['Descripcion'] = excel_df['Descripcion'].str.replace(r'[$%&]', 'Y', regex=True)

            # Guardar el DataFrame actualizado en el archivo Excel
            excel_df.to_excel(ruta_excel, index=False)

            print(f"Datos trasladados correctamente a {ruta_excel}")

# Ruta base para buscar archivos
directorio_base = os.path.join(UPLOAD_FOLDER, "extractos", "FIDUCIA")

# Ejecutar la función
try:
    trasladar_datos_a_excel(directorio_base)
except Exception as e:
    print(f"Error durante el procesamiento: {e}")


