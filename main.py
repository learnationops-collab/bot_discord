import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pandas as pd
import asyncio

# Carga las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# --- CONFIGURACIÓN DE IDs DE CANALES, CATEGORÍAS Y ROLES (¡REEMPLAZA ESTOS VALORES EN TU ARCHIVO .ENV!) ---
# PARA OBTENER EL ID: Activa el Modo Desarrollador en Discord (Ajustes de Usuario -> Avanzado),
# luego haz clic derecho en el canal/categoría/rol y selecciona "Copiar ID".
NUEVO_INGRESO_CHANNEL_ID = int(os.getenv('NUEVO_INGRESO_CHANNEL_ID')) if os.getenv('NUEVO_INGRESO_CHANNEL_ID') else None
AYUDA_TECNICA_CATEGORY_ID = int(os.getenv('AYUDA_TECNICA_CATEGORY_ID')) if os.getenv('AYUDA_TECNICA_CATEGORY_ID') else None
ATENCION_AL_CLIENTE_CATEGORY_ID = int(os.getenv('ATENCION_AL_CLIENTE_CATEGORY_ID')) if os.getenv('ATENCION_AL_CLIENTE_CATEGORY_ID') else None
SOPORTE_TECNICO_ROLE_ID = int(os.getenv('SOPORTE_TECNICO_ROLE_ID')) if os.getenv('SOPORTE_TECNICO_ROLE_ID') else None
ATENCION_AL_CLIENTE_ROLE_ID = int(os.getenv('ATENCION_AL_CLIENTE_ROLE_ID')) if os.getenv('ATENCION_AL_CLIENTE_ROLE_ID') else None

# Configura los intents (permisos) para tu bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Necesario para on_member_join

# Inicializa el bot con un prefijo de comando y los intents
bot = commands.Bot(command_prefix='&', intents=intents)

# Diccionario para almacenar el estado de las conversaciones de "Hablar con un Humano"
# Formato: {user_id: {'state': int, 'answers': [], 'channel_id': None}}
# state: 0 = no en conversación, 1 = esperando respuesta a Pregunta 1, etc.
user_conversations = {}

# --- Evento que se dispara cuando el bot está listo y conectado a Discord ---
@bot.event
async def on_ready():
    """
    Se ejecuta cuando el bot ha iniciado sesión y está listo.
    Imprime el nombre y la ID del bot en la consola.
    """
    print(f'Bot conectado como {bot.user}')
    print(f'ID del bot: {bot.user.id}')
    print('------')

