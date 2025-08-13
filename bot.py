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
from cogs.bug_info import BugInfo # <--- NUEVA LÍNEA

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
    Carga todos los cogs del bot de forma asíncrona.
    """
    try:
        await bot.load_extension('cogs.events')
        await bot.load_extension('cogs.commands')
        await bot.load_extension('cogs.ticket_management')
        await bot.load_extension('cogs.human_interaction')
        await bot.load_extension('cogs.resources')
        await bot.load_extension('cogs.bug_info') # <--- NUEVA LÍNEA
        print("✅ Cogs cargados exitosamente.")
    except Exception as e:
        print(f"❌ Error al cargar un cog: {e}")

# ... (resto del código del bot.py se mantiene igual) ...

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(load_cogs())
    
    if config.TOKEN:
        try:
            bot.run(config.TOKEN)
        except discord.LoginFailure:
            print("❌ Error de inicio de sesión: Token inválido. Por favor, verifica tu TOKEN en el archivo .env")
        except Exception as e:
            print(f"❌ Ocurrió un error al iniciar el bot: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No se encontró el TOKEN del bot. Asegúrate de que está configurado en tu archivo .env.")
