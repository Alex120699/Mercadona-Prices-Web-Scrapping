import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

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


# Función para mostrar KPIs básicos con filtros interactivos
def show_kpis(df):
    st.header("KPIs Básicos de Productos")

    # Filtro de categoría (L1)
    selected_category = st.selectbox("Selecciona una categoría L1", df['categoryL1'].unique())

    # Filtrar el DataFrame según la categoría seleccionada
    filtered_df = df[df['categoryL1'] == selected_category]

    # 1. Número de productos por categoría L1
    st.subheader(f"Número de productos en la categoría: {selected_category}")
    category_count = filtered_df['categoryL1'].value_counts()

    # Graficar
    plt.figure(figsize=(10, 6))
    sns.barplot(x=category_count.index, y=category_count.values, palette="viridis")
    plt.title("Número de productos por categoría")
    plt.xlabel("Categoría L1")
    plt.ylabel("Número de productos")
    st.pyplot(plt)

    # 2. Distribución de precios en diferentes rangos
    st.subheader("Distribución de productos por precio")
    # Limpiar precios y convertir a número
    filtered_df['price_numeric'] = filtered_df['price'].apply(lambda x: float(x.split(' ')[0].replace(',', '.')))

    # Crear bins para los precios
    price_bins = [0, 1, 2, 3, 5, 7, 10, 25, 50]
    price_labels = ['0-1', '1-2', '2-3', '3-5', '5-7', '7-10', '10-25', '25-50']

    # Categorizar los precios
    filtered_df['price_range'] = pd.cut(filtered_df['price_numeric'], bins=price_bins, labels=price_labels, right=False)

    # Contar los productos por rango de precios
    price_range_count = filtered_df['price_range'].value_counts().sort_index()

    # Graficar
    plt.figure(figsize=(10, 6))
    sns.barplot(x=price_range_count.index, y=price_range_count.values, palette="coolwarm")
    plt.title("Distribución de productos por rango de precios")
    plt.xlabel("Rango de precios")
    plt.ylabel("Número de productos")
    st.pyplot(plt)

    # 3. Número de productos por subcategoría L2
    st.subheader("Número de productos por subcategoría L2")
    subcategory_count = filtered_df['categoryL2'].value_counts()

    # Graficar
    plt.figure(figsize=(10, 6))
    sns.barplot(x=subcategory_count.index, y=subcategory_count.values, palette="muted")
    plt.title(f"Número de productos en subcategoría para {selected_category}")
    plt.xlabel("Subcategoría L2")
    plt.ylabel("Número de productos")
    plt.xticks(rotation=90)
    st.pyplot(plt)

# Función principal para la aplicación
def main():
    # Cargar datos
    df = pd.DataFrame(load_data())
    
    # Título de la app
    st.title("Visualización de Productos de Mercadona")

    # Mostrar el número total de productos
    st.write(f"Total de productos disponibles: {len(df)}")

    # Opciones de navegación
    option = st.sidebar.selectbox("Selecciona una opción", ["Ver productos", "Ver detalles de producto", "KPIs Básicos"])
    
    if option == "Ver productos":
        show_product_table(df)
    elif option == "Ver detalles de producto":
        show_product_details(df)
    elif option == "KPIs Básicos":
        show_kpis(df)

if __name__ == "__main__":
    main()