# --- Función de REPORTE (sin cambios) ---
@bot.command(name='reporte', help='Genera un análisis básico de una tabla (actualmente con datos ficticios).')
async def reporte(ctx, sheets_link: str, sheet_name: str):
    """
    Genera un análisis básico de una tabla de Google Sheets.
    Requiere un enlace de Google Sheets y el nombre de la hoja.
    Actualmente, utiliza datos ficticios para demostración.

    Argumentos:
        ctx (commands.Context): El contexto del comando.
        sheets_link (str): El enlace compartido (URL) del Google Sheet (no usado con datos ficticios).
        sheet_name (str): El nombre exacto de la hoja dentro del Google Sheet (no usado con datos ficticios).
    """
    await ctx.send("Procesando el reporte con **datos ficticios** para demostración. Por favor, espera...")
    try:
        data = {
            'Producto': ['Laptop', 'Monitor', 'Teclado', 'Mouse', 'Webcam', 'Auriculares', 'Impresora', 'SSD', 'Router', 'Micrófono'],
            'Ventas': [150, 80, 200, 350, 60, 120, 40, 90, 70, 110],
            'Precio_Unitario': [1200.50, 300.00, 75.25, 25.00, 50.00, 90.00, 250.00, 80.00, 60.00, 45.00],
            'Region': ['Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur'],
            'Estado': ['Activo', 'Inactivo', 'Activo', 'Activo', 'Inactivo', 'Activo', 'Activo', 'Activo', 'Inactivo', 'Activo'],
            'Stock': [10, 5, 20, 30, 8, 15, 3, 12, 7, 10]
        }
        df = pd.DataFrame(data)
        
        df.loc[0, 'Precio_Unitario'] = None
        df.loc[3, 'Stock'] = None
        df.loc[6, 'Region'] = None

        if df.empty:
            await ctx.send(f"La hoja '{sheet_name}' está vacía o no se encontraron registros con encabezados.")
            return

        analysis_output = []
        analysis_output.append(f"**📊 Análisis de la hoja '{sheet_name}' (Datos Ficticios):**")
        analysis_output.append(f"- **Filas:** {len(df)}")
        analysis_output.append(f"- **Columnas:** {len(df.columns)}")
        analysis_output.append(f"- **Nombres de Columnas:** {', '.join(df.columns)}")
        
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            analysis_output.append("\n- **Valores Nulos por Columna:**")
            for col, count in null_counts.items():
                if count > 0:
                    analysis_output.append(f"  - `{col}`: {count}")
        else:
            analysis_output.append("\n- No se encontraron valores nulos.")

        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            analysis_output.append("\n- **Estadísticas Descriptivas (Columnas Numéricas):**")
            description = df[numeric_cols].describe().to_string()
            if len(description) > 1800:
                description = description[:1800] + "\n... (recortado) ..."
            analysis_output.append(f"```\n{description}\n```")
        else:
            analysis_output.append("\n- No se encontraron columnas numéricas para estadísticas descriptivas.")
            
        analysis_output.append("\n- **Valores Únicos en Columnas Categóricas (hasta 10):**")
        found_categorical = False
        for col in df.columns:
            unique_vals = df[col].nunique()
            if unique_vals > 1 and unique_vals <= 10: 
                analysis_output.append(f"  - `{col}`: {', '.join(map(str, df[col].unique()))}")
                found_categorical = True
        if not found_categorical:
            analysis_output.append("  - No se encontraron columnas categóricas con pocos valores únicos.")

        response = "\n".join(analysis_output)
        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error al procesar el reporte (con datos ficticios): `{e}`.")
        print(f"Error detallado en la función reporte (ficticio): {e}")

@reporte.error
async def reporte_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Error: Faltan argumentos. Usa `&reporte <link_google_sheets> <nombre_hoja>` para generar el reporte.")

# --- Función auxiliar para generar el mensaje de ayuda ---
def _get_help_message():
    """
    Genera el mensaje de ayuda con los comandos disponibles del bot.
    """
    help_message = "**🤖 Comandos disponibles de Neurocogniciones Bot:**\n\n"
    
    for command in bot.commands:
        if command.name == 'help':
            continue
        
        help_message += f"`&{command.name}`"
        
        if command.usage:
            help_message += f" `{command.usage}`"
        
        help_message += f": {command.help}\n"

    help_message += "\n**Ejemplos de uso:**\n"
    help_message += "`&reporte <link_google_sheets> <nombre_hoja>` - Genera un análisis de la hoja 'MiHoja' en el Google Sheet proporcionado (actualmente con datos ficticios).\n"
    help_message += "`&ayuda` - Muestra este mensaje de ayuda."
    return help_message

# --- Función de AYUDA personalizada (sin cambios) ---
@bot.command(name='ayuda', help='Muestra información sobre los comandos disponibles y cómo usarlos.')
async def ayuda(ctx):
    """
    Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos.
    """
    await ctx.send(_get_help_message())

# --- Limpiar mensajes (sin cambios) ---
@bot.command(name='limpiar', help='Elimina un número específico de mensajes del canal.')
async def limpiar(ctx, cantidad: int):
    """
    Elimina un número específico de mensajes del canal.
    """
    await ctx.channel.purge(limit=cantidad + 1)
    await ctx.send(f"✅ Se eliminaron {cantidad} mensajes del canal.", delete_after=3)

@limpiar.error
async def limpiar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Error: Faltan argumentos. Usa `&limpiar <cantidad>` para eliminar un número específico de mensajes.")

# --- NUEVAS FUNCIONALIDADES: Interacción con botones ---

