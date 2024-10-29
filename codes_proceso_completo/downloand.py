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
import random
from selenium.webdriver.common.action_chains import ActionChains

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = os.path.abspath("")  # Cambia esto por el directorio deseado

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

# Función para rotar user agents y proxies
def obtener_opciones_navegador(carpeta_descargas):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": carpeta_descargas,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)

    # Rotar el user agent
    user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={user_agent}")

    return options

# Función para mover el mouse aleatoriamente antes de la descarga
def mover_mouse_aleatoriamente(driver):
    action = ActionChains(driver)
    width, height = driver.get_window_size().values()  # Obtener el tamaño de la ventana del navegador
    for _ in range(5):  # Realizar 5 movimientos aleatorios
        x_offset = random.randint(0, width)
        y_offset = random.randint(0, height)
        action.move_by_offset(x_offset, y_offset)
        action.perform()
        time.sleep(0.5)

# Función para verificar si el CAPTCHA está resuelto
def esperar_verificacion_captcha(driver):
    try:
        WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="captcha-message"]'), 'Verificado'))
        logging.info("CAPTCHA verificado.")
        return True
    except Exception as e:
        logging.error("CAPTCHA no verificado: " + str(e))
        return False

# Función para buscar y descargar una factura usando el CUFE
def buscar_y_descargar_factura(driver, cufe, carpeta_descargas):
    nombre_archivo = os.path.join(carpeta_descargas, f'{cufe}.pdf')
    if os.path.exists(nombre_archivo):
        logging.info(f'La factura para el CUFE {cufe} ya existe. No se descargará nuevamente.')
        return

    try:
        driver.get('https://catalogo-vpfe.dian.gov.co/User/SearchDocument')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'DocumentKey')))

        # Esperar que el CAPTCHA esté verificado
        if esperar_verificacion_captcha(driver):
            mover_mouse_aleatoriamente(driver)  # Mover el mouse para simular actividad humana

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
 #Función para configurar la carpeta de descargas del navegador
def configurar_descargas(carpeta_descargas):
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)

    options = obtener_opciones_navegador(carpeta_descargas)
    
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



            # Configurar una instancia del navegador por cada CUFE
            drivers = [configurar_descargas(carpeta_descargas) for _ in range(min(3, len(facturas_pendientes)))]  # Máximo de 3 navegadores
            
            # Ejecutar la búsqueda y descarga en paralelo
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(buscar_y_descargar_factura, drivers[i % len(drivers)], cufe, carpeta_descargas): cufe for i, cufe in enumerate(facturas_pendientes)}

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

            # Verificar si el número de facturas pendientes ha cambiado
            if len(facturas_pendientes) == facturas_pendientes_anterior:
                reinicios += 1
                if reinicios >= max_reinicios:
                    logging.warning('Se alcanzó el número máximo de reinicios consecutivos sin progreso.')
                    break
            else:
                reinicios = 0  # Reiniciar el contador de reinicios si hubo progreso
        except Exception as e:
            logging.error(f'Error en el procesamiento: {e}')

if __name__ == "__main__":
    archivo_excel = os.path.join(UPLOAD_FOLDER, 'archivo final.xlsx')
    carpeta_descargas = os.path.join(UPLOAD_FOLDER, 'descargas')

    configurar_descargas(carpeta_descargas)
    cufes = leer_cufes_desde_excel(archivo_excel)

    if cufes:
        procesar_cufes(cufes, carpeta_descargas)
    else:
        logging.info("No se encontraron CUFEs para procesar.") 