# Archivo: cogs/commands.py

import discord
from discord.ext import commands
import asyncio # Necesario para el sleep en el comando limpiar

import config # Importa la configuración para acceder a user_conversations
from utils.helpers import get_help_message # Importa la función de ayuda
# Importar las vistas aquí. Asumimos que views/main_menu.py existirá.
from views.main_menu import MainMenuView, CloseTicketView # Se importará cuando se cree el archivo

class Commands(commands.Cog):
    """
    Cog que contiene los comandos generales del bot de Discord.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='iniciar', help='Inicia la interacción guiada con el bot.')
    async def iniciar(self, ctx):
        """
        Inicia la interacción guiada con el bot, presentando opciones con botones.
        """
        try:
            # Se pasa la instancia del bot (self.bot) a MainMenuView
            view = MainMenuView(self.bot)
            # Almacena el mensaje para que la vista pueda editarlo en caso de timeout
            view.message = await ctx.send("Hola, soy el Bot de Neurocogniciones. ¿Cómo puedo ayudarte hoy?", view=view)
        except Exception as e:
            await ctx.send(f"Ocurrió un error al iniciar la interacción: `{e}`")
            print(f"Error en el comando iniciar: {e}")


    @commands.command(name='ayuda', help='Muestra información sobre los comandos disponibles y cómo usarlos.')
    async def ayuda(self, ctx):
        """
        Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos.
        """
        # Usar la función get_help_message del módulo helpers
        await ctx.send(get_help_message(self.bot.commands))

    @commands.command(name='limpiar', help='Elimina un número específico de mensajes del canal.')
    @commands.has_permissions(manage_messages=True) # Requiere permiso para gestionar mensajes
    async def limpiar(self, ctx, cantidad: int):
        """
        Elimina un número específico de mensajes del canal.
        """
        if cantidad <= 0:
            await ctx.send("❌ La cantidad de mensajes a eliminar debe ser un número positivo.", delete_after=5)
            return

        try:
            # +1 para incluir el mensaje del comando 'limpiar'
            await ctx.channel.purge(limit=cantidad + 1)
            await ctx.send(f"✅ Se eliminaron {cantidad} mensajes del canal.", delete_after=3)
        except discord.Forbidden:
            await ctx.send("❌ No tengo los permisos necesarios para eliminar mensajes. Asegúrate de que el bot tenga el permiso 'Gestionar mensajes'.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error al intentar limpiar mensajes: `{e}`", delete_after=5)
            print(f"Error en el comando limpiar: {e}")

    @limpiar.error
    async def limpiar_error(self, ctx, error):
        """
        Manejador de errores para el comando 'limpiar'.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Error: Faltan argumentos. Usa `&limpiar <cantidad>` para eliminar un número específico de mensajes.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Error: La cantidad debe ser un número entero. Usa `&limpiar <cantidad>`.", delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes los permisos necesarios para usar este comando. Necesitas el permiso 'Gestionar mensajes'.", delete_after=5)
        else:
            await ctx.send(f"❌ Ocurrió un error inesperado con el comando limpiar: `{error}`", delete_after=5)
            print(f"Error inesperado en limpiar_error: {error}")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Comandos al bot.
    """
    await bot.add_cog(Commands(bot))
