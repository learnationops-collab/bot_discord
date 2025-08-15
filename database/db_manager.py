import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.helpers import collect_paginated_api # Útil para obtener todos los resultados de una consulta paginada
import unicodedata

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class DBManager:
    """
    Clase para gestionar la conexión y las operaciones con la base de datos de Notion.
    Permite insertar y recuperar recursos para el bot.
    """
    def __init__(self):
        """
        Inicializa el DBManager cargando el token de Notion y el ID de la base de datos
        desde las variables de entorno.
        """
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion = None # El cliente de Notion se inicializará en connect

        # Validación básica de las variables de entorno de Notion
        if not self.notion_token or not self.notion_database_id:
            print("¡ADVERTENCIA! Las variables de entorno de Notion (NOTION_TOKEN, NOTION_DATABASE_ID) no están completamente configuradas.")
            print("Asegúrate de que NOTION_TOKEN y NOTION_DATABASE_ID estén definidos en tu archivo .env.")

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
        Inicializa el cliente de Notion utilizando el token de integración.
        Retorna el objeto de cliente de Notion si es exitoso, None en caso de error.
        """
        if self.notion is None:
            try:
                self.notion = Client(auth=self.notion_token)
                print("Cliente de Notion inicializado exitosamente.")
            except Exception as e:
                print(f"Error al inicializar el cliente de Notion: {e}")
                self.notion = None # Asegurarse de que el cliente sea None si falla
        return self.notion

    def close(self):
        """
        No se necesita una acción explícita de cierre para el cliente de Notion,
        ya que gestiona las conexiones internamente.
        """
        self.notion = None
        print("Cliente de Notion 'cerrado' (desreferenciado).")

    def insert_resource(self, resource_name: str, link: str, category: str, difficulty: str, subcategory: str = None):
        """
        Inserta un nuevo recurso en la base de datos de Notion.
        Los campos de texto se normalizan antes de la inserción para asegurar
        que estén en minúsculas y sin acentos, facilitando búsquedas consistentes.

        Args:
            resource_name (str): Nombre descriptivo del recurso.
            link (str): Enlace (URL) del recurso.
            category (str): Categoría principal del recurso.
            difficulty (str): Dificultad del recurso ('básico' o 'avanzado').
            subcategory (str, optional): Subcategoría o problema específico. Por defecto None.

        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario.
        """
        if not self.notion:
            self.connect()
        if not self.notion:
            return False

        try:
            # Normalizar los datos antes de la inserción
            normalized_resource_name = self._normalize_string(resource_name)
            normalized_category = self._normalize_string(category)
            normalized_subcategory = self._normalize_string(subcategory)
            normalized_difficulty = self._normalize_string(difficulty)

            # Construir el diccionario de propiedades para la página de Notion
            properties = {
                "resource_name": {"title": [{"text": {"content": normalized_resource_name}}]},
                "link": {"url": link},
                "category": {"select": {"name": normalized_category}},
                "difficulty": {"select": {"name": normalized_difficulty}}
            }
            if normalized_subcategory:
                # Asumimos que 'Subcategory' es una propiedad de tipo 'Select'
                properties["subcategory"] = {"select": {"name": normalized_subcategory}}

            self.notion.pages.create(
                parent={"database_id": self.notion_database_id},
                properties=properties
            )
            print(f"Recurso '{resource_name}' insertado en Notion.")
            return True
        except Exception as e:
            print(f"Error al insertar el recurso '{resource_name}' en Notion: {e}")
            return False

    def get_resources(self, category: str = None, subcategory: str = None, difficulty: str = None):
        """
        Recupera recursos de la base de datos de Notion basándose en filtros opcionales.
        Los parámetros de búsqueda se normalizan (minúsculas y sin acentos)
        para coincidir con el formato de los datos almacenados en la base de datos.

        Args:
            category (str, optional): Filtra por categoría. Por defecto None (sin filtro).
            subcategory (str, optional): Filtra por subcategoría. Por defecto None (sin filtro).
            difficulty (str, optional): Filtra por dificultad. Por defecto None (sin filtro).

        Returns:
            list: Una lista de diccionarios, donde cada diccionario representa un recurso.
                  Retorna una lista vacía si no se encuentran recursos o si hay un error.
        """
        if not self.notion:
            self.connect()
        if not self.notion:
            return []

        filter_conditions = []

        # Normalizar los parámetros de búsqueda antes de usarlos en la consulta
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)

        if normalized_category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": category}
            })
        if normalized_subcategory:
            filter_conditions.append({
                "property": "subcategory",
                "select": {"equals": subcategory}
            })
        if normalized_difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": difficulty}
            })

        query_filter = {}
        if filter_conditions:
            if len(filter_conditions) == 1:
                query_filter = filter_conditions[0]
            else:
                query_filter["and"] = filter_conditions

        resources = []
        try:
            # Usar collect_paginated_api para obtener todos los resultados si hay muchos
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )

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
            print(f"Recursos encontrados en Notion: {len(resources)}")
        except Exception as e:
            print(f"Error al obtener recursos de Notion: {e}")
        return resources

    def get_distinct_difficulties(self):
        """
        Obtiene una lista de todas las dificultades distintas disponibles en la base de datos de Notion.
        """
        if not self.notion:
            self.connect()
        if not self.notion:
            return []

        difficulties = set()
        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id
            )
            for page in pages:
                difficulty = page["properties"].get("difficulty", {}).get("select", {}).get("name")
                if difficulty:
                    difficulties.add(difficulty)
        except Exception as e:
            print(f"Error al obtener dificultades distintas de Notion: {e}")
        return sorted(list(difficulties))

    def get_distinct_categories(self, difficulty: str = None):
        """
        Obtiene una lista de todas las categorías distintas disponibles,
        opcionalmente filtradas por dificultad.
        """
        if not self.notion:
            self.connect()
        if not self.notion:
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

        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            for page in pages:
                category = page["properties"].get("category", {}).get("select", {}).get("name")
                if category:
                    categories.add(category)
        except Exception as e:
            print(f"Error al obtener categorías distintas de Notion: {e}")
        return sorted(list(categories))

    def get_distinct_subcategories(self, difficulty: str = None, category: str = None):
        """
        Obtiene una lista de todas las subcategorías distintas disponibles,
        opcionalmente filtradas por dificultad y/o categoría.
        """
        if not self.notion:
            self.connect()
            print("Conectando a Notion para obtener subcategorías...")
        if not self.notion:
            print("No se pudo conectar a Notion para obtener subcategorías.")
            print("Asegúrate de que el cliente de Notion esté inicializado correctamente.")
            return []

        subcategories = set()
        filter_conditions = []
        if difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": self._normalize_string(difficulty)}
            })
            print(f"Filtrando por dificultad: {difficulty}")
        if category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": category}
            })
            print(f"Filtrando por categoría: {category}")

        query_filter = {}
        if filter_conditions:
            query_filter["and"] = filter_conditions
            print(f"Condiciones de filtro aplicadas: {query_filter}")

        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            for page in pages:
                subcategory = page["properties"].get("subcategory", {}).get("select", {}).get("name")
                if subcategory:
                    print(f"Subcategoría encontrada: {subcategory}")
                    subcategories.add(subcategory)
        except Exception as e:
            print(f"Error al obtener subcategorías distintas de Notion: {e}")
        return sorted(list(subcategories))

'''
# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Asegúrate de tener estas variables en tu .env para que el ejemplo funcione
    # NOTION_TOKEN="secret_YOUR_NOTION_INTEGRATION_TOKEN"
    # NOTION_DATABASE_ID="YOUR_NOTION_DATABASE_ID"

    db_manager = DBManager()

    # Prueba de conexión
    if db_manager.connect():
        print("Conexión de prueba a Notion exitosa.")

        # Prueba de inserción de recurso
        print("\n--- Probando inserción de recurso en Notion ---")
        success = db_manager.insert_resource(
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

        # Prueba de recuperación de recursos
        print("\n--- Probando recuperación de recursos (categoría 'autogestion') ---")
        autogestion_resources = db_manager.get_resources(category="autogestion")
        for res in autogestion_resources:
            print(res)

        print("\n--- Probando recuperación de recursos (dificultad 'basico') ---")
        basic_resources = db_manager.get_resources(difficulty="basico")
        for res in basic_resources:
            print(res)

        print("\n--- Probando recuperación de recursos (categoría 'autorregulacion', subcategoría 'ansiedad') ---")
        ansiedad_resources = db_manager.get_resources(category="autorregulacion", subcategory="ansiedad")
        for res in ansiedad_resources:
            print(res)

        print("\n--- Probando obtención de dificultades distintas ---")
        difficulties = db_manager.get_distinct_difficulties()
        print(f"Dificultades distintas: {difficulties}")

        print("\n--- Probando obtención de categorías distintas (filtrado por 'avanzado') ---")
        categories_advanced = db_manager.get_distinct_categories(difficulty="avanzado")
        print(f"Categorías avanzadas: {categories_advanced}")

        print("\n--- Probando obtención de subcategorías distintas (filtrado por 'autogestion' y 'basico') ---")
        subcategories_autogestion_basico = db_manager.get_distinct_subcategories(difficulty="basico", category="autogestion")
        print(f"Subcategorías de autogestión (básico): {subcategories_autogestion_basico}")

    else:
        print("No se pudo conectar a la base de datos de Notion para las pruebas.")

    db_manager.close() # Asegurarse de "cerrar" el cliente al finalizar
'''
