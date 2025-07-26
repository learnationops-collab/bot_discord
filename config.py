import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- TOKEN DEL BOT ---
# El token de tu bot de Discord. Es crucial mantenerlo seguro y no compartirlo.
TOKEN = os.getenv('TOKEN')

# --- CONFIGURACIÓN DE IDs DE CANALES, CATEGORÍAS Y ROLES ---
# Estos IDs se obtienen activando el Modo Desarrollador en Discord (Ajustes de Usuario -> Avanzado),
# luego haciendo clic derecho en el canal/categoría/rol y seleccionando "Copiar ID".
# Es fundamental que estos valores se configuren en tu archivo .env.

# Diccionario para almacenar IDs de categorías, facilitando la configuración por área.
# Las claves son nombres descriptivos y los valores son los IDs de las categorías.
CATEGORY_IDS = {
    'OPERACIONES': int(os.getenv('OPERACIONES_CATEGORY_ID')) if os.getenv('OPERACIONES_CATEGORY_ID') else None,
    'FULFILLMENT': int(os.getenv('FULFILLMENT_CATEGORY_ID')) if os.getenv('FULFILLMENT_CATEGORY_ID') else None,
    'SALES': int(os.getenv('SALES_CATEGORY_ID')) if os.getenv('SALES_CATEGORY_ID') else None,
}

# Diccionario para almacenar IDs de canales específicos.
CHANNEL_IDS = {
    'BOT_TEST': int(os.getenv('BOT_TEST_CHANNEL_ID')) if os.getenv('BOT_TEST_CHANNEL_ID') else None,
}

# Diccionario para almacenar IDs de roles.
ROLE_IDS = {
    'CSMS': int(os.getenv('CSMS_ROLE_ID')) if os.getenv('CSMS_ROLE_ID') else None, # Ajustado a CSMS_ROLE_ID
    'DEBUG': int(os.getenv('DEBUG_ROLE_ID')) if os.getenv('DEBUG_ROLE_ID') else None,
}

# --- CONFIGURACIÓN DE NOTION ---
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_RESOURCES_ID = os.getenv('NOTION_DATABASE_RESOURCES_ID')
NOTION_DATABASE_SALES_ID = os.getenv('NOTION_DATABASE_SALES_ID')

# Diccionario para almacenar el estado de las conversaciones de "Hablar con un Humano"
# Formato: {user_id: {'state': int, 'answers': [], 'channel_id': None}}
# state: 0 = no en conversación, 1 = esperando respuesta a Pregunta 1, etc.
# NOTA: En una aplicación más grande, este diccionario debería persistir en una base de datos.
user_conversations = {}

def validate_env_variables():
    """
    Valida que las variables de entorno esenciales estén configuradas.
    Imprime advertencias si alguna variable importante no se encuentra.
    """
    if TOKEN is None:
        print("¡ADVERTENCIA! La variable de entorno 'TOKEN' no está definida. El bot no podrá iniciar sesión.")

    # Validar IDs de categorías
    for category_name, category_id in CATEGORY_IDS.items():
        if category_id is None:
            print(f"¡ADVERTENCIA! La variable de entorno '{category_name}_CATEGORY_ID' no está definida.")

    # Validar IDs de canales
    for channel_name, channel_id in CHANNEL_IDS.items():
        if channel_id is None:
            print(f"¡ADVERTENCIA! La variable de entorno '{channel_name}_CHANNEL_ID' no está definida.")

    # Validar IDs de roles
    for role_name, role_id in ROLE_IDS.items():
        if role_id is None:
            print(f"¡ADVERTENCIA! La variable de entorno '{role_name}_ROLE_ID' no está definida.")

    if NOTION_TOKEN is None:
        print("¡ADVERTENCIA! 'NOTION_TOKEN' no está definido. La integración con Notion podría fallar.")
    if NOTION_DATABASE_RESOURCES_ID is None:
        print("¡ADVERTENCIA! 'NOTION_DATABASE_RESOURCES_ID' no está definido. La gestión de recursos de Notion podría fallar.")
    if NOTION_DATABASE_SALES_ID is None:
        print("¡ADVERTENCIA! 'NOTION_DATABASE_SALES_ID' no está definido. La gestión de ventas de Notion podría fallar.")

# Llama a la función de validación al cargar el módulo
validate_env_variables()
