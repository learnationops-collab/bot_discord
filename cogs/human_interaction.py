# Archivo: cogs/human_interaction.py
# Este cog maneja el flujo de interacción para "Hablar con un Humano",
# recopilando información del usuario sin crear nuevos canales.

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a user_conversations y IDs
# from views.main_menu import CloseTicketView # Ya no es necesaria ya que no se crean tickets

class HumanInteraction(commands.Cog):
    """
    Cog que maneja el flujo de interacción para "Hablar con un Humano",
    recopilando información y notificando al equipo correspondiente.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Maneja los mensajes para el flujo de conversación "Hablar con un Humano".
        Este listener se activa para cada mensaje enviado en el servidor.
        """
        # Ignorar mensajes del propio bot
        if message.author == self.bot.user:
            return

        user_id = message.author.id
        # Si el usuario está en una conversación de "Hablar con un Humano"
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] > 0:
            conversation_state = config.user_conversations[user_id]
            current_question_number = conversation_state['state']

            # Almacenar la respuesta actual
            conversation_state['answers'].append(f"Pregunta {current_question_number}: {message.content}")

            if current_question_number == 1:
                conversation_state['state'] = 2
                await message.channel.send("**2. ¿Qué soluciones has intentado hasta ahora?**")
            elif current_question_number == 2:
                # Todas las preguntas respondidas
                config.user_conversations[user_id]['state'] = 0 # Reiniciar estado
                
                guild = message.guild

                # Validar que el ID del rol de CSMS esté configurado
                if config.ROLE_IDS['CSMS'] is None:
                    await message.channel.send("❌ Error de configuración: El ID del rol de CSMS no está definido en .env o no es válido. Contacta a un administrador.")
                    return
                
                csms_role = guild.get_role(config.ROLE_IDS['CSMS'])
                if not csms_role:
                    await message.channel.send("❌ Error: No se encontró el rol de CSMS con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.")
                    return

                # Obtener el canal de destino para las notificaciones (ej. BOT_TEST_CHANNEL_ID)
                if config.CHANNEL_IDS['BOT_TEST'] is None:
                    await message.channel.send("❌ Error de configuración: El ID del canal de prueba del bot (BOT_TEST_CHANNEL_ID) no está definido en .env o no es válido. Contacta a un administrador.")
                    return

                notification_channel = self.bot.get_channel(config.CHANNEL_IDS['BOT_TEST'])
                if not notification_channel:
                    await message.channel.send("❌ Error: No se encontró el canal de notificaciones con el ID proporcionado (BOT_TEST_CHANNEL_ID). Por favor, verifica el archivo .env o contacta a un administrador.")
                    return

                try:
                    await message.channel.send(
                        f"¡Gracias por tus respuestas, {message.author.mention}! "
                        "Hemos enviado tu solicitud a nuestro equipo. Se pondrán en contacto contigo pronto."
                    )

                    # Publicar las respuestas en el canal de notificaciones
                    answers_message = f"**ℹ️ Solicitud de Contacto Humano de {message.author.mention} ({message.author.name}):**\n"
                    for ans in conversation_state['answers']:
                        answers_message += f"- {ans}\n"
                    answers_message += f"\nCanal de origen: {message.channel.mention}" # Añadir el canal de origen

                    await notification_channel.send(answers_message)
                    await notification_channel.send(f"{csms_role.mention}, un nuevo cliente necesita asistencia. Por favor, revisen la información en el mensaje anterior.")

                except discord.Forbidden:
                    await message.channel.send("❌ No tengo los permisos necesarios para enviar mensajes en el canal de notificaciones. Por favor, asegúrate de que el bot tenga los permisos adecuados.")
                except Exception as e:
                    await message.channel.send(f"❌ Ocurrió un error al procesar tu solicitud: `{e}`")
                    print(f"Error al enviar notificación de contacto humano: {e}")
            
            # No procesar el mensaje como un comando si está en un flujo de conversación
            return
        
        # ELIMINADO: La llamada a await self.bot.process_commands(message) ha sido eliminada de aquí.
        # Esto evita que los comandos se procesen dos veces, ya que bot.py ya lo maneja.


# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de HumanInteraction al bot.
    """
    await bot.add_cog(HumanInteraction(bot))
