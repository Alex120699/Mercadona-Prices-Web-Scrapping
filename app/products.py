import streamlit as st
import pandas as pd
from scripts.db_utils import get_db_connection  # Importar la conexión a la base de datos

def show():
    st.title("📦 Lista de Productos")

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

    # Mostrar tabla interactiva con las nuevas columnas
    st.dataframe(df[[
        'nombre',                   # Nombre del producto
        'precio_con_descuento',     # Precio con descuento
        'categoria_L1',             # Categoría nivel 1
        'categoria_L2',             # Categoría nivel 2
        'categoria_L3',             # Categoría nivel 3
        'url',                      # URL del producto
        'imagen',                   # URL de la imagen
        'iva',                      # IVA aplicado
        'packaging',                # Tipo de empaque
        'bulk_price',               # Precio al por mayor
        'unit_size',                # Tamaño de la unidad
        'size_format',              # Formato del tamaño
        'selling_method',           # Método de venta
        'is_pack',                  # ¿Es un pack?
        'is_new',                   # ¿Es nuevo?
        'price_decreased',          # ¿El precio ha disminuido?
        'unavailable_from'          # Fecha de no disponibilidad
    ]])

    # Cerrar la conexión a la base de datos
    conn.close()