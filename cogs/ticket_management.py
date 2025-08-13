# Archivo: cogs/ticket_management.py

import discord
from discord.ext import commands
import asyncio
import config

class TicketManagement(commands.Cog):
    """
    Cog que maneja la creación y cierre de canales privados para reportes de bugs.
    """
    def __init__(self, bot):
        self.bot = bot

    async def create_bug_channel(self, member: discord.Member):
        """
        Crea un canal de texto privado para reportar un bug entre el usuario y el rol de Operaciones.
        """
        guild = member.guild
        category_id = config.GENERAL_CATEGORY_ID
        role_id = config.OPERECIONES_ROLES_ID

        if not guild or not category_id or not role_id:
            return None, "Error: Faltan variables de configuración para crear el canal de bug."

        category = discord.utils.get(guild.categories, id=category_id)
        if not category:
            return None, "Error: La categoría general no se encontró."

        try:
            # Obtener el rol de Operaciones y el objeto del bot en el servidor
            operaciones_role = guild.get_role(role_id)
            bot_member = guild.me
            if not operaciones_role:
                return None, "Error: El rol de Operaciones no se encontró."

            # Definir permisos para el canal privado
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False), # Ocultar para todos
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True), # Permitir al creador
                operaciones_role: discord.PermissionOverwrite(read_messages=True, send_messages=True), # Permitir a Operaciones
                bot_member: discord.PermissionOverwrite(read_messages=True, send_messages=True) # Permitir al bot leer y enviar mensajes
            }

            channel_name = f"bug-{member.name.lower().replace(' ', '-')}"
            new_channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites
            )

            return new_channel, f"Canal de bug creado: {new_channel.mention}"

        except discord.Forbidden:
            return None, "Error: No tengo permisos para crear canales o configurar permisos. Asegúrate de que el bot tiene el permiso 'manage_channels'."
        except Exception as e:
            print(f"Error al crear el canal de bug: {e}")
            return None, f"Error inesperado al crear el canal de bug: `{e}`"

    async def close_bug_channel(self, channel: discord.TextChannel):
        """
        Cierra un canal de bug.
        """
        try:
            await channel.delete()
        except discord.Forbidden:
            print(f"Error: No tengo permisos para eliminar el canal {channel.name}.")
        except Exception as e:
            print(f"Error inesperado al intentar cerrar el canal: {e}")


async def setup(bot):
    """
    Función de configuración para añadir el cog de TicketManagement al bot.
    """
    await bot.add_cog(TicketManagement(bot))
