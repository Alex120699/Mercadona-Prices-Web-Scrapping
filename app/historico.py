# app/cambios_precios.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from scripts.db_utils import get_db_connection

def calcular_porcentaje_cambio(precio_inicial, precio_final):
    """Calcula el porcentaje de cambio entre dos precios."""
    if precio_inicial == 0:
        return 0
    return ((precio_final - precio_inicial) / precio_inicial) * 100

def formatear_cambio(precio_inicial, precio_final):
    """Formatea el cambio de precio con emoji y porcentaje."""
    cambio = precio_final - precio_inicial
    porcentaje = calcular_porcentaje_cambio(precio_inicial, precio_final)
    
    if cambio > 0:
        emoji = "📈"
        texto = f"Subida de {cambio:.2f}€ ({porcentaje:.1f}%)"
        color = "green"
    elif cambio < 0:
        emoji = "📉"
        texto = f"Bajada de {abs(cambio):.2f}€ ({abs(porcentaje):.1f}%)"
        color = "red"
    else:
        emoji = "➡️"
        texto = "Sin cambios"
        color = "gray"
    
    return f"{emoji} {texto}", color

def show():
    st.title("📊 Cambios de Precios")

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la lista de productos con nombre, tamaño y URL de imagen
    cursor.execute("SELECT id, nombre, unit_size, size_format, imagen as url_imagen FROM productos")
    productos = cursor.fetchall()

    # Convertir a DataFrame
    df_productos = pd.DataFrame(productos, columns=["id", "nombre", "unit_size", "size_format", "url_imagen"])

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
    df_historico["Fecha de actualización"] = pd.to_datetime(df_historico["Fecha de actualización"])

    # Filtrar por período de tiempo
    st.sidebar.header("Filtros")
    
    # Obtener el rango de fechas disponible
    fecha_min = df_historico["Fecha de actualización"].min()
    fecha_max = df_historico["Fecha de actualización"].max()
    
    # Obtener fechas únicas ordenadas
    fechas_unicas = sorted(df_historico["Fecha de actualización"].dt.date.unique())
    
    # Opción para seleccionar tipo de filtro
    tipo_filtro = st.sidebar.radio(
        "Tipo de filtro:",
        ["Período predefinido", "Intervalo personalizado"]
    )

    if tipo_filtro == "Período predefinido":
        periodo = st.sidebar.selectbox(
            "Selecciona el período de tiempo:",
            ["Último día", "Última semana", "Último mes"]
        )

        # Calcular la fecha de inicio según el período seleccionado
        if periodo == "Último día":
            # Usar las fechas de la base de datos
            if len(fechas_unicas) >= 2:
                fecha_fin = fechas_unicas[-1]
                fecha_inicio = fechas_unicas[-2]
            else:
                st.warning("No hay suficientes días de datos para mostrar cambios.")
                return
        elif periodo == "Última semana":
            fecha_fin = fechas_unicas[-1]
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif periodo == "Último mes":
            fecha_fin = fechas_unicas[-1]
            fecha_inicio = fecha_fin - timedelta(days=30)
    else:
        # Selector de fechas personalizado
        st.sidebar.write("Selecciona el intervalo de fechas:")
        fecha_inicio = st.sidebar.date_input(
            "Fecha inicial",
            min_value=fecha_min.date(),
            max_value=fecha_max.date(),
            value=fecha_min.date()
        )
        fecha_fin = st.sidebar.date_input(
            "Fecha final",
            min_value=fecha_min.date(),
            max_value=fecha_max.date(),
            value=fecha_max.date()
        )

    # Filtrar el histórico por el período seleccionado
    df_historico_filtrado = df_historico[
        (df_historico["Fecha de actualización"].dt.date >= fecha_inicio) & 
        (df_historico["Fecha de actualización"].dt.date <= fecha_fin)
    ]

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
        st.warning(f"⚠️ No se encontraron cambios de precios en el período seleccionado.")
    else:
        # Combinar con los nombres de los productos
        df_cambios = df_cambios.merge(df_productos, left_on="producto_id", right_on="id")

        # Ordenar por cambio (ascendente y descendente)
        df_top_subidas = df_cambios.sort_values(by="cambio", ascending=False).head(10)
        df_top_bajadas = df_cambios.sort_values(by="cambio", ascending=True).head(10)

        # Mostrar los cambios en formato de texto
        st.subheader("📈 Top 10 Subidas de Precios")
        for _, row in df_top_subidas.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                if pd.notna(row["url_imagen"]):
                    st.image(row["url_imagen"], width=150)
                else:
                    st.write("Sin imagen")
            with col2:
                cambio_texto, color = formatear_cambio(row["precio_inicial"], row["precio_final"])
                st.markdown(f"### {row['nombre_y_tamaño']}")
                st.markdown(f"<h2 style='color: {color};'>{cambio_texto}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color: gray;'>Precio inicial: {row['precio_inicial']:.2f}€ → Precio final: {row['precio_final']:.2f}€</h3>", unsafe_allow_html=True)
            st.divider()

        st.subheader("📉 Top 10 Bajadas de Precios")
        for _, row in df_top_bajadas.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                if pd.notna(row["url_imagen"]):
                    st.image(row["url_imagen"], width=150)
                else:
                    st.write("Sin imagen")
            with col2:
                cambio_texto, color = formatear_cambio(row["precio_inicial"], row["precio_final"])
                st.markdown(f"### {row['nombre_y_tamaño']}")
                st.markdown(f"<h2 style='color: {color};'>{cambio_texto}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color: gray;'>Precio inicial: {row['precio_inicial']:.2f}€ → Precio final: {row['precio_final']:.2f}€</h3>", unsafe_allow_html=True)
            st.divider()

    # Cerrar la conexión
    conn.close()