# Archivo: cogs/fulfillment/resources.py
# Cog que maneja la búsqueda y presentación de recursos a los estudiantes en el área de Fulfillment.

import discord
from discord.ext import commands
from database.db_manager import DBManager # Importa el gestor de la base de datos

# Asumimos que las vistas para la selección de recursos (dificultad, categoría, subcategoría)
# serán definidas en views/resource_views.py o views/main_menu.py
# Por ahora, solo importamos MainMenuView como referencia si fuera necesario.
# from views.main_menu import MainMenuView # Podría ser necesaria si el flujo inicia desde allí

class Resources(commands.Cog):
    """
    Cog que maneja la búsqueda y presentación de recursos a los estudiantes.
    La interacción principal para recursos se gestiona a través de botones/vistas.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager() # Instancia el gestor de la base de datos

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Se ejecuta cuando el bot ha iniciado sesión y está listo.
        Asegura que la conexión a la base de datos de Notion esté establecida.
        """
        print("Intentando conectar DBManager para Resources cog...")
        if not self.db_manager.connect():
            print("❌ Error: No se pudo conectar a la base de datos de Notion para el cog de Recursos.")
        else:
            print("✅ DBManager conectado para Resources cog.")

    # --- Métodos para el flujo de búsqueda de recursos (invocados por vistas/botones) ---

    async def send_difficulty_selection(self, interaction: discord.Interaction):
        """
        Envía un mensaje con botones para que el usuario seleccione la dificultad del recurso.
        Este método sería llamado, por ejemplo, cuando el usuario hace clic en "Buscar Recursos".
        Utiliza interaction.followup.send porque la interacción ya ha sido deferida.
        """
        difficulties = await self.db_manager.get_distinct_difficulties()
        if not difficulties:
            # Usar followup.send ya que la interacción ya fue deferida por el botón inicial
            await interaction.followup.send("No se encontraron dificultades de recursos disponibles en este momento.", ephemeral=True)
            return

        # Aquí deberías construir y enviar una vista (discord.ui.View) con los botones de dificultad.
        # Por simplicidad, aquí solo se muestra un mensaje de texto.
        # La implementación real de los botones iría en views/resource_views.py
        difficulty_options = "\n".join([f"• {d.capitalize()}" for d in difficulties])
        message_content = f"Por favor, selecciona la dificultad del recurso:\n{difficulty_options}"
        
        # Usar followup.send ya que la interacción ya fue deferida
        await interaction.followup.send(message_content, ephemeral=True)
        print(f"Enviado selector de dificultad a {interaction.user.name}")

        # Ejemplo de cómo se podría enviar una vista (requiere que la vista esté definida):
        # from views.resource_views import DifficultySelectionView
        # view = DifficultySelectionView(self.bot, difficulties)
        # await interaction.followup.send("Selecciona la dificultad:", view=view, ephemeral=True)


    async def send_category_selection(self, interaction: discord.Interaction, difficulty: str):
        """
        Envía un mensaje con botones para que el usuario seleccione la categoría,
        basado en la dificultad previamente seleccionada.
        Utiliza interaction.followup.send porque la interacción ya ha sido deferida.
        """
        categories = await self.db_manager.get_distinct_categories(difficulty=difficulty)
        if not categories:
            await interaction.followup.send(f"No se encontraron categorías para la dificultad '{difficulty}'.", ephemeral=True)
            return

        category_options = "\n".join([f"• {c.capitalize()}" for c in categories])
        message_content = f"Has seleccionado dificultad: **{difficulty.capitalize()}**.\n" \
                          f"Ahora, selecciona una categoría:\n{category_options}"
        await interaction.followup.send(message_content, ephemeral=True)
        print(f"Enviado selector de categoría ({difficulty}) a {interaction.user.name}")

        # Similar a send_difficulty_selection, aquí iría la lógica para enviar una vista de categorías.


    async def send_subcategory_selection(self, interaction: discord.Interaction, difficulty: str, category: str):
        """
        Envía un mensaje con botones para que el usuario seleccione la subcategoría,
        basado en la dificultad y categoría previamente seleccionadas.
        Utiliza interaction.followup.send porque la interacción ya ha sido deferida.
        """
        subcategories = await self.db_manager.get_distinct_subcategories(difficulty=difficulty, category=category)
        if not subcategories:
            await interaction.followup.send(f"No se encontraron subcategorías para '{category}' en dificultad '{difficulty}'.", ephemeral=True)
            return

        subcategory_options = "\n".join([f"• {s.capitalize()}" for s in subcategories])
        message_content = f"Has seleccionado dificultad: **{difficulty.capitalize()}**, categoría: **{category.capitalize()}**.\n" \
                          f"Ahora, selecciona una subcategoría:\n{subcategory_options}"
        await interaction.followup.send(message_content, ephemeral=True)
        print(f"Enviado selector de subcategoría ({difficulty}, {category}) a {interaction.user.name}")

        # Aquí iría la lógica para enviar una vista de subcategorías.


    async def display_resources(self, interaction: discord.Interaction, difficulty: str, category: str, subcategory: str = None):
        """
        Recupera y muestra los recursos finales basados en las selecciones del usuario.
        Utiliza interaction.followup.send porque la interacción ya ha sido deferida.
        """
        resources = await self.db_manager.get_resources(
            difficulty=difficulty,
            category=category,
            subcategory=subcategory
        )

        if not resources:
            await interaction.followup.send("No se encontraron recursos que coincidan con tu selección.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Recursos sobre {category.capitalize()}" + (f" ({subcategory.capitalize()})" if subcategory else ""),
            description=f"Dificultad: {difficulty.capitalize()}",
            color=discord.Color.blue()
        )

        for i, res in enumerate(resources):
            resource_name = res.get('resource_name', 'Nombre no disponible')
            link = res.get('link', '#')
            embed.add_field(name=f"{i+1}. {resource_name}", value=f"[Enlace al recurso]({link})", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)
        print(f"Mostrados recursos ({difficulty}, {category}, {subcategory}) a {interaction.user.name}")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Resources al bot.
    """
    await bot.add_cog(Resources(bot))
