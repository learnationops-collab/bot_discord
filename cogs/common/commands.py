# Archivo: cogs/common/commands.py
# Este cog contiene los comandos generales del bot de Discord que son comunes a todas las áreas.

import discord
from discord.ext import commands
# asyncio ya no es necesario si no hay sleep u otras operaciones asíncronas directas aquí

import config # Importa la configuración para acceder a user_conversations
from utils.helpers import get_help_message # Importa la función de ayuda
# Importar las vistas aquí. Asumimos que views/main_menu.py existirá.
from views.main_menu import MainMenuView # Solo se importa MainMenuView ahora

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

        # Si el comando se usa en un canal relacionado con "recursos" o "ayuda",
        # se informa que el comando es para iniciar una nueva interacción en canales públicos.
        if "recursos-" in channel_name or "ayuda-" in channel_name or "atencion-cliente-" in channel_name:
            message = (
                "Este comando está diseñado para usarse en canales públicos para iniciar una nueva interacción.\n"
                "Actualmente te encuentras en un canal de soporte/recursos. "
                "Si deseas iniciar una nueva interacción, por favor, usa `&iniciar` en un canal público."
            )
            if isinstance(ctx_or_interaction, discord.Interaction) and not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True)
            elif isinstance(ctx_or_interaction, discord.Interaction):
                await interaction.followup.send(message, ephemeral=True)
            else:
                await ctx.send(message)
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
        Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos,
        adaptándose al tipo de canal.
        """
        channel_name = ctx.channel.name.lower()

        # Mensaje de ayuda genérico para canales que no son públicos
        if "recursos-" in channel_name or "ayuda-" in channel_name or "atencion-cliente-" in channel_name:
            help_message = (
                "ℹ️ **Ayuda en Canales de Interacción Específica:**\n\n"
                "Estás en un canal de interacción específica (recursos, ayuda, etc.).\n"
                "• Por favor, continúa la interacción actual o usa `&iniciar` en un canal público para comenzar una nueva."
            )
        else:
            # Mensaje de ayuda para canales públicos
            help_message = get_help_message(self.bot.commands)

        await ctx.send(help_message)


# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Comandos al bot.
    """
    await bot.add_cog(Commands(bot))
