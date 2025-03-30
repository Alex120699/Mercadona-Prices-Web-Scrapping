import sqlite3
import ollama
from scripts.db_utils import get_db_connection
import streamlit as st
import re
import json
import ast

def contar_tokens(texto):
    """
    Estima el número de tokens en un texto basado en la regla de 1 token ≈ 4 caracteres.
    
    Parámetros:
        texto (str): El texto a analizar.
    
    Retorna:
        int: Número estimado de tokens.
    """
    return len(texto) // 4  # División entera para evitar decimales


def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM productos")
    products = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return products


def limpiar_respuesta_category_llm(respuesta):
    """
    Limpia la respuesta del LLM para obtener solo el valor de la categoría.

    Parámetros:
        respuesta (str): La respuesta completa del LLM con texto adicional.

    Retorna:
        str: La categoría seleccionada (por ejemplo, "EQUIPMENT").
    """
     # Elimina todo el contenido dentro de <think>...</think>
    response_no_think = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()

    respuesta_limpia = json.loads(response_no_think)

    return respuesta_limpia

def obtener_categorias():
    """
    Extrae todas las categorías L1, L2 y L3 desde la base de datos.

    Retorna:
        dict: Diccionario estructurado {L1: {L2: [L3]}}.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Usamos LOWER() en SQL para asegurar que las categorías se comparen en minúsculas
    cursor.execute("SELECT DISTINCT LOWER(categoria_L1), LOWER(categoria_L2), LOWER(categoria_L3) FROM productos")
    
    categorias = {}
    for l1, l2, l3 in cursor.fetchall():
        if l1 not in categorias:
            categorias[l1] = {}
        if l2 not in categorias[l1]:
            categorias[l1][l2] = []
        if l3 not in categorias[l1][l2]:
            categorias[l1][l2].append(l3)

    conn.close()
    return categorias


import ollama

def clasificar_categoria_llm(query, categorias, model, nivel="L1"):
    """
    Usa el LLM para clasificar la búsqueda del usuario en un nivel de categoría.

    Parámetros:
        query (str): Texto de búsqueda del usuario.
        categorias (list): Lista de categorías disponibles en ese nivel.
        nivel (str): Nivel de categoría actual ("L1", "L2", "L3").

    Retorna:
        str: Categoría elegida.
    """
    # Normalizamos las categorías disponibles a minúsculas para comparación uniforme
    categorias_normalizadas = [categoria.lower() for categoria in categorias]

    # Normalizamos la query del usuario a minúsculas para que sea consistente
    query_normalizada = query.lower()

    # Creamos el texto de opciones de categorías para pasar al modelo
    opciones_texto = "\n".join(categorias_normalizadas)

    # Construimos el prompt para el LLM
    prompt = f"""El usuario busca: "{query_normalizada}".

    Estas son las categorías disponibles para {nivel}:
    {opciones_texto}

    
    IMPORTANTE:
    - Devuelve solo una categoría **exactamente como está escrita** en la lista.
    - No crees nuevas categorías ni hagas modificaciones.
    - Responde en formato JSON: {{"{nivel}": "nombre_de_categoria"}}.
    - No agregues explicaciones ni texto adicional.
    """

    # Ejecutamos la consulta al modelo
    respuesta = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    
    # Limpiamos la respuesta para obtener la categoría en el formato adecuado
    respuesta_limpia = limpiar_respuesta_category_llm(respuesta["message"]["content"])

    # Imprimimos y devolvemos la categoría elegida
    #print(respuesta_limpia)
    print(respuesta_limpia[nivel])
    return respuesta_limpia[nivel]



def obtener_productos_por_categoria(categoria_l1, categoria_l2, categoria_l3):
    """
    Obtiene productos de una categoría L3 específica.

    Retorna:
        dict: {id_producto: nombre_producto}
    """
    conn = get_db_connection()
    cursor = conn.cursor()


    # Suponiendo que la respuesta del LLM está en mayúsculas, convertimos a minúsculas
    categoria_l1_normalizada = categoria_l1.lower()
    categoria_l2_normalizada = categoria_l2.lower()
    categoria_l3_normalizada = categoria_l3.lower()

    cursor.execute("""
        SELECT id, nombre, packaging, unit_size, size_format FROM productos 
        WHERE LOWER(categoria_L1) = ? AND LOWER(categoria_L2) = ? AND LOWER(categoria_L3) = ?
    """, (categoria_l1_normalizada, categoria_l2_normalizada, categoria_l3_normalizada))

    #("cursor: ",cursor)
    #print("cursor.fetchall(): ",cursor.fetchall())
    list_of_rows = cursor.fetchall()

    productos = {}
    for row in list_of_rows:
        #print("row: ",row)  # Depurar qué datos contiene cada fila
        print(row["nombre"])
        productos[str(row['id'])] = {
            "nombre": row['nombre'],
            "packaging": row['packaging'],
            "unit_size": row['unit_size'],
            "size_format": row['size_format']
        }

# Verificar el diccionario
    print("Productos encontrados: ", len(productos))
    conn.close()
    #print(productos)
    return productos



def buscar_similares(query,model):
    categorias = obtener_categorias()

    # Paso 1: Determinar categoría L1
    categoria_l1 = clasificar_categoria_llm(query, list(categorias.keys()), model, nivel="L1")

    # Paso 2: Determinar categoría L2 dentro de L1
    categoria_l2 = clasificar_categoria_llm(query, list(categorias[categoria_l1].keys()), model, nivel="L2")

    # Paso 3: Determinar categoría L3 dentro de L2
    categoria_l3 = clasificar_categoria_llm(query, categorias[categoria_l1][categoria_l2], model, nivel="L3")

    print(f"Categoría final seleccionada: {categoria_l1} > {categoria_l2} > {categoria_l3}")

    productos_filtrados = obtener_productos_por_categoria(categoria_l1, categoria_l2, categoria_l3)

    #print("Productos seleccionados: ",productos_filtrados)

    return productos_filtrados


def limpiar_think(respuesta):
    """
    Extrae la parte de la respuesta que está fuera de <think>...</think> y devuelve el ID en formato JSON.
    """
    # Elimina todo el contenido dentro de <think>...</think>
    respuesta_limpia = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()

    return respuesta_limpia

def limpiar_respuesta_llm(respuesta):
    """
    Extrae la parte de la respuesta que está fuera de <think>...</think> y devuelve el ID en formato JSON.
    """
    # Elimina todo el contenido dentro de <think>...</think>
    respuesta_limpia = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()
    
    # Buscar un patrón JSON válido dentro de la respuesta
    match = re.search(r'{"id"\s*:\s*"(\d+)"}', respuesta_limpia)
    if match:
        return json.loads(match.group(0))  # Devuelve el JSON con el ID
    
    # Si no encuentra JSON, extrae solo el número
    cliente_id = re.sub(r'\D', '', respuesta_limpia)  
    return {"id": int(cliente_id)} if cliente_id.isdigit() else None


# Mostrar información adicional a LLM
def preparar_input_llm(productos):
    #print(productos)
    input_llm = ""
    for producto in productos:
        values = productos[producto]
        input_llm += f"ID: {producto}, Nombre: {values['nombre']}, packaging: {values['packaging']}, unit_size: {values['unit_size']}, size_format: {values['size_format']}%\n"
    return input_llm


def elegir_mejor_producto(query,productos,model):
    """
    Usa el LLM para seleccionar el producto correcto según la búsqueda del usuario.

    Parámetros:
        query (str): El término de búsqueda.
        productos (dict): Diccionario {id: nombre} de los productos.

    Retorna:
        str: ID del producto seleccionado.
    """
    input_llm = preparar_input_llm(productos)


    prompt = f"""
    Eres un buscador de productos en un supermercado español.
    Primero debes entender que producto estás buscando, puede que necesites traducirlo al inglés para saber mejor.
    El usuario busca: "{query}". Aquí están los productos disponibles:

    {{
        {input_llm}
    }}

    Devuelve solo el ID correcto en formato JSON. Ejemplo: {{"id": "30501"}}.
    No incluyas explicaciones ni texto adicional.
    Remember: YOU ARE LOOKING FOR {query}!
    """
    print(contar_tokens(prompt))
    #Ollama truncates input token lenght to 2048 by default.
    respuesta = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}], options={"num_ctx": 8000})
    print(respuesta.prompt_eval_count)
    print(respuesta["message"]["content"])
    respuesta_limpia = limpiar_respuesta_llm(respuesta["message"]["content"])
    print(respuesta_limpia,respuesta_limpia["id"])
    return respuesta_limpia["id"]


# Función para obtener la información del cliente corregido
def obtener_info_producto(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM productos WHERE id = ?", (product_id,))

    resultado = cursor.fetchone()

    conn.close()
    
    if resultado:
        return dict(resultado)  # Convierte la fila en un diccionario
    return None

def generar_resumen(producto,model):
    prompt = f"""Reescribe la siguiente información en un resumen corto y objetivo, sin adjetivos ni opiniones:
    
    - Nombre: {producto['nombre']}
    - Categoría: {producto['categoria_L1']} > {producto['categoria_L2']} > {producto['categoria_L3']}
    - Precio con descuento: {producto['precio_con_descuento']}€ {f"(antes {producto['precio_sin_descuento']}€)" if producto['precio_sin_descuento'] else ""}
    - Packaging: {producto['packaging']}
    - Tamaño: {producto['unit_size']} {producto['size_format']}
    - IVA: {producto['iva']}%
    - URL: {producto['url']}
    
    Genera una descripción breve pero natural para este producto, como si estuvieras recomendándoselo a alguien. Usa un tono cercano, pero profesional. 

    Ejemplo de salida:
    "Si buscas un eyeliner resistente al agua que dure todo el día, el **Perfilador de Ojos Eyeliner Waterproof Deliplus** es una gran opción. De color negro intenso, su formato en lápiz lo hace fácil de aplicar. Además, no incluye envase innecesario y tiene un precio accesible de 3,5€. Puedes verlo aquí: [URL]"

    No incluyas texto innecesario ni frases genéricas como "este producto es excelente". Solo describe lo más relevante con naturalidad.
