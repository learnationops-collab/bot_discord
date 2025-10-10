import os
from notion_client import Client
from datetime import datetime, timezone
import config

# Inicializa el cliente de Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def add_activity_log(id_member: str, nombre: str, entrada: bool, canal: str, tiempo_coneccion: int = None):
    #print(f"[DEBUG] add_activity_log llamada con: id_member={id_member}, nombre={nombre}, entrada={entrada}, canal={canal}, tiempo_coneccion={tiempo_coneccion}")
    
    # Usar `now(timezone.utc)` para asegurar que la fecha y hora estén en UTC.
    now_utc = datetime.now(timezone.utc).isoformat()

    properties = {
        "id_member": {"title": [{"text": {"content": id_member}}]},
        "nombre": {"rich_text": [{"text": {"content": nombre}}]},
        "fecha_hora": {"date": {"start": now_utc}},
        "entrada": {"checkbox": entrada},
        "canal": {"rich_text": [{"text": {"content": canal}}]},
    }
    if tiempo_coneccion is not None:
        properties["tiempo_coneccion"] = {"number": tiempo_coneccion}

    #print(f"[DEBUG] Propiedades para Notion: {properties}")
    try:
        response = notion.pages.create(
            parent={"database_id": config.NOTION_DATABASE_ACTIVIDAD_ID},
            properties=properties,
        )
        #print(f"[DEBUG] Respuesta de Notion API (add_activity_log): {response}")
    except Exception as e:
        print(f"Error al agregar el registro de actividad en Notion: {e}")

def find_last_connection(id_member: str, canal: str):
    #print(f"[DEBUG] find_last_connection llamada con: id_member={id_member}, canal={canal}")
    filter_params = {
        "and": [
            {"property": "id_member", "title": {"equals": id_member}},
            {"property": "canal", "rich_text": {"equals": canal}},
            {"property": "entrada", "checkbox": {"equals": True}},
        ]
    }
    sort_params = [{"property": "fecha_hora", "direction": "descending"}]
    #print(f"[DEBUG] Parámetros de consulta para Notion: filter={filter_params}, sorts={sort_params}")
    try:
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter=filter_params,
            sorts=sort_params,
            page_size=1,
        )
        #print(f"[DEBUG] Respuesta de Notion API (find_last_connection): {response}")
        results = response.get("results")
        if results:
            return results[0]
        return None
    except Exception as e:
        print(f"Error al buscar el último registro de conexión en Notion: {e}")
        return None

def get_exit_logs_for_today():
    """
    Recupera todos los registros de SALIDA de actividad del día actual desde Notion.
    """
    try:
        today_utc = datetime.now(timezone.utc).date().isoformat()
        
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter={
                "and": [
                    {
                        "property": "fecha_hora",
                        "date": {
                            "on_or_after": today_utc
                        }
                    },
                    {
                        "property": "entrada",
                        "checkbox": {
                            "equals": False
                        }
                    }
                ]
            }
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error al obtener los registros de salida de Notion: {e}")
        return []

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