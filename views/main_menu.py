# Archivo: views/main_menu.py

import discord
import asyncio
import config # Importa la configuración para acceder a user_conversations

class CloseTicketView(discord.ui.View):
    """
    Vista que contiene un botón para cerrar un canal de ticket.
    """
    def __init__(self, channel_to_close: discord.TextChannel):
        super().__init__(timeout=300) # 5 minutos de timeout para el botón
        self.channel_to_close = channel_to_close

    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Cierra el canal de soporte actual cuando se hace clic en el botón.
        """
        await interaction.response.send_message("Cerrando este canal de soporte en 5 segundos...", ephemeral=False)
        # Deshabilita el botón inmediatamente para evitar clics múltiples
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        await asyncio.sleep(5) # Espera 5 segundos antes de eliminar el canal
        try:
            await self.channel_to_close.delete()
        except discord.Forbidden:
            await interaction.followup.send("❌ No tengo permisos para eliminar este canal. Por favor, contacta a un administrador.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error al intentar cerrar el canal: `{e}`", ephemeral=True)
            print(f"Error al cerrar el canal {self.channel_to_close.name}: {e}")

class MainMenuView(discord.ui.View):
    """
    Vista del menú principal del bot, presentando opciones iniciales con botones.
    """
    def __init__(self, bot):
        super().__init__(timeout=180) # 3 minutos de timeout para la interacción
        self.bot = bot
        self.message = None # Para almacenar el mensaje y poder editarlo en caso de timeout

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones y edita el mensaje original.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(content="La interacción ha expirado. Si necesitas ayuda, usa `&iniciar` de nuevo.", view=self)
            except discord.NotFound:
                print("Mensaje de MainMenuView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de MainMenuView en timeout: {e}")

    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help")
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'.
        Delega la creación del ticket al cog de `TicketManagement`.
        """
        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        ticket_cog = self.bot.get_cog("TicketManagement")
        if ticket_cog:
            # Llama a la función de creación de ticket del cog
            await ticket_cog.create_technical_ticket(interaction)
        else:
            await interaction.response.send_message("❌ Error interno: El módulo de gestión de tickets no está cargado. Contacta a un administrador.", ephemeral=True)

    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource")
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'.
        Informa al usuario sobre el comando para buscar recursos.
        """
        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            "Entendido. Para ayudarte a encontrar el recurso que necesitas, "
            "por favor, usa el comando `&recurso` seguido de tu problema principal "
            "(ej. `&recurso aprendizaje` o `&recurso autogestión`). "
            "También puedes usar `&recurso ayuda` para ver las categorías disponibles.",
            ephemeral=False
        )
        # La lógica detallada de selección de recursos se implementará en cogs/resources.py

    @discord.ui.button(label="Hablar con un Humano", style=discord.ButtonStyle.danger, custom_id="human_contact")
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'.
        Inicia un flujo de preguntas para recopilar información, gestionado por el cog de interacción humana.
        """
        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        user_id = interaction.user.id
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] != 0:
            await interaction.response.send_message("Ya tienes una conversación en curso para contactar a un humano. Por favor, completa esa conversación o espera.", ephemeral=True)
            return

        # Inicializa el estado de la conversación en el diccionario de configuración
        config.user_conversations[user_id] = {'state': 1, 'answers': [], 'channel_id': None}
        await interaction.response.send_message(
            "Para poder ayudarte mejor y que un miembro de nuestro equipo te contacte, "
            "por favor, responde a la primera pregunta en este chat:\n\n"
            "**1. ¿Cuál es el problema principal que tienes?**",
            ephemeral=False
        )

# Este archivo no necesita una función `setup` porque solo contiene clases de vista,
# que serán instanciadas y utilizadas por los cogs o comandos del bot.