# Clase para la vista de selección de recursos
class ResourcesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        # Los botones se añaden automáticamente a través de los decoradores @discord.ui.button

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message') and self.message:
            try:
                await self.message.edit(content="La selección de recursos ha expirado. Si necesitas más ayuda, usa `&iniciar` de nuevo.", view=self)
            except discord.NotFound:
                print("Mensaje de ResourcesView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de ResourcesView en timeout: {e}")


    @discord.ui.button(label="Guías de Estudio", style=discord.ButtonStyle.secondary, custom_id="study_guides")
    async def study_guides_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Guías de Estudio'."""
        await interaction.response.send_message(
            "Aquí tienes algunas guías de estudio útiles: "
            "[Guía 1 sobre Neurociencia Cognitiva](https://www.ejemplo.com/guia1), "
            "[Guía 2 sobre Métodos de Estudio Efectivos](https://www.ejemplo.com/guia2)\n"
            "¡Esperamos que te sean de gran ayuda!",
            ephemeral=False # False para que todos en el canal puedan ver la respuesta
        )

    @discord.ui.button(label="Material de Apoyo", style=discord.ButtonStyle.secondary, custom_id="support_material")
    async def support_material_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Material de Apoyo'."""
        await interaction.response.send_message(
            "Accede a nuestro material de apoyo complementario aquí: "
            "[Colección de Artículos y Videos](https://www.ejemplo.com/material_apoyo)\n"
            "Este material está diseñado para reforzar tu aprendizaje.",
            ephemeral=False
        )

    @discord.ui.button(label="Preguntas Frecuentes (FAQ)", style=discord.ButtonStyle.secondary, custom_id="faq")
    async def faq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Preguntas Frecuentes (FAQ)'."""
        await interaction.response.send_message(
            "Consulta nuestras Preguntas Frecuentes para encontrar respuestas rápidas a las dudas más comunes: "
            "[Ir a la Sección de Preguntas Frecuentes](https://www.ejemplo.com/faq_neurocogniciones)\n"
            "Es posible que tu pregunta ya esté resuelta allí.",
            ephemeral=False
        )

