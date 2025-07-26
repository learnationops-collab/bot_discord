# Archivo: cogs/fulfillment/resources.py
# Cog que maneja la búsqueda y presentación de recursos a los estudiantes en el área de Fulfillment.

import discord
from discord.ext import commands
from database.db_manager import DBManager # Importa el gestor de la base de datos
from services.resource_service import ResourceService # Importa el servicio de recursos
from views.resource_views import DifficultySelectionView, CategorySelectionView, SubcategorySelectionView, ResourceDisplayView # Importa las nuevas vistas

class Resources(commands.Cog):
    """
    Cog que maneja la búsqueda y presentación de recursos a los estudiantes.
    La interacción principal para recursos se gestiona a través de botones/vistas.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager() # Instancia el gestor de la base de datos
        self.resource_service = ResourceService() # Instancia el servicio de recursos

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Se ejecuta cuando el bot ha iniciado sesión y está listo.
        Asegura que la conexión a la base de datos de Notion esté establecida.
        """
        print("Intentando conectar DBManager para Resources cog...")
        # CAMBIO AQUÍ: Asegurarse de await self.db_manager.connect()
        if not await self.db_manager.connect():
            print("❌ Error: No se pudo conectar a la base de datos de Notion para el cog de Recursos.")
        else:
            print("✅ DBManager conectado para Resources cog.")

    # --- Métodos para el flujo de búsqueda de recursos (invocados por vistas/botones) ---

    async def send_difficulty_selection(self, interaction: discord.Interaction):
        """
        Envía un mensaje con la vista para que el usuario seleccione la dificultad del recurso.
        Este método es llamado cuando el usuario hace clic en "Necesito un Recurso" en el menú principal.
        """
        # La interacción ya ha sido deferida por el botón inicial en MainMenuView
        
        # Crear y enviar la vista de selección de dificultad
        view = DifficultySelectionView(self.bot)
        # Usar followup.send ya que la interacción ya fue deferida
        message = await interaction.followup.send("Por favor, selecciona la dificultad del recurso:", view=view, ephemeral=True)
        view.message = message # Asignar el mensaje a la vista para el timeout
        print(f"Enviado selector de dificultad a {interaction.user.name}")


    async def send_category_selection(self, interaction: discord.Interaction, difficulty: str):
        """
        Envía un mensaje con la vista para que el usuario seleccione la categoría,
        basado en la dificultad previamente seleccionada.
        """
        # La interacción ya ha sido deferida por el botón de dificultad
        
        view = CategorySelectionView(self.bot, difficulty)
        # Usar followup.send ya que la interacción ya fue deferida
        message = await interaction.followup.send(f"Has seleccionado dificultad: **{difficulty.capitalize()}**.\n" \
                                                 f"Ahora, selecciona una categoría:", view=view, ephemeral=True)
        view.message = message # Asignar el mensaje a la vista para el timeout
        print(f"Enviado selector de categoría ({difficulty}) a {interaction.user.name}")


    async def send_subcategory_selection(self, interaction: discord.Interaction, difficulty: str, category: str):
        """
        Envía un mensaje con la vista para que el usuario seleccione la subcategoría,
        basado en la dificultad y categoría previamente seleccionadas.
        """
        # La interacción ya ha sido deferida por el botón de categoría
        
        view = SubcategorySelectionView(self.bot, difficulty, category)
        # Usar followup.send ya que la interacción ya fue deferida
        message = await interaction.followup.send(f"Has seleccionado dificultad: **{difficulty.capitalize()}**, categoría: **{category.capitalize()}**.\n" \
                                                 f"Ahora, selecciona una subcategoría o ver todos:", view=view, ephemeral=True)
        view.message = message # Asignar el mensaje a la vista para el timeout
        print(f"Enviado selector de subcategoría ({difficulty}, {category}) a {interaction.user.name}")


    async def display_resources(self, interaction: discord.Interaction, difficulty: str, category: str, subcategory: str = None):
        """
        Recupera y muestra los recursos finales basados en las selecciones del usuario.
        """
        # La interacción ya ha sido deferida por el botón de subcategoría o "ver todos"
        
        resources = await self.resource_service.get_resources( # Usar el servicio de recursos
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
            # Asegurarse de que el enlace sea un URL válido para que Discord lo muestre como tal
            formatted_link = f"[Enlace al recurso]({link})" if link and link.startswith('http') else "Enlace no disponible"
            embed.add_field(name=f"{i+1}. {resource_name}", value=formatted_link, inline=False)

        view = ResourceDisplayView(self.bot, resources, difficulty, category, subcategory)
        message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = message # Asignar el mensaje a la vista para el timeout
        print(f"Mostrados recursos ({difficulty}, {category}, {subcategory}) a {interaction.user.name}")


# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Resources al bot.
    """
    await bot.add_cog(Resources(bot))
