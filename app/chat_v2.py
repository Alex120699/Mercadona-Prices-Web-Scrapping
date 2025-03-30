import sqlite3
import re
import json
import streamlit as st
import ollama
from scripts.db_utils import get_db_connection
from typing import Dict, List, Optional, Tuple
import unicodedata

# ---------------------------
# CONSTANTES
# ---------------------------
MODELS = [
        'llama3.2',
        'gemma3',
        'phi3',
        'deepseek-r1',
        'llama2-uncensored',
        'mistral',
        'qwen2.5',
        'deepseek-r1:8b',
        'llama3.1',
        'gemma2',
        'gemma3:12b',
        'deepseek-r1:14b',
        'phi3:14b',
        'qwen2.5:14b',
        'qwen2.5:14b-instruct-q3_K_M',
        'gemma3:27b',
        'deepseek-r1:32b'
]

# Niveles de categoría
CAT_LEVELS = ['L1', 'L2', 'L3']

# ---------------------------
# FUNCIONES DE NORMALIZACIÓN
# ---------------------------
def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparación eliminando tildes y convirtiendo a minúsculas"""
    if not texto:
        return ""
    # Normaliza a forma NFKD (descompone tildes y caracteres)
    texto = unicodedata.normalize('NFKD', texto.lower())
    # Elimina los caracteres de combinación (tildes)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    return texto


def normalizar_categorias(categorias: Dict) -> Dict:
    """Normaliza todas las categorías en la estructura"""
    return {
        normalizar_texto(l1): {
            normalizar_texto(l2): [normalizar_texto(l3) for l3 in l3s]
            for l2, l3s in l2s.items()
        }
        for l1, l2s in categorias.items()
    }




# ---------------------------
# FUNCIONES DE BASE DE DATOS
# ---------------------------
def get_products():
    """Obtiene todos los productos de la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM productos")
    products = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return products

def obtener_categorias():
    """Extrae todas las categorías L1, L2 y L3 desde la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT LOWER(categoria_L1), LOWER(categoria_L2), LOWER(categoria_L3) FROM productos")
    
    categorias = {}
    for l1, l2, l3 in cursor.fetchall():
        categorias.setdefault(l1, {}).setdefault(l2, []).append(l3)
    
    conn.close()
    return categorias

def obtener_productos_por_categoria(categoria_l1: str, categoria_l2: str, categoria_l3: str) -> Dict:
    """Obtiene productos de una categoría L3 específica con manejo de tildes"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Normalizamos las categorías para comparación
    cat_l1_norm = normalizar_texto(categoria_l1)
    cat_l2_norm = normalizar_texto(categoria_l2)
    cat_l3_norm = normalizar_texto(categoria_l3)

    # Consulta con condiciones normalizadas
    cursor.execute("""
        SELECT id, nombre, packaging, unit_size, size_format, precio_con_descuento, bulk_price
        FROM productos 
        WHERE 
            LOWER(REPLACE(REPLACE(REPLACE(categoria_L1, 'á', 'a'), 'é', 'e'), 'í', 'i')) = ? 
            AND LOWER(REPLACE(REPLACE(REPLACE(categoria_L2, 'á', 'a'), 'é', 'e'), 'í', 'i')) = ? 
            AND LOWER(REPLACE(REPLACE(REPLACE(categoria_L3, 'á', 'a'), 'é', 'e'), 'í', 'i')) = ?
    """, (cat_l1_norm, cat_l2_norm, cat_l3_norm))

    productos = {
        str(row['id']): {
            "nombre": row['nombre'],
            "packaging": row['packaging'],
            "unit_size": row['unit_size'],
            "size_format": row['size_format'],
            "price": row["precio_con_descuento"],
            "price_per_unit_of_measure": row["bulk_price"]
        } for row in cursor.fetchall()
    }
    
    conn.close()
    return productos

