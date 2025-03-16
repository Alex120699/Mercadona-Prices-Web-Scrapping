import json
import streamlit as st

# Función para cargar los productos desde el archivo JSON
def load_products():
    with open('products.json', 'r') as f:
        products = json.load(f)
    return products


# Cargar productos
products = load_products()

# Contar y mostrar el número de productos
num_products = len(products)

# Mostrar en la app de Streamlit
st.write(f'Número de productos en el archivo JSON: {num_products}')
