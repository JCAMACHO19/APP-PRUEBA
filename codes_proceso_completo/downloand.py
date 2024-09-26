import os
import logging
import openpyxl
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = os.path.abspath("")

# Función para leer los CUFEs desde un archivo Excel
def leer_cufes_desde_excel(archivo_excel):
    try:
        libro = openpyxl.load_workbook(archivo_excel)
        hoja = libro.active
        cufes = []
        
        # Buscar los índices de las columnas basados en los títulos
        columnas = {cell.value: idx for idx, cell in enumerate(hoja[1], start=1)}
        
        if 'CUFE/CUDE' not in columnas or 'Estado de Factura' not in columnas:
            logging.error(f"Las columnas 'CUFE/CUDE' o 'Estado de Factura' no se encontraron en el archivo Excel.")
            return []
        
        indice_cufe = columnas['CUFE/CUDE']
        indice_estado = columnas['Estado de Factura']
        
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            cufe = fila[indice_cufe - 1]
            estado = fila[indice_estado - 1]
            if estado == 'Revisar':
                cufes.append(cufe)
        return cufes
    except Exception as e:
        logging.error(f'Error al leer el archivo Excel: {e}')
        return []

# Función para verificar si el archivo fue descargado correctamente y eliminar duplicados
def verificar_descarga(cufe, carpeta_descargas):
    nombre_archivo = os.path.join(carpeta_descargas, f'{cufe}.pdf')
    if os.path.exists(nombre_archivo):
        if os.path.isfile(nombre_archivo):
            # Eliminar duplicados si existen
            archivos_duplicados = [f for f in os.listdir(carpeta_descargas) if f.startswith(cufe) and f.endswith('.pdf')]
            if len(archivos_duplicados) > 1:
                for archivo in archivos_duplicados[1:]:
                    os.remove(os.path.join(carpeta_descargas, archivo))
            logging.info(f'La factura para CUFE {cufe} ha sido descargada correctamente.')
        return True
    logging.warning(f'La factura para CUFE {cufe} no se encuentra en la carpeta de descargas.')
    return False

# Función para verificar qué facturas no están descargadas
def verificar_facturas_pendientes(cufes, carpeta_descargas):
    facturas_pendientes = [cufe for cufe in cufes if not os.path.exists(os.path.join(carpeta_descargas, f'{cufe}.pdf'))]
    logging.info(f'Se encontraron {len(facturas_pendientes)} facturas pendientes de descargar.')
    return facturas_pendientes

# Función para buscar y descargar una factura usando el CUFE con reintentos
def buscar_y_descargar_factura(driver, cufe, carpeta_descargas):
    nombre_archivo = os.path.join(carpeta_descargas, f'{cufe}.pdf')
    if os.path.exists(nombre_archivo):
        logging.info(f'La factura para el CUFE {cufe} ya existe. No se descargará nuevamente.')
        return

    try:
        driver.get('https://catalogo-vpfe.dian.gov.co/User/SearchDocument')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'DocumentKey')))

        campo_cufe = driver.find_element(By.ID, 'DocumentKey')
        campo_cufe.clear()
        campo_cufe.send_keys(cufe)
        time.sleep(1)
        campo_cufe.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')))
        enlace_descarga = driver.find_element(By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')
        enlace_descarga.click()

        time.sleep(5)
        logging.info(f'Intentando descargar la factura para CUFE {cufe}.')
        
        # Verificar si la descarga fue exitosa
        if verificar_descarga(cufe, carpeta_descargas):
            return True
    except Exception as e:
        logging.error(f'Error al intentar descargar la factura para CUFE {cufe}: {e}')
    
    return False

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

# Función principal que gestiona la descarga de facturas con reinicio en caso de error
def procesar_cufes(cufes, carpeta_descargas):
    facturas_pendientes = verificar_facturas_pendientes(cufes, carpeta_descargas)
    
    reinicios = 0  # Contador de reinicios consecutivos
    max_reinicios = 3  # Máximo de reinicios permitidos sin cambios

    while facturas_pendientes:
        try:
            facturas_pendientes_anterior = len(facturas_pendientes)  # Almacenar el número anterior de facturas pendientes

            # Configurar tres instancias del navegador
            drivers = [configurar_descargas(carpeta_descargas) for _ in range(3)]
            
            # Ejecutar la búsqueda y descarga en paralelo
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(buscar_y_descargar_factura, drivers[i % 3], cufe, carpeta_descargas): cufe for i, cufe in enumerate(facturas_pendientes)}

                cufes_fallidas = []

                for future in as_completed(futures):
                    cufe = futures[future]
                    try:
                        if not future.result():
                            cufes_fallidas.append(cufe)
                    except Exception as e:
                        logging.error(f'Error en la tarea para CUFE {cufe}: {e}')
                        cufes_fallidas.append(cufe)

            # Si hubo CUFEs fallidas, reiniciar el proceso
            facturas_pendientes = cufes_fallidas

            # Cerrar todos los navegadores
            for driver in drivers:
                if driver:
                    driver.quit()

            # Verificar si el número de facturas pendientes sigue siendo el mismo
            if len(facturas_pendientes) == facturas_pendientes_anterior:
                reinicios += 1
                logging.info(f'No hubo cambios en el número de facturas pendientes. Reinicios consecutivos: {reinicios}')
            else:
                reinicios = 0  # Reiniciar el contador si hay cambios

            # Si se alcanza el máximo de reinicios sin cambios, finalizar la ejecución
            if reinicios >= max_reinicios:
                logging.error('El número de facturas pendientes no cambió después de 3 reinicios consecutivos. Finalizando ejecución.')
                break

            if facturas_pendientes:
                logging.info(f'Reiniciando el proceso para {len(facturas_pendientes)} CUFEs fallidas.')
            else:
                logging.info('Proceso de descarga completado exitosamente.')
        except Exception as e:
            logging.error(f'Error general en el proceso: {e}')
            facturas_pendientes = facturas_pendientes  # Reiniciar el proceso si algo falla en el ciclo

# Obtener la lista de subcarpetas dentro de "archivos_usuarios"
subcarpetas = [os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d) for d in os.listdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios")) if os.path.isdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d))]

# Asegurarse de que hay subcarpetas disponibles
if not subcarpetas:
    raise ValueError("No se encontraron subcarpetas dentro de la carpeta 'archivos_usuarios'.")

# Iterar sobre cada subcarpeta para procesar los archivos dentro de ella
for subcarpeta in subcarpetas:
    # Ruta del archivo de entrada en la subcarpeta
    archivo_excel = os.path.join(subcarpeta, "archivo final.xlsx")
    carpeta_descargas = subcarpeta  # Usar la misma subcarpeta para las descargas de facturas
    
    # Leer los CUFEs desde el archivo Excel
    cufes = leer_cufes_desde_excel(archivo_excel)
    
    if cufes:
        # Procesar los CUFEs
        procesar_cufes(cufes, carpeta_descargas)
    else:
        logging.info(f"No se encontraron CUFEs para procesar en {archivo_excel}.")