def obtener_info_producto(product_id):
    """Obtiene toda la información de un producto específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = ?", (product_id,))
    resultado = dict(cursor.fetchone()) if cursor.fetchone() else None
    conn.close()
    return resultado

def obtener_categorias_normalizadas() -> Dict:
    """Obtiene categorías ya normalizadas desde la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            categoria_L1, 
            categoria_L2, 
            categoria_L3 
        FROM productos
    """)
    
    categorias = {}
    for l1, l2, l3 in cursor.fetchall():
        l1_norm = normalizar_texto(l1)
        l2_norm = normalizar_texto(l2)
        l3_norm = normalizar_texto(l3)
        
        if l1_norm not in categorias:
            categorias[l1_norm] = {}
        if l2_norm not in categorias[l1_norm]:
            categorias[l1_norm][l2_norm] = []
        if l3_norm not in categorias[l1_norm][l2_norm]:
            categorias[l1_norm][l2_norm].append(l3_norm)
    
    conn.close()
    return categorias



# ---------------------------
# FUNCIONES DE PROCESAMIENTO LLM
# ---------------------------
def clasificar_categoria_llm(query, categorias, model, nivel="L1"):
    """Clasifica la búsqueda en categorías usando LLM"""
    prompt = f"""
    El usuario busca: "{query.lower()}".

    Categorías disponibles para {nivel}:
    {", ".join([c.lower() for c in categorias])}

    Devuelve solo una categoría en formato: {{"{nivel}": "nombre_de_categoria"}}.
    """
    print("PROMPT: \n\n",prompt)
    respuesta = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return limpiar_respuesta_json(respuesta["message"]["content"])[nivel]

def buscar_similares(query, model):
    """Ejecuta el pipeline completo de búsqueda de productos similares"""
    categorias = obtener_categorias()
    
    # Clasificación jerárquica
    l1 = clasificar_categoria_llm(query, list(categorias.keys()), model, "L1")
    l2 = clasificar_categoria_llm(query, list(categorias[l1].keys()), model, "L2")
    l3 = clasificar_categoria_llm(query, categorias[l1][l2], model, "L3")

    return obtener_productos_por_categoria(l1, l2, l3)

def analizar_productos(query: str, productos: Dict, model: str) -> str:
    """
    Genera un análisis comparativo completo de los productos sin elegir uno específico.
    
    Args:
        query: Búsqueda original del usuario
        productos: Diccionario completo de productos {id: {info}}
        model: Modelo de LLM a usar
        
    Returns:
        str: Análisis comparativo detallado en formato de texto
    """
    prompt = f"""
    Eres un experto en análisis comparativo de productos de supermercado. 
    El usuario buscó: "{query}"

    Estos son los productos disponibles:
    {json.dumps(productos, indent=2, ensure_ascii=False)}

    Genera un análisis que:
    1. Compare objetivamente las características clave (nombre, packaging, tamaño)
    2. Destaque las diferencias relevantes
    3. Mencione casos de uso ideales para cada opción
    4. No elijas un "mejor" producto
    5. Usa un tono profesional pero claro

    Formato esperado:
    '''
    [Introducción general sobre los productos encontrados]

    - [Nombre Producto 1]:
      * Características: [packaging], [tamaño]
      * Ideal para: [casos de uso]
      * Notas: [observaciones relevantes]

    - [Nombre Producto 2]:
      * Características: [packaging], [tamaño]
      * Ideal para: [casos de use]
      * Notas: [observaciones relevantes]

    [Conclusión comparativa general]
    '''
    """
    
    respuesta = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.5}
    )
    
    return respuesta["message"]["content"].strip()

def generar_resumen(query: str, productos: Dict, analisis: str, model: str) -> str:
    """
    Genera una respuesta final integrando el análisis con los datos completos.
    
    Args:
        query: Búsqueda original
        productos: Diccionario completo de productos
        analisis: Texto generado por analizar_productos()
        model: Modelo de LLM a usar
        
    Returns:
        str: Recomendación completa con formato
    """
    # Preparamos datos estructurados para el prompt
    datos_productos = "\n".join(
        f"- {info['nombre']} (ID: {id}): "
        f"{info['packaging']} de {info['unit_size']}{info['size_format']}, "
        f"Precio: {info['price']}€, "
        f"Precio/{info["size_format"]}: {info["price_per_unit_of_measure"]}€"
        for id, info in productos.items()
    )

    prompt = f"""
    Basándote en este análisis comparativo previo:
    {analisis}

    Y en los datos completos de los productos:
    {datos_productos}

    Genera una respuesta final para el usuario que:
    1. Comience con un resumen ejecutivo de las opciones
    2. Integre naturalmente el análisis comparativo
    3. Incluya información de precios (si está disponible)
    4. Mantenga un tono útil y objetivo
    5. Use este formato:

    **Resumen para "{query}"**  
    [Introducción general]  

    **Opciones disponibles:**  
    [Análisis integrado con datos reales]  

    **Conclusión:**  
    [Recomendaciones de uso generales sin favorecer un producto específico]  
    """
    
    respuesta = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return respuesta["message"]["content"].strip()


def generar_prompt_clasificacion(
    query: str, 
    opciones: List[str], 
    nivel: str
) -> str:
    """Genera un prompt optimizado para clasificación de categorías"""
    return f"""
    TAREA: Clasificar una búsqueda de producto en una categoría específica.

    INSTRUCCIONES:
    1. Analiza la búsqueda: "{query}"
    2. Selecciona la categoría {nivel} MÁS APROPIADA
    3. DEBES usar EXACTAMENTE uno de estos nombres (sin modificar):
    {", ".join(opciones)}

    REGLAS:
    - Respuesta SOLO en formato: {{"{nivel}": "nombre_exacto"}}
    - No inventes categorías
    - Si no está claro, elige la más genérica
    - Considera sinónimos y variaciones lingüísticas

    EJEMPLO: Si la categoría es "bebidas" y el usuario busca "refresco", 
    debes devolver "bebidas"
    """

def filtrar_productos_relevantes(query: str, productos: Dict, model: str) -> Dict:
    """
    Filtra los productos manteniendo solo los que realmente coinciden con la búsqueda.
    
    Args:
        query: Término de búsqueda original
        productos: Diccionario completo de productos {id: {info}}
        model: Modelo LLM a usar
        
    Returns:
        Dict: Subconjunto de productos relevantes
    """
    prompt = f"""
    Eres un filtro inteligente de productos. Analiza esta búsqueda y lista de productos:
    
    BÚSQUEDA ORIGINAL: "{query}"
    
    PRODUCTOS EN CATEGORÍA (formato JSON):
    {json.dumps(productos, indent=2, ensure_ascii=False)}
    
    TAREA:
    1. Identifica qué productos coinciden REALMENTE con la búsqueda
    2. Excluye productos que sean de otra categoría aunque estén en el mismo grupo L3
    3. Considera sinónimos y variaciones lingüísticas
    
    RESPONDE en formato JSON con este esquema:
    {{
        "productos_relevantes": {{
            "id_producto": {{
                "nombre": "str",
                "match_score": float (0-1),
                "razon": "str"
            }}
        }},
        "exclusiones": {{
            "id_producto": "razón_de_exclusión"
        }}
    }}
    """
    
    respuesta = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )
    
    try:
        resultado = json.loads(respuesta["message"]["content"])
        return {
            id: productos[id] 
            for id in resultado["productos_relevantes"]
            if id in productos
        }
    except:
        return productos  # Fallback si hay error

def generar_resumen_focalizado(query: str, productos_filtrados: Dict, model: str) -> str:
    """
    Genera un resumen exclusivo sobre los productos relevantes.
    
    Args:
        query: Búsqueda original
        productos_filtrados: Diccionario ya filtrado
        model: Modelo LLM a usar
        
    Returns:
        str: Resumen en formato Markdown
    """
    if not productos_filtrados:
        return "No encontré productos que coincidan exactamente con tu búsqueda."
    
    prompt = f"""
    Eres un asistente de supermercado. Genera un resumen SOBRE LOS PRODUCTOS QUE COINCIDEN EXACTAMENTE con esta búsqueda:
    
    BÚSQUEDA: "{query}"
    
    PRODUCTOS FILTRADOS (solo coincidencias exactas):
    {json.dumps(productos_filtrados, indent=2, ensure_ascii=False)}
    
    INSTRUCCIONES:
    1. Enfócate SOLO en estos productos
    2. Destaca diferencias en packaging, tamaño y precio, tanto bruto como por kilo
    3. Usa este formato:
    
    **Resultados exactos para "{query}"**  
    - [Nombre 1]: [Packaging] de [tamaño]. [Nota diferencial]  
    - [Nombre 2]: [Packaging] de [tamaño]. [Nota diferencial]  
    
    **Conclusión:** Breve comparativa entre las opciones disponibles.
    """
    print("START PROMPT","🔥" * 20)
    print(prompt)
    print("END PROMPT","🔥" * 20)
    respuesta = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    print("START RESPUESTA","🔥" * 20)
    print(respuesta["message"]["content"])
    print("END RESPUESTA","🔥" * 20)
    return respuesta["message"]["content"].strip()


def clasificar_categoria(
    query: str, 
    opciones: List[str], 
    model: str, 
    nivel: str,
    max_intentos: int = 3
) -> Optional[str]:
    """Clasifica una búsqueda en categorías con validación y reintentos"""
    query_norm = normalizar_texto(query)
    opciones_norm = {normalizar_texto(o): o for o in opciones}
    
    # Primero intentamos matching exacto o parcial
    for opcion_norm, opcion_real in opciones_norm.items():
        if opcion_norm in query_norm or query_norm in opcion_norm:
            return opcion_real
    
    # Si no hay match directo, usamos el LLM
    for intento in range(max_intentos):
        try:
            prompt = generar_prompt_clasificacion(
                query, 
                list(opciones_norm.values()), 
                nivel
            )
            print("START PROMPT","🔥" * 20)
            print(prompt)
            respuesta = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2}  # Menor creatividad
            )
            print("END PROMPT","🔥" * 20)
            print("START RESPONSE","🔥" * 20)
            print(respuesta["message"]["content"])
            resultado = json.loads(respuesta["message"]["content"])
            print("END RESPONSE","🔥" * 20)
            categoria = resultado[nivel]
            
            # Validamos que la categoría devuelta sea válida
            if categoria in opciones_norm.values():
                return categoria
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error en intento {intento + 1}: {str(e)}")
            continue
    
    return None

def buscar_similares_mejorado(query: str, model: str) -> Tuple[Dict, Dict]:
    """Pipeline mejorado de búsqueda que devuelve productos Y categorías"""
    categorias = obtener_categorias_normalizadas()
    
    # Clasificación jerárquica con validación
    l1 = clasificar_categoria(query, list(categorias.keys()), model, "L1")
    if not l1:
        return {}, {}
    
    l2 = clasificar_categoria(query, list(categorias[l1].keys()), model, "L2")
    if not l2:
        return {}, {}
    
    l3 = clasificar_categoria(query, categorias[l1][l2], model, "L3")
    if not l3:
        return {}, {}
    
    productos = obtener_productos_por_categoria(l1, l2, l3)
    categorias_seleccionadas = {
        'L1': l1,
        'L2': l2, 
        'L3': l3
    }
    print(productos,categorias_seleccionadas)
    return productos, categorias_seleccionadas


# ---------------------------
# FUNCIONES UTILITARIAS
# ---------------------------
def contar_tokens(texto):
    """Estima el número de tokens en un texto"""
    return len(texto) // 4

def limpiar_respuesta_json(respuesta):
    """Limpia y extrae JSON de respuestas LLM"""
    respuesta_limpia = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()
    return json.loads(respuesta_limpia)

def limpiar_respuesta_texto(respuesta):
    """Limpia texto de marcado innecesario en respuestas LLM"""
    return re.sub(r'<.*?>', '', respuesta).strip()

# ---------------------------
# INTERFAZ DE USUARIO
# ---------------------------
def show():
    st.title("🔍 Análisis Comparativo de Productos")
    
    model = st.selectbox("Modelo:", MODELS)
    query = st.text_input("¿Qué producto buscas?")
    
    if st.button("Analizar") and query:
        with st.spinner("Buscando productos..."):
            productos, categorias = buscar_similares_mejorado(query, model)
            
        # Mostrar categorías seleccionadas
        with st.expander("📊 Categorías seleccionadas"):
            st.write(f"L1: {categorias.get('L1', 'No identificada')}")
            st.write(f"L2: {categorias.get('L2', 'No identificada')}")
            st.write(f"L3: {categorias.get('L3', 'No identificada')}")

        if not productos:
            st.warning("No se encontraron productos. Prueba con términos más específicos.")
            return
        
        # 2. Filtrado inteligente
        with st.spinner("Filtrando productos relevantes..."):
            productos_filtrados = filtrar_productos_relevantes(query, productos, model)  

         # 3. Generar resumen focalizado
            with st.spinner("Preparando recomendación..."):
                resumen = generar_resumen_focalizado(query, productos_filtrados, model)
            
        # Mostrar resultados
        st.markdown(resumen)
        
        # Opcional: Mostrar productos descartados
        if len(productos_filtrados) != len(productos):
            with st.expander("⚠️ Productos descartados (misma categoría pero no coinciden)"):
                descartados = {k: v for k, v in productos.items() if k not in productos_filtrados}
                st.json(descartados)

if __name__ == "__main__":
    show()