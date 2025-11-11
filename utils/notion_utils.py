import os
from notion_client import Client
from datetime import datetime, timezone, timedelta
import config

# Inicializa el cliente de Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def add_activity_log(id_member: str, nombre: str, entrada: bool, canal: str, tiempo_coneccion: int = None):
    
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

    try:
        response = notion.pages.create(
            parent={"database_id": config.NOTION_DATABASE_ACTIVIDAD_ID},
            properties=properties,
        )
    except Exception as e:
        print(f"Error al agregar el registro de actividad en Notion: {e}")

def find_last_connection(id_member: str, canal: str):
    filter_params = {
        "and": [
            {"property": "id_member", "title": {"equals": id_member}},
            {"property": "canal", "rich_text": {"equals": canal}},
            {"property": "entrada", "checkbox": {"equals": True}},
        ]
    }
    sort_params = [{"property": "fecha_hora", "direction": "descending"}]
    try:
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter=filter_params,
            sorts=sort_params,
            page_size=1,
        )
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

        filter_query = {
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

        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter=filter_query
        )

        return response.get("results", [])
    except Exception as e:
        print(f"Error al obtener los registros de salida de Notion: {e}")
        return []

def get_exit_logs_for_date(target_date):
    """
    Recupera todos los registros de SALIDA de actividad para una fecha específica desde Notion.
    """
    try:
        # Convertir la fecha a un objeto datetime en UTC al inicio del día
        start_of_day_utc = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        # El final del día es el inicio del día siguiente
        end_of_day_utc = start_of_day_utc + timedelta(days=1)

        # Formatear las fechas a ISO 8601 para la API de Notion
        start_date_iso = start_of_day_utc.isoformat()
        end_date_iso = end_of_day_utc.isoformat()

        filter_query = {
            "and": [
                {
                    "property": "fecha_hora",
                    "date": {
                        "on_or_after": start_date_iso,
                        "before": end_date_iso
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

        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter=filter_query
        )

        return response.get("results", [])
    except Exception as e:
        print(f"Error al obtener los registros de salida de Notion para la fecha {target_date}: {e}")
        return []

def get_activity_logs_for_today():
    """
    Recupera todos los registros de actividad del día actual desde la base de datos de Notion.

    Returns:
        list: Una lista de páginas de registros de actividad.
    """
    try:
        today_utc = datetime.now(timezone.utc).date().isoformat()
        response = notion.databases.query(
            database_id=config.NOTION_DATABASE_ACTIVIDAD_ID,
            filter={
                "property": "fecha_hora",
                "date": {
                    "on_or_after": today_utc
                }
            }
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error al obtener los registros de actividad de Notion: {e}")
        return []