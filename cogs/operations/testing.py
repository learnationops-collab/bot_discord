# Archivo: cogs/operations/testing.py
# Este cog contiene comandos y funciones para testear el bot en el área de Operaciones.

import discord
from discord.ext import commands
import time
import config  # Importa la configuración para acceder a user_conversations

class Testing(commands.Cog):
    """
    Cog que proporciona comandos para realizar pruebas y verificar el estado del bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='Verifica la latencia del bot.')
    async def ping(self, ctx):
        """
        Responde con la latencia del bot (ping) en milisegundos.
        Útil para verificar si el bot está respondiendo y su velocidad.
        """
        # Calcular la latencia de la API de Discord
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f'� ¡Pong! Latencia: `{latency_ms}ms`')
        print(f"Comando &ping ejecutado por {ctx.author.name}. Latencia: {latency_ms}ms")

    @commands.command(name='test_db_resources', help='(DEBUG) Prueba la conexión y obtención de recursos de Notion.')
    @commands.has_role(config.ROLE_IDS['DEBUG']) # Solo usuarios con el rol DEBUG pueden usar este comando
    async def test_db_resources(self, ctx):
        """
        Comando de depuración para probar la conexión a la base de datos de recursos de Notion
        y obtener algunas dificultades.
        """
        await ctx.send("Iniciando prueba de conexión y obtención de recursos de Notion...")
        # Importar DBManager aquí para evitar importaciones circulares si es necesario
        from database.db_manager import DBManager
        db_manager = DBManager()

        if not db_manager.connect():
            await ctx.send("❌ Error: No se pudo conectar a la base de datos de Notion para recursos. Revisa el TOKEN y los IDs.")
            return

        try:
            difficulties = await db_manager.get_distinct_difficulties()
            if difficulties:
                await ctx.send(f"✅ Conexión a DB de recursos exitosa. Dificultades encontradas: `{', '.join(difficulties)}`")
            else:
                await ctx.send("✅ Conexión a DB de recursos exitosa, pero no se encontraron dificultades. La base de datos podría estar vacía o las propiedades no coinciden.")
        except Exception as e:
            await ctx.send(f"❌ Error al consultar recursos de Notion: `{e}`")
            print(f"Error en test_db_resources: {e}")
        finally:
            db_manager.close()

    @commands.command(name='test_db_sales', help='(DEBUG) Prueba la conexión y obtención de datos de ventas de Notion.')
    @commands.has_role(config.ROLE_IDS['DEBUG']) # Solo usuarios con el rol DEBUG pueden usar este comando
    async def test_db_sales(self, ctx):
        """
        Comando de depuración para probar la conexión a la base de datos de ventas de Notion
        y obtener algunos datos recientes.
        """
        await ctx.send("Iniciando prueba de conexión y obtención de datos de ventas de Notion...")
        from database.db_manager import DBManager
        db_manager = DBManager()

        if not db_manager.connect():
            await ctx.send("❌ Error: No se pudo conectar a la base de datos de Notion para ventas. Revisa el TOKEN y los IDs.")
            return

        try:
            # Intentar obtener los últimos 5 registros de ventas (puedes ajustar el filtro)
            sales_data = await db_manager.get_sales_data(start_date="2020-01-01") # Obtener desde una fecha muy antigua
            if sales_data:
                response_msg = f"✅ Conexión a DB de ventas exitosa. Se encontraron {len(sales_data)} registros de ventas. Primeros 3:\n"
                for i, sale in enumerate(sales_data[:3]):
                    response_msg += f"- Fecha: `{sale.get('date')}`, Producto: `{sale.get('product')}`, Monto: `{sale.get('sales_amount')}`\n"
                await ctx.send(response_msg)
            else:
                await ctx.send("✅ Conexión a DB de ventas exitosa, pero no se encontraron registros de ventas. La base de datos podría estar vacía o las propiedades no coinciden.")
        except Exception as e:
            await ctx.send(f"❌ Error al consultar datos de ventas de Notion: `{e}`")
            print(f"Error en test_db_sales: {e}")
        finally:
            db_manager.close()

    # Puedes añadir más comandos de prueba aquí, por ejemplo:
    # - Un comando para simular un flujo de conversación
    # - Un comando para verificar permisos de roles
    # - Un comando para verificar el estado de los cogs cargados

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Testing al bot.
    """
    await bot.add_cog(Testing(bot))
