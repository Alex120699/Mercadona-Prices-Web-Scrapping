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
    
    st.subheader(f"Producto: {product_info['nombre']}")
    st.write(f"**Categoría L1:** {product_info['categoria_L1']}")
    st.write(f"**Categoría L2:** {product_info['categoria_L2']}")
    st.write(f"**Categoría L3:** {product_info['categoria_L3']}")
    st.write(f"**Precio actual:** {product_info['precio_con_descuento']}€")
    st.write(f"**Packaging:** {product_info['packaging']}")
    st.write(f"**Precio por unidad (Bulk Price):** {product_info['bulk_price']}€")
    st.write(f"**Tamaño de unidad:** {product_info['unit_size']} {product_info['size_format']}")
    st.write(f"**IVA:** {product_info['iva']}%")
    st.write(f"**Método de venta:** {'Pack' if product_info['selling_method'] == 1 else 'Unitario'}")
    st.write(f"**¿Es pack?:** {'Sí' if product_info['is_pack'] == 1 else 'No'}")
    st.write(f"**¿Es nuevo?:** {'Sí' if product_info['is_new'] == 1 else 'No'}")
    st.write(f"**¿Ha disminuido de precio?:** {'Sí' if product_info['price_decreased'] == 1 else 'No'}")
    st.write(f"**Disponible a partir de:** {product_info['unavailable_from'] if product_info['unavailable_from'] else 'Disponible'}")
    st.write(f"**URL del producto:** [Ver producto]({product_info['url']})")

    # Cerrar la conexión
    conn.close()