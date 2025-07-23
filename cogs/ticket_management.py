# Archivo: cogs/ticket_management.py

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a IDs de roles y categorías
# CloseTicketView y DifficultySelectionView ya no se importan aquí
# ya que no se crearán nuevos canales ni se cerrarán tickets de esta forma.

class TicketManagement(commands.Cog):
    """
    Cog que manejaba la creación y gestión de tickets de soporte técnico y canales de búsqueda de recursos.
    Ahora, estas interacciones se manejarán directamente en el canal de inicio.
    """
    def __init__(self, bot):
        self.bot = bot

    # Las funciones create_technical_ticket y create_resource_search_channel
    # han sido eliminadas ya que no se crearán nuevos canales.
    # La lógica para iniciar estos flujos se ha movido a views/main_menu.py.

    # El comando cerrar_ticket también se elimina, ya que no hay canales de ticket específicos
    # para cerrar en este nuevo flujo. Si se necesita una forma de "finalizar" una conversación
    # en el canal principal, se puede implementar un comando o botón diferente.
    # @commands.command(name='cerrar_ticket', help='Cierra el canal de soporte actual (solo en canales de ticket).')
    # async def cerrar_ticket(self, ctx):
    #    ... (lógica eliminada) ...

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de TicketManagement al bot.
    """
    await bot.add_cog(TicketManagement(bot))
