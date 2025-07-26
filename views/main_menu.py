# Archivo: views/main_menu.py
# Contiene las clases de vista (botones) para el menú principal del bot.

import discord
import asyncio
import config # Importa la configuración para acceder a user_conversations

# Ya no necesitamos importar DBManager aquí, ya que la lógica de recursos
# y sus interacciones se manejarán directamente en el cog de Resources.

class MainMenuView(discord.ui.View):
    """
    Vista del menú principal del bot, presentando opciones iniciales con botones.
    """
    def __init__(self, bot):
        super().__init__(timeout=180) # 3 minutos de timeout para la interacción
        self.bot = bot
        self.message = None # Para almacenar el mensaje

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción ha expirado. Puedes usar `&iniciar` para mostrarlo de nuevo.", view=self)
            except discord.NotFound:
                print("Mensaje de MainMenuView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de MainMenuView en timeout: {e}")

    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help", emoji="🛠️")
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'.
        Informa al usuario sobre cómo obtener ayuda técnica sin crear un canal.
        """
        await interaction.response.defer() # Deferir la respuesta para evitar "Unknown interaction"

        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Ayuda Técnica'.", view=self)

        # Enviar un mensaje al usuario indicando cómo proceder
        await interaction.followup.send(
            "Para obtener ayuda técnica, por favor, describe tu problema detalladamente en este chat. "
            "Un miembro de nuestro equipo de soporte será notificado y te asistirá lo antes posible.",
            ephemeral=False # Para que el mensaje sea visible para otros si es un canal público
        )
        print(f"Usuario {interaction.user.name} solicitó Ayuda Técnica.")


    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource", emoji="📚")
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'.
        Inicia el flujo de selección de recursos delegando al cog de Resources.
        """
        await interaction.response.defer() # Deferir la respuesta

        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Necesito un Recurso'. Iniciando el flujo de búsqueda...", view=self)

        # Llama al método del cog de Resources para iniciar la selección de dificultad
        resources_cog = self.bot.get_cog("Resources")
        if resources_cog:
            await resources_cog.send_difficulty_selection(interaction)
        else:
            await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado. Contacta a un administrador.", ephemeral=True)
        print(f"Usuario {interaction.user.name} solicitó un Recurso.")


    @discord.ui.button(label="Hablar con un Humano", style=discord.ButtonStyle.danger, custom_id="human_contact", emoji="🙋")
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'.
        Inicia un flujo de preguntas para recopilar información, gestionado por el cog de interacción humana.
        """
        await interaction.response.defer() # Deferir la interacción

        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Hablar con un Humano'. Iniciando conversación...", view=self)

        user_id = interaction.user.id
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] != 0:
            await interaction.followup.send("Ya tienes una conversación en curso para contactar a un humano. Por favor, completa esa conversación o espera.", ephemeral=True)
            return

        # Inicializa el estado de la conversación y envía la primera pregunta
        config.user_conversations[user_id] = {'state': 1, 'answers': [], 'channel_id': interaction.channel_id} # Guarda el ID del canal
        await interaction.followup.send(
            "Para poder ayudarte mejor y que un miembro de nuestro equipo te contacte, "
            "por favor, responde a la primera pregunta en este chat:\n\n"
            "**1. ¿Cuál es el problema principal que tienes?**",
            ephemeral=False
        )
        print(f"Usuario {interaction.user.name} inició conversación con un humano.")

# Este archivo no necesita una función `setup` porque solo contiene clases de vista,
# que serán instanciadas y utilizadas por los cogs o comandos del bot.
