import os
import fitz  # PyMuPDF
import PyPDF2
import pandas as pd
import re

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

UPLOAD_FOLDER =  os.path.abspath("")

# Ruta donde se encuentra la carpeta PRUEBA IMPORTE DE DOCUMENTOS
directorio = os.path.join(UPLOAD_FOLDER,"archivos_usuarios")

# Obtener todos los archivos PDF en la carpeta PRUEBA IMPORTE DE DOCUMENTOS
archivos_pdf = [os.path.join(directorio, archivo) for archivo in os.listdir(directorio) if archivo.endswith('.pdf')]

# Lista para almacenar los datos extraídos de cada PDF
datos = []
descripciones = []
tipos_documentos = []
referencias_factura = []

# Procesar cada archivo PDF encontrado
for ruta_pdf in archivos_pdf:
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

    # Añadir la descripción y otras informaciones a las listas
    descripciones.append(descripcion)
    tipos_documentos.append(tipo_documento)
    referencias_factura.append(ref_factura)

    # Convertir valores numéricos
    for key in ["Nit del Emisor:", "Total Bruto Factura", "Total neto factura (=)", "Total factura (=)", "IVA", "INC", "Rete fuente"]:
        if variables_encontradas.get(key) is not None:
            variables_encontradas[key] = convertir_a_numero(variables_encontradas[key])

    # Añadir los datos extraídos a la lista
    datos.append(variables_encontradas)

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(datos)

# Añadir las nuevas columnas al DataFrame
df['descripcion'] = descripciones
df['Tipo de doc'] = tipos_documentos
df['Ref. Factura'] = referencias_factura

# Guardar el DataFrame en un archivo de Excel
ruta_excel = os.path.join(directorio, 'datos_facturas.xlsx')
df.to_excel(ruta_excel, index=False)

print(f"Archivo de Excel creado en: {ruta_excel}")
