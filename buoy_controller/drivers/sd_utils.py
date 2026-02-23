import json
import os

SD_MOUNT_POINT = "/sd"


def _safe_write(filepath, data):
    """
    Función interna: asegura escritura física en SD.
    """
    try:
        with open(filepath, "a") as f:
            json.dump(data, f)
            f.write("\n")
            f.flush()  # vaciar buffer Python
        os.sync()  # vaciar buffer del sistema de archivos
        return True
    except Exception as e:
        print("❌ Error al escribir en SD:", e)
        return False


def save_json(data, filename):
    """
    Guarda un diccionario JSON en un archivo en /sd.
    Si el archivo no existe, lo crea.
    """
    filepath = f"{SD_MOUNT_POINT}/{filename}"
    if _safe_write(filepath, data):
        print("✅ Guardado en:", filepath)


def copy_json(data, filename):
    """
    Crea una copia secundaria del JSON (como respaldo).
    """
    filepath = f"{SD_MOUNT_POINT}/{filename}"
    if _safe_write(filepath, data):
        print("🗂️ Copia creada en:", filepath)


def append_json(data, filename):
    """
    Equivalente para recibir datos desde nodos hijos (nodo padre).
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
