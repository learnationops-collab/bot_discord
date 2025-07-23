# Archivo: views/main_menu.py

import discord
import asyncio
import config # Importa la configuración para acceder a user_conversations
# Importamos el DBManager para interactuar con la base de datos de recursos
from database.db_manager import DBManager

# Instancia global del DBManager para ser utilizada por las vistas
db_manager = DBManager()

# La clase CloseTicketView se elimina ya que no se crearán nuevos canales de ticket.

class ResourceDisplayView(discord.ui.View):
    """
    Vista para mostrar los recursos finales encontrados.
    """
    def __init__(self, resources: list, current_difficulty: str, current_category: str, current_subcategory: str = None):
        super().__init__(timeout=180) # 3 minutos de timeout
        self.resources = resources
        self.current_difficulty = current_difficulty
        self.current_category = current_category
        self.current_subcategory = current_subcategory
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
                await self.message.edit(content="La interacción de recursos ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de ResourceDisplayView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de ResourceDisplayView en timeout: {e}")

    async def send_resources(self, interaction: discord.Interaction):
        """
        Envía el mensaje con los recursos encontrados.
        """
        try:
            if self.resources:
                response_message = f"📚 **Recursos encontrados para '{self.current_category}'"
                if self.current_subcategory:
                    response_message += f" (Subcategoría: '{self.current_subcategory}')"
                response_message += f" (Dificultad: '{self.current_difficulty}'):**\n\n"

                for i, res in enumerate(self.resources):
                    response_message += (
                        f"**{i+1}. {res['resource_name']}**\n"
                        f"   Enlace: <{res['link']}>\n"
                        f"   Categoría: `{res['category']}`\n"
                    )
                    if res['subcategory']:
                        response_message += f"   Subcategoría: `{res['subcategory']}`\n"
                    response_message += f"   Dificultad: `{res['difficulty']}`\n\n"
                
                # Dividir el mensaje si es demasiado largo para Discord
                if len(response_message) > 2000:
                    self.message = await interaction.followup.send(response_message[:1990] + "...\n(Mensaje truncado. Por favor, refina tu búsqueda.)", view=self)
                else:
                    self.message = await interaction.followup.send(response_message, view=self)
            else:
                self.message = await interaction.followup.send(
                    f"No se encontraron recursos para la dificultad `{self.current_difficulty}`, "
                    f"categoría `{self.current_category}`"
                    f"{f' y subcategoría `{self.current_subcategory}`' if self.current_subcategory else ''}. "
                    "Intenta con otra selección.", ephemeral=False, view=self
                )
        except Exception as e:
            print(f"Error en send_resources: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al mostrar los recursos. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en send_resources: {e_followup}")


class SubcategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una subcategoría de recursos.
    """
    def __init__(self, bot, difficulty: str, category: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.difficulty = difficulty
        self.category = category
        self.message = None

        self._add_subcategory_buttons()

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
                await self.message.edit(content="La interacción de selección de subcategoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de SubcategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de SubcategorySelectionView en timeout: {e}")

    def _add_subcategory_buttons(self):
        """Añade botones para cada subcategoría disponible."""
        try:
            if not db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para obtener subcategorías.")
                self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
                return

            subcategories = db_manager.get_distinct_subcategories(difficulty=self.difficulty, category=self.category)
            if not subcategories:
                self.add_item(discord.ui.Button(label="No hay subcategorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
                return

            for subcategory in subcategories:
                # Discord tiene un límite de 25 botones por vista
                if len(self.children) < 25:
                    self.add_item(discord.ui.Button(label=subcategory.title(), style=discord.ButtonStyle.secondary, custom_id=f"subcat_{subcategory}"))
                else:
                    break # Evitar añadir más de 25 botones
        except Exception as e:
            print(f"Error en _add_subcategory_buttons: {e}")
            self.add_item(discord.ui.Button(label="Error al cargar subcategorías", style=discord.ButtonStyle.red, disabled=True))


    @discord.ui.button(label="Ver todos los recursos de esta categoría", style=discord.ButtonStyle.primary, custom_id="view_all_in_category", row=4)
    async def view_all_in_category_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción para ver todos los recursos de la categoría seleccionada
        sin filtrar por subcategoría.
        """
        try:
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            resources = db_manager.get_resources(category=self.category, difficulty=self.difficulty)
            
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content=f"Mostrando recursos para '{self.category}' (Dificultad: '{self.difficulty}').", view=self)

            resource_view = ResourceDisplayView(resources, self.difficulty, self.category)
            await resource_view.send_resources(interaction)
        except Exception as e:
            print(f"Error en view_all_in_category_button: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al intentar ver todos los recursos de esta categoría. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en view_all_in_category_button: {e_followup}")


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de subcategoría se maneja aquí dinámicamente.
        """
        try:
            if interaction.data and interaction.data.get("custom_id", "").startswith("subcat_"):
                selected_subcategory = interaction.data["custom_id"].replace("subcat_", "")
                await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
                resources = db_manager.get_resources(
                    category=self.category,
                    subcategory=selected_subcategory,
                    difficulty=self.difficulty
                )
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(content=f"Has seleccionado la subcategoría: **{selected_subcategory.title()}** (Categoría: {self.category.title()}, Dificultad: {self.difficulty.title()}).", view=self)
                
                resource_view = ResourceDisplayView(resources, self.difficulty, self.category, selected_subcategory)
                await resource_view.send_resources(interaction)
                return False # No continuar con otros botones en esta interacción
            return True # Permitir que otros botones se procesen
        except Exception as e:
            print(f"Error en SubcategorySelectionView.interaction_check: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu selección de subcategoría. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en SubcategorySelectionView.interaction_check: {e_followup}")
            return False # Fallar la verificación de interacción si hay un error


class CategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una categoría de recursos.
    """
    def __init__(self, bot, difficulty: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.difficulty = difficulty
        self.message = None

        self._add_category_buttons()

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
                await self.message.edit(content="La interacción de selección de categoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de CategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de CategorySelectionView en timeout: {e}")

    def _add_category_buttons(self):
        """Añade botones para cada categoría disponible."""
        try:
            if not db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para obtener categorías.")
                self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
                return

            categories = db_manager.get_distinct_categories(difficulty=self.difficulty)
            if not categories:
                self.add_item(discord.ui.Button(label="No hay categorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
                return

            for category in categories:
                if len(self.children) < 25: # Discord tiene un límite de 25 botones por vista
                    self.add_item(discord.ui.Button(label=category.title(), style=discord.ButtonStyle.primary, custom_id=f"cat_{category}"))
                else:
                    break
        except Exception as e:
            print(f"Error en _add_category_buttons: {e}")
            self.add_item(discord.ui.Button(label="Error al cargar categorías", style=discord.ButtonStyle.red, disabled=True))


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de categoría se maneja aquí dinámicamente.
        """
        try:
            if interaction.data and interaction.data.get("custom_id", "").startswith("cat_"):
                selected_category = interaction.data["custom_id"].replace("cat_", "")
                await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
                
                # Obtener subcategorías para la dificultad y categoría seleccionadas
                subcategories = db_manager.get_distinct_subcategories(difficulty=self.difficulty, category=selected_category)
                
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(content=f"Has seleccionado la categoría: **{selected_category.title()}** (Dificultad: {self.difficulty.title()}).", view=self)

                if subcategories:
                    subcategory_view = SubcategorySelectionView(self.bot, self.difficulty, selected_category)
                    await interaction.followup.send("Por favor, selecciona una subcategoría o ver todos:", view=subcategory_view)
                    subcategory_view.message = interaction.message # Asignar el mensaje para timeout
                else:
                    # Si no hay subcategorías, ir directamente a mostrar recursos de la categoría
                    resources = db_manager.get_resources(category=selected_category, difficulty=self.difficulty)
                    resource_view = ResourceDisplayView(resources, self.difficulty, selected_category)
                    await resource_view.send_resources(interaction)
                return False # No continuar con otros botones en esta interacción
            return True # Permitir que otros botones se procesen
        except Exception as e:
            print(f"Error en CategorySelectionView.interaction_check: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu selección de categoría. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en CategorySelectionView.interaction_check: {e_followup}")
            return False # Fallar la verificación de interacción si hay un error


class DifficultySelectionView(discord.ui.View):
    """
    Vista para seleccionar la dificultad de los recursos.
    """
    def __init__(self, bot):
        super().__init__(timeout=180) # 3 minutos de timeout
        self.bot = bot
        self.message = None # Para almacenar el mensaje

        self._add_difficulty_buttons()

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
                await self.message.edit(content="La interacción de selección de dificultad ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de DifficultySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de DifficultySelectionView en timeout: {e}")

    def _add_difficulty_buttons(self):
        """Añade botones para cada dificultad disponible."""
        try:
            if not db_manager.connect():
                print("Error: No se pudo conectar a la base de datos para obtener dificultades. Asegúrate de que la DB esté corriendo y las credenciales sean correctas.")
                self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
                return

            difficulties = db_manager.get_distinct_difficulties()
            print(f"Dificultades obtenidas de la DB: {difficulties}") # DEBUG: Para ver qué devuelve la DB
            
            if not difficulties:
                self.add_item(discord.ui.Button(label="No hay dificultades disponibles", style=discord.ButtonStyle.grey, disabled=True))
                return

            for difficulty in difficulties:
                # Discord tiene un límite de 25 botones por vista
                if len(self.children) < 25:
                    self.add_item(discord.ui.Button(label=difficulty.title(), style=discord.ButtonStyle.primary, custom_id=f"diff_{difficulty}"))
                else:
                    break # Evitar añadir más de 25 botones
        except Exception as e:
            print(f"Error en _add_difficulty_buttons: {e}")
            self.add_item(discord.ui.Button(label="Error al cargar dificultades", style=discord.ButtonStyle.red, disabled=True))


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de dificultad se maneja aquí dinámicamente.
        """
        try:
            if interaction.data and interaction.data.get("custom_id", "").startswith("diff_"):
                selected_difficulty = interaction.data["custom_id"].replace("diff_", "")
                await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
                
                # Deshabilitar los botones de esta vista
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(content=f"Has seleccionado la dificultad: **{selected_difficulty.title()}**.", view=self)

                # Crear y enviar la siguiente vista de selección de categoría
                category_view = CategorySelectionView(self.bot, selected_difficulty)
                await interaction.followup.send("Por favor, selecciona una categoría:", view=category_view)
                category_view.message = interaction.message # Asignar el mensaje para timeout
                return False # No continuar con otros botones en esta interacción

            return True # Permitir que otros botones se procesen
        except Exception as e:
            print(f"Error en DifficultySelectionView.interaction_check: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu selección de dificultad. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en DifficultySelectionView.interaction_check: {e_followup}")
            return False # Fallar la verificación de interacción si hay un error


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

    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help", emoji="🛠️",
                       row=0)
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'.
        Inicia el flujo de ayuda técnica directamente en el canal actual.
        """
        try:
            await interaction.response.defer() # Deferir la interacción para que no expire
            
            # Deshabilitar todos los botones de este mensaje
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content="Has seleccionado 'Ayuda Técnica'. Por favor, describe tu problema técnico aquí y un miembro de nuestro equipo te ayudará.", view=self)
            
            # Obtener el rol de soporte técnico y mencionarlo
            if config.SOPORTE_TECNICO_ROLE_ID:
                support_role = interaction.guild.get_role(config.SOPORTE_TECNICO_ROLE_ID)
                if support_role:
                    await interaction.followup.send(f"{support_role.mention}, un usuario necesita ayuda técnica en este canal. Por favor, revisen la conversación.")
                else:
                    await interaction.followup.send("❌ Error: No se encontró el rol de Soporte Técnico con el ID configurado. Contacta a un administrador.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Error de configuración: El ID del rol de Soporte Técnico no está definido. Contacta a un administrador.", ephemeral=True)
        except Exception as e:
            print(f"Error en technical_help_button: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu solicitud de ayuda técnica. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en technical_help_button: {e_followup}")


    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource", emoji="📚",
                       row=0)
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'.
        Inicia el flujo de selección de recursos en el canal actual.
        """
        try:
            await interaction.response.defer() # Deferir la interacción para que no expire

            # Deshabilitar los botones del menú principal para esta interacción
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content="Has seleccionado 'Necesito un Recurso'.", view=self)
            
            # Iniciar el flujo de selección de recursos en el mismo canal
            difficulty_view = DifficultySelectionView(self.bot)
            await interaction.followup.send("Por favor, selecciona la dificultad del recurso:", view=difficulty_view)
            difficulty_view.message = interaction.message # Asignar el mensaje para timeout
        except Exception as e:
            print(f"Error en request_resource_button: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu solicitud de recursos. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en request_resource_button: {e_followup}")


    @discord.ui.button(label="Hablar con un Humano", style=discord.ButtonStyle.danger, custom_id="human_contact", emoji="❓", # Cambiado de "🙋" a "❓"
                       row=0)
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'.
        Inicia un flujo de preguntas para recopilar información, gestionado por el cog de interacción humana,
        todo en el canal actual.
        """
        try:
            await interaction.response.defer() # Deferir la interacción para que no expire

            # Deshabilitar los botones del menú principal para esta interacción
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content="Has seleccionado 'Hablar con un Humano'.", view=self)

            user_id = interaction.user.id
            if user_id in config.user_conversations and config.user_conversations[user_id]['state'] != 0:
                await interaction.followup.send("Ya tienes una conversación en curso para contactar a un humano. Por favor, completa esa conversación o espera.", ephemeral=True)
                return

            # Inicializa el estado de la conversación y envía la primera pregunta
            config.user_conversations[user_id] = {'state': 1, 'answers': [], 'channel_id': interaction.channel.id} # Guardar el ID del canal actual
            await interaction.followup.send(
                "Para poder ayudarte mejor y que un miembro de nuestro equipo te contacte, "
                "por favor, responde a la primera pregunta en este chat:\n\n"
                "**1. ¿Cuál es el problema principal que tienes?**",
                ephemeral=False
            )
        except Exception as e:
            print(f"Error en human_contact_button: {e}")
            try:
                await interaction.followup.send("❌ Ocurrió un error al procesar tu solicitud para hablar con un humano. Intenta de nuevo más tarde.", ephemeral=True)
            except Exception as e_followup:
                print(f"Error al enviar followup en human_contact_button: {e_followup}")

# Este archivo no necesita una función `setup` porque solo contiene clases de vista,
# que serán instanciadas y utilizadas por los cogs o comandos del bot.
