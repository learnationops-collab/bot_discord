import os
from notion_client import Client
from datetime import datetime
import config

# Inicializa el cliente de Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def add_activity_log(id_member: str, nombre: str, entrada: bool, canal: str, tiempo_coneccion: int = None):
    """
    Agrega un nuevo registro de actividad a la base de datos de Notion.

    Args:
        id_member (str): El ID del miembro.
        nombre (str): El nombre del miembro.
        entrada (bool): True si el miembro se conecta, False si se desconecta.
        canal (str): El nombre del canal.
        tiempo_coneccion (int, optional): El tiempo de conexión en segundos. Defaults to None.
    """
    properties = {
        "id_member": {"title": [{"text": {"content": id_member}}]},
        "nombre": {"rich_text": [{"text": {"content": nombre}}]},
        "fecha_hora": {"date": {"start": datetime.now().isoformat()}},
        "entrada": {"checkbox": entrada},
        "canal": {"rich_text": [{"text": {"content": canal}}]},
    }
    if tiempo_coneccion is not None:
        properties["tiempo_coneccion"] = {"number": tiempo_coneccion}

    try:
        notion.pages.create(
            parent={"database_id": config.NOTION_DATABASE_ACTIVIDAD_ID},
            properties=properties,
        )
    except Exception as e:
        print(f"Error al agregar el registro de actividad en Notion: {e}")

def find_last_connection(id_member: str, canal: str):
    """
    Encuentra el último registro de conexión para un miembro en un canal específico.

    Args:
        id_member (str): El ID del miembro.
        canal (str): El nombre del canal.

    Returns:
        dict: El objeto de página de Notion para el último registro de conexión, o None si no se encuentra.
    """
    try:
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter={
                "and": [
                    {"property": "id_member", "title": {"equals": id_member}},
                    {"property": "canal", "rich_text": {"equals": canal}},
                    {"property": "entrada", "checkbox": {"equals": True}},
                ]
            },
            sorts=[{"property": "fecha_hora", "direction": "descending"}],
            page_size=1,
        )
        results = response.get("results")
        if results:
            return results[0]
        return None
    except Exception as e:
        print(f"Error al buscar el último registro de conexión en Notion: {e}")
        return None



def get_activity_logs_for_today():
    """
    Recupera todos los registros de actividad del día actual desde la base de datos de Notion.

    Returns:
        list: Una lista de páginas de registros de actividad.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter={
                "property": "fecha_hora",
                "date": {
                    "on_or_after": today
                }
            }
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error al obtener los registros de actividad de Notion: {e}")
        return []