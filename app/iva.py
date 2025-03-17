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
    iva_category_counts = df.groupby('categoria_L1')['iva'].value_counts().unstack().fillna(0)
    iva_category_counts.plot(kind='pie', figsize=(10, 6), autopct='%1.1f%%', legend=True)
    st.pyplot()

    # Gráfico 2: Promedio de Precio por Producto según IVA (Bar Chart)
    st.header("2. Promedio de Precio por Producto según IVA")
    iva_avg_price = df.groupby('iva')['precio_con_descuento'].mean()
    iva_avg_price.plot(kind='bar', figsize=(10, 6), color='skyblue')
    plt.title("Promedio de Precio por IVA")
    plt.ylabel("Precio Promedio (€)")
    st.pyplot()

    # Gráfico 3: Comparación de Productos con y sin IVA (Stacked Bar Chart)
    st.header("3. Comparación de Productos con y sin IVA")
    df['precio_con_iva'] = df['precio_con_descuento'] * (1 + df['iva'] / 100)
    iva_comparison = df.groupby('nombre')[['precio_con_descuento', 'precio_con_iva']].mean()
    iva_comparison.plot(kind='bar', stacked=True, figsize=(12, 6), color=['lightgreen', 'lightcoral'])
    plt.title("Comparación de Precios con y sin IVA")
    plt.ylabel("Precio (€)")
    st.pyplot()

    # Gráfico 4: Número de Productos por Tipo de IVA (Bar Chart)
    st.header("4. Número de Productos por Tipo de IVA")
    iva_counts = df['iva'].value_counts()
    iva_counts.plot(kind='bar', figsize=(10, 6), color='lightblue')
    plt.title("Número de Productos por Tipo de IVA")
    plt.ylabel("Número de Productos")
    st.pyplot()

# Llamar a la función para mostrar los gráficos
iva_dashboard()
