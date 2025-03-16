import streamlit as st
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Cargar los datos del JSON
@st.cache
def load_data():
    with open("products.json", "r") as f:
        return json.load(f)

# Función para visualizar los productos en una tabla interactiva
def show_product_table(df):
    category_filter = st.selectbox("Seleccionar Categoría", df['categoryL1'].unique())
    price_filter = st.slider("Filtrar por precio", 0, 100, (0, 100))

    filtered_df = df[
        (df['categoryL1'] == category_filter) &
        (df['price'].apply(lambda x: float(x.split(" ")[0].replace(",", "."))) >= price_filter[0]) &
        (df['price'].apply(lambda x: float(x.split(" ")[0].replace(",", "."))) <= price_filter[1])
    ]

    st.dataframe(filtered_df)

# Función para mostrar la tendencia de precios
def show_price_trend(df):
    product_filter = st.selectbox("Selecciona el producto", df['description'].unique())
    product_data = df[df['description'] == product_filter]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=product_data, x="price_date", y="price", ax=ax, marker='o')
    ax.set_title(f"Tendencia de Precios de {product_filter}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precio (€)")
    st.pyplot(fig)

# Función para mostrar el historial de precios
def show_price_history(df):
    product_filter = st.selectbox("Selecciona el producto", df['description'].unique())
    product_data = df[df['description'] == product_filter]
    
    product_data['price_date'] = pd.to_datetime(product_data['price_date'])
    product_data_sorted = product_data.sort_values(by='price_date')
    
    st.write(f"Historial de precios de {product_filter}")
    st.dataframe(product_data_sorted[['price_date', 'price']])

# Función principal para la aplicación
def main():
    # Cargar datos
    df = pd.DataFrame(load_data())
    
    # Título de la app
    st.title("Visualización de Productos")

    # Mostrar el número total de productos
    st.write(f"Total de productos: {len(df)}")

    # Opciones de navegación
    option = st.sidebar.selectbox("Selecciona una opción", ["Ver productos", "Ver tendencia de precios", "Historial de precios"])
    
    if option == "Ver productos":
        show_product_table(df)
    elif option == "Ver tendencia de precios":
        show_price_trend(df)
    elif option == "Historial de precios":
        show_price_history(df)

if __name__ == "__main__":
    main()
