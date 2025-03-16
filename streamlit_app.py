import streamlit as st
import pandas as pd
import json

# Cargar los datos del JSON
with open("products.json", "r") as f:
    products_data = json.load(f)

# Convertir los datos a un DataFrame de pandas
df = pd.DataFrame(products_data)

# Título de la app
st.title("Visualización de Productos")

# Mostrar el número total de productos
st.write(f"Total de productos: {len(df)}")

# Filtros interactivos para mostrar productos
category_filter = st.selectbox("Seleccionar Categoría", df['categoryL1'].unique())
price_filter = st.slider("Filtrar por precio", 0, 100, (0, 100))

# Filtrar según la categoría y el precio
filtered_df = df[
    (df['categoryL1'] == category_filter) &
    (df['price'].apply(lambda x: float(x.split(" ")[0].replace(",", "."))) >= price_filter[0]) &
    (df['price'].apply(lambda x: float(x.split(" ")[0].replace(",", "."))) <= price_filter[1])
]

# Mostrar la tabla de productos filtrados
st.dataframe(filtered_df)

