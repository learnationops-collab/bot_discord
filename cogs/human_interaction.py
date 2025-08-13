# Archivo: cogs/human_interaction.py

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a user_conversations y IDs
from views.main_menu import CloseTicketView # Importa la vista para cerrar el ticket (aunque ya no se usará directamente para el nuevo canal, se mantiene si hay otros flujos que la usen)

class HumanInteraction(commands.Cog):
    """
    Cog que maneja el flujo de interacción para "Hablar con un Humano",
    incluyendo preguntas y gestión de las respuestas en el mismo canal.
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
        # Si el usuario está en una conversación de "Hablar con un Humano" y el estado es mayor a 0 (indicando que las preguntas han comenzado)
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] > 0:
            conversation_state = config.user_conversations[user_id]
            current_question_number = conversation_state['state']
            
            # Almacenar la respuesta actual
            # Aquí almacenamos la respuesta de la pregunta anterior
            conversation_state['answers'].append(f"Pregunta {current_question_number}: {message.content}")

            # Definir las preguntas
            questions = [
                "1. Describe el problema o dificultad que encontraste. Sé específico y da todos los detalles necesarios para que podamos ayudarte mejor.",
                "2. ¿Qué acciones intentaste para resolverlo?",
                "3. ¿Qué herramienta del programa crees que podría ayudarte a solucionarlo?",
                "4. ¡Muchas gracias por tu información! Mientras te contacta la Client Success Manager, ¿cuál podría ser tu primer paso para empezar a resolver tu problema?"
            ]

            # Avanzar a la siguiente pregunta o finalizar la conversación
            if current_question_number < len(questions):
                conversation_state['state'] += 1
                await message.channel.send(f"**{questions[conversation_state['state'] - 1]}**")
            else:
                # Todas las preguntas respondidas. Publicar las respuestas en el canal actual y etiquetar.
                config.user_conversations[user_id]['state'] = 0 # Reiniciar estado para el usuario
                
                guild = message.guild
                
                # Publicar las respuestas en el canal actual
                answers_message = "**ℹ️ Información:**\n"
                for i, ans_text in enumerate(conversation_state['answers']):
                    # Reconstruir las preguntas originales en el mensaje final
                    # Se usa .split('.', 1)[0] para obtener solo el número de la pregunta
                    # y .split(':', 1)[1].strip() para obtener la respuesta del usuario.
                    answers_message += f"**{questions[i].split('.', 1)[0]}.** {ans_text.split(':', 1)[1].strip()}\n"

                answers_message += f"\nCliente: {message.author.mention}"
                
                # Etiquetar a la persona seleccionada
                selected_human_id = conversation_state.get('selected_human')
                if selected_human_id:
                    answers_message += f"\nContacto solicitado: <@{selected_human_id}>"

                # Enviar el resumen de la conversación
                await message.channel.send(answers_message)

                # Etiquetar a la persona específica y al rol de atención al cliente (si existe)
                mention_message = f"{message.author.mention} necesita asistencia. Por favor, revisa la información."
                if config.ATENCION_AL_CLIENTE_ROLE_ID:
                    human_contact_role = guild.get_role(config.ATENCION_AL_CLIENTE_ROLE_ID)
                    if human_contact_role:
                        mention_message = f"{human_contact_role.mention}, {mention_message}"
                
                if selected_human_id:
                    mention_message += f" <@{selected_human_id}>, te han seleccionado para este caso."
                
                await message.channel.send(mention_message)

                await message.channel.send(
                    f"¡Gracias por tus respuestas, {message.author.mention}! Nuestro equipo de atención al cliente revisará la información y se pondrá en contacto contigo pronto en este mismo chat."
                )

                # Limpiar el estado de la conversación para el usuario una vez finalizada
                del config.user_conversations[user_id]
            
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
