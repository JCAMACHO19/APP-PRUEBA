import pandas as pd
import os

# Ruta del archivo CSV
file_path_csv = r'C:\Users\jcamacho\Desktop\PRUEBA IMPORTE DE DOCUMENTOS\MovDocCuenta_CSV.csv'

# Leer el archivo CSV, omitiendo las primeras 7 filas
df = pd.read_csv(file_path_csv, skiprows=7, encoding='latin1', dtype={'Centro Costos': str, 'Cuenta Contable': str})

# Ruta del archivo Excel de salida
excel_path = r'C:\Users\jcamacho\Desktop\PRUEBA IMPORTE DE DOCUMENTOS\MovDocCuenta_Excel.xlsx'

# Eliminar archivo Excel si ya existe
if os.path.exists(excel_path):
    os.remove(excel_path)

# Guardar el DataFrame en un archivo Excel
df.to_excel(excel_path, index=False)

# Leer el archivo Excel
df = pd.read_excel(excel_path, dtype={'Centro Costos': str, 'Cuenta Contable': str})

# Filtrar filas que contengan "CP", "AJ", "LG" en la columna "Tipo Doc."
df_filtered = df[df['Tipo Doc.'].isin(['CP', 'AJ', 'LG'])]

# Calcular la moda de "Cuenta Contable" para cada "NIT" en el DataFrame filtrado
def moda_cuenta_contable(grupo):
    cuentas_especiales = ['53152001', '73359507', '53959501']
    # Filtrar las cuentas que no sean especiales
    cuentas_no_especiales = grupo[~grupo['Cuenta Contable'].isin(cuentas_especiales)]
    # Si hay cuentas no especiales, retornar la moda de estas
    if not cuentas_no_especiales.empty:
        return cuentas_no_especiales['Cuenta Contable'].mode()[0]
    # Si todas las cuentas son especiales, retornar la moda normal
    return grupo['Cuenta Contable'].mode()[0]

modas = df_filtered.groupby('NIT', group_keys=False).apply(moda_cuenta_contable).reset_index()
modas.columns = ['NIT', 'Cuenta Contable Moda']

# Unir el DataFrame original con el de las modas
df = pd.merge(df, modas, on='NIT', how='left')

# Seleccionar solo las columnas necesarias
df = df[['NIT', 'Cuenta Contable Moda', 'Tipo Doc.', 'Centro Costos']]

# Eliminar filas duplicadas basadas en la columna "NIT"
df = df.drop_duplicates(subset='NIT')

# Eliminar filas sin dato en la columna 'Cuenta Contable Moda'
df = df.dropna(subset=['Cuenta Contable Moda'])

# Convertir la columna 'Cuenta Contable Moda' a formato texto
df['Cuenta Contable Moda'] = df['Cuenta Contable Moda'].astype(str)

# Función para determinar el valor de la columna "IVA"
def calcular_iva(cuenta):
    if cuenta[:4] in ['5110', '5120', '5130', '5135', '5140', '7310', '7330', '7335']:
        return '24081003'
    else:
        return '24081001'

# Aplicar la función a la columna "Cuenta Contable Moda" y crear la nueva columna "IVA"
df['IVA'] = df['Cuenta Contable Moda'].apply(calcular_iva)

# Guardar el resultado en un nuevo archivo Excel
output_file_path = r'C:\Users\jcamacho\Desktop\PRUEBA IMPORTE DE DOCUMENTOS\Cuenta_contable.xlsx'
df.to_excel(output_file_path, index=False)

# Eliminar archivos temporales
if os.path.exists(file_path_csv):
    os.remove(file_path_csv)

if os.path.exists(excel_path):
    os.remove(excel_path)

print(f'El archivo modificado se ha guardado en {output_file_path}')
