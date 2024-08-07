from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import openpyxl
import os
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para leer los CUFEs desde un archivo Excel
def leer_cufes_desde_excel(archivo_excel):
    try:
        libro = openpyxl.load_workbook(archivo_excel)
        hoja = libro.active
        cufes = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):  # Asumiendo que la primera fila es el encabezado
            cufe = fila[1]  # Índice CUFE está en la segunda columna
            estado = fila[13]  # Estado Factura
            if estado not in ['Contabilizado', 'Anulado', 'Anulada', 'COSTO MUNICIPIO LA GLORIA', 'COSTO MUNICIPIO SAN CAYETANO', 'COSTO MUNICIPIO SAN JOSE DE CUCUTA']:
                cufes.append(cufe)
        return cufes
    except Exception as e:
        logging.error(f'Error al leer el archivo Excel: {e}')
        return []

# Función para buscar y descargar una factura usando el CUFE
def buscar_y_descargar_factura(driver, cufe, carpeta_descargas):
    nombre_archivo = os.path.join(carpeta_descargas, f'{cufe}.pdf')
    if os.path.exists(nombre_archivo):
        logging.info(f'La factura para el CUFE {cufe} ya existe. No se descargará nuevamente.')
        return

    try:
        driver.get('https://catalogo-vpfe.dian.gov.co/User/SearchDocument')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'DocumentKey')))

        campo_cufe = driver.find_element(By.ID, 'DocumentKey')
        campo_cufe.clear()  # Asegurarse de que el campo esté vacío antes de ingresar el CUFE
        campo_cufe.send_keys(cufe)
        time.sleep(1)  # Asegurarse de que el CUFE se ingrese completamente
        campo_cufe.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')))
        enlace_descarga = driver.find_element(By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')
        enlace_descarga.click()

        time.sleep(5)  # Ajusta según sea necesario
        logging.info(f'Intentando descargar la factura para CUFE {cufe}.')
    except Exception as e:
        logging.error(f'Error al intentar descargar la factura para CUFE {cufe}: {e}')

# Función para configurar la carpeta de descargas del navegador
def configurar_descargas(carpeta_descargas):
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": carpeta_descargas,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f'Error al configurar el navegador: {e}')
        return None

UPLOAD_FOLDER =  os.path.abspath("")

# Ejemplo de uso
archivo_excel = os.path.join(UPLOAD_FOLDER,"archivos_usuarios", "archivo final.xlsx")
carpeta_descargas = os.path.join(UPLOAD_FOLDER,"archivos_usuarios")

# Leer los CUFEs desde el archivo Excel
cufes = leer_cufes_desde_excel(archivo_excel)

# Configurar el navegador y la carpeta de descargas
driver = configurar_descargas(carpeta_descargas)

if driver:
    # Buscar y descargar facturas para cada CUFE
    for cufe in cufes:
        buscar_y_descargar_factura(driver, cufe, carpeta_descargas)
        # renombrar_archivos_pdf(carpeta_descargas)  # Comentado para mantener el nombre original

    # Cerrar el navegador
    driver.quit()
