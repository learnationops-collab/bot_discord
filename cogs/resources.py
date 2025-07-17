# Archivo: cogs/resources.py

import discord
from discord.ext import commands
from database.db_manager import DBManager # Importa el gestor de la base de datos

class Resources(commands.Cog):
    """
    Cog que maneja la búsqueda y presentación de recursos a los estudiantes.
    La interacción principal para recursos ahora se maneja a través de botones
    definidos en views/main_menu.py.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager() # Instancia el gestor de la base de datos

    # El comando '&recurso' ha sido eliminado ya que la interacción
    # para la búsqueda de recursos ahora se gestiona completamente a través
    # de las vistas (botones) definidas en views/main_menu.py.
    # Si en el futuro se necesita un comando directo, se puede añadir aquí.

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Resources al bot.
    """
    await bot.add_cog(Resources(bot))
