# Archivo: bot.py
# Punto de entrada principal para el Bot de Neurocogniciones.

import os
import discord
from discord.ext import commands
import asyncio

# Importa las configuraciones y el gestor de la base de datos
import config
from database.db_manager import DBManager

# Importa todos los cogs (módulos) que hemos creado
from cogs.events import Events
from cogs.commands import Commands
from cogs.ticket_management import TicketManagement
from cogs.human_interaction import HumanInteraction
from cogs.resources import Resources

# --- CONFIGURACIÓN DE INTENTS (PERMISOS) ---
# Los intents definen qué eventos de Discord tu bot puede recibir.
# Es crucial habilitar solo los que necesitas para optimizar el rendimiento
# y cumplir con las políticas de Discord.
intents = discord.Intents.default()
intents.message_content = True  # Necesario para leer el contenido de los mensajes (para comandos y flujos de conversación)
intents.members = True          # Necesario para el evento on_member_join (bienvenida a nuevos miembros)
intents.guilds = True           # Necesario para operaciones a nivel de servidor (crear canales, obtener roles)

# Inicializa el bot con un prefijo de comando y los intents definidos.
# El prefijo '&' significa que los comandos se activarán con '&comando'.
bot = commands.Bot(command_prefix='&', intents=intents)

# --- FUNCIÓN PARA CARGAR LOS COGS ---
async def load_cogs():
    """
    Carga todos los cogs (extensiones) del bot.
    Cada cog encapsula un conjunto de funcionalidades relacionadas.
    """
    print("Cargando cogs...")
    cogs_to_load = [
        "cogs.events",
        "cogs.commands",
        "cogs.ticket_management",
        "cogs.human_interaction",
        "cogs.resources"
    ]
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog '{cog}' cargado exitosamente.")
        except commands.ExtensionAlreadyLoaded:
            print(f"⚠️ Cog '{cog}' ya estaba cargado.")
        except commands.ExtensionNotFound:
            print(f"❌ Error: Cog '{cog}' no encontrado. Asegúrate de que el archivo existe y la ruta es correcta.")
        except Exception as e:
            print(f"❌ Error al cargar el cog '{cog}': {e}")
            import traceback
            traceback.print_exc() # Imprime el traceback completo para depuración
    print("Carga de cogs completada.")

# --- EVENTO on_ready (Manejado en cogs/events.py) ---
# Este evento ya está manejado en el cog 'Events'.
# No es necesario definirlo aquí en el archivo principal si ya está en un cog.

# --- EVENTO on_message ---
# Este evento es crucial para que el bot procese los comandos y los listeners de mensajes en los cogs.
# Si tienes un on_message en el archivo principal, debes asegurarte de llamar a process_commands.
@bot.event
async def on_message(message):
    """
    Maneja cada mensaje recibido por el bot.
    Es vital para que los comandos y los listeners de cogs funcionen.
    """
    # Ignorar mensajes del propio bot para evitar bucles infinitos
    if message.author == bot.user:
        return

    # Procesar los comandos definidos en los cogs
    # Esto también permite que los listeners de mensajes en los cogs (como en human_interaction.py)
    # se activen antes de que los comandos sean procesados, si es necesario.
    await bot.process_commands(message)

# --- INICIO DEL BOT ---
# Esta es la función principal que se ejecuta cuando se inicia el script.
async def main():
    """
    Función principal para inicializar y ejecutar el bot.
    """
    # Cargar los cogs antes de que el bot se conecte
    await load_cogs()

    # Iniciar el bot con el token cargado desde config.py
    if config.TOKEN:
        try:
            await bot.start(config.TOKEN)
        except discord.LoginFailure:
            print("❌ Error de inicio de sesión: Token inválido. Por favor, verifica tu TOKEN en el archivo .env")
        except Exception as e:
            print(f"❌ Ocurrió un error al iniciar el bot: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No se encontró el TOKEN del bot. Asegúrate de que está configurado en tu archivo .env.")

# Ejecutar la función principal
if __name__ == "__main__":
    # Cargar los cogs antes de que el bot se conecte
    # Esto se puede hacer en un bloque try-except si quieres manejar errores de carga de cogs
    # antes de intentar iniciar el bot.
    asyncio.run(load_cogs()) # Ejecuta load_cogs de forma síncrona antes de bot.run

    # Iniciar el bot con el token cargado desde config.py
    if config.TOKEN:
        try:
            # Usa bot.run() para una gestión más robusta del ciclo de vida del bot
            bot.run(config.TOKEN)
        except discord.LoginFailure:
            print("❌ Error de inicio de sesión: Token inválido. Por favor, verifica tu TOKEN en el archivo .env")
        except Exception as e:
            print(f"❌ Ocurrió un error al iniciar el bot: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No se encontró el TOKEN del bot. Asegúrate de que está configurado en tu archivo .env.")
