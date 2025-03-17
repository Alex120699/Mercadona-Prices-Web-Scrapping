import streamlit as st
import json
import pandas as pd

@st.cache_data
def load_data():
    with open("products.json", "r") as f:
        return json.load(f)

def show():
    st.title("🔍 Detalles del Producto")

    # Cargar datos
    df = pd.DataFrame(load_data())

    # Selección de producto
    selected_product = st.selectbox("Selecciona un producto:", df['description'].unique())

    # Mostrar detalles del producto seleccionado
    product_info = df[df['description'] == selected_product].iloc[0]
    
    st.write(f"**Descripción:** {product_info['description']}")
    st.write(f"**Precio:** {product_info['price']}")
    st.write(f"**Categoría:** {product_info['categoryL1']} > {product_info['categoryL2']}")
    st.write(f"[Ver en tienda]({product_info['ProductURL']})")
