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
    selected_category_l1 = st.selectbox("Selecciona una categoría L1:", ["Todas"] + list(df['categoryL1'].unique()))
    filtered_df = df if selected_category_l1 == "Todas" else df[df['categoryL1'] == selected_category_l1]
    
    if not filtered_df.empty:
        selected_category_l2 = st.selectbox("Selecciona una categoría L2:", ["Todas"] + list(filtered_df['categoryL2'].unique()))
        filtered_df = filtered_df if selected_category_l2 == "Todas" else filtered_df[filtered_df['categoryL2'] == selected_category_l2]
    
    # Número de productos por subcategoría
    st.subheader("Número de productos por subcategoría (L2)")
    category_counts = filtered_df['categoryL2'].value_counts()

    # Graficar
    plt.figure(figsize=(10, 6))
    sns.barplot(x=category_counts.index, y=category_counts.values, palette="muted")
    plt.xticks(rotation=90)
    plt.title(f"Productos en {selected_category_l1}")
    plt.xlabel("Subcategoría L2")
    plt.ylabel("Cantidad de productos")
    st.pyplot(plt)

    # Distribución de precios
    st.subheader("Distribución de precios")
    
    filtered_df['price_numeric'] = filtered_df['price'].apply(lambda x: float(x.split(' ')[0].replace(',', '.')))

    plt.figure(figsize=(10, 6))
    sns.histplot(filtered_df['price_numeric'], bins=20, kde=True, color="blue")
    plt.title(f"Distribución de precios en {selected_category_l1}")
    plt.xlabel("Precio (€)")
    plt.ylabel("Frecuencia")
    st.pyplot(plt)
    
    # Comparación de productos con y sin "Hacendado" en el título
    st.subheader("Comparación de productos con 'Hacendado'")
    
    filtered_df['is_hacendado'] = filtered_df['description'].str.contains("Hacendado", case=False, na=False)
    hacendado_counts = filtered_df['is_hacendado'].value_counts()

    plt.figure(figsize=(6, 4))
    plt.pie(hacendado_counts, labels=["Hacendado", "Otros"], autopct='%1.1f%%', colors=["green", "gray"], startangle=90)
    plt.title("Productos con y sin 'Hacendado'")
    st.pyplot(plt)