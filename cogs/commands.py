# Archivo: cogs/commands.py

import discord
from discord.ext import commands
import asyncio # Necesario para el sleep en el comando limpiar

import config # Importa la configuración para acceder a user_conversations
from utils.helpers import get_help_message # Importa la función de ayuda
# Importar las vistas aquí. Asumimos que views/main_menu.py existirá.
from views.main_menu import MainMenuView, CloseTicketView, DifficultySelectionView # Se importará cuando se cree el archivo

class Commands(commands.Cog):
    """
    Cog que contiene los comandos generales del bot de Discord.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='iniciar', help='Inicia la interacción guiada con el bot.')
    async def iniciar(self, ctx_or_interaction):
        """
        Inicia la interacción guiada con el bot, presentando opciones con botones.
        Puede ser llamado como un comando o desde una interacción de botón.
        """
        # Determinar si el argumento es un Context o una Interaction
        if isinstance(ctx_or_interaction, commands.Context):
            ctx = ctx_or_interaction
            channel = ctx.channel
            send_func = ctx.send
            response_func = ctx.send # Para compatibilidad, aunque no es una respuesta de interacción
        elif isinstance(ctx_or_interaction, discord.Interaction):
            interaction = ctx_or_interaction
            ctx = None # No hay Context object en este caso
            channel = interaction.channel
            # Para interacciones, la primera respuesta debe ser con interaction.response.send_message
            # Las respuestas subsiguientes pueden ser con interaction.followup.send
            if interaction.response.is_done():
                send_func = interaction.followup.send
            else:
                send_func = interaction.response.send_message
            response_func = interaction.response.send_message # Para la primera respuesta
        else:
            print(f"Tipo de argumento inesperado para iniciar: {type(ctx_or_interaction)}")
            return

        channel_name = channel.name.lower()

        # Si el comando se usa en un canal de recursos, reiniciar la búsqueda de recursos
        if "recursos-" in channel_name:
            if isinstance(ctx_or_interaction, discord.Interaction) and not interaction.response.is_done():
                await interaction.response.defer() # Deferir la interacción si no ha sido respondida

            difficulty_view = DifficultySelectionView(self.bot)
            message_content = "Has solicitado reiniciar la búsqueda de recursos. Por favor, selecciona la dificultad:"
            
            if isinstance(ctx_or_interaction, discord.Interaction):
                # Si es una interacción, usar followup.send
                difficulty_view.message = await interaction.followup.send(message_content, view=difficulty_view)
            else:
                # Si es un comando, usar ctx.send
                difficulty_view.message = await ctx.send(message_content, view=difficulty_view)
            return
        
        # Si el comando se usa en un canal de ayuda técnica o atención al cliente, no permitir iniciar
        elif "ayuda-tecnica-" in channel_name or "atencion-cliente-" in channel_name:
            message = (
                "Este comando está diseñado para usarse en canales públicos para iniciar una nueva interacción.\n"
                "Actualmente te encuentras en un canal de soporte/recursos. "
                "Si deseas iniciar una nueva interacción, por favor, cierra este canal con el botón 'Cerrar Ticket' "
                "o el comando `&cerrar_ticket` y usa `&iniciar` en un canal público."
            )
            if isinstance(ctx_or_interaction, discord.Interaction) and not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True)
            elif isinstance(ctx_or_interaction, discord.Interaction):
                await interaction.followup.send(message, ephemeral=True)
            else:
                await ctx.send(message, delete_after=15) # Eliminar el mensaje después de 15 segundos
            return

        # Lógica original para canales públicos
        try:
            # Se pasa la instancia del bot (self.bot) a MainMenuView
            view = MainMenuView(self.bot)
            
            # Enviar el mensaje inicial del menú
            if isinstance(ctx_or_interaction, discord.Interaction) and not interaction.response.is_done():
                # Si es una interacción y aún no se ha respondido, usar response.send_message
                await response_func("Hola, soy el Bot de Neurocogniciones. ¿Cómo puedo ayudarte hoy?", view=view)
                # El mensaje de la vista se asigna después de la respuesta inicial
                view.message = await interaction.original_response()
            else:
                # Si es un comando o una interacción ya respondida, usar la función de envío normal
                view.message = await send_func("Hola, soy el Bot de Neurocogniciones. ¿Cómo puedo ayudarte hoy?", view=view)
                
            # Nota: La lógica para deshabilitar botones y eliminar el mensaje
            # en caso de timeout o finalización de la interacción se maneja
            # dentro de las clases de View (en views/main_menu.py).
                
        except Exception as e:
            if isinstance(ctx_or_interaction, commands.Context):
                await ctx.send(f"Ocurrió un error al iniciar la interacción: `{e}`")
            elif isinstance(ctx_or_interaction, discord.Interaction):
                # Si la interacción ya fue respondida, usar followup
                if interaction.response.is_done():
                    await interaction.followup.send(f"Ocurrió un error al iniciar la interacción: `{e}`", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Ocurrió un error al iniciar la interacción: `{e}`", ephemeral=True)
            print(f"Error en el comando iniciar: {e}")


    @commands.command(name='ayuda', help='Muestra información sobre los comandos disponibles y cómo usarlos.')
    async def ayuda(self, ctx):
        """
        Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos,
        adaptándose al tipo de canal.
        """
        channel_name = ctx.channel.name.lower()

        if "recursos-" in channel_name:
            help_message = (
                "📚 **Ayuda para la Búsqueda de Recursos:**\n\n"
                "Estás en un canal de búsqueda de recursos.\n"
                "• Utiliza los botones para seleccionar la dificultad, categoría y subcategoría de los recursos.\n"
                "• Si deseas reiniciar la búsqueda, usa el comando `&iniciar`.\n"
                "• Para cerrar este canal, usa el botón 'Cerrar Ticket' o el comando `&cerrar_ticket`."
            )
        elif "ayuda-tecnica-" in channel_name or "atencion-cliente-" in channel_name:
            help_message = (
                "ℹ️ **Ayuda en Canales de Soporte/Atención:**\n\n"
                "Estás en un canal de soporte o atención al cliente.\n"
                "• Por favor, describe tu problema a nuestro equipo.\n"
                "• Para cerrar este canal, usa el botón 'Cerrar Ticket' o el comando `&cerrar_ticket`.\n"
                "• El comando `&iniciar` solo funciona en canales públicos."
            )
        else:
            # Mensaje de ayuda para canales públicos
            help_message = get_help_message(self.bot.commands)
        
        await ctx.send(help_message)

    @commands.command(name='limpiar', help='Elimina un número específico de mensajes o todos los mensajes del canal.')
    @commands.has_permissions(manage_messages=True) # Requiere permiso para gestionar mensajes
    async def limpiar(self, ctx, cantidad_o_asterisco: str):
        """
        Elimina un número específico de mensajes del canal o todos los mensajes si se usa '*'.
        Uso: &limpiar <cantidad> o &limpiar *
        """
        if cantidad_o_asterisco == '*':
            try:
                # Elimina todos los mensajes del canal
                await ctx.channel.purge()
                await ctx.send(f"✅ Se eliminaron todos los mensajes del canal.", delete_after=3)
            except discord.Forbidden:
                await ctx.send("❌ No tengo los permisos necesarios para eliminar mensajes. Asegúrate de que el bot tenga el permiso 'Gestionar mensajes'.", delete_after=5)
            except Exception as e:
                await ctx.send(f"❌ Ocurrió un error al intentar limpiar mensajes: `{e}`", delete_after=5)
                print(f"Error en el comando limpiar (todos los mensajes): {e}")
        else:
            try:
                cantidad = int(cantidad_o_asterisco)
                if cantidad <= 0:
                    await ctx.send("❌ La cantidad de mensajes a eliminar debe ser un número positivo.", delete_after=5)
                    return

                # +1 para incluir el mensaje del comando 'limpiar'
                await ctx.channel.purge(limit=cantidad + 1)
                await ctx.send(f"✅ Se eliminaron {cantidad} mensajes del canal.", delete_after=3)
            except ValueError:
                await ctx.send("❌ Error: El argumento debe ser un número entero o '*'. Usa `&limpiar <cantidad>` o `&limpiar *`.", delete_after=5)
            except discord.Forbidden:
                await ctx.send("❌ No tengo los permisos necesarios para eliminar mensajes. Asegúrate de que el bot tenga el permiso 'Gestionar mensajes'.", delete_after=5)
            except Exception as e:
                await ctx.send(f"❌ Ocurrió un error al intentar limpiar mensajes: `{e}`", delete_after=5)
                print(f"Error en el comando limpiar (cantidad específica): {e}")

    @limpiar.error
    async def limpiar_error(self, ctx, error):
        """
        Manejador de errores para el comando 'limpiar'.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Error: Faltan argumentos. Usa `&limpiar <cantidad>` para eliminar un número específico de mensajes o `&limpiar *` para eliminar todos.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            # Este error ahora es manejado dentro de la función limpiar para 'ValueError'
            await ctx.send("❌ Error: El argumento debe ser un número entero o '*'. Usa `&limpiar <cantidad>` o `&limpiar *`.", delete_after=5)
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
