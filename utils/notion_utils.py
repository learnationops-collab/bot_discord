
import os
from notion_client import Client
from datetime import datetime
import config

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def add_activity_log(id_member: str, entrada: bool, canal: str):
    """
    Adds a new activity log to the Notion database.

    Args:
        id_member (str): The ID of the member.
        entrada (bool): True if the member is connecting, False if disconnecting.
        canal (str): The name of the channel.
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
        print(f"Error adding activity log to Notion: {e}")

def get_activity_logs_for_today():
    """
    Retrieves all activity logs for the current day from the Notion database.

    Returns:
        list: A list of activity log pages.
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
        print(f"Error getting activity logs from Notion: {e}")
        return []
