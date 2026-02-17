import json
import os

SD_MOUNT_POINT = "/sd"


def save_json(data, filename):
    """
    Guarda un diccionario JSON en un archivo en /sd
    Si el archivo no existe, lo crea.
    """
    try:
        filepath = f"{SD_MOUNT_POINT}/{filename}"
        with open(filepath, "a") as f:
            json.dump(data, f)
            f.write("\n")
        print("✅ Guardado en:", filepath)
    except Exception as e:
        print("❌ Error al guardar en SD:", e)


def copy_json(data, filename):
    """
    Crea una copia secundaria del JSON (como respaldo).
    """
    try:
        filepath = f"{SD_MOUNT_POINT}/{filename}"
        with open(filepath, "a") as f:
            json.dump(data, f)
            f.write("\n")
        print("🗂️ Copia creada en:", filepath)
    except Exception as e:
        print("⚠️ Error en copia de respaldo:", e)


def append_json(data, filename):
    """
    Función equivalente para recibir datos desde nodos hijos (nodo padre).
    """
    save_json(data, filename)


def list_files():
    """
    Lista archivos en la SD.
    """
    try:
        return os.listdir(SD_MOUNT_POINT)
    except Exception as e:
        print("⚠️ No se pudo listar archivos:", e)
        return []


def file_exists(filename):
    """
    Verifica si un archivo existe.
    """
    try:
        return filename in os.listdir(SD_MOUNT_POINT)
    except Exception:
        return False
