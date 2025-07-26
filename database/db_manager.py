import os
from dotenv import load_dotenv
import unicodedata

# Importamos el nuevo NotionService que crearemos en services/notion_service.py
# Asumimos que NotionService manejará la conexión y las llamadas directas a la API de Notion.
from services.notion_service import NotionService

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class DBManager:
    """
    Clase para gestionar las operaciones de datos con las bases de datos de Notion.
    Actúa como una capa de abstracción sobre NotionService para manejar las IDs
    específicas de las bases de datos de recursos y ventas.
    """
    def __init__(self):
        """
        Inicializa el DBManager cargando los IDs de las bases de datos de Notion
        desde las variables de entorno y el token de Notion para pasar a NotionService.
        """
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_resources_id = os.getenv('NOTION_DATABASE_RESOURCES_ID')
        self.notion_database_sales_id = os.getenv('NOTION_DATABASE_SALES_ID')
        self.notion_service = None # El cliente de NotionService se inicializará en connect

        # Validación básica de las variables de entorno de Notion
        if not self.notion_token:
            print("¡ADVERTENCIA! La variable de entorno 'NOTION_TOKEN' no está configurada.")
        if not self.notion_database_resources_id:
            print("¡ADVERTENCIA! 'NOTION_DATABASE_RESOURCES_ID' no está definido en tu archivo .env.")
        if not self.notion_database_sales_id:
            print("¡ADVERTENCIA! 'NOTION_DATABASE_SALES_ID' no está definido en tu archivo .env.")


    def _normalize_string(self, text: str) -> str:
        """
        Normaliza una cadena de texto: la convierte a minúsculas y elimina acentos.
        Esto es útil para búsquedas consistentes.
        """
        if text is None:
            return None
        # Normaliza a la forma de descomposición canónica, luego elimina los caracteres diacríticos
        normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return normalized_text.lower()

    def connect(self):
        """
        Inicializa el cliente de NotionService.
        Retorna el objeto de cliente de NotionService si es exitoso, None en caso de error.
        """
        if self.notion_service is None:
            try:
                # Pasamos el token al NotionService
                self.notion_service = NotionService(self.notion_token)
                # El NotionService se encargará de inicializar el cliente de Notion
                if self.notion_service.connect():
                    print("Cliente de NotionService inicializado exitosamente.")
                else:
                    self.notion_service = None # Si la conexión falla en NotionService, lo reseteamos
            except Exception as e:
                print(f"Error al inicializar el cliente de NotionService: {e}")
                self.notion_service = None # Asegurarse de que el cliente sea None si falla
        return self.notion_service

    def close(self):
        """
        No se necesita una acción explícita de cierre para el cliente de Notion,
        ya que gestiona las conexiones internamente. Desreferenciamos el servicio.
        """
        if self.notion_service:
            self.notion_service.close() # Llama al método close del servicio si existe
        self.notion_service = None
        print("Cliente de NotionService 'cerrado' (desreferenciado).")

    async def insert_resource(self, resource_name: str, link: str, category: str, difficulty: str, subcategory: str = None):
        """
        Inserta un nuevo recurso en la base de datos de recursos de Notion.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return False

        # Normalizar los datos antes de la inserción
        normalized_resource_name = self._normalize_string(resource_name)
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)

        return await self.notion_service.insert_page(
            database_id=self.notion_database_resources_id,
            properties={
                "resource_name": {"title": [{"text": {"content": normalized_resource_name}}]},
                "link": {"url": link},
                "category": {"select": {"name": normalized_category}},
                "difficulty": {"select": {"name": normalized_difficulty}},
                "subcategory": {"select": {"name": normalized_subcategory}} if normalized_subcategory else None
            }
        )

    async def get_resources(self, category: str = None, subcategory: str = None, difficulty: str = None):
        """
        Recupera recursos de la base de datos de recursos de Notion basándose en filtros opcionales.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return []

        filter_conditions = []

        # Normalizar los parámetros de búsqueda antes de usarlos en la consulta
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)

        if normalized_category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": normalized_category}
            })
        if normalized_subcategory:
            filter_conditions.append({
                "property": "subcategory",
                "select": {"equals": normalized_subcategory}
            })
        if normalized_difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": normalized_difficulty}
            })

        query_filter = {}
        if filter_conditions:
            if len(filter_conditions) == 1:
                query_filter = filter_conditions[0]
            else:
                query_filter["and"] = filter_conditions

        pages = await self.notion_service.query_database(
            database_id=self.notion_database_resources_id,
            filter=query_filter
        )

        resources = []
        for page in pages:
            props = page["properties"]
            resource = {
                "resource_name": props.get("resource_name", {}).get("title", [{}])[0].get("plain_text") if props.get("resource_name") else None,
                "link": props.get("link", {}).get("url"),
                "category": props.get("category", {}).get("select", {}).get("name"),
                "subcategory": props.get("subcategory", {}).get("select", {}).get("name"),
                "difficulty": props.get("difficulty", {}).get("select", {}).get("name"),
            }
            resources.append(resource)
        return resources

    async def get_distinct_difficulties(self):
        """
        Obtiene una lista de todas las dificultades distintas disponibles en la base de datos de recursos.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return []

        difficulties = set()
        pages = await self.notion_service.query_database(
            database_id=self.notion_database_resources_id
        )
        for page in pages:
            difficulty = page["properties"].get("difficulty", {}).get("select", {}).get("name")
            if difficulty:
                difficulties.add(difficulty)
        return sorted(list(difficulties))

    async def get_distinct_categories(self, difficulty: str = None):
        """
        Obtiene una lista de todas las categorías distintas disponibles en la base de datos de recursos,
        opcionalmente filtradas por dificultad.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return []

        categories = set()
        filter_conditions = []
        if difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": self._normalize_string(difficulty)}
            })

        query_filter = {}
        if filter_conditions:
            query_filter["and"] = filter_conditions

        pages = await self.notion_service.query_database(
            database_id=self.notion_database_resources_id,
            filter=query_filter
        )
        for page in pages:
            category = page["properties"].get("category", {}).get("select", {}).get("name")
            if category:
                categories.add(category)
        return sorted(list(categories))

    async def get_distinct_subcategories(self, difficulty: str = None, category: str = None):
        """
        Obtiene una lista de todas las subcategorías distintas disponibles en la base de datos de recursos,
        opcionalmente filtradas por dificultad y/o categoría.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return []

        subcategories = set()
        filter_conditions = []
        if difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": self._normalize_string(difficulty)}
            })
        if category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": self._normalize_string(category)}
            })

        query_filter = {}
        if filter_conditions:
            query_filter["and"] = filter_conditions

        pages = await self.notion_service.query_database(
            database_id=self.notion_database_resources_id,
            filter=query_filter
        )
        for page in pages:
            subcategory = page["properties"].get("subcategory", {}).get("select", {}).get("name")
            if subcategory:
                subcategories.add(subcategory)
        return sorted(list(subcategories))

    # --- Nuevas funciones para la base de datos de Ventas ---
    async def insert_sales_report(self, date: str, product: str, sales_amount: float, region: str, notes: str = None):
        """
        Inserta un nuevo reporte de ventas en la base de datos de ventas de Notion.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return False

        # Normalizar los datos antes de la inserción si es necesario (ej. producto, región)
        normalized_product = self._normalize_string(product)
        normalized_region = self._normalize_string(region)

        properties = {
            "Date": {"date": {"start": date}},
            "Product": {"select": {"name": normalized_product}},
            "Sales Amount": {"number": sales_amount},
            "Region": {"select": {"name": normalized_region}}
        }
        if notes:
            properties["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

        return await self.notion_service.insert_page(
            database_id=self.notion_database_sales_id,
            properties=properties
        )

    async def get_sales_data(self, start_date: str = None, end_date: str = None, product: str = None, region: str = None):
        """
        Recupera datos de ventas de la base de datos de ventas de Notion basándose en filtros opcionales.
        Delega la operación al NotionService.
        """
        if not self.notion_service:
            self.connect()
        if not self.notion_service:
            return []

        filter_conditions = []

        if start_date and end_date:
            filter_conditions.append({
                "property": "Date",
                "date": {"on_or_after": start_date, "on_or_before": end_date}
            })
        elif start_date:
            filter_conditions.append({
                "property": "Date",
                "date": {"on_or_after": start_date}
            })
        elif end_date:
            filter_conditions.append({
                "property": "Date",
                "date": {"on_or_before": end_date}
            })

        if product:
            filter_conditions.append({
                "property": "Product",
                "select": {"equals": self._normalize_string(product)}
            })
        if region:
            filter_conditions.append({
                "property": "Region",
                "select": {"equals": self._normalize_string(region)}
            })

        query_filter = {}
        if filter_conditions:
            if len(filter_conditions) == 1:
                query_filter = filter_conditions[0]
            else:
                query_filter["and"] = filter_conditions

        pages = await self.notion_service.query_database(
            database_id=self.notion_database_sales_id,
            filter=query_filter
        )

        sales_data = []
        for page in pages:
            props = page["properties"]
            data = {
                "date": props.get("Date", {}).get("date", {}).get("start"),
                "product": props.get("Product", {}).get("select", {}).get("name"),
                "sales_amount": props.get("Sales Amount", {}).get("number"),
                "region": props.get("Region", {}).get("select", {}).get("name"),
                "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("plain_text") if props.get("Notes") else None,
            }
            sales_data.append(data)
        return sales_data


# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Asegúrate de tener estas variables en tu .env para que el ejemplo funcione
    # NOTION_TOKEN="secret_YOUR_NOTION_INTEGRATION_TOKEN"
    # NOTION_DATABASE_RESOURCES_ID="YOUR_RESOURCES_DATABASE_ID"
    # NOTION_DATABASE_SALES_ID="YOUR_SALES_DATABASE_ID"

    async def test_db_manager():
        db_manager = DBManager()

        # Prueba de conexión
        if db_manager.connect():
            print("Conexión de prueba a Notion exitosa.")

            # --- Pruebas de Recursos ---
            print("\n--- Probando inserción de recurso en Notion ---")
            success = await db_manager.insert_resource(
                resource_name="Guía de Productividad Avanzada",
                link="https://ejemplo.com/guia_productividad_notion",
                category="Autogestión",
                subcategory="Gestión del Tiempo",
                difficulty="Avanzado"
            )
            if success:
                print("Inserción de recurso de prueba exitosa.")
            else:
                print("Fallo en la inserción del recurso de prueba.")

            print("\n--- Probando recuperación de recursos (categoría 'autogestion') ---")
            autogestion_resources = await db_manager.get_resources(category="autogestion")
            for res in autogestion_resources:
                print(res)

            print("\n--- Probando obtención de dificultades distintas ---")
            difficulties = await db_manager.get_distinct_difficulties()
            print(f"Dificultades distintas: {difficulties}")

            # --- Pruebas de Ventas ---
            print("\n--- Probando inserción de reporte de ventas en Notion ---")
            sales_success = await db_manager.insert_sales_report(
                date="2025-07-25",
                product="Servicio Premium",
                sales_amount=150.75,
                region="Europa",
                notes="Cliente muy interesado en futuras actualizaciones."
            )
            if sales_success:
                print("Inserción de reporte de ventas de prueba exitosa.")
            else:
                print("Fallo en la inserción del reporte de ventas de prueba.")

            print("\n--- Probando recuperación de datos de ventas (producto 'Servicio Premium') ---")
            sales_data = await db_manager.get_sales_data(product="Servicio Premium")
            for data in sales_data:
                print(data)

        else:
            print("No se pudo conectar a la base de datos de Notion para las pruebas.")

        db_manager.close() # Asegurarse de "cerrar" el cliente al finalizar

    import asyncio
    asyncio.run(test_db_manager())