# Clase para la vista del menú principal
class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
            await self.message.edit(content="La interacción ha expirado. Si necesitas ayuda, usa `&iniciar` de nuevo.", view=self)

    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help")
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'.
        Crea un canal privado de ayuda técnica para el usuario.
        """
        user = interaction.user
        guild = interaction.guild

        # Validar que el ID del rol de soporte técnico esté configurado
        if SOPORTE_TECNICO_ROLE_ID is None:
            await interaction.response.send_message("❌ Error de configuración: El ID del rol de Soporte Técnico no está definido en .env o no es válido. Contacta a un administrador.", ephemeral=True)
            return
        support_role = guild.get_role(SOPORTE_TECNICO_ROLE_ID)
        if not support_role:
            await interaction.response.send_message("❌ Error: No se encontró el rol de Soporte Técnico con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.", ephemeral=True)
            return

        # Definir permisos para el nuevo canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Nadie puede ver el canal por defecto
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El usuario puede ver y escribir
            bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), # El bot puede ver y escribir
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True) # El rol de soporte puede ver y escribir
        }

        try:
            # Validar que el ID de la categoría de ayuda técnica esté configurado
            if AYUDA_TECNICA_CATEGORY_ID is None:
                await interaction.response.send_message("❌ Error de configuración: El ID de la categoría de Ayuda Técnica no está definido en .env o no es válido. Contacta a un administrador.", ephemeral=True)
                return
            category = guild.get_channel(AYUDA_TECNICA_CATEGORY_ID)
            if not category:
                await interaction.response.send_message("❌ Error: No se encontró la categoría de Ayuda Técnica con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.", ephemeral=True)
                return

            channel_name = f"ayuda-tecnica-{user.name.lower().replace(' ', '-')}-{user.discriminator}"
            new_channel = await category.create_text_channel(channel_name, overwrites=overwrites)

            await interaction.response.send_message(
                f"¡Hola {user.mention}! He creado un canal privado para tu soporte técnico: {new_channel.mention}\n"
                "Por favor, dirígete a ese canal para describir tu problema. "
                "Un miembro de nuestro equipo de soporte técnico te ayudará pronto.\n\n"
                "Para salir de este canal y cerrarlo cuando tu problema esté resuelto, usa el botón 'Cerrar Ticket' o el comando `&cerrar_ticket`.",
                ephemeral=False # Para que todos vean que se creó el ticket
            )

            # Enviar mensaje de bienvenida e instrucciones en el nuevo canal
            welcome_message_in_channel = (
                f"¡Bienvenido/a a tu canal de soporte técnico, {user.mention}!\n"
                "Aquí puedes describir tu problema técnico en detalle. Por favor, sé lo más específico posible.\n"
                "Un miembro del equipo de soporte revisará tu caso.\n\n"
                "**Indicaciones de uso:**\n"
                "• Describe tu problema claramente.\n"
                "• Menciona los pasos que ya has intentado para solucionarlo.\n"
                "• Si es posible, adjunta capturas de pantalla o videos.\n\n"
                "Cuando tu problema esté resuelto o desees cerrar este canal, por favor, usa el botón de abajo:\n"
            )
            await new_channel.send(welcome_message_in_channel, view=CloseTicketView(new_channel))

        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo los permisos necesarios para crear canales. Por favor, asegúrate de que el bot tenga el permiso 'Gestionar Canales'.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Ocurrió un error al crear el canal de ayuda técnica: `{e}`", ephemeral=True)
            print(f"Error al crear canal de ayuda técnica: {e}")


    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource")
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'."""
        resources_view = ResourcesView()
        # Envía la respuesta inicial y luego obtiene el objeto Message para poder editarlo después
        await interaction.response.send_message(
            "¿Qué tipo de recurso necesitas?",
            view=resources_view,
            ephemeral=False
        )
        resources_view.message = await interaction.original_response() # <-- CORRECCIÓN AQUÍ

    @discord.ui.button(label="Hablar con un Humano", style=discord.ButtonStyle.danger, custom_id="human_contact")
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'.
        Inicia un flujo de preguntas para recopilar información.
        """
        user_id = interaction.user.id
        if user_id in user_conversations and user_conversations[user_id]['state'] != 0:
            await interaction.response.send_message("Ya tienes una conversación en curso para contactar a un humano. Por favor, completa esa conversación o espera.", ephemeral=True)
            return

        user_conversations[user_id] = {'state': 1, 'answers': [], 'channel_id': None}
        await interaction.response.send_message(
            "Para poder ayudarte mejor y que un miembro de nuestro equipo te contacte, "
            "por favor, responde a la primera pregunta en este chat:\n\n"
            "**1. ¿Cuál es el problema principal que tienes?**",
            ephemeral=False
        )

# Clase para el botón de cerrar ticket (reutilizable)
class CloseTicketView(discord.ui.View):
    def __init__(self, channel_to_close: discord.TextChannel):
        super().__init__(timeout=300) # 5 minutos de timeout
        self.channel_to_close = channel_to_close

    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cierra el canal de soporte actual."""
        await interaction.response.send_message("Cerrando este canal de soporte en 5 segundos...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await self.channel_to_close.delete()
        except discord.Forbidden:
            await interaction.followup.send("❌ No tengo permisos para eliminar este canal. Por favor, contacta a un administrador.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error al intentar cerrar el canal: `{e}`", ephemeral=True)

# --- Manejo de mensajes para el flujo "Hablar con un Humano" ---
@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return

    user_id = message.author.id
    # Si el usuario está en una conversación de "Hablar con un Humano"
    if user_id in user_conversations and user_conversations[user_id]['state'] > 0:
        conversation_state = user_conversations[user_id]
        current_question_number = conversation_state['state']
        
        # Almacenar la respuesta actual
        conversation_state['answers'].append(f"Pregunta {current_question_number}: {message.content}")

        if current_question_number == 1:
            conversation_state['state'] = 2
            await message.channel.send("**2. ¿Qué soluciones has intentado hasta ahora?**")
        elif current_question_number == 2:
            conversation_state['state'] = 3
            await message.channel.send("**3. ¿Estás comprometido/a a seguir las indicaciones para resolverlo?**")
        elif current_question_number == 3:
            # Todas las preguntas respondidas, crear canal de atención al cliente
            user_conversations[user_id]['state'] = 0 # Reiniciar estado
            
            guild = message.guild

            # Validar que el ID del rol de atención al cliente esté configurado
            if ATENCION_AL_CLIENTE_ROLE_ID is None:
                await message.channel.send("❌ Error de configuración: El ID del rol de Atención al Cliente no está definido en .env o no es válido. Contacta a un administrador.")
                return
            human_contact_role = guild.get_role(ATENCION_AL_CLIENTE_ROLE_ID)
            if not human_contact_role:
                await message.channel.send("❌ Error: No se encontró el rol de Atención al Cliente con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.")
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                human_contact_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            try:
                # Validar que el ID de la categoría de atención al cliente esté configurado
                if ATENCION_AL_CLIENTE_CATEGORY_ID is None:
                    await message.channel.send("❌ Error de configuración: El ID de la categoría de Atención al Cliente no está definido en .env o no es válido. Contacta a un administrador.")
                    return
                category = guild.get_channel(ATENCION_AL_CLIENTE_CATEGORY_ID)
                if not category:
                    await message.channel.send("❌ Error: No se encontró la categoría de Atención al Cliente con el ID proporcionado. Por favor, verifica el archivo .env o contacta a un administrador.")
                    return

                channel_name = f"atencion-cliente-{message.author.name.lower().replace(' ', '-')}-{message.author.discriminator}"
                new_human_channel = await category.create_text_channel(channel_name, overwrites=overwrites)
                
                user_conversations[user_id]['channel_id'] = new_human_channel.id # Guardar el ID del canal creado

                # MENSAJE CORREGIDO: Eliminar 'ephemeral=False' de message.channel.send
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
    
    # Procesar comandos si el mensaje no es parte de un flujo de conversación
    await bot.process_commands(message)


# --- NUEVA FUNCIONALIDAD: Mensaje de bienvenida automático en canal 'nuevo_ingreso' ---
@bot.event
async def on_member_join(member):
    """
    Se dispara cuando un nuevo miembro se une al servidor.
    Envía un mensaje de bienvenida y las indicaciones de uso del bot
    si el miembro se une al canal 'nuevo_ingreso'.
    """
    if member.bot:
        return

    # Validar que el ID del canal de nuevo ingreso esté configurado
    if NUEVO_INGRESO_CHANNEL_ID is None:
        print("Advertencia: NUEVO_INGRESO_CHANNEL_ID no está definido en .env o no es válido. La bienvenida automática no funcionará.")
        return

    channel = bot.get_channel(NUEVO_INGRESO_CHANNEL_ID)
    if channel:
        welcome_message = (
            f"¡Bienvenido/a al servidor de Neurocogniciones, {member.mention}!\n"
            "Soy el Bot de Neurocogniciones y estoy aquí para ayudarte.\n\n"
            "Para comenzar, puedes usar el comando `&iniciar` para interactuar con nuestros menús de ayuda.\n\n"
            "Aquí tienes una guía rápida de cómo usarme:\n"
        )
        help_content = _get_help_message()
        await channel.send(welcome_message + help_content)
    else:
        print(f"Advertencia: No se encontró el canal con ID {NUEVO_INGRESO_CHANNEL_ID}. La bienvenida automática no funcionará.")


# Comando para iniciar la interacción con el bot
@bot.command(name='iniciar', help='Inicia la interacción guiada con el bot.')
async def iniciar(ctx):
    """
    Inicia la interacción guiada con el bot, presentando opciones con botones.
    """
    view = MainMenuView()
    # Almacena el mensaje para que la vista pueda editarlo en caso de timeout
    view.message = await ctx.send("Hola, soy el Bot de Neurocogniciones. ¿Cómo puedo ayudarte hoy?", view=view)

# --- Inicia el bot con el token cargado ---
bot.run(TOKEN)
