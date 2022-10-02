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


def get_into_mercadona_web(driver,codigo_postal):
    # Inicializamos el navegador
    driver.get('https://tienda.mercadona.es/categories/112')

    #INSERTAR CODIGO POSTAL
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'input.ym-hide-content'.replace(' ', '.'))))\
        .send_keys(str(codigo_postal))

    #CLICK CONTINUAR
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'button.button button-primary button-big'.replace(' ', '.'))))\
        .click()

    #ACCEPT COOKIES
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'button.ui-button ui-button--small ui-button--primary ui-button--positive'.replace(' ', '.'))))\
        .click()


def get_mercadona_info(codigo_postal):

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--disable-extensions')

    driver_path = r'C:\Users\alexc\Downloads\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(driver_path, chrome_options=options)

    get_into_mercadona_web(driver,codigo_postal)

    categories_structure_list = []
    #RECORREMOS LAS CATEGORIAS
    num_categories = len(driver.find_elements(By.XPATH,"/html/body/div[1]/div[2]/div[1]/ul/li"))+1
    print(num_categories)
    for i in range(1,num_categories):

        #OBTENEMOS NOMBRE DE LA CATEGORIA
        category = WebDriverWait(driver, 5)\
            .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/button/span/label')))\
            .text
        
        #CLICK EN CATEGORIA
        WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH,
                                            f'/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/button/span/label')))\
            .click()

        #RECORREMOS LAS SUBCATEGORIAS
        for j in range(1,len(driver.find_elements(By.XPATH,f"/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/ul/li"))+1):

            #OBTENEMOS NOMBRE DE LA CATEGORIA
            subcategory = WebDriverWait(driver, 5)\
            .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/ul/li[{j}]')))\
            .text

            #CLICK EN SUBCATEGORIA
            WebDriverWait(driver, 5)\
                .until(EC.element_to_be_clickable((By.XPATH,
                                                f'/html/body/div[1]/div[2]/div[1]/ul/li[{i}]/div/ul/li[{j}]')))\
                .click()
            #RECORREMOS LAS SUBSUBCATEGORIAS
            for k in range(1,len(driver.find_elements(By.XPATH,f"/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section"))+1):
            
                #OBTENEMOS EL NOMBRE DE LA SUBSUBCATEGORIA
                subsubcategory = WebDriverWait(driver, 5)\
                    .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section[{k}]/h2')))\
                    .text

                #RECORREMOS LOS PRODUCTOS
                for l in range(1,len(driver.find_elements(By.XPATH,f'/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section[{k}]/div/div'))+1):
                    print(i,j,k,l)
                    #OBTENEMOS EL NOMBRE DEL PRODUCTO
                    producto = WebDriverWait(driver,5)\
                        .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section[{k}]/div/div[{l}]/button/div[2]/h4')))\
                        .text        
                    
                    cantidad = WebDriverWait(driver,5)\
                        .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section[{k}]/div/div[{l}]/button/div[2]/div[1]')))\
                        .text                         

                    precio = WebDriverWait(driver,5)\
                        .until(EC.presence_of_element_located((By.XPATH,
                                                    f'/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section[{k}]/div/div[{l}]/button/div[2]/div[2]/p[1]')))\
                        .text                         
                    precio = float(precio.replace(",",".").replace(" €",""))
                    if type(precio)!=float:
                        print("Ups")
                    categories_structure_list.append([category,subcategory,subsubcategory,producto,cantidad,precio])

    data = pd.DataFrame()
    data["Category"] = np.array(categories_structure_list)[:,0]
    data["Subcategory"] = np.array(categories_structure_list)[:,1]
    data["Subsubcategory"] = np.array(categories_structure_list)[:,2]
    data["Producto"] = np.array(categories_structure_list)[:,3]
    data["Cantidad"] = np.array(categories_structure_list)[:,4]
    data["Precio"] = list(map(float,list(np.array(categories_structure_list)[:,5])))

    data.to_csv(f"mercadona_prices_{codigo_postal}_{str(date.today())}.csv")