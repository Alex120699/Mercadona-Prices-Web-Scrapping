import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    with open("products.json", "r") as f:
        return json.load(f)

def show():
    st.title("📊 KPIs de Productos")

    df = pd.DataFrame(load_data())

    # Selección de categoría
    selected_category = st.selectbox("Selecciona una categoría:", df['categoryL1'].unique())

    # Filtrar datos por categoría seleccionada
    filtered_df = df[df['categoryL1'] == selected_category]

    # Número de productos por subcategoría
    st.subheader("Número de productos por subcategoría (L2)")
    category_counts = filtered_df['categoryL2'].value_counts()

    # Graficar
    plt.figure(figsize=(10, 6))
    sns.barplot(x=category_counts.index, y=category_counts.values, palette="muted")
    plt.xticks(rotation=90)
    plt.title(f"Productos en {selected_category}")
    plt.xlabel("Subcategoría L2")
    plt.ylabel("Cantidad de productos")
    st.pyplot(plt)

    # Distribución de precios
    st.subheader("Distribución de precios")

    filtered_df['price_numeric'] = filtered_df['price'].apply(lambda x: float(x.split(' ')[0].replace(',', '.')))

    plt.figure(figsize=(10, 6))
    sns.histplot(filtered_df['price_numeric'], bins=20, kde=True, color="blue")
    plt.title(f"Distribución de precios en {selected_category}")
    plt.xlabel("Precio (€)")
    plt.ylabel("Frecuencia")
    st.pyplot(plt)
