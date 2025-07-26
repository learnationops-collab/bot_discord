# Archivo: views/resource_views.py
# Contiene las clases de vista (botones y selectores) para el flujo de selección de recursos.

import discord
import asyncio

# Importamos DBManager aquí para que las vistas puedan obtener los datos directamente
# Esto es aceptable para vistas que necesitan datos para construir sus opciones.
from database.db_manager import DBManager

# Instancia global del DBManager para ser utilizada por las vistas
# NOTA: En una aplicación de gran escala, podrías considerar pasar el db_manager
# a las vistas a través de su constructor si necesitas un control más granular
# sobre la conexión, pero para este caso, una instancia global es suficiente.
db_manager = DBManager()

class ResourceDisplayView(discord.ui.View):
    """
    Vista para mostrar los recursos finales encontrados y un botón para volver al menú principal.
    """
    def __init__(self, bot, resources: list, current_difficulty: str, current_category: str, current_subcategory: str = None):
        super().__init__(timeout=300) # 5 minutos de timeout
        self.bot = bot
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
                await self.message.edit(content="La interacción de recursos ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de ResourceDisplayView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de ResourceDisplayView en timeout: {e}")

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.secondary, custom_id="back_to_main_menu", emoji="🏠")
    async def back_to_main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Vuelve a mostrar el menú principal del bot.
        """
        await interaction.response.defer()
        # Deshabilitar todos los botones de la vista actual
        for item in self.children:
            item.disabled = True
        # No intentamos editar interaction.message aquí, ya que el siguiente paso enviará un nuevo mensaje
        # Si self.message está asignado, podemos intentar editarlo para deshabilitar los botones
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Advertencia: Mensaje de ResourceDisplayView no encontrado al intentar deshabilitar botones. Continuando.")
            except Exception as e:
                print(f"Error al deshabilitar botones en ResourceDisplayView: {e}")

        # Obtener el cog de comandos para llamar a la función iniciar
        commands_cog = self.bot.get_cog("Commands")
        if commands_cog:
            await commands_cog.iniciar(interaction)
        else:
            await interaction.followup.send("❌ Error interno: El módulo de comandos no está cargado.", ephemeral=True)


class SubcategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una subcategoría de recursos o ver todos los recursos de la categoría.
    """
    def __init__(self, bot, difficulty: str, category: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.difficulty = difficulty
        self.category = category
        self.message = None

        asyncio.create_task(self._add_subcategory_buttons()) # Ejecutar asíncronamente

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(content="La interacción de selección de subcategoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de SubcategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de SubcategorySelectionView en timeout: {e}")

    async def _add_subcategory_buttons(self):
        """Añade botones para cada subcategoría disponible."""
        if not await db_manager.connect(): # Usar el método asíncrono connect
            print("Error: No se pudo conectar a la base de datos para obtener subcategorías.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        # Usar ResourceService para obtener las subcategorías
        from services.resource_service import ResourceService
        resource_service = ResourceService()
        subcategories = await resource_service.get_distinct_subcategories(difficulty=self.difficulty, category=self.category)

        if not subcategories:
            self.add_item(discord.ui.Button(label="No hay subcategorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
        else:
            for subcategory in subcategories:
                # Discord tiene un límite de 25 botones por vista
                if len(self.children) < 24: # Dejar espacio para el botón "Ver todos"
                    self.add_item(discord.ui.Button(label=subcategory.title(), style=discord.ButtonStyle.secondary, custom_id=f"subcat_{subcategory}"))
                else:
                    break # Evitar añadir más de 25 botones

        # Añadir el botón para ver todos los recursos de la categoría
        self.add_item(discord.ui.Button(label="Ver todos los recursos de esta categoría", style=discord.ButtonStyle.primary, custom_id="view_all_in_category", row=4))
        # Después de añadir los ítems, es posible que necesites actualizar el mensaje si ya fue enviado
        if self.message:
            await self.message.edit(view=self)


    @discord.ui.button(label="Volver a Categorías", style=discord.ButtonStyle.secondary, custom_id="back_to_categories", row=4)
    async def back_to_categories_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Vuelve a la selección de categorías.
        """
        await interaction.response.defer()
        # Deshabilitar todos los botones de la vista actual
        for item in self.children:
            item.disabled = True
        # No intentamos editar interaction.message aquí, ya que el siguiente paso enviará un nuevo mensaje
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Advertencia: Mensaje de SubcategorySelectionView no encontrado al intentar deshabilitar botones. Continuando.")
            except Exception as e:
                print(f"Error al deshabilitar botones en SubcategorySelectionView: {e}")

        resources_cog = self.bot.get_cog("Resources")
        if resources_cog:
            await resources_cog.send_category_selection(interaction, self.difficulty)
        else:
            await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Verifica que solo el usuario que inició la interacción pueda usar los botones
        y maneja la lógica para los botones de subcategoría.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("subcat_"):
            selected_subcategory = interaction.data["custom_id"].replace("subcat_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            # Deshabilitar los botones de esta vista (si self.message está disponible)
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(content=f"Has seleccionado la subcategoría: **{selected_subcategory.title()}** (Categoría: {self.category.title()}, Dificultad: {self.difficulty.title()}).", view=self)
                except discord.NotFound:
                    print("Advertencia: Mensaje de SubcategorySelectionView no encontrado al intentar editar. Continuando.")
                except Exception as e:
                    print(f"Error al editar mensaje en SubcategorySelectionView: {e}")

            # Llamar al cog de Resources para mostrar los recursos
            resources_cog = self.bot.get_cog("Resources")
            if resources_cog:
                await resources_cog.display_resources(interaction, self.difficulty, self.category, selected_subcategory)
            else:
                await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)
            return False # La interacción ha sido manejada

        elif interaction.data and interaction.data.get("custom_id", "") == "view_all_in_category":
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB

            # Deshabilitar los botones de esta vista (si self.message está disponible)
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(content=f"Mostrando todos los recursos para la categoría: **{self.category.title()}** (Dificultad: {self.difficulty.title()}).", view=self)
                except discord.NotFound:
                    print("Advertencia: Mensaje de SubcategorySelectionView no encontrado al intentar editar. Continuando.")
                except Exception as e:
                    print(f"Error al editar mensaje en SubcategorySelectionView: {e}")

            # Llamar al cog de Resources para mostrar todos los recursos de la categoría
            resources_cog = self.bot.get_cog("Resources")
            if resources_cog:
                await resources_cog.display_resources(interaction, self.difficulty, self.category, None) # Subcategoría None
            else:
                await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)
            return False # La interacción ha sido manejada

        return True # Permitir que otros botones se procesen (como 'back_to_categories')


class CategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una categoría de recursos.
    """
    def __init__(self, bot, difficulty: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.difficulty = difficulty
        self.message = None

        asyncio.create_task(self._add_category_buttons()) # Ejecutar asíncronamente

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(content="La interacción de selección de categoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de CategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de CategorySelectionView en timeout: {e}")

    async def _add_category_buttons(self):
        """Añade botones para cada categoría disponible."""
        if not await db_manager.connect(): # Usar el método asíncrono connect
            print("Error: No se pudo conectar a la base de datos para obtener categorías.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        # Usar ResourceService para obtener las categorías
        from services.resource_service import ResourceService
        resource_service = ResourceService()
        categories = await resource_service.get_distinct_categories(difficulty=self.difficulty)

        if not categories:
            self.add_item(discord.ui.Button(label="No hay categorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
        else:
            for category in categories:
                if len(self.children) < 25: # Discord tiene un límite de 25 botones por vista
                    self.add_item(discord.ui.Button(label=category.title(), style=discord.ButtonStyle.primary, custom_id=f"cat_{category}"))
                else:
                    break
        # Después de añadir los ítems, es posible que necesites actualizar el mensaje si ya fue enviado
        if self.message:
            await self.message.edit(view=self)


    @discord.ui.button(label="Volver a Dificultades", style=discord.ButtonStyle.secondary, custom_id="back_to_difficulties", row=4)
    async def back_to_difficulties_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Vuelve a la selección de dificultades.
        """
        await interaction.response.defer()
        # Deshabilitar todos los botones de la vista actual
        for item in self.children:
            item.disabled = True
        # No intentamos editar interaction.message aquí, ya que el siguiente paso enviará un nuevo mensaje
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                print("Advertencia: Mensaje de CategorySelectionView no encontrado al intentar deshabilitar botones. Continuando.")
            except Exception as e:
                print(f"Error al deshabilitar botones en CategorySelectionView: {e}")

        resources_cog = self.bot.get_cog("Resources")
        if resources_cog:
            await resources_cog.send_difficulty_selection(interaction)
        else:
            await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Verifica que solo el usuario que inició la interacción pueda usar los botones
        y maneja la lógica para los botones de categoría.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("cat_"):
            selected_category = interaction.data["custom_id"].replace("cat_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            # Deshabilitar los botones de esta vista (si self.message está disponible)
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(content=f"Has seleccionado la categoría: **{selected_category.title()}** (Dificultad: {self.difficulty.title()}).", view=self)
                except discord.NotFound:
                    print("Advertencia: Mensaje de CategorySelectionView no encontrado al intentar editar. Continuando.")
                except Exception as e:
                    print(f"Error al editar mensaje en CategorySelectionView: {e}")

            # Llamar al cog de Resources para enviar la siguiente vista de selección de subcategoría
            resources_cog = self.bot.get_cog("Resources")
            if resources_cog:
                await resources_cog.send_subcategory_selection(interaction, self.difficulty, selected_category)
            else:
                await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)
            return False # La interacción ha sido manejada

        return True # Permitir que otros botones se procesen (como 'back_to_difficulties')


class DifficultySelectionView(discord.ui.View):
    """
    Vista para seleccionar la dificultad de los recursos.
    """
    def __init__(self, bot):
        super().__init__(timeout=300) # 5 minutos de timeout
        self.bot = bot
        self.message = None # Para almacenar el mensaje

        asyncio.create_task(self._add_difficulty_buttons()) # Ejecutar asíncronamente

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(content="La interacción de selección de dificultad ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de DifficultySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de DifficultySelectionView en timeout: {e}")

    async def _add_difficulty_buttons(self):
        """Añade botones para cada dificultad disponible."""
        if not await db_manager.connect(): # Usar el método asíncrono connect
            print("Error: No se pudo conectar a la base de datos para obtener dificultades. Asegúrate de que la DB esté corriendo y las credenciales sean correctas.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        # Usar ResourceService para obtener las dificultades
        from services.resource_service import ResourceService
        resource_service = ResourceService()
        difficulties = await resource_service.get_distinct_difficulties()
        
        print(f"Dificultades obtenidas de la DB: {difficulties}") # DEBUG: Para ver qué devuelve la DB
        
        if not difficulties:
            self.add_item(discord.ui.Button(label="No hay dificultades disponibles", style=discord.ButtonStyle.grey, disabled=True))
        else:
            for difficulty in difficulties:
                # Discord tiene un límite de 25 botones por vista
                if len(self.children) < 25:
                    self.add_item(discord.ui.Button(label=difficulty.title(), style=discord.ButtonStyle.primary, custom_id=f"diff_{difficulty}"))
                else:
                    break # Evitar añadir más de 25 botones
        # Después de añadir los ítems, es posible que necesites actualizar el mensaje si ya fue enviado
        if self.message:
            await self.message.edit(view=self)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Verifica que solo el usuario que inició la interacción pueda usar los botones
        y maneja la lógica para los botones de dificultad.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("diff_"):
            selected_difficulty = interaction.data["custom_id"].replace("diff_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            # Deshabilitar los botones de esta vista (si self.message está disponible)
            for item in self.children:
                item.disabled = True
            if self.message: # Solo intenta editar si el mensaje está asignado
                try:
                    await self.message.edit(content=f"Has seleccionado la dificultad: **{selected_difficulty.title()}**.", view=self)
                except discord.NotFound:
                    print("Advertencia: Mensaje de DifficultySelectionView no encontrado al intentar editar. Continuando.")
                except Exception as e:
                    print(f"Error al editar mensaje en DifficultySelectionView: {e}")

            # Llamar al cog de Resources para enviar la siguiente vista de selección de categoría
            resources_cog = self.bot.get_cog("Resources")
            if resources_cog:
                await resources_cog.send_category_selection(interaction, selected_difficulty)
            else:
                await interaction.followup.send("❌ Error interno: El módulo de recursos no está cargado.", ephemeral=True)
            return False # La interacción ha sido manejada

        return True # Permitir que otros botones se procesen (si hubiera más)
