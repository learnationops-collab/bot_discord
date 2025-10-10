
import os
from notion_client import Client
from datetime import datetime
import config

# Inicializa el cliente de Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def add_activity_log(id_member: str, entrada: bool, canal: str):
    """
    Agrega un nuevo registro de actividad a la base de datos de Notion.

    Args:
        id_member (str): El ID del miembro.
        entrada (bool): True si el miembro se conecta, False si se desconecta.
        canal (str): El nombre del canal.
    """
    try:
        notion.pages.create(
            parent={"database_id": config.NOTION_DATABASE_ACTIVIDAD_ID},
            properties={
                "id_member": {"title": [{"text": {"content": id_member}}]},
                "fecha_hora": {"date": {"start": datetime.now().isoformat()}},
                "entrada": {"checkbox": entrada},
                "canal": {"rich_text": [{"text": {"content": canal}}]},
            },
        )
    except Exception as e:
        print(f"Error al agregar el registro de actividad en Notion: {e}")

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

