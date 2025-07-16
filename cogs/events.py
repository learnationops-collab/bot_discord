# Archivo: cogs/events.py

import discord
from discord.ext import commands
import config # Importa la configuración desde el módulo config
from utils.helpers import get_help_message # Importa la función de ayuda

class Events(commands.Cog):
    """
    Cog que maneja los eventos principales del bot de Discord.
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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Se dispara cuando un nuevo miembro se une al servidor.
        Envía un mensaje de bienvenida y las indicaciones de uso del bot
        si el miembro se une al canal de nuevo ingreso configurado.
        """
        if member.bot:
            # Ignorar si el miembro que se une es otro bot
            return

        # Validar que el ID del canal de nuevo ingreso esté configurado
        if config.NUEVO_INGRESO_CHANNEL_ID is None:
            print("Advertencia: NUEVO_INGRESO_CHANNEL_ID no está definido en .env o no es válido. La bienvenida automática no funcionará.")
            return

        # Obtener el canal de nuevo ingreso usando el ID de configuración
        channel = self.bot.get_channel(config.NUEVO_INGRESO_CHANNEL_ID)
        if channel:
            welcome_message = (
                f"¡Bienvenido/a al servidor de Neurocogniciones, {member.mention}!\n"
                "Soy el Bot de Neurocogniciones y estoy aquí para ayudarte.\n\n"
                "Para comenzar, puedes usar el comando `&iniciar` para interactuar con nuestros menús de ayuda.\n\n"
                "Aquí tienes una guía rápida de cómo usarme:\n"
            )
            # Usar la función get_help_message del módulo helpers
            help_content = get_help_message(self.bot.commands)
            await channel.send(welcome_message + help_content)
        else:
            print(f"Advertencia: No se encontró el canal con ID {config.NUEVO_INGRESO_CHANNEL_ID}. La bienvenida automática no funcionará.")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Eventos al bot.
    """
    await bot.add_cog(Events(bot))
