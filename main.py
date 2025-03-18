# main.py
import datetime
import subprocess
from scripts.db_utils import create_database, get_db_connection
from scripts.api_utils import actualizar_datos

def git_push():
    """Sube los cambios a GitHub."""
    try:
        # Añadir todos los cambios
        subprocess.run(["git", "add", "."], check=True)
        
        # Hacer commit
        subprocess.run(["git", "commit", "-m", "Actualización automática de la base de datos"], check=True)
        
        # Subir los cambios
        subprocess.run(["git", "push"], check=True)
        print("Cambios subidos a GitHub correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al subir los cambios a GitHub: {e}")



if __name__ == "__main__":
    # Crear las tablas si no existen
    create_database()

    # Ejecutar la lógica principal para actualizar los datos
    actualizar_datos()

    # Guardar la fecha y hora de la última actualización
    with open("last_refresh.txt", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Subir los cambios a GitHub
    git_push()