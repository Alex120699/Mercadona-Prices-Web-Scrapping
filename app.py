# app.py

import streamlit as st

st.title('Mi Primera App en Streamlit')

st.write('¡Hola, mundo! Esta es mi primera app en Streamlit desplegada en la nube.')

if st.button('Haz clic aquí'):
    st.write('¡Has hecho clic en el botón!')
