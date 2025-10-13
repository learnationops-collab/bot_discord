# Archivo: cogs/commands.py

import discord
from discord.ext import commands
import asyncio # Necesario para el sleep en el comando limpiar

import config # Importa la configuración para acceder a user_conversations
from utils.helpers import get_help_message # Importa la función de ayuda
# Importar las vistas aquí. Asumimos que views/main_menu.py existirá.
# CloseTicketView ya no se importa aquí
from views.main_menu import MainMenuView, DifficultySelectionView 

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
            send_func = ctx.send
            response_func = ctx.send # Para compatibilidad, aunque no es una respuesta de interacción
        elif isinstance(ctx_or_interaction, discord.Interaction):
            interaction = ctx_or_interaction
            ctx = None # No hay Context object en este caso
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

        # Lógica para canales públicos (ahora todo sucede aquí)
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
                
            # Nota: La lógica para deshabilitar botones en caso de timeout o finalización de la interacción
            # se maneja dentro de las clases de View (en views/main_menu.py).
                
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
        Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos.
        Ahora es un mensaje de ayuda general.
        """
        # Mensaje de ayuda general, ya que todo sucede en el mismo canal
        help_message = get_help_message(self.bot.commands)
        
        await ctx.send(help_message)
    
    @commands.command(name='bug', help='Crea un canal privado para reportar un bug a Operaciones.')
    async def bug(self, ctx):
        """
        Comando para reportar un bug. Crea un canal privado con Operaciones y
        inicia un flujo de preguntas para recopilar la información.
        """
        # Obtenemos las instancias de los cogs necesarios
        ticket_cog = self.bot.get_cog('TicketManagement')
        bug_info_cog = self.bot.get_cog('BugInfo')

        if not ticket_cog or not bug_info_cog:
            await ctx.send("❌ Error: El módulo de gestión de tickets o de información de bugs no está disponible. Contacta a un administrador.")
            return

        # Llamamos a la función para crear el canal de bug
        channel, message = await ticket_cog.create_bug_channel(ctx.author)

        if channel:
            # Si el canal se creó exitosamente, enviamos la confirmación al canal original
            # y llamamos al flujo de preguntas en el nuevo cog.
            await ctx.send(f"✅ Ingresa al {message} y reporta el problema respondiendo las preguntas.")
            await bug_info_cog.start_bug_report_flow(channel, ctx.author)
        else:
            # Si hubo un error, enviamos el mensaje de error al canal original
            await ctx.send(f"❌ No se pudo crear el canal de bug. {message}")

    @commands.command(name='bug_resuelto', help='Cierra el canal de bug y envía un reporte de la solución.')
    async def bug_resuelto(self, ctx):
        """
        Comando para cerrar un canal de bug y enviar un reporte de la solución.
        """
        # Verificar si el comando se ejecuta en un canal de bugs.
        if not ctx.channel.name.startswith('bug-'):
            await ctx.send("❌ Este comando solo puede ser usado en un canal de bug. Si quieres crear uno, usa `&bug`.")
            return

        bug_info_cog = self.bot.get_cog('BugInfo')
        if not bug_info_cog:
            await ctx.send("❌ Error: El módulo de información de bugs no está disponible. Contacta a un administrador.")
            return

        await bug_info_cog.start_bug_solved_flow(ctx.channel, ctx.author)

    @commands.command(name='act_report', help='Genera y envía el reporte diario de actividad manualmente.')
    @commands.has_permissions(administrator=True) # Opcional: Restringir a administradores
    async def act_report(self, ctx):
        """
        Comando para generar manualmente el reporte de actividad diaria.
        """
        scheduled_task_cog = self.bot.get_cog('ScheduledMessageTask')
        if scheduled_task_cog:
            await ctx.send("Generando reporte de actividad...")
            await scheduled_task_cog.daily_activity_report()
            await ctx.send("Reporte generado.")
        else:
            await ctx.send("Error: El cog de tareas programadas no está cargado.")
    '''
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
                await ctx.send(f"✅ Se eliminaron todos los mensajes del canal.") # No eliminar el mensaje
            except discord.Forbidden:
                await ctx.send("❌ No tengo los permisos necesarios para eliminar mensajes. Asegúrate de que el bot tenga el permiso 'Gestionar mensajes'.") # No eliminar el mensaje
            except Exception as e:
                await ctx.send(f"❌ Ocurrió un error al intentar limpiar mensajes: `{e}`") # No eliminar el mensaje
                print(f"Error en el comando limpiar (todos los mensajes): {e}")
        else:
            try:
                cantidad = int(cantidad_o_asterisco)
                if cantidad <= 0:
                    await ctx.send("❌ La cantidad de mensajes a eliminar debe ser un número positivo.") # No eliminar el mensaje
                    return

                # +1 para incluir el mensaje del comando 'limpiar'
                await ctx.channel.purge(limit=cantidad + 1)
                await ctx.send(f"✅ Se eliminaron {cantidad} mensajes del canal.") # No eliminar el mensaje
            except ValueError:
                await ctx.send("❌ Error: El argumento debe ser un número entero o '*'. Usa `&limpiar <cantidad>` o `&limpiar *`.") # No eliminar el mensaje
            except discord.Forbidden:
                await ctx.send("❌ No tengo los permisos necesarios para eliminar mensajes. Asegúrate de que el bot tenga el permiso 'Gestionar mensajes'.") # No eliminar el mensaje
            except Exception as e:
                await ctx.send(f"❌ Ocurrió un error al intentar limpiar mensajes: `{e}`") # No eliminar el mensaje
                print(f"Error en el comando limpiar (cantidad específica): {e}")

    @limpiar.error
    async def limpiar_error(self, ctx, error):
        """
        Manejador de errores para el comando 'limpiar'.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Error: Faltan argumentos. Usa `&limpiar <cantidad>` para eliminar un número específico de mensajes o `&limpiar *` para eliminar todos.") # No eliminar el mensaje
        elif isinstance(error, commands.BadArgument):
            # Este error ahora es manejado dentro de la función limpiar para 'ValueError'
            await ctx.send("❌ Error: El argumento debe ser un número entero o '*'. Usa `&limpiar <cantidad>` o `&limpiar *`.") # No eliminar el mensaje
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes los permisos necesarios para usar este comando. Necesitas el permiso 'Gestionar mensajes'.") # No eliminar el mensaje
        else:
            await ctx.send(f"❌ Ocurrió un error inesperado con el comando limpiar: `{error}`") # No eliminar el mensaje
            print(f"Error inesperado en limpiar_error: {error}")
    '''

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Comandos al bot.
    """
    await bot.add_cog(Commands(bot))