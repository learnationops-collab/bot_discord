# Archivo: cogs/sales/reports.py
# Este cog contiene comandos y lógica para generar reportes cualitativos,
# analizar tendencias y realizar predicciones en el área de Ventas.

import discord
from discord.ext import commands
from database.db_manager import DBManager # Importa el gestor de la base de datos
import datetime # Para manejar fechas en los reportes
import pandas as pd # Útil para análisis de datos, aunque no se usará en el ejemplo básico
import config # Importa la configuración para acceder a user_conversations

class Reports(commands.Cog):
    """
    Cog que proporciona comandos para la gestión de reportes y análisis de ventas.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager() # Instancia el gestor de la base de datos

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Se ejecuta cuando el bot ha iniciado sesión y está listo.
        Asegura que la conexión a la base de datos de Notion esté establecida para ventas.
        """
        print("Intentando conectar DBManager para Reports cog (Ventas)...")
        if not self.db_manager.connect():
            print("❌ Error: No se pudo conectar a la base de datos de Notion para el cog de Ventas.")
        else:
            print("✅ DBManager conectado para Reports cog (Ventas).")

    @commands.command(name='reporte_ventas', help='Genera un reporte cualitativo de ventas.')
    @commands.has_role(config.ROLE_IDS['CSMS']) # Solo usuarios con el rol CSMS pueden usar este comando
    async def sales_report(self, ctx, start_date: str = None, end_date: str = None, product: str = None, region: str = None):
        """
        Genera un reporte cualitativo de ventas basado en los filtros proporcionados.
        Ejemplo: &reporte_ventas 2025-01-01 2025-01-31 ProductoA Europa
        """
        await ctx.send("Generando reporte de ventas, por favor espera...")

        # Validar y formatear fechas si se proporcionan
        try:
            if start_date:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            await ctx.send("❌ Formato de fecha inválido. Usa el formato `AAAA-MM-DD`.")
            return

        try:
            sales_data = await self.db_manager.get_sales_data(
                start_date=start_date,
                end_date=end_date,
                product=product,
                region=region
            )

            if not sales_data:
                await ctx.send("ℹ️ No se encontraron datos de ventas que coincidan con los filtros proporcionados.")
                return

            # Construir el reporte cualitativo
            report_message = f"📊 **Reporte de Ventas**\n"
            report_message += f"Periodo: {start_date if start_date else 'Inicio'} al {end_date if end_date else 'Fin'}\n"
            report_message += f"Producto: {product if product else 'Todos'}\n"
            report_message += f"Región: {region if region else 'Todas'}\n\n"

            total_sales_amount = 0
            for i, sale in enumerate(sales_data):
                total_sales_amount += sale.get('sales_amount', 0)
                report_message += (
                    f"**{i+1}. Fecha:** `{sale.get('date', 'N/A')}`\n"
                    f"   **Producto:** `{sale.get('product', 'N/A')}`\n"
                    f"   **Monto:** `${sale.get('sales_amount', 'N/A'):.2f}`\n"
                    f"   **Región:** `{sale.get('region', 'N/A')}`\n"
                    f"   **Notas:** `{sale.get('notes', 'Sin notas')}`\n\n"
                )
                # Limitar el tamaño del mensaje para Discord
                if len(report_message) > 1800 and i < len(sales_data) - 1:
                    report_message += "...\n(Reporte truncado. Considera filtros más específicos.)"
                    break

            report_message += f"--- \n**Ventas Totales en el Periodo:** `${total_sales_amount:.2f}`"

            await ctx.send(report_message)
            print(f"Reporte de ventas generado por {ctx.author.name} con filtros: {start_date}, {end_date}, {product}, {region}")

        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error al generar el reporte de ventas: `{e}`")
            print(f"Error en sales_report: {e}")

    @commands.command(name='analizar_tendencias', help='Analiza tendencias de ventas (placeholder).')
    @commands.has_role(config.ROLE_IDS['CSMS'])
    async def sales_trends(self, ctx):
        """
        Comando para analizar tendencias de ventas.
        Actualmente es un placeholder.
        """
        await ctx.send("📈 **Análisis de Tendencias de Ventas:**\n"
                       "Esta función está en desarrollo. Pronto podrás ver gráficos y proyecciones aquí.")
        print(f"Comando analizar_tendencias ejecutado por {ctx.author.name}.")


    @commands.command(name='predecir_ventas', help='Realiza una predicción de ventas (placeholder).')
    @commands.has_role(config.ROLE_IDS['CSMS'])
    async def sales_predict(self, ctx):
        """
        Comando para realizar predicciones de ventas.
        Actualmente es un placeholder.
        """
        await ctx.send("🔮 **Predicción de Ventas:**\n"
                       "Esta función está en desarrollo. Pronto podrás obtener predicciones basadas en datos históricos.")
        print(f"Comando predecir_ventas ejecutado por {ctx.author.name}.")


# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Reports al bot.
    """
    await bot.add_cog(Reports(bot))
