import os
import fitz  # PyMuPDF
import PyPDF2
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

def buscar_variables(documento):
    """Función para buscar las variables en el texto extraído del documento PDF"""
    variables = {
        "Número de Factura:": None,
        "Fecha de Emisión:": None,
        "Fecha de Vencimiento:": None,
        "Razón Social:": None,
        "Nit del Emisor:": None,
        "Total Bruto Factura": None,
        "Total neto factura (=)": None,
        "Total factura (=)": None,
        "IVA": None,
        "INC": None, 
        "Rete fuente": None
    }

    # Procesar cada página del documento
    for page_num in range(documento.page_count):
        page = documento.load_page(page_num)
        texto = page.get_text("text")

        for variable in variables:
            if variable in texto:
                # Encontrar la posición de la variable
                index = texto.find(variable)
                if index != -1:
                    # Extraer el valor después de la variable
                    start_index = index + len(variable)
                    
                    if variable in ["Total Bruto Factura", "Total neto factura (=)", "Total factura (=)","IVA","INC","Rete fuente"]:
                        # Saltar el espacio adicional para estas variables
                        start_index = texto.find('\n', start_index) + 1
                        end_index = texto.find('\n', start_index)
                    else:
                        end_index = texto.find('\n', start_index)
                        if end_index == -1:
                            end_index = None
                    
                    valor = texto[start_index:end_index].strip()
                    
                    # Manejar valores con espacios adicionales
                    if variable in ["Total Bruto Factura", "Total neto factura (=)", "Total factura (=)","IVA","INC","Rete fuente"]:
                        valor = valor.split()[-1]
                    
                    variables[variable] = valor

        # Ajuste para identificar "IVA" solo si está entre "Total Bruto Factura" y "INC"
        if variables["Total Bruto Factura"] and variables["INC"]:
            bruto_index = texto.find("Total Bruto Factura")
            inc_index = texto.find("INC")
            iva_index = texto.find("IVA", bruto_index, inc_index)
            
            if iva_index != -1:
                start_index = texto.find('\n', iva_index) + 1
                end_index = texto.find('\n', start_index)
                variables["IVA"] = texto[start_index:end_index].strip().split()[-1]

    return variables

def convertir_a_numero(valor):
    """Convierte un valor a tipo numérico si es posible, manteniendo las comas como separadores decimales"""
    try:
        # Reemplazar puntos por nada y comas por puntos para convertir a float
        return pd.to_numeric(valor.replace('.', '').replace(',', '.').strip())
    except ValueError:
        return valor

def extraer_texto(pdf_path):
    texto = ""
    with open(pdf_path, 'rb') as file:
        lector_pdf = PyPDF2.PdfReader(file)
        for pagina in range(len(lector_pdf.pages)):
            pagina_obj = lector_pdf.pages[pagina]
            texto += pagina_obj.extract_text()
    return texto

def extraer_primera_descripcion(texto):
    lines = texto.split('\n')
    descripcion = None
    for i, line in enumerate(lines):
        if "Descripción" in line:
            # Extraer la descripción de las líneas 12 y 13 después de la línea "Descripción"
            if i + 12 < len(lines) and i + 13 < len(lines):
                descripcion = lines[i + 12].strip() + " " + lines[i + 13].strip()
            break
    if descripcion:
        # Eliminar todos los números de la primera palabra
        palabras = descripcion.split()
        primera_palabra = ''.join([c for c in palabras[0] if not c.isdigit()])
        descripcion = primera_palabra + ' ' + ' '.join(palabras[1:])
    return descripcion

def extraer_tipo_documento(texto):
    """Función para identificar el tipo de documento basado en el texto extraído"""
    if "Nota Crédito" in texto:
        return "Nota Crédito"
    elif "FACTURA ELECTRÓNICA" in texto:
        return "FACTURA ELECTRÓNICA DE VENTA"
    elif "FACTURA ELECTRÓNICA DE TRANSPORTE" in texto:
        return "FACTURA ELECTRÓNICA DE VENTA"
    else:
        return "Tipo Desconocido"

