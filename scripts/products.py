import streamlit as st
import json
import pandas as pd

@st.cache_data
def load_data():
    with open("products.json", "r") as f:
        return json.load(f)

def show():
    st.title("📦 Lista de Productos")

    # Cargar datos
    df = pd.DataFrame(load_data())

    # Mostrar tabla interactiva
    st.dataframe(df[['description', 'price', 'categoryL1', 'categoryL2', 'ProductURL']])
