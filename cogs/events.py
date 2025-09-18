# Archivo: cogs/events.py

import discord
from discord.ext import commands
import config # Importa la configuración desde el módulo config

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
        Crea un nuevo canal privado para el miembro y le da la bienvenida.
        """
        if member.bot:
            return

        guild = member.guild
        category_id = config.NUEVO_INGRESO_CATEGORY_ID
        role_id = config.ATENCION_AL_CLIENTE_ROLE_ID

        if not all([category_id, role_id]):
            print("Advertencia: La categoría de nuevo ingreso o el rol de atención al cliente no están configurados.")
            return

        category = guild.get_channel(category_id)
        atencion_role = guild.get_role(role_id)

        if not category or not atencion_role:
            print("Advertencia: No se pudo encontrar la categoría o el rol especificado.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            atencion_role: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"bienvenida-{member.name}"
        try:
            new_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            welcome_message = (
                f"¡Bienvenido/a al servidor de Neurocogniciones, {member.mention}!\n"
                "Soy el Bot de Neurocogniciones y estoy aquí para ayudarte."
            )
            await new_channel.send(welcome_message)
        except discord.Forbidden as e:
            print(f"Error de permisos al crear o enviar mensajes en el canal de bienvenida: {e}")
        except Exception as e:
            print(f"Ha ocurrido un error al crear el canal de bienvenida: {e}")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Eventos al bot.
    """
    await bot.add_cog(Events(bot))
