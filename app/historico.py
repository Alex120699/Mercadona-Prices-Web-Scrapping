# app/historico.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scripts.db_utils import get_db_connection

def show():
    st.title("📈 Histórico de Precios")

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la lista de productos
    cursor.execute("SELECT id, nombre FROM productos")
    productos = cursor.fetchall()

    # Convertir a DataFrame
    df_productos = pd.DataFrame(productos, columns=["id", "nombre"])

    # Selección de producto
    selected_product = st.selectbox(
        "Selecciona un producto:",
        df_productos["nombre"]
    )

    # Obtener el ID del producto seleccionado
    producto_id = df_productos[df_productos["nombre"] == selected_product]["id"].iloc[0]

    # Obtener el histórico de precios del producto seleccionado
    cursor.execute("""
    SELECT precio_con_descuento, fecha_actualizacion
    FROM precios_historicos
    WHERE producto_id = ?
    ORDER BY fecha_actualizacion
    """, (producto_id,))
    historico = cursor.fetchall()

    if historico:
        # Convertir a DataFrame
        df_historico = pd.DataFrame(historico, columns=["Precio", "Fecha de actualización"])

        # Mostrar gráfico de dispersión
        st.header("Gráfico de Precios")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Gráfico de dispersión
        ax.scatter(df_historico["Fecha de actualización"], df_historico["Precio"], color='blue', label='Precio')
        
        # Añadir etiquetas y título
        ax.set_title(f"Histórico de Precios: {selected_product}")
        ax.set_xlabel("Fecha de actualización")
        ax.set_ylabel("Precio (€)")
        ax.legend()
        
        # Rotar las etiquetas del eje X para mejor legibilidad
        plt.xticks(rotation=45)
        
        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

        # Mostrar tabla con los datos históricos
        st.header("Datos Históricos")
        st.dataframe(df_historico)
    else:
        st.warning("No hay datos históricos para este producto.")

    # Cerrar la conexión
    conn.close()