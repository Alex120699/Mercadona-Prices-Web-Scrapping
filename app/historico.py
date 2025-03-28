# app/cambios_precios.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from scripts.db_utils import get_db_connection

def show():
    st.title("📊 Cambios de Precios")

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la lista de productos con nombre y tamaño
    cursor.execute("SELECT id, nombre, unit_size, size_format FROM productos")
    productos = cursor.fetchall()

    # Convertir a DataFrame
    df_productos = pd.DataFrame(productos, columns=["id", "nombre", "unit_size", "size_format"])

    # Combinar nombre y tamaño para mostrar en la tabla
    df_productos["nombre_y_tamaño"] = (
        df_productos["nombre"] + " (" + df_productos["unit_size"].astype(str) + " " + df_productos["size_format"] + ")"
    )

    # Obtener el histórico de precios de todos los productos
    cursor.execute("""
    SELECT producto_id, precio_con_descuento, fecha_actualizacion
    FROM precios_historicos
    ORDER BY producto_id, fecha_actualizacion
    """)
    historico = cursor.fetchall()

    # Convertir a DataFrame
    df_historico = pd.DataFrame(historico, columns=["producto_id", "Precio", "Fecha de actualización"])

    # Convertir la columna "Fecha de actualización" a datetime
    df_historico["Fecha de actualización"] = pd.to_datetime(df_historico["Fecha de actualización"])

    # Filtrar por período de tiempo
    st.sidebar.header("Filtros")
    periodo = st.sidebar.selectbox(
        "Selecciona el período de tiempo:",
        ["Último día", "Última semana", "Último mes"]
    )

    # Calcular la fecha de inicio según el período seleccionado
    hoy = datetime.now()
    if periodo == "Último día":
        fecha_inicio = hoy - timedelta(days=1)
    elif periodo == "Última semana":
        fecha_inicio = hoy - timedelta(weeks=1)
    elif periodo == "Último mes":
        fecha_inicio = hoy - timedelta(days=30)

    # Filtrar el histórico por el período seleccionado
    df_historico_filtrado = df_historico[df_historico["Fecha de actualización"] >= fecha_inicio]

    # Calcular los cambios de precios
    cambios_precios = []
    for producto_id in df_historico_filtrado["producto_id"].unique():
        df_producto = df_historico_filtrado[df_historico_filtrado["producto_id"] == producto_id]
        if len(df_producto) > 1:
            precio_inicial = df_producto.iloc[0]["Precio"]
            precio_final = df_producto.iloc[-1]["Precio"]
            cambio = precio_final - precio_inicial
            cambios_precios.append({
                "producto_id": producto_id,
                "cambio": cambio,
                "precio_inicial": precio_inicial,
                "precio_final": precio_final
            })

    # Convertir a DataFrame
    df_cambios = pd.DataFrame(cambios_precios)

    # Manejar el caso de datos vacíos
    if df_cambios.empty:
        if periodo == "Último día":
            st.warning("⚠️ No ha habido cambios de precios entre ayer y hoy.")
        else:
            st.warning(f"⚠️ No se encontraron cambios de precios en el período seleccionado: {periodo}.")
    else:
        # Combinar con los nombres de los productos
        df_cambios = df_cambios.merge(df_productos, left_on="producto_id", right_on="id")

        # Ordenar por cambio (ascendente y descendente)
        df_top_subidas = df_cambios.sort_values(by="cambio", ascending=False).head(10)
        df_top_bajadas = df_cambios.sort_values(by="cambio", ascending=True).head(10)

        # Mostrar top 10 subidas
        st.header("Top 10 Subidas de Precios")
        st.dataframe(df_top_subidas[["nombre_y_tamaño", "cambio", "precio_inicial", "precio_final"]])

        # Mostrar top 10 bajadas
        st.header("Top 10 Bajadas de Precios")
        st.dataframe(df_top_bajadas[["nombre_y_tamaño", "cambio", "precio_inicial", "precio_final"]])

    # Cerrar la conexión
    conn.close()