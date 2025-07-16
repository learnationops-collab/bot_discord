# Archivo: cogs/resources.py

import discord
from discord.ext import commands
from database.db_manager import DBManager # Importa el gestor de la base de datos

class Resources(commands.Cog):
    """
    Cog que maneja la búsqueda y presentación de recursos a los estudiantes.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager() # Instancia el gestor de la base de datos

    @commands.command(name='recurso', help='Busca recursos por categoría, subcategoría o dificultad.')
    async def recurso(self, ctx, category: str = None, subcategory: str = None, difficulty: str = None):
        """
        Permite a los usuarios buscar recursos específicos en la base de datos.
        Ejemplos:
        &recurso aprendizaje
        &recurso autogestion "gestion del tiempo"
        &recurso autorregulacion "" basico
        &recurso ayuda (para ver categorías disponibles)
        """
        if not self.db_manager.connect():
            await ctx.send("❌ No se pudo conectar a la base de datos de recursos. Por favor, contacta a un administrador.")
            return

        # Si el usuario pide ayuda con el comando &recurso
        if category and category.lower() == 'ayuda':
            await ctx.send(
                "📚 **Tipos de Recursos Disponibles:**\n\n"
                "Puedes buscar recursos por las siguientes categorías principales:\n"
                "- `aprendizaje` (ej. 'olvido de estudio', 'esquemas no adaptados')\n"
                "- `autogestión` (ej. 'falta de tiempo', 'no cumplo mi organización')\n"
                "- `autorregulación` (ej. 'ansiedad', 'desmotivación', 'desbordado emocionalmente')\n\n"
                "También puedes especificar la dificultad: `básico` o `avanzado`.\n\n"
                "**Ejemplos de uso:**\n"
                "`&recurso aprendizaje`\n"
                "`&recurso autogestión \"gestión del tiempo\"`\n"
                "`&recurso autorregulación desmotivación básico`\n"
                "Si la subcategoría tiene espacios, ponla entre comillas dobles."
            )
            return

        # Si no se proporciona ninguna categoría, se le pide al usuario que especifique
        if not category:
            await ctx.send(
                "Por favor, especifica una categoría para buscar recursos (ej. `&recurso aprendizaje`).\n"
                "Usa `&recurso ayuda` para ver las categorías disponibles."
            )
            return

        # Buscar recursos en la base de datos
        resources = self.db_manager.get_resources(category=category, subcategory=subcategory, difficulty=difficulty)

        if resources:
            response_message = f"📚 **Recursos encontrados para '{category}'"
            if subcategory:
                response_message += f" (Subcategoría: '{subcategory}')"
            if difficulty:
                response_message += f" (Dificultad: '{difficulty}')"
            response_message += ":**\n\n"

            for i, res in enumerate(resources):
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
                await ctx.send(response_message[:1990] + "...\n(Mensaje truncado. Por favor, refina tu búsqueda.)")
            else:
                await ctx.send(response_message)
        else:
            await ctx.send(
                f"No se encontraron recursos para la categoría `{category}`"
                f"{f', subcategoría `{subcategory}`' if subcategory else ''}"
                f"{f' y dificultad `{difficulty}`' if difficulty else ''}. "
                "Intenta con otra búsqueda o usa `&recurso ayuda`."
            )

    @recurso.error
    async def recurso_error(self, ctx, error):
        """
        Manejador de errores para el comando 'recurso'.
        """
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Error en los argumentos. Asegúrate de que la subcategoría con espacios esté entre comillas dobles. Usa `&recurso ayuda` para ver ejemplos.")
        else:
            await ctx.send(f"❌ Ocurrió un error inesperado al buscar recursos: `{error}`")
            print(f"Error inesperado en recurso_error: {error}")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Resources al bot.
    """
    await bot.add_cog(Resources(bot))
