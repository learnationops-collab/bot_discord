# Archivo: cogs/human_interaction.py

import discord
from discord.ext import commands
import asyncio

import config # Importa la configuración para acceder a user_conversations y IDs
from views.main_menu import CloseTicketView # Importa la vista para cerrar el ticket

class HumanInteraction(commands.Cog):
    """
    Cog que maneja el flujo de interacción para "Hablar con un Humano",
    incluyendo preguntas y creación de canales de atención al cliente.
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

                # Definir permisos para el nuevo canal de atención al cliente
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    human_contact_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }

                try:
                    # Validar que el ID de la categoría de atención al cliente esté configurado
                    if config.ATENCION_AL_CLIENTE_CATEGORY_ID is None:
                        await message.channel.send("❌ Error de configuración: El ID de la categoría de Atención al Cliente no está definido en .env o no es válido. Contacta a un administrador.")
                        return
                    category = guild.get_channel(config.ATENCION_AL_CLIENTE_CATEGORY_ID)
                    if not category:
                        await message.channel.send("❌ Error: No se encontró la categoría de Atención al Cliente con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.")
                        return

                    channel_name = f"atencion-cliente-{message.author.name.lower().replace(' ', '-')}-{message.author.discriminator}"
                    new_human_channel = await category.create_text_channel(channel_name, overwrites=overwrites)
                    
                    config.user_conversations[user_id]['channel_id'] = new_human_channel.id # Guardar el ID del canal creado

                    await message.channel.send(
                        f"¡Gracias por tus respuestas, {message.author.mention}! He creado un canal privado para que nuestro equipo de atención al cliente te asista: {new_human_channel.mention}\n"
                        "Por favor, dirígete a ese canal. Un miembro del equipo revisará la información y se pondrá en contacto contigo pronto.\n\n"
                        "Para salir de este canal y cerrarlo cuando tu problema esté resuelto, usa el botón 'Cerrar Ticket' o el comando `&cerrar_ticket`."
                    )

                    # Publicar las respuestas en el nuevo canal de atención al cliente
                    answers_message = "**ℹ️ Información del Cliente para Atención al Cliente:**\n"
                    for ans in conversation_state['answers']:
                        answers_message += f"- {ans}\n"
                    answers_message += f"\nCliente: {message.author.mention}"
                    
                    await new_human_channel.send(answers_message, view=CloseTicketView(new_human_channel))
                    await new_human_channel.send(f"{human_contact_role.mention}, un nuevo cliente necesita asistencia. Por favor, revisen el canal.")

                except discord.Forbidden:
                    await message.channel.send("❌ No tengo los permisos necesarios para crear canales de atención al cliente. Por favor, asegúrate de que el bot tenga el permiso 'Gestionar Canales'.")
                except Exception as e:
                    await message.channel.send(f"❌ Ocurrió un error al crear el canal de atención al cliente: `{e}`")
                    print(f"Error al crear canal de atención al cliente: {e}")
            
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
