# Archivo: cogs/human_interaction.py

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a user_conversations y IDs
# CloseTicketView ya no se importa aquí ya que no se crearán tickets.

class HumanInteraction(commands.Cog):
    """
    Cog que maneja el flujo de interacción para "Hablar con un Humano",
    ahora completamente dentro del canal donde se inició la conversación.
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
        # y el mensaje es en el canal donde se inició la conversación
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] > 0 and \
           config.user_conversations[user_id]['channel_id'] == message.channel.id:
            
            try:
                conversation_state = config.user_conversations[user_id]
                current_question_number = conversation_state['state']

                # Almacenar la respuesta actual
                conversation_state['answers'].append(f"Pregunta {current_question_number}: {message.content}")

                if current_question_number == 1:
                    conversation_state['state'] = 2
                    await message.channel.send("**2. ¿Qué soluciones has intentado hasta ahora?**")
                elif current_question_number == 2:
                    # Todas las preguntas respondidas (se eliminó la pregunta 3)
                    config.user_conversations[user_id]['state'] = 0 # Reiniciar estado
                    
                    guild = message.guild

                    # Validar que el ID del rol de atención al cliente esté configurado
                    if config.ATENCION_AL_CLIENTE_ROLE_ID is None:
                        await message.channel.send("❌ Error de configuración: El ID del rol de Atención al Cliente no está definido en .env o no es válido. Contacta a un administrador.")
                        return
                    human_contact_role = guild.get_role(config.ATENCION_AL_CLIENTE_ROLE_ID)
                    if not human_contact_role:
                        await message.channel.send("❌ Error: No se encontró el rol de Atención al Cliente con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.")
                        return

                    # Publicar las respuestas en el canal actual y notificar al rol
                    answers_message = "**ℹ️ Información del Cliente para Atención al Cliente:**\n"
                    for ans in conversation_state['answers']:
                        answers_message += f"- {ans}\n"
                    answers_message += f"\nCliente: {message.author.mention}"
                    
                    await message.channel.send(answers_message)
                    await message.channel.send(f"{human_contact_role.mention}, un nuevo cliente necesita asistencia en este canal. Por favor, revisen la información proporcionada.")
                    await message.channel.send("Gracias por tu información. Un miembro de nuestro equipo se pondrá en contacto contigo en este chat lo antes posible.")

                # No procesar el mensaje como un comando si está en un flujo de conversación
                return
            except Exception as e:
                print(f"Error en human_interaction.on_message para el usuario {user_id}: {e}")
                try:
                    await message.channel.send("❌ Ocurrió un error inesperado durante la conversación. Por favor, intenta iniciar el flujo de nuevo con `&iniciar`.")
                except Exception as e_send:
                    print(f"Error al enviar mensaje de error en human_interaction.on_message: {e_send}")
        
        # ELIMINADO: La llamada a await self.bot.process_commands(message) ha sido eliminada de aquí.
        # Esto evita que los comandos se procesen dos veces, ya que bot.py ya lo maneja.


# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de HumanInteraction al bot.
    """
    await bot.add_cog(HumanInteraction(bot))
