import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scripts.db_utils import get_db_connection

def show():
    """Muestra los gráficos relacionados con el IVA aplicado a los productos."""

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todos los productos
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    # Obtener los nombres de las columnas
    columns = [description[0] for description in cursor.description]

    # Convertir los productos a un DataFrame
    df = pd.DataFrame(productos, columns=columns)

    # Página de Dashboard en Streamlit
    st.title("📊 Dashboard: IVA en Productos")

    # --- Filtros en la parte superior ---
    st.sidebar.header("Filtros")

    # Filtro por categoría L1
    categorias = df['categoria_L1'].unique()
    selected_categories = st.sidebar.multiselect(
        "Selecciona categorías:",
        options=categorias,
        default=categorias  # Selecciona todas las categorías por defecto
    )

    # Filtro por rango de precios
    min_price = df['precio_con_descuento'].min()
    max_price = df['precio_con_descuento'].max()
    price_range = st.sidebar.slider(
        "Selecciona un rango de precios:",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price))
    )

    # Aplicar filtros al DataFrame
    filtered_df = df[
        (df['categoria_L1'].isin(selected_categories)) &
        (df['precio_con_descuento'] >= price_range[0]) &
        (df['precio_con_descuento'] <= price_range[1])
    ]

    # --- Gráficos ---

    # Gráfico 1: Distribución del IVA por Categoría (Pie Chart)
    st.header("1. Distribución del IVA por Categoría")
    iva_category_counts = filtered_df.groupby('categoria_L1')['iva'].value_counts().unstack(fill_value=0)
    iva_category_totals = iva_category_counts.sum(axis=1)

    # Crear la figura para el gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_category_totals.plot(kind='pie', autopct='%1.1f%%', legend=False, ax=ax)
    ax.set_ylabel("")  # Eliminar el label del eje Y
    st.pyplot(fig)

    # Gráfico 2: Promedio de Precio por Producto según IVA (Bar Chart)
    st.header("2. Promedio de Precio por Producto según IVA")
    iva_avg_price = filtered_df.groupby('iva')['precio_con_descuento'].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_avg_price.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title("Promedio de Precio por IVA")
    ax.set_ylabel("Precio Promedio (€)")
    st.pyplot(fig)

    # Gráfico 3: Comparación de Productos con y sin IVA (Stacked Bar Chart)
    st.header("3. Comparación de Productos con y sin IVA")
    filtered_df['precio_con_iva'] = filtered_df['precio_con_descuento'] * (1 + filtered_df['iva'] / 100)
    iva_comparison = filtered_df.groupby('nombre')[['precio_con_descuento', 'precio_con_iva']].mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    iva_comparison.plot(kind='bar', stacked=True, color=['lightgreen', 'lightcoral'], ax=ax)
    ax.set_title("Comparación de Precios con y sin IVA")
    ax.set_ylabel("Precio (€)")
    st.pyplot(fig)

    # Gráfico 4: Número de Productos por Tipo de IVA (Bar Chart)
    st.header("4. Número de Productos por Tipo de IVA")
    iva_counts = filtered_df['iva'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_counts.plot(kind='bar', color='lightblue', ax=ax)
    ax.set_title("Número de Productos por Tipo de IVA")
    ax.set_ylabel("Número de Productos")
    st.pyplot(fig)

    # Cerrar la conexión a la base de datos
    conn.close()