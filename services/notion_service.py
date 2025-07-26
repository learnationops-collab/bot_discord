# Archivo: services/notion_service.py
# Este servicio encapsula la lógica de interacción directa con la API de Notion.

from notion_client import Client
from notion_client.helpers import collect_paginated_api
import asyncio
import os
import datetime

class NotionService:
    """
    Clase para gestionar la conexión y las operaciones de bajo nivel con la API de Notion.
    Abstrae las llamadas directas al cliente de Notion.
    """
    def __init__(self, notion_token: str):
        """
        Inicializa el NotionService con el token de integración de Notion.
        """
        self.notion_token = notion_token
        self.notion_client = None # El cliente de Notion se inicializará en connect

    def connect(self): # <--- CAMBIO AQUÍ: Ya NO es un método asíncrono
        """
        Inicializa el cliente de Notion utilizando el token de integración.
        Retorna True si la inicialización fue exitosa, False en caso contrario.
        """
        if self.notion_client is None:
            try:
                self.notion_client = Client(auth=self.notion_token)
                print("Cliente de Notion inicializado exitosamente en NotionService.")
                return True
            except Exception as e:
                print(f"Error al inicializar el cliente de Notion en NotionService: {e}")
                self.notion_client = None
                return False
        return True # Ya está conectado

    def close(self):
        """
        No se necesita una acción explícita de cierre para el cliente de Notion,
        ya que gestiona las conexiones internamente. Desreferenciamos el cliente.
        """
        self.notion_client = None
        print("Cliente de Notion en NotionService 'cerrado' (desreferenciado).")

    async def insert_page(self, database_id: str, properties: dict) -> bool:
        """
        Inserta una nueva página (fila) en una base de datos de Notion.

        Args:
            database_id (str): El ID de la base de datos donde se insertará la página.
            properties (dict): Un diccionario con las propiedades de la página,
                               siguiendo el formato de la API de Notion.

        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario.
        """
        if not self.notion_client:
            print("Error: Cliente de Notion no inicializado. No se puede insertar la página.")
            return False
        try:
            await self.notion_client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            print(f"Página insertada exitosamente en la base de datos {database_id}.")
            return True
        except Exception as e:
            print(f"Error al insertar la página en Notion (DB: {database_id}): {e}")
            return False

    async def query_database(self, database_id: str, filter: dict = None, sorts: list = None) -> list:
        """
        Consulta una base de datos de Notion y recupera todas las páginas que coinciden con el filtro.
        Maneja la paginación automáticamente.

        Args:
            database_id (str): El ID de la base de datos a consultar.
            filter (dict, optional): Un diccionario con las condiciones de filtro. Por defecto None.
            sorts (list, optional): Una lista de diccionarios para ordenar los resultados. Por defecto None.

        Returns:
            list: Una lista de objetos de página de Notion (diccionarios).
                  Retorna una lista vacía si no se encuentran resultados o si hay un error.
        """
        if not self.notion_client:
            print("Error: Cliente de Notion no inicializado. No se puede consultar la base de datos.")
            return []
        try:
            # Prepara los argumentos de la consulta
            query_args = {
                "database_id": database_id,
                "sorts": sorts if sorts else []
            }
            
            # Solo añade el filtro si no es None y no está vacío
            if filter and len(filter) > 0:
                query_args["filter"] = filter

            pages = await asyncio.to_thread(
                collect_paginated_api,
                self.notion_client.databases.query,
                **query_args # Usa ** para desempaquetar el diccionario como argumentos de palabra clave
            )
            print(f"Consulta exitosa en la base de datos {database_id}. Páginas encontradas: {len(pages)}")
            return list(pages) # collect_paginated_api devuelve un generador, lo convertimos a lista
        except Exception as e:
            print(f"Error al consultar la base de datos de Notion (DB: {database_id}): {e}")
            return []

# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Para ejecutar este ejemplo, necesitas un NOTION_TOKEN válido en tu .env
    # y un NOTION_DATABASE_ID para probar.
    # NOTION_TOKEN="secret_YOUR_NOTION_INTEGRATION_TOKEN"
    # NOTION_DATABASE_RESOURCES_ID="YOUR_NOTION_DATABASE_ID_FOR_TESTING"

    async def test_notion_service():
        from dotenv import load_dotenv
        load_dotenv()
        test_token = os.getenv('NOTION_TOKEN')
        test_db_id = os.getenv('NOTION_DATABASE_RESOURCES_ID') # Usamos el ID de recursos para la prueba

        if not test_token or not test_db_id:
            print("Por favor, configura NOTION_TOKEN y NOTION_DATABASE_RESOURCES_ID en tu archivo .env para ejecutar las pruebas.")
            return

        service = NotionService(test_token)

        # CAMBIO AQUÍ: Ya NO se usa await en service.connect()
        if service.connect():
            print("\n--- Probando inserción de página ---")
            # Asegúrate de que las propiedades coincidan con tu base de datos de Notion
            # Ejemplo para la base de datos de recursos
            insert_success = await service.insert_page(
                database_id=test_db_id,
                properties={
                    "resource_name": {"title": [{"text": {"content": "Recurso de Prueba" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")}}]},
                    "link": {"url": "https://ejemplo.com/test"},
                    "category": {"select": {"name": "TestCategory"}},
                    "difficulty": {"select": {"name": "basico"}}
                }
            )
            if insert_success:
                print("Página de prueba insertada.")
            else:
                print("Fallo al insertar página de prueba.")

            print("\n--- Probando consulta de base de datos con filtro ---")
            pages_with_filter = await service.query_database(database_id=test_db_id, filter={"property": "category", "select": {"equals": "testcategory"}})
            for page in pages_with_filter:
                print(f"Página encontrada (con filtro): {page.get('properties', {}).get('resource_name', {}).get('title', [{}])[0].get('plain_text')}")

            print("\n--- Probando consulta de base de datos sin filtro ---")
            pages_without_filter = await service.query_database(database_id=test_db_id, filter={})
            for page in pages_without_filter:
                print(f"Página encontrada (sin filtro): {page.get('properties', {}).get('resource_name', {}).get('title', [{}])[0].get('plain_text')}")

        else:
            print("No se pudo conectar a NotionService para las pruebas.")

        service.close()

    import asyncio
    asyncio.run(test_notion_service())
