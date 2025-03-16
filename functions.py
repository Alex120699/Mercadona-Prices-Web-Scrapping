from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import numpy as np
from datetime import date
import os
import toml
from selenium.webdriver.chrome.service import Service
import requests
import uuid


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

def extract_product_data(driver):

    #Read description
    description_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.title2-b.private-product-detail__description'))
                )
     #Leer el texto de la descripción
    description_text = description_element.text

    #Read technical attributes
    product_format_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-format.product-format__size'))
    )
    span_elements = product_format_element.find_elements(By.CSS_SELECTOR, 'span.headline1-r')
    technical_attributes = ""
    for span in span_elements:
        technical_attributes = technical_attributes + " " + span.text


    #Read PRice
    price_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[4]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/p[1]'))
    )
    price_text = price_element.text

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


    attributes = {"description":description_text, "technical_attributes":technical_attributes,"price":price_text,"img_path":img_path}

    return attributes

def get_mercadona_info():

    # Cargar configuración desde TOML
    print("Cargando config.toml...")

    config = toml.load("config.toml")

    # Cargar codigo postal como input para la web
    print("Cargando valores...")
    codigo_postal = config["settings"]["codigo_postal"]
    driver_path = config["settings"]["driver_path"]


    # Configurar opciones de Chrome
    print(f"Usando ChromeDriver en: {driver_path}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")  # Para evitar problemas en versiones recientes
    # chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument('--disable-extensions')

    # Crear una instancia del WebDriver
    print("Iniciando WebDriver...")

    service = Service(driver_path)  # Usar Service para definir el path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.google.com")  # Prueba con una página más simple


    print("WebDriver iniciado correctamente.")


    get_into_mercadona_web(driver,codigo_postal)


    categories_structure_list = []
    #RECORREMOS LAS CATEGORIAS
    print("Checking number of categories...")
    categories = driver.find_elements(By.CSS_SELECTOR, 'label.subhead1-r')

    product_list = []

    for i,category in enumerate(categories):
        category_text = category.text
        print("Category in progress: ",category_text)
        i=i+1
        #CLICK EN CATEGORIA
        label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//*[@id="root"]/div[2]/div[1]/ul/li[{i}]/div/button/span/label'))
        )
        label.click()

        #Comprobamos subcategorias
        subcategories = driver.find_elements(By.CSS_SELECTOR, 'button.category-item__link')

        #RECORREMOS LAS SUBCATEGORIAS
        for j,subcategory in enumerate(subcategories):
            j=j+1
            subcategory_text = subcategory.text
            print("SubCategory in progress: ",subcategory_text)
            
            #CLICK EN SUBCATEGORIA
            WebDriverWait(driver, 5)\
                .until(EC.element_to_be_clickable((By.XPATH,
                                                f'/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/ul/li[{j}]')))\
                .click()
            

            print("Checking SubSubCategories...")
            subsubcategories = driver.find_elements(By.CSS_SELECTOR, 'h2.section__header.headline1-b')


            #Comprobamos productos
            products = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h4.subhead1-r.product-cell__description-name'))
            )
            
            #RECORREMOS LOS PRODUCTOS
            for product in products:
                
                print("Product in progress: ",product.text)

                #CLICAMOS EL PRODUCTO
                product.click()
    
                attributes = extract_product_data(driver)
                
                attributes["categoryL1"] = category_text
                attributes["categoryL2"] = subcategory_text
                attributes["ProductURL"] = driver.current_url
                
                #CERRAMOS EL PRODUCTO
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="modal-close-button"]'))
                )
                close_button.click()            

                product_list.append(attributes)
                break
            break
        break

    save_data(product_list)

def save_data(list):
    import json
    json_file_path = 'products.json'

    # Guardar la lista de productos en el archivo JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(list, json_file, ensure_ascii=False, indent=4)

    # data = pd.DataFrame()
    # data["Category"] = np.array(categories_structure_list)[:,0]
    # data["Subcategory"] = np.array(categories_structure_list)[:,1]
    # data["Subsubcategory"] = np.array(categories_structure_list)[:,2]
    # data["Producto"] = np.array(categories_structure_list)[:,3]
    # data["Cantidad"] = np.array(categories_structure_list)[:,4]
    # data["Precio"] = list(map(float,list(np.array(categories_structure_list)[:,5])))

    # current_dir = os.getcwd()
    # print(current_dir)
    # file_path = os.path.join(current_dir,"data",f'mercadona_prices_{codigo_postal}_{str(date.today())}.csv')

    # data.to_csv(file_path)