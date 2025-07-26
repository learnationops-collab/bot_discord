# Archivo: services/resource_service.py
# Este servicio maneja la lógica de negocio para la búsqueda y gestión de recursos.

import datetime
from database.db_manager import DBManager # Importa el gestor de la base de datos

class ResourceService:
    """
    Clase que proporciona métodos para buscar y gestionar recursos.
    Interactúa con DBManager para obtener los datos brutos de recursos.
    """
    def __init__(self):
        """
        Inicializa el ResourceService y una instancia de DBManager.
        """
        self.db_manager = DBManager()

    async def connect_db(self):
        """
        Intenta conectar el DBManager. Se llama al iniciar el servicio o antes de operaciones.
        """
        if not self.db_manager.connect():
            print("❌ Error: No se pudo conectar a la base de datos de Notion para ResourceService.")
            return False
        print("✅ DBManager conectado para ResourceService.")
        return True

    async def get_resources(self, category: str = None, subcategory: str = None, difficulty: str = None) -> list:
        """
        Recupera recursos de la base de datos basándose en filtros opcionales.

        Args:
            category (str, optional): Filtra por categoría.
            subcategory (str, optional): Filtra por subcategoría.
            difficulty (str, optional): Filtra por dificultad.

        Returns:
            list: Una lista de diccionarios, donde cada diccionario representa un recurso.
                  Retorna una lista vacía si no se encuentran recursos o si hay un error.
        """
        if not await self.connect_db():
            return []

        try:
            resources = await self.db_manager.get_resources(
                category=category,
                subcategory=subcategory,
                difficulty=difficulty
            )
            print(f"Recursos obtenidos de la DB: {len(resources)}")
            return resources
        except Exception as e:
            print(f"Error al obtener recursos en ResourceService: {e}")
            return []

    async def get_distinct_difficulties(self) -> list:
        """
        Obtiene una lista de todas las dificultades distintas disponibles en la base de datos de recursos.
        """
        if not await self.connect_db():
            return []
        try:
            difficulties = await self.db_manager.get_distinct_difficulties()
            print(f"Dificultades distintas obtenidas: {difficulties}")
            return difficulties
        except Exception as e:
            print(f"Error al obtener dificultades distintas en ResourceService: {e}")
            return []

    async def get_distinct_categories(self, difficulty: str = None) -> list:
        """
        Obtiene una lista de todas las categorías distintas disponibles,
        opcionalmente filtradas por dificultad.
        """
        if not await self.connect_db():
            return []
        try:
            categories = await self.db_manager.get_distinct_categories(difficulty=difficulty)
            print(f"Categorías distintas obtenidas: {categories}")
            return categories
        except Exception as e:
            print(f"Error al obtener categorías distintas en ResourceService: {e}")
            return []

    async def get_distinct_subcategories(self, difficulty: str = None, category: str = None) -> list:
        """
        Obtiene una lista de todas las subcategorías distintas disponibles,
        opcionalmente filtradas por dificultad y/o categoría.
        """
        if not await self.connect_db():
            return []
        try:
            subcategories = await self.db_manager.get_distinct_subcategories(
                difficulty=difficulty,
                category=category
            )
            print(f"Subcategorías distintas obtenidas: {subcategories}")
            return subcategories
        except Exception as e:
            print(f"Error al obtener subcategorías distintas en ResourceService: {e}")
            return []

    # Puedes añadir métodos para insertar, actualizar o eliminar recursos si fuera necesario
    # async def add_resource(self, resource_name: str, link: str, category: str, difficulty: str, subcategory: str = None) -> bool:
    #     """
    #     Añade un nuevo recurso a la base de datos.
    #     """
    #     if not await self.connect_db():
    #         return False
    #     try:
    #         success = await self.db_manager.insert_resource(
    #             resource_name=resource_name,
    #             link=link,
    #             category=category,
    #             difficulty=difficulty,
    #             subcategory=subcategory
    #         )
    #         return success
    #     except Exception as e:
    #         print(f"Error al añadir recurso en ResourceService: {e}")
    #         return False


# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Para ejecutar este ejemplo, asegúrate de tener las variables de entorno de Notion
    # (NOTION_TOKEN, NOTION_DATABASE_RESOURCES_ID) configuradas en tu .env

    async def test_resource_service():
        from dotenv import load_dotenv
        load_dotenv()

        service = ResourceService()

        print("\n--- Probando obtención de dificultades ---")
        difficulties = await service.get_distinct_difficulties()
        print(f"Dificultades: {difficulties}")

        if difficulties:
            first_difficulty = difficulties[0]
            print(f"\n--- Probando obtención de categorías para dificultad '{first_difficulty}' ---")
            categories = await service.get_distinct_categories(difficulty=first_difficulty)
            print(f"Categorías: {categories}")

            if categories:
                first_category = categories[0]
                print(f"\n--- Probando obtención de subcategorías para '{first_category}' ({first_difficulty}) ---")
                subcategories = await service.get_distinct_subcategories(difficulty=first_difficulty, category=first_category)
                print(f"Subcategorías: {subcategories}")

                print(f"\n--- Probando obtención de recursos para '{first_category}' ({first_difficulty}) ---")
                resources = await service.get_resources(category=first_category, difficulty=first_difficulty)
                for res in resources:
                    print(res)
            else:
                print("No se encontraron categorías para la dificultad de prueba.")
        else:
            print("No se encontraron dificultades para la prueba.")

        # Cerrar la conexión de la base de datos al finalizar las pruebas
        service.db_manager.close()

    import asyncio
    asyncio.run(test_resource_service())
