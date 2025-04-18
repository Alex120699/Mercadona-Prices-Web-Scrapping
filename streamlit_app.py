import streamlit as st
import app.home as home
import app.products as products
import app.detalle_producto as details
import app.kpis as kpis
import app.iva as iva
import app.historico as historico
#import app.chat_v2 as chat

# Sidebar para la navegación
st.sidebar.title("Navegación")
option = st.sidebar.radio("Selecciona una opción:", ["Home", "Ver productos", "Detalles de producto", "Cambios de Precios", "KPIs", "IVA Dashboards","Chat"])


# Cargar el script según la opción seleccionada
if option == "Home":
    home.show()
elif option == "Ver productos":
    products.show()
elif option == "Detalles de producto":
    details.show()
elif option == "Cambios de Precios":
    historico.show()
elif option == "KPIs":
    kpis.show()
elif option == "IVA Dashboards":
    iva.show()
# elif option == "Chat":
#     chat.show()