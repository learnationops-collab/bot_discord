import os
import psycopg2
from dotenv import load_dotenv
import unicodedata # Necesario para la normalización de cadenas

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class DBManager:
    """
    Clase para gestionar la conexión y las operaciones con la base de datos PostgreSQL.
    Permite insertar y recuperar recursos para el bot.
    """
    def __init__(self):
        """
        Inicializa el DBManager cargando las credenciales de la base de datos
        desde las variables de entorno.
        """
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST', 'localhost') # Por defecto 'localhost'
        self.db_port = os.getenv('DB_PORT', '5432')     # Por defecto '5432'
        self.conn = None # La conexión se establecerá cuando sea necesario

        # Validación básica de las variables de entorno de la base de datos
        if not all([self.db_name, self.db_user, self.db_password]):
            print("¡ADVERTENCIA! Las variables de entorno de la base de datos (DB_NAME, DB_USER, DB_PASSWORD) no están completamente configuradas.")
            print("Asegúrate de que DB_NAME, DB_USER y DB_PASSWORD estén definidos en tu archivo .env.")

    def _normalize_string(self, text: str) -> str:
        """
        Normaliza una cadena de texto: la convierte a minúsculas y elimina acentos.
        Esto es útil para búsquedas insensibles a mayúsculas/minúsculas y acentos.
        """
        if text is None:
            return None
        # Normaliza a la forma de descomposición canónica, luego elimina los caracteres diacríticos
        normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return normalized_text.lower()

    def connect(self):
        """
        Establece una conexión con la base de datos PostgreSQL.
        Retorna el objeto de conexión si es exitosa, None en caso de error.
        """
        if self.conn is not None and not self.conn.closed:
            # Si ya hay una conexión abierta y no está cerrada, la reutilizamos
            return self.conn

        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            print("Conexión a la base de datos establecida exitosamente.")
            return self.conn
        except psycopg2.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            self.conn = None # Asegurarse de que la conexión sea None si falla
            return None

    def close(self):
        """
        Cierra la conexión activa con la base de datos.
        """
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                print("Conexión a la base de datos cerrada.")
            except psycopg2.Error as e:
                print(f"Error al cerrar la conexión de la base de datos: {e}")

    def insert_resource(self, resource_name: str, link: str, category: str, difficulty: str, subcategory: str = None):
        """
        Inserta un nuevo recurso en la tabla 'resources'.
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
        # Normalizar los datos antes de la inserción
        normalized_resource_name = self._normalize_string(resource_name)
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)

        sql = """
        INSERT INTO resources (resource_name, link, category, subcategory, difficulty)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING resource_id;
        """
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (normalized_resource_name, link, normalized_category, normalized_subcategory, normalized_difficulty))
                    resource_id = cur.fetchone()[0]
                    conn.commit()
                    print(f"Recurso '{resource_name}' insertado con ID: {resource_id}")
                    return True
            except psycopg2.Error as e:
                print(f"Error al insertar el recurso '{resource_name}': {e}")
                conn.rollback() # Revertir la transacción en caso de error
                return False
            finally:
                pass
        return False

    def get_resources(self, category: str = None, subcategory: str = None, difficulty: str = None):
        """
        Recupera recursos de la tabla 'resources' basándose en filtros opcionales.
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
        sql = "SELECT resource_name, link, category, subcategory, difficulty FROM resources WHERE 1=1"
        params = []

        # Normalizar los parámetros de búsqueda antes de usarlos en la consulta
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)

        if normalized_category:
            sql += " AND category ILIKE %s" # ILIKE para búsqueda insensible a mayúsculas/minúsculas
            params.append(f"%{normalized_category}%")
        if normalized_subcategory:
            sql += " AND subcategory ILIKE %s"
            params.append(f"%{normalized_subcategory}%")
        if normalized_difficulty:
            sql += " AND difficulty ILIKE %s"
            params.append(f"%{normalized_difficulty}%")

        resources = []
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description] # Obtener nombres de columnas
                    for row in rows:
                        resources.append(dict(zip(columns, row)))
                print(f"Recursos encontrados: {len(resources)}")
            except psycopg2.Error as e:
                print(f"Error al obtener recursos: {e}")
            finally:
                pass
        return resources

    def get_distinct_difficulties(self):
        """
        Obtiene una lista de todas las dificultades distintas disponibles en la tabla de recursos.
        """
        sql = "SELECT DISTINCT difficulty FROM resources ORDER BY difficulty ASC;"
        difficulties = []
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    rows = cur.fetchall()
                    difficulties = [row[0] for row in rows if row[0] is not None]
            except psycopg2.Error as e:
                print(f"Error al obtener dificultades distintas: {e}")
            finally:
                pass
        return difficulties

    def get_distinct_categories(self, difficulty: str = None):
        """
        Obtiene una lista de todas las categorías distintas disponibles,
        opcionalmente filtradas por dificultad.
        """
        sql = "SELECT DISTINCT category FROM resources WHERE 1=1"
        params = []
        if difficulty:
            sql += " AND difficulty ILIKE %s"
            params.append(f"%{self._normalize_string(difficulty)}%")
        sql += " ORDER BY category ASC;"

        categories = []
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    categories = [row[0] for row in rows if row[0] is not None]
            except psycopg2.Error as e:
                print(f"Error al obtener categorías distintas: {e}")
            finally:
                pass
        return categories

    def get_distinct_subcategories(self, difficulty: str = None, category: str = None):
        """
        Obtiene una lista de todas las subcategorías distintas disponibles,
        opcionalmente filtradas por dificultad y/o categoría.
        """
        sql = "SELECT DISTINCT subcategory FROM resources WHERE subcategory IS NOT NULL"
        params = []
        if difficulty:
            sql += " AND difficulty ILIKE %s"
            params.append(f"%{self._normalize_string(difficulty)}%")
        if category:
            sql += " AND category ILIKE %s"
            params.append(f"%{self._normalize_string(category)}%")
        sql += " ORDER BY subcategory ASC;"

        subcategories = []
        conn = self.connect()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    subcategories = [row[0] for row in rows if row[0] is not None]
            except psycopg2.Error as e:
                print(f"Error al obtener subcategorías distintas: {e}")
            finally:
                pass
        return subcategories


# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Asegúrate de tener estas variables en tu .env para que el ejemplo funcione
    # DB_NAME=neurocogniciones_db
    # DB_USER=nombre_usuario
    # DB_PASSWORD=tu_contraseña_segura
    # DB_HOST=localhost
    # DB_PORT=5432

    db_manager = DBManager()

    # Prueba de conexión
    if db_manager.connect():
        print("Conexión de prueba exitosa.")
        # Prueba de inserción con acentos y mayúsculas
        print("\n--- Probando inserción de recurso con acentos y mayúsculas ---")
        success = db_manager.insert_resource(
            resource_name="Guía de Productividad Avanzada",
            link="https://ejemplo.com/guia_productividad",
            category="Autogestión",
            subcategory="Gestión del Tiempo",
            difficulty="Avanzado"
        )
        if success:
            print("Inserción de recurso de prueba exitosa.")
        else:
            print("Fallo en la inserción del recurso de prueba.")

        # Prueba de recuperación de recursos con diferentes casos y acentos
        print("\n--- Probando recuperación de recursos (categoría 'APRENDIZAJE' con acento) ---")
        learning_resources = db_manager.get_resources(category="APRENDIZAJE")
        for res in learning_resources:
            print(res)

        print("\n--- Probando recuperación de recursos (dificultad 'basico' sin acento) ---")
        basic_resources = db_manager.get_resources(difficulty="basico")
        for res in basic_resources:
            print(res)

        print("\n--- Probando recuperación de recursos (categoría 'autorregulacion', subcategoría 'ansiedad') ---")
        anxiety_resources = db_manager.get_resources(category="autorregulacion", subcategory="ansiedad")
        for res in anxiety_resources:
            print(res)

        print("\n--- Probando recuperación de recursos (categoría 'autogestion', subcategoría 'gestion del tiempo') ---")
        time_management_resources = db_manager.get_resources(category="autogestion", subcategory="gestion del tiempo")
        for res in time_management_resources:
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
        print("No se pudo conectar a la base de datos para las pruebas.")

    db_manager.close() # Asegurarse de cerrar la conexión al finalizar
