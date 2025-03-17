import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Asegúrate de importar la conexión a la base de datos y obtener el DataFrame con los datos
from scripts.db_utils import get_db_connection

def iva_dashboard():
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

    # Gráfico 1: Distribución del IVA por Categoría (Pie Chart)
    st.header("1. Distribución del IVA por Categoría")
    iva_category_counts = df.groupby('categoria_L1')['iva'].value_counts().unstack(fill_value=0)
    
    # Calcular la suma total por IVA para cada categoría
    iva_category_totals = iva_category_counts.sum(axis=1)
    
    # Crear la figura para el gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_category_totals.plot(kind='pie', autopct='%1.1f%%', legend=True, ax=ax)
    st.pyplot(fig)

    # Gráfico 2: Promedio de Precio por Producto según IVA (Bar Chart)
    st.header("2. Promedio de Precio por Producto según IVA")
    iva_avg_price = df.groupby('iva')['precio_con_descuento'].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_avg_price.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title("Promedio de Precio por IVA")
    ax.set_ylabel("Precio Promedio (€)")
    st.pyplot(fig)

    # Gráfico 3: Comparación de Productos con y sin IVA (Stacked Bar Chart)
    st.header("3. Comparación de Productos con y sin IVA")
    df['precio_con_iva'] = df['precio_con_descuento'] * (1 + df['iva'] / 100)
    iva_comparison = df.groupby('nombre')[['precio_con_descuento', 'precio_con_iva']].mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    iva_comparison.plot(kind='bar', stacked=True, color=['lightgreen', 'lightcoral'], ax=ax)
    ax.set_title("Comparación de Precios con y sin IVA")
    ax.set_ylabel("Precio (€)")
    st.pyplot(fig)

    # Gráfico 4: Número de Productos por Tipo de IVA (Bar Chart)
    st.header("4. Número de Productos por Tipo de IVA")
    iva_counts = df['iva'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    iva_counts.plot(kind='bar', color='lightblue', ax=ax)
    ax.set_title("Número de Productos por Tipo de IVA")
    ax.set_ylabel("Número de Productos")
    st.pyplot(fig)

# Llamar a la función para mostrar los gráficos
iva_dashboard()
