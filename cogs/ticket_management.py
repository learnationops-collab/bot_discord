# Archivo: cogs/ticket_management.py

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a IDs de roles y categorías
# Importamos CloseTicketView desde views.main_menu.py.
# Asegúrate de que esta clase esté definida en ese archivo cuando lo crees.
from views.main_menu import CloseTicketView, DifficultySelectionView # Importar DifficultySelectionView para el flujo de recursos

class TicketManagement(commands.Cog):
    """
    Cog que maneja la creación y gestión de tickets de soporte técnico y canales de búsqueda de recursos.
    """
    def __init__(self, bot):
        self.bot = bot

    async def create_technical_ticket(self, interaction: discord.Interaction):
        """
        Crea un canal privado de ayuda técnica para el usuario que interactúa.
        Esta función está diseñada para ser llamada por un botón de una vista
        (por ejemplo, desde MainMenuView).
        Se asume que la interacción ya fue diferida por la vista que la llamó.

        Args:
            interaction (discord.Interaction): La interacción del botón que activó esta función.
        """
        user = interaction.user
        guild = interaction.guild

        # Validar que el ID del rol de soporte técnico esté configurado
        if config.SOPORTE_TECNICO_ROLE_ID is None:
            await interaction.followup.send("❌ Error de configuración: El ID del rol de Soporte Técnico no está definido en .env o no es válido. Contacta a un administrador.", ephemeral=True)
            return
        support_role = guild.get_role(config.SOPORTE_TECNICO_ROLE_ID)
        if not support_role:
            await interaction.followup.send("❌ Error: No se encontró el rol de Soporte Técnico con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.", ephemeral=True)
            return

        # Generar el nombre esperado del canal (debe ser consistente)
        expected_channel_name_prefix = f"ayuda-tecnica-{user.name.lower().replace(' ', '-')}"
        
        # *** NUEVA LÓGICA: Verificar si el canal ya existe para el usuario ***
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.category_id == config.AYUDA_TECNICA_CATEGORY_ID:
                # Una forma más robusta de verificar si el canal pertenece al usuario
                # Podríamos buscar el ID del usuario en el nombre del canal o en los permisos
                # Para simplificar, buscamos el prefijo y si el usuario tiene permisos de lectura
                if expected_channel_name_prefix in channel.name.lower():
                    # Verificar si el usuario tiene permiso explícito para leer mensajes en este canal
                    if channel.permissions_for(user).read_messages:
                        await interaction.followup.send(f"Ya tienes un canal de ayuda técnica abierto: {channel.mention}. Por favor, usa ese canal para tu consulta.", ephemeral=True)
                        return # Salir de la función si el canal ya existe

        # Definir permisos para el nuevo canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Nadie puede ver el canal por defecto
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El usuario puede ver y escribir
            self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El bot puede ver y escribir
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True) # El rol de soporte puede ver y escribir
        }

        try:
            # Validar que el ID de la categoría de ayuda técnica esté configurado
            if config.AYUDA_TECNICA_CATEGORY_ID is None:
                await interaction.followup.send("❌ Error de configuración: El ID de la categoría de Ayuda Técnica no está definido en .env o no es válido. Contacta a un administrador.", ephemeral=True)
                return
            category = guild.get_channel(config.AYUDA_TECNICA_CATEGORY_ID)
            if not category:
                await interaction.followup.send("❌ Error: No se encontró la categoría de Ayuda Técnica con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.", ephemeral=True)
                return

            # Crear el nombre del canal de forma única (añadiendo el ID del usuario para mayor unicidad)
            channel_name = f"{expected_channel_name_prefix}-{user.id}"
            new_channel = await category.create_text_channel(channel_name, overwrites=overwrites)

            # Usar followup.send ya que la interacción ya fue respondida por MainMenuView
            await interaction.followup.send(
                f"¡Hola {user.mention}! He creado un canal privado para tu soporte técnico: {new_channel.mention}\n"
                "Por favor, dirígete a ese canal para describir tu problema. "
                "Un miembro de nuestro equipo de soporte técnico te ayudará pronto.\n\n"
                "Para salir de este canal y cerrarlo cuando tu problema esté resuelto, usa el botón 'Cerrar Ticket' o el comando `&cerrar_ticket`.",
                ephemeral=False # Para que todos vean que se creó el ticket
            )

            # Enviar mensaje de bienvenida e instrucciones en el nuevo canal privado
            welcome_message_in_channel = (
                f"¡Bienvenido/a a tu canal de soporte técnico, {user.mention}!\n"
                "Aquí puedes describir tu problema técnico en detalle. Por favor, sé lo más específico posible.\n"
                "Un miembro del equipo de soporte revisará tu caso.\n\n"
                "**Indicaciones de uso:**\n"
                "• Describe tu problema claramente.\n"
                "• Menciona los pasos que ya has intentado para solucionarlo.\n"
                "• Si es posible, adjunta capturas de pantalla o videos.\n\n"
                "Cuando tu problema esté resuelto o desees cerrar este canal, por favor, usa el botón de abajo:\n"
            )
            # Se pasa la instancia del canal al CloseTicketView para que pueda cerrarlo
            await new_channel.send(welcome_message_in_channel, view=CloseTicketView(new_channel))

        except discord.Forbidden:
            # Si el bot no tiene permisos para crear canales en la categoría especificada
            await interaction.followup.send("❌ No tengo los permisos necesarios para crear canales. Por favor, asegúrate de que el bot tenga el permiso 'Gestionar Canales' en la categoría de ayuda técnica.", ephemeral=True)
        except Exception as e:
            # Captura cualquier otro error inesperado durante la creación del canal
            await interaction.followup.send(f"❌ Ocurrió un error al crear el canal de ayuda técnica: `{e}`", ephemeral=True)
            print(f"Error al crear canal de ayuda técnica: {e}")

    async def create_resource_search_channel(self, interaction: discord.Interaction):
        """
        Crea un canal privado para el usuario que desea buscar recursos.
        Este canal guiará al usuario a través de la selección de dificultad, categoría y subcategoría.
        """
        user = interaction.user
        guild = interaction.guild

        # Generar el nombre esperado del canal (debe ser consistente)
        expected_channel_name_prefix = f"recursos-{user.name.lower().replace(' ', '-')}"

        # *** NUEVA LÓGICA: Verificar si el canal ya existe para el usuario ***
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.category_id == config.RESOURCES_CATEGORY_ID:
                if expected_channel_name_prefix in channel.name.lower():
                    if channel.permissions_for(user).read_messages:
                        await interaction.followup.send(f"Ya tienes un canal de búsqueda de recursos abierto: {channel.mention}. Por favor, usa ese canal para continuar tu búsqueda.", ephemeral=True)
                        return # Salir de la función si el canal ya existe

        # Definir permisos para el nuevo canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Nadie puede ver el canal por defecto
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El usuario puede ver y escribir
            self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El bot puede ver y escribir
            # No se asigna rol de soporte aquí, ya que es un canal de autoservicio
        }

        try:
            # Validar que el ID de la categoría de recursos esté configurado
            if config.RESOURCES_CATEGORY_ID is None:
                await interaction.followup.send("❌ Error de configuración: El ID de la categoría de Recursos no está definido en .env o no es válido. Contacta a un administrador.", ephemeral=True)
                return
            category = guild.get_channel(config.RESOURCES_CATEGORY_ID)
            if not category:
                await interaction.followup.send("❌ Error: No se encontró la categoría de Recursos con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.", ephemeral=True)
                return

            # Crear el nombre del canal de forma única (añadiendo el ID del usuario para mayor unicidad)
            channel_name = f"{expected_channel_name_prefix}-{user.id}"
            new_channel = await category.create_text_channel(channel_name, overwrites=overwrites)

            await interaction.followup.send(
                f"¡Hola {user.mention}! He creado un canal privado para ayudarte a encontrar recursos: {new_channel.mention}\n"
                "Por favor, dirígete a ese canal para continuar con la búsqueda.",
                ephemeral=False
            )

            # Iniciar el flujo de selección de recursos en el nuevo canal
            difficulty_view = DifficultySelectionView(self.bot)
            await new_channel.send("Por favor, selecciona la dificultad del recurso:", view=difficulty_view)
            difficulty_view.message = new_channel.last_message # Asignar el mensaje para timeout

            # Enviar el botón para cerrar el ticket en el nuevo canal
            await new_channel.send("Cuando hayas terminado de buscar recursos, puedes cerrar este canal:", view=CloseTicketView(new_channel))

        except discord.Forbidden:
            await interaction.followup.send("❌ No tengo los permisos necesarios para crear canales de recursos. Por favor, asegúrate de que el bot tenga el permiso 'Gestionar Canales' en la categoría de recursos.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error al crear el canal de búsqueda de recursos: `{e}`", ephemeral=True)
            print(f"Error al crear canal de búsqueda de recursos: {e}")


    @commands.command(name='cerrar_ticket', help='Cierra el canal de soporte actual (solo en canales de ticket).')
    async def cerrar_ticket(self, ctx):
        """
        Comando para cerrar un canal de soporte.
        Solo funciona si el comando se usa dentro de un canal de soporte creado por el bot.
        Verifica el nombre del canal para determinar si es un canal de ticket.
        """
        channel_name = ctx.channel.name.lower()
        # Verificación simple basada en el prefijo del nombre del canal
        if "ayuda-tecnica-" in channel_name or "atencion-cliente-" in channel_name or "recursos-" in channel_name:
            # Primero, intenta enviar un mensaje de confirmación
            try:
                await ctx.send("Cerrando este canal de soporte en 5 segundos...")
            except discord.errors.NotFound:
                # Si el canal ya no existe, simplemente retorna
                print(f"Advertencia: El canal {ctx.channel.name} ya no existe al intentar enviar mensaje de cierre.")
                return
            except Exception as e:
                print(f"Error al enviar mensaje de cierre en el canal {ctx.channel.name}: {e}")
                # Si no se puede enviar el mensaje, aún se puede intentar eliminar el canal
                pass # Continuar para intentar eliminar el canal

            await asyncio.sleep(5) # Espera antes de eliminar el canal
            try:
                await ctx.channel.delete() # Intenta eliminar el canal
            except discord.Forbidden:
                # Si el bot no tiene permisos para eliminar el canal
                try:
                    await ctx.send("❌ No tengo permisos para eliminar este canal. Por favor, contacta a un administrador.")
                except discord.errors.NotFound:
                    print(f"Advertencia: El canal {ctx.channel.name} ya no existe al intentar enviar mensaje de error de permisos.")
                except Exception as e_send:
                    print(f"Error al enviar mensaje de error de permisos en el canal {ctx.channel.name}: {e_send}")
            except discord.errors.NotFound:
                # Si el canal ya fue eliminado por otra entidad (ej. un usuario, otro bot)
                print(f"Advertencia: El canal {ctx.channel.name} ya fue eliminado antes de que el bot pudiera hacerlo.")
            except Exception as e:
                # Captura cualquier otro error inesperado durante la eliminación del canal
                try:
                    await ctx.send(f"❌ Ocurrió un error al intentar cerrar el canal: `{e}`")
                except discord.errors.NotFound:
                    print(f"Advertencia: El canal {ctx.channel.name} ya no existe al intentar enviar mensaje de error general.")
                except Exception as e_send:
                    print(f"Error al enviar mensaje de error general en el canal {ctx.channel.name}: {e_send}")
        else:
            # Si el comando se usa en un canal que no es de ticket
            try:
                await ctx.send("Este comando solo puede usarse en un canal de soporte técnico, de atención al cliente o de búsqueda de recursos.", ephemeral=True)
            except discord.errors.NotFound:
                print(f"Advertencia: El canal {ctx.channel.name} ya no existe al intentar enviar mensaje de uso incorrecto.")
            except Exception as e:
                print(f"Error al enviar mensaje de uso incorrecto en el canal {ctx.channel.name}: {e}")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de TicketManagement al bot.
    """
    await bot.add_cog(TicketManagement(bot))
