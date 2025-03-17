import streamlit as st
import pandas as pd
from scripts.db_utils import get_db_connection

def show():
    st.title("🔍 Detalles del Producto")

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener los productos
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    # Obtener los nombres de las columnas
    columns = [description[0] for description in cursor.description]

    # Convertir a DataFrame
    df = pd.DataFrame(productos, columns=columns)
    print(df.head())
    # Selección de producto
    selected_product = st.selectbox("Selecciona un producto:", df['nombre'].unique())

    # Mostrar detalles del producto seleccionado
    product_info = df[df['nombre'] == selected_product].iloc[0]
    
    st.write(f"**Nombre:** {product_info['nombre']}")
    st.write(f"**Precio con descuento:** {product_info['precio_con_descuento']}")
    st.write(f"**Precio sin descuento:** {product_info['precio_sin_descuento']}")
    st.write(f"**Categoría:** {product_info['categoria_L1']} > {product_info['categoria_L2']} > {product_info['categoria_L3']}")
    st.write(f"[Ver en tienda]({product_info['url']})")

    # Cerrar la conexión
    conn.close()