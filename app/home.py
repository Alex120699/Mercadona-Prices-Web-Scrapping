# app/home.py
import streamlit as st
import subprocess
import sys

def get_last_refresh_date():
    """Lee la fecha de la última actualización desde el archivo."""
    try:
        with open("last_refresh.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Nunca"

def show():
    st.title("🏠 Página de Inicio")

    # Mostrar la fecha de la última actualización
    last_refresh = get_last_refresh_date()
    st.write(f"Última actualización: **{last_refresh}**")

    # Botón de actualización
    if st.button("🔄 Actualizar Datos"):
        with st.spinner("Actualizando datos..."):
            # Ejecutar main.py para actualizar los datos
            try:
                import sys
                subprocess.run([sys.executable, "main.py"], check=True)

                st.success("¡Datos actualizados correctamente!")
                # Actualizar la fecha de la última actualización
                last_refresh = get_last_refresh_date()
                st.write(f"Última actualización: **{last_refresh}**")
            except subprocess.CalledProcessError as e:
                st.error(f"Error al actualizar los datos: {e}")