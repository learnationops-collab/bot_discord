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
            "1. **¿En qué plataforma ocurrió el problema?** (Por ejemplo: Manychat, Kommo, Zapier, Google Sheets, etc.)",
            "2. **Describe el problema en detalle.** (Qué pasó, qué estabas haciendo, etc.)",
            "3. **Por favor, envía una imagen para ver más detalles del problema**"
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
                # Esperar la respuesta del usuario con un tiempo de espera de 800 segundos
                response = await self.bot.wait_for('message', check=check_message, timeout=800.0)
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
        embed.add_field(name="Detalles: ", value=answers.get("answer_3", "N/A"), inline=False)
        embed.set_footer(text=f"ID del Usuario: {member.id}")

        # Enviar el reporte al canal de bugs oficial y al canal privado
        bug_channel = self.bot.get_channel(config.BUGS_CHANNEL_ID)
        if bug_channel:
            report_message = await bug_channel.send(f"Reporte de {member.mention} para el equipo de <@&{config.OPERECIONES_ROLES_ID}>:", embed=embed)
            # Guardar el ID del mensaje en el topic del canal
            await channel.edit(topic=f"ID del reporte de bug: {report_message.id}")
            await channel.send("✅ ¡Reporte enviado! El equipo de Operaciones ha sido notificado en el canal oficial de bugs y se comunicará contigo por este medio.")
        else:
            await channel.send(f"✅ ¡Reporte enviado! No se pudo enviar al canal oficial de bugs (ID no encontrado), pero el equipo de <@&{config.OPERECIONES_ROLES_ID}> ha sido notificado.")
            print(f"Advertencia: No se encontró el canal de bugs con el ID: {config.BUGS_CHANNEL_ID}")

    async def start_bug_solved_flow(self, channel: discord.TextChannel, member: discord.Member):
        """
        Inicia un flujo de preguntas para saber cómo se resolvió el problema.
        """
        await channel.send(f"¡Hola, {member.mention}! Responde a las siguientes preguntas para documentar la solución del bug. El canal se cerrará una vez finalizado el proceso.")
        
        questions = [
            "1. **¿Cuál fue la solución?**",
            "2. **Detalles: **",
            "3. **¿Hay alguna información adicional a tener en cuenta?**"
        ]

        answers = {}

        def check_message(message):
            return message.author == member and message.channel == channel

        for i, question in enumerate(questions):
            await channel.send(question)
            try:
                response = await self.bot.wait_for('message', check=check_message, timeout=500.0)
                answers[f"answer_{i+1}"] = response.content
            except asyncio.TimeoutError:
                await channel.send("❌ Se ha agotado el tiempo. El canal no se cerrará. Puedes usar `&bug_resuelto` nuevamente si lo deseas.")
                return

        # Compilar el reporte de la solución
        plataforma = "No especificada"
        descripcion_problema = "No especificada"
        if channel.topic and "ID del reporte de bug: " in channel.topic:
            try:
                report_id = int(channel.topic.split("ID del reporte de bug: ")[1])
                bug_channel = self.bot.get_channel(config.BUGS_CHANNEL_ID)
                if bug_channel:
                    report_message = await bug_channel.fetch_message(report_id)
                    if report_message.embeds:
                        for field in report_message.embeds[0].fields:
                            if field.name == "Plataforma":
                                plataforma = field.value
                            elif field.name == "Descripción del Problema":
                                descripcion_problema = field.value
            except (ValueError, discord.NotFound, discord.Forbidden):
                pass

        embed = discord.Embed(
            title="✅ Bug Resuelto",
            description=f"Solución documentada por {member.mention}.",
            color=0x00ff00  # Verde
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="Plataforma", value=plataforma, inline=False)
        embed.add_field(name="Descripción del Problema", value=descripcion_problema, inline=False)
        embed.add_field(name="Solución Final", value=answers.get("answer_1", "N/A"), inline=False)
        embed.add_field(name="Detalles: ", value=answers.get("answer_2", "N/A"), inline=False)
        embed.add_field(name="Información a tener en cuenta", value=answers.get("answer_3", "N/A"), inline=False)

        # Enviar el reporte al canal de bugs oficial y luego cerrar el canal privado
        bug_channel = self.bot.get_channel(config.BUGS_CHANNEL_ID)
        if bug_channel:
            await bug_channel.send(f"Reporte de solución para el equipo de <@&{config.OPERECIONES_ROLES_ID}>:", embed=embed)
            await channel.send("✅ ¡Reporte de solución enviado! El equipo de Operaciones ha sido notificado y este canal se cerrará en 5 segundos.")
            await asyncio.sleep(5)
            # Intentar eliminar el canal
            ticket_cog = self.bot.get_cog('TicketManagement')
            if ticket_cog:
                await ticket_cog.close_bug_channel(channel)
        else:
            await channel.send("❌ No se pudo enviar el reporte de solución (ID de canal de bugs no encontrado). El canal no se cerrará automáticamente.")
            print(f"Advertencia: No se encontró el canal de bugs con el ID: {config.BUGS_CHANNEL_ID}")

async def setup(bot):
    """
    Función de configuración para añadir el cog de BugInfo al bot.
    """
    await bot.add_cog(BugInfo(bot))