def extraer_ref_factura(texto):
    """Función para extraer la referencia de factura que sigue a la segunda aparición de 'Factura Electrónica'"""
    # Encontrar todas las apariciones de "Factura Electrónica"
    matches = list(re.finditer(r'Factura Electrónica\s*([\w\d-]+)', texto))
    if len(matches) > 1:
        # Obtener la segunda coincidencia y su texto asociado
        segunda_aparicion = matches[1]
        return segunda_aparicion.group(1).strip()
    return None

def ajustar_total_bruto_factura(df):
    """Ajusta 'Total Bruto Factura' para que se cumpla la ecuación:
    Total Bruto Factura + IVA + INC = Total factura (=)"""

    # Crear una lista para almacenar mensajes de ajuste
    mensajes_ajuste = []

    for index, row in df.iterrows():
        total_bruto = row['Total Bruto Factura']
        iva = row['IVA']
        inc = row['INC']
        total_factura = row['Total factura (=)']

        # Calcular la suma de Total Bruto Factura + IVA + INC
        suma = total_bruto + iva + inc

        # Verificar si hay una diferencia
        diferencia = total_factura - suma

        if diferencia != 0:
            # Ajustar la diferencia al valor de Total Bruto Factura
            nuevo_total_bruto = total_bruto + diferencia
            # Asegurar que Total Bruto Factura no sea negativo
            if nuevo_total_bruto < 0:
                nuevo_total_bruto = 0
            df.at[index, 'Total Bruto Factura'] = nuevo_total_bruto
            # Añadir mensaje de ajuste
            mensajes_ajuste.append(f"Ajustado: diferencia de {diferencia}")
        else:
            mensajes_ajuste.append("Sin ajuste")

    # Añadir la columna de mensajes de ajuste al DataFrame
    df['Mensaje Ajuste'] = mensajes_ajuste

def procesar_pdf(ruta_pdf):
    """Función para procesar un solo PDF y devolver los datos extraídos"""
    # Abrir el archivo PDF
    documento = fitz.open(ruta_pdf)

    # Buscar las variables en el documento
    variables_encontradas = buscar_variables(documento)

    # Cerrar el documento PDF
    documento.close()

    # Extraer el texto del PDF para otras operaciones
    texto = extraer_texto(ruta_pdf)
    descripcion = extraer_primera_descripcion(texto)
    tipo_documento = extraer_tipo_documento(texto)
    ref_factura = extraer_ref_factura(texto) if tipo_documento == "Nota Crédito" else ""

    # Convertir valores numéricos
    for key in ["Nit del Emisor:", "Total Bruto Factura", "Total neto factura (=)", "Total factura (=)", "IVA", "INC", "Rete fuente"]:
        if variables_encontradas.get(key) is not None:
            variables_encontradas[key] = convertir_a_numero(variables_encontradas[key])

    return variables_encontradas, descripcion, tipo_documento, ref_factura

# Ruta donde se encuentra la carpeta PRUEBA IMPORTE DE DOCUMENTOS
directorio = os.path.join(os.path.abspath(""), "archivos_usuarios")

# Obtener todos los archivos PDF en la carpeta PRUEBA IMPORTE DE DOCUMENTOS
archivos_pdf = [os.path.join(directorio, archivo) for archivo in os.listdir(directorio) if archivo.endswith('.pdf')]

# Lista para almacenar los datos extraídos de cada PDF
datos = []
descripciones = []
tipos_documentos = []
referencias_factura = []

# Ejecutar la extracción de información en paralelo
with ThreadPoolExecutor() as executor:
    resultados = executor.map(procesar_pdf, archivos_pdf)

# Procesar los resultados
for variables_encontradas, descripcion, tipo_documento, ref_factura in resultados:
    datos.append(variables_encontradas)
    descripciones.append(descripcion)
    tipos_documentos.append(tipo_documento)
    referencias_factura.append(ref_factura)

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(datos)

# Añadir las nuevas columnas al DataFrame
df['descripcion'] = descripciones
df['Tipo de doc'] = tipos_documentos
df['Ref. Factura'] = referencias_factura

# Ajustar 'Total Bruto Factura' para que se cumpla la ecuación
ajustar_total_bruto_factura(df)

# Guardar el DataFrame en un archivo de Excel
ruta_excel = os.path.join(directorio, "archivo_final.xlsx")
df.to_excel(ruta_excel, index=False)

