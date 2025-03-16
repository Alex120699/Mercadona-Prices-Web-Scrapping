import streamlit as st
import pandas as pd
import json

# Cargar los datos del JSON
@st.cache
def load_data():
    with open("products.json", "r") as f:
        return json.load(f)

# Función para mostrar los productos
def show_product_table(df):
    # Filtro por categoría
    category_filter = st.selectbox("Selecciona Categoría", df['categoryL1'].unique())
    
    filtered_df = df[df['categoryL1'] == category_filter]
    
    st.write(f"Mostrando {len(filtered_df)} productos de la categoría {category_filter}")
    
    # Mostrar los productos filtrados
    st.dataframe(filtered_df)

# Función para mostrar detalles del producto
def show_product_details(df):
    # Filtro por producto
    product_filter = st.selectbox("Selecciona Producto", df['description'].unique())
    product_data = df[df['description'] == product_filter].iloc[0]
    
    # Mostrar detalles
    st.write(f"### {product_data['description']}")
    st.write(f"**Precio:** {product_data['price']}")
    st.write(f"**Atributos técnicos:** {product_data['technical_attributes']}")
    st.write(f"**Categoría L1:** {product_data['categoryL1']}")
    st.write(f"**Categoría L2:** {product_data['categoryL2']}")
    st.write(f"[Ver Producto en Mercadona]({product_data['ProductURL']})")

# Función principal para la aplicación
def main():
    # Cargar datos
    df = pd.DataFrame(load_data())
    
    # Título de la app
    st.title("Visualización de Productos de Mercadona")

    # Mostrar el número total de productos
    st.write(f"Total de productos disponibles: {len(df)}")

    # Opciones de navegación
    option = st.sidebar.selectbox("Selecciona una opción", ["Ver productos", "Ver detalles de producto"])
    
    if option == "Ver productos":
        show_product_table(df)
    elif option == "Ver detalles de producto":
        show_product_details(df)

if __name__ == "__main__":
    main()
