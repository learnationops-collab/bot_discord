# Archivo: cogs/common/events.py
# Este cog maneja los eventos principales del bot de Discord que son comunes a todas las áreas.

import discord
from discord.ext import commands
import config # Importa la configuración desde el módulo config
# from utils.helpers import get_help_message # Importa la función de ayuda si es necesaria para la bienvenida

class Events(commands.Cog):
    """
    Cog que maneja los eventos principales del bot de Discord, como la conexión y
    (opcionalmente) la bienvenida a nuevos miembros.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Se ejecuta cuando el bot ha iniciado sesión y está listo.
        Imprime el nombre y la ID del bot en la consola.
        """
        print(f'Bot conectado como {self.bot.user}')
        print(f'ID del bot: {self.bot.user.id}')
        print('------')

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     """
    #     Se dispara cuando un nuevo miembro se une al servidor.
    #     Actualmente comentado porque NUEVO_INGRESO_CHANNEL_ID no está en las variables de entorno.
    #     Si se necesita una funcionalidad de bienvenida, se debe reevaluar cómo se gestiona el canal.
    #     """
    #     if member.bot:
    #         # Ignorar si el miembro que se une es otro bot
    #         return

    #     # Si se decide reintroducir esta funcionalidad, se necesitaría una forma de obtener el canal
    #     # de bienvenida, ya sea a través de una nueva variable de entorno o un método diferente.
    #     # Por ejemplo, si se envía un DM:
    #     # welcome_message = (
    #     #     f"¡Bienvenido/a al servidor de Neurocogniciones, {member.mention}!\n"
    #     #     "Soy el Bot de Neurocogniciones y estoy aquí para ayudarte.\n\n"
    #     #     "Para comenzar, puedes usar el comando `&iniciar` para interactuar con nuestros menús de ayuda.\n\n"
    #     #     "Aquí tienes una guía rápida de cómo usarme:\n"
    #     # )
    #     # # Asegúrate de que get_help_message esté importado si lo usas
    #     # # help_content = get_help_message(self.bot.commands)
    #     # await member.send(welcome_message) # Envía un mensaje directo

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Eventos al bot.
    """
    await bot.add_cog(Events(bot))

