import streamlit as st
import home as home
import app.products as products
import app.details as details
import app.kpis as kpis

# Sidebar para la navegación
st.sidebar.title("Navegación")
option = st.sidebar.radio("Selecciona una opción:", ["Home", "Ver productos", "Detalles de producto", "KPIs"])

# Cargar el script según la opción seleccionada
if option == "Home":
    home.show()
elif option == "Ver productos":
    products.show()
elif option == "Detalles de producto":
    details.show()
elif option == "KPIs":
    kpis.show()