"""
    
    respuesta = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

    respuesta_limpia = limpiar_think(respuesta["message"]["content"])
    return respuesta_limpia



def show():

# --- STREAMLIT UI ---
    st.title("🔍 Búsqueda Inteligente de producto con LLM")

        # Lista de modelos disponibles
    MODELS = [
        "llama3.2:3b",
        "gemma3:4b",
        "deepseek-r1:7b",
        "llama2-uncensored:7b",
        "mistral:7b",
        "qwen2.5:7b",
        "deepseek-r1:8b",
        "llama3.1:8b",
        "phi3:3.8b",
        "gemma2:9b",
        "gemma3:12b",
        "deepseek-r1:14b",
        "phi3:14b",
        "qwen2.5:14b",
        "qwen2.5:14b-instruct-q3_K_M",
        "gemma3:27b",
        "deepseek-r1:32b"
    ]


    # Selección del modelo
    selected_model = st.selectbox(
        "Selecciona un modelo:",
        MODELS,
        index=0  # Selecciona el primer modelo por defecto
    )


    query = st.text_input("Escribe el nombre del producto:")

    if st.button("Buscar"):
        if query:
            #products = get_products()
            opciones = buscar_similares(query,selected_model)
            #st.write("📌 **Opciones encontradas:**")

            product_id = elegir_mejor_producto(query,opciones,selected_model)
            st.write(f"✅ **Producto elegido por el LLM:** {product_id}")

            resultados = obtener_info_producto(product_id)

            if resultados:
                st.write("📊 **Información del Producto:**")
                resumen = generar_resumen(resultados,selected_model)
                st.write(resumen)
            else:
                st.write("⚠️ No se encontraron datos para este producto.")

        else:
            st.write("⚠️ Por favor, ingresa un nombre de producto.")