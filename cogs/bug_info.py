# Archivo: cogs/bug_info.py
import discord
from discord.ext import commands
import asyncio

import config

class BugInfo(commands.Cog):
    """
    Cog que gestiona el flujo conversacional para recopilar información de bugs.
    """
    def __init__(self, bot):
        self.bot = bot

    async def start_bug_report_flow(self, channel: discord.TextChannel, member: discord.Member):
        """
        Inicia un flujo de preguntas y respuestas para recolectar la información del bug.
        """
        # Mensaje de bienvenida y primera pregunta
        await channel.send(
            f"¡Hola, {member.mention}! El equipo de <@&{config.OPERECIONES_ROLES_ID}> ha sido notificado. "
            "Por favor, responde a las siguientes preguntas para ayudarnos a resolver tu bug de la mejor manera posible."
        )

        questions = [
            "1. **¿En qué plataforma ocurrió el problema?** (Por ejemplo: Windows, macOS, navegador web, aplicación móvil)",
            "2. **Describe el problema en detalle.** (Qué pasó, qué estabas haciendo, etc.)",
            "3. **¿Qué soluciones has intentado para solucionarlo?**"
        ]

        # Almacenará las respuestas del usuario
        answers = {}

        def check_message(message):
            """Función de verificación para wait_for."""
            return message.author == member and message.channel == channel

        # Iterar a través de las preguntas
        for i, question in enumerate(questions):
            await channel.send(question)
            try:
                # Esperar la respuesta del usuario con un tiempo de espera de 180 segundos
                response = await self.bot.wait_for('message', check=check_message, timeout=180.0)
                answers[f"answer_{i+1}"] = response.content
            except asyncio.TimeoutError:
                # Si el usuario no responde a tiempo
                await channel.send("❌ Se ha agotado el tiempo. Por favor, reinicia el proceso con `&bug` si deseas continuar.")
                return

        # Una vez que se tienen todas las respuestas, compilar el reporte
        embed = discord.Embed(
            title="🐞 Nuevo Reporte de Bug",
            description=f"Reporte enviado por {member.mention}",
            color=0xff0000  # Rojo
        )
        # Corrección: Verifica si el usuario tiene un avatar antes de intentar acceder a su URL
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="Plataforma", value=answers.get("answer_1", "N/A"), inline=False)
        embed.add_field(name="Descripción del Problema", value=answers.get("answer_2", "N/A"), inline=False)
        embed.add_field(name="Soluciones Intentadas", value=answers.get("answer_3", "N/A"), inline=False)
        embed.set_footer(text=f"ID del Usuario: {member.id}")

        # Enviar el reporte al canal de bugs oficial y al canal privado
        bug_channel = self.bot.get_channel(config.BUGS_CHANNEL_ID)
        if bug_channel:
            await bug_channel.send(f"Reporte de {member.mention} para el equipo de <@&{config.OPERECIONES_ROLES_ID}>:", embed=embed)
            await channel.send("✅ ¡Reporte enviado! El equipo de Operaciones ha sido notificado en el canal oficial de bugs y se comunicará contigo por este medio.")
        else:
            await channel.send(f"✅ ¡Reporte enviado! No se pudo enviar al canal oficial de bugs (ID no encontrado), pero el equipo de <@&{config.OPERECIONES_ROLES_ID}> ha sido notificado.")
            print(f"Advertencia: No se encontró el canal de bugs con el ID: {config.BUGS_CHANNEL_ID}")

async def setup(bot):
    """
    Función de configuración para añadir el cog de BugInfo al bot.
    """
    await bot.add_cog(BugInfo(bot))
