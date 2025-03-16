from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import date
import os
import toml
from selenium.webdriver.chrome.service import Service
import requests
import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductExtractor:
    def __init__(self, driver):
        self.driver = driver

    def _get_element(self, by, value, timeout=10):
        """Helper function to find elements with a timeout"""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            print(f"Error finding element: {value}. Error: {e}")
            return None

    def extract_description(self):
        """Extracts product description"""
        description_element = self._get_element(By.CSS_SELECTOR, 'h1.title2-b.private-product-detail__description')
        return description_element.text if description_element else ""

    def extract_technical_attributes(self):
        """Extracts technical attributes like size, format, etc."""
        product_format_element = self._get_element(By.CSS_SELECTOR, 'div.product-format.product-format__size')
        technical_attributes = ""
        if product_format_element:
            span_elements = product_format_element.find_elements(By.CSS_SELECTOR, 'span.headline1-r')
            for span in span_elements:
                technical_attributes += " " + span.text
        return technical_attributes.strip()

    def extract_price(self):
        """Extracts product price"""
        price_element = self._get_element(By.XPATH, '//*[@id="root"]/div[4]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/p[1]')
        return price_element.text if price_element else ""

    def extract_product_data(self):
        """Main method to extract all product data"""
        description = self.extract_description()
        technical_attributes = self.extract_technical_attributes()
        price = self.extract_price()

        # Combine all attributes into a dictionary
        return {
            "description": description,
            "technical_attributes": technical_attributes,
            "price": price
        }

def get_into_mercadona_web(driver, codigo_postal):
    # Ir a la página de Mercadona
    print("Opening Mercadona website...")
    driver.get('https://tienda.mercadona.es/categories/112')

    # Esperar y escribir el código postal
    print("Filling Postal Code...")
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.ym-hide-content'))
    ).send_keys(str(codigo_postal))
    
    time.sleep(1)  # Pequeña pausa para evitar problemas de carga

    print("Clicking continue...")
    # Clic en el botón "Continuar"
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button-primary'))
    ).click()
    
    time.sleep(1)

    print("Accepting cookies...")
    # Aceptar cookies
    WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ui-button.ui-button--small.ui-button--tertiary.ui-button--positive'))
    ).click()


    print("Código postal ingresado y cookies aceptadas.")

def get_images(driver):
    #Read image
    img_element = driver.find_element(By.TAG_NAME, 'img')
    img_url = img_element.get_attribute('src')
    if not os.path.exists('imgs'):
        os.makedirs('imgs')
    img_data = requests.get(img_url).content
    img_filename = str(uuid.uuid4()) + '.jpg'
    img_path = os.path.join('imgs', img_filename)
    img_data = requests.get(img_url).content
    with open(img_path, 'wb') as file:
        file.write(img_data)

    return img_path


def load_config():
    """Carga la configuración desde el archivo TOML."""
    print("Cargando config.toml...")
    config = toml.load("config.toml")
    return config["settings"]["codigo_postal"], config["settings"]["driver_path"]

def init_webdriver(driver_path):
    """Inicia y configura el WebDriver."""
    print(f"Usando ChromeDriver en: {driver_path}")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_categories(driver):
    """Obtiene las categorías principales."""
    return driver.find_elements(By.CSS_SELECTOR, 'label.subhead1-r')

def navigate_to_subcategory(driver, i):
    """Navega a una subcategoría específica haciendo clic en la categoría correspondiente."""
    label = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[@id="root"]/div[2]/div[1]/ul/li[{i}]/div/button/span/label'))
    )
    label.click()

def get_subcategories(driver):
    """Obtiene las subcategorías dentro de una categoría."""
    return driver.find_elements(By.CSS_SELECTOR, 'button.category-item__link')

def get_products(driver):
    """Obtiene los productos dentro de una subcategoría."""
    return WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h4.subhead1-r.product-cell__description-name'))
    )

def process_product(driver, product, category_text, subcategory_text):
    """Extrae la información de un producto y la agrega a la lista."""
    print(f"Processing product: {product.text}")
    product.click()

    # Extraer información del producto
    extractor = ProductExtractor(driver)
    attributes = extractor.extract_product_data()
    attributes["categoryL1"] = category_text
    attributes["categoryL2"] = subcategory_text
    attributes["ProductURL"] = driver.current_url

    # Cerrar producto
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="modal-close-button"]'))
    )
    close_button.click()

    return attributes

def save_data(list):
    import json
    json_file_path = 'products.json'

    # Guardar la lista de productos en el archivo JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(list, json_file, ensure_ascii=False, indent=4)


def get_mercadona_info():
    """Función principal que gestiona todo el flujo de extracción de datos."""
    # Cargar configuración y configurar el WebDriver
    codigo_postal, driver_path = load_config()
    driver = init_webdriver(driver_path)
    

     # Iniciar la página de Mercadona
    print("Iniciando WebDriver en Mercadona...")
    get_into_mercadona_web(driver, codigo_postal)
    
    # Lista para almacenar los productos
    product_list = []

    # Recorrer las categorías
    print("Checking number of categories...")
    categories = get_categories(driver)

    for i, category in enumerate(categories):
        category_text = category.text
        print(f"Category in progress: {category_text}")

        # Navegar a la categoría
        navigate_to_subcategory(driver, i+1)

        # Obtener las subcategorías
        subcategories = get_subcategories(driver)

        for j, subcategory in enumerate(subcategories):
            subcategory_text = subcategory.text
            print(f"SubCategory in progress: {subcategory_text}")

            # Hacer clic en la subcategoría
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f'/html/body/div[1]/div[2]/div[1]/ul/li[{i+1}]/div/ul/li[{j+1}]'))
            ).click()

            # Obtener los productos
            products = get_products(driver)

            for product in products:
                # Procesar el producto
                product_data = process_product(driver, product, category_text, subcategory_text)
                product_list.append(product_data)

    # Guardar los datos extraídos
    save_data(product_list)