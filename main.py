import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pandas as pd
# import gspread # Librería para interactuar con Google Sheets (ahora opcional para la demo)

# Carga las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Configura los intents (permisos) para tu bot
# message_content es crucial para que el bot pueda leer el contenido de los mensajes (comandos)
# members es necesario si planeas implementar un mensaje automático al unirse un nuevo miembro
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Asegúrate de que este intent esté habilitado en el Portal de Desarrolladores de Discord

# Inicializa el bot con un prefijo de comando y los intents
bot = commands.Bot(command_prefix='&', intents=intents)

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
    # Puedes enviar un mensaje a un canal específico aquí al iniciar el bot,
    # por ejemplo, para un canal de bienvenida o de logs.
    # channel = bot.get_channel(YOUR_CHANNEL_ID) # Reemplaza YOUR_CHANNEL_ID con el ID de tu canal
    # if channel:
    #     await channel.send("¡Hola a todos! Estoy listo para ayudar. Usa `&iniciar` para comenzar.")

# --- Función de REPORTE ---
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
        # --- Generación de datos ficticios para demostración ---
        # Este bloque reemplaza la conexión a Google Sheets temporalmente.
        # Cuando tengas configurada tu cuenta de Google Cloud y el archivo service_account.json,
        # puedes eliminar o comentar este bloque y descomentar el código de gspread.
        data = {
            'Producto': ['Laptop', 'Monitor', 'Teclado', 'Mouse', 'Webcam', 'Auriculares', 'Impresora', 'SSD', 'Router', 'Micrófono'],
            'Ventas': [150, 80, 200, 350, 60, 120, 40, 90, 70, 110],
            'Precio_Unitario': [1200.50, 300.00, 75.25, 25.00, 50.00, 90.00, 250.00, 80.00, 60.00, 45.00],
            'Region': ['Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur'],
            'Estado': ['Activo', 'Inactivo', 'Activo', 'Activo', 'Inactivo', 'Activo', 'Activo', 'Activo', 'Inactivo', 'Activo'],
            'Stock': [10, 5, 20, 30, 8, 15, 3, 12, 7, 10]
        }
        df = pd.DataFrame(data)
        
        # Simular algunos valores nulos para el análisis
        df.loc[0, 'Precio_Unitario'] = None
        df.loc[3, 'Stock'] = None
        df.loc[6, 'Region'] = None

        # --- Fin de la generación de datos ficticios ---

        # El resto del análisis sigue siendo el mismo, ya que opera sobre el DataFrame 'df'.
        if df.empty:
            await ctx.send(f"La hoja '{sheet_name}' está vacía o no se encontraron registros con encabezados.")
            return

        # --- Realizar el análisis básico ---
        analysis_output = []
        analysis_output.append(f"**📊 Análisis de la hoja '{sheet_name}' (Datos Ficticios):**")
        analysis_output.append(f"- **Filas:** {len(df)}")
        analysis_output.append(f"- **Columnas:** {len(df.columns)}")
        analysis_output.append(f"- **Nombres de Columnas:** {', '.join(df.columns)}")
        
        # Contar valores nulos por columna
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0: # Si hay al menos un valor nulo en alguna columna
            analysis_output.append("\n- **Valores Nulos por Columna:**")
            for col, count in null_counts.items():
                if count > 0:
                    analysis_output.append(f"  - `{col}`: {count}")
        else:
            analysis_output.append("\n- No se encontraron valores nulos.")

        # Generar estadísticas descriptivas para columnas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            analysis_output.append("\n- **Estadísticas Descriptivas (Columnas Numéricas):**")
            description = df[numeric_cols].describe().to_string()
            # Limitar la longitud de la descripción para ajustarse al límite de mensajes de Discord (2000 caracteres)
            if len(description) > 1800: # Dejamos un margen para el resto del mensaje
                description = description[:1800] + "\n... (recortado) ..."
            analysis_output.append(f"```\n{description}\n```") # Formato de bloque de código para legibilidad
        else:
            analysis_output.append("\n- No se encontraron columnas numéricas para estadísticas descriptivas.")
            
        # Mostrar valores únicos para columnas con un número limitado de categorías
        analysis_output.append("\n- **Valores Únicos en Columnas Categóricas (hasta 10):**")
        found_categorical = False
        for col in df.columns:
            unique_vals = df[col].nunique()
            # Si tiene entre 2 y 10 valores únicos (más de 1 para evitar columnas con un solo valor, menos de 10 para no saturar)
            if unique_vals > 1 and unique_vals <= 10: 
                analysis_output.append(f"  - `{col}`: {', '.join(map(str, df[col].unique()))}")
                found_categorical = True
        if not found_categorical:
            analysis_output.append("  - No se encontraron columnas categóricas con pocos valores únicos.")


        # Unir todas las partes del análisis en un solo mensaje
        response = "\n".join(analysis_output)
        await ctx.send(response)

    except Exception as e:
        # Captura cualquier otro error inesperado
        await ctx.send(f"❌ Ocurrió un error al procesar el reporte (con datos ficticios): `{e}`.")
        print(f"Error detallado en la función reporte (ficticio): {e}") # Imprime el error completo en la consola para depuración

# --- Reporte sin argumentos ---
@reporte.error
async def reporte_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Error: Faltan argumentos. Usa `&reporte <link_google_sheets> <nombre_hoja>` para generar el reporte.")

# --- Función de AYUDA personalizada ---
@bot.command(name='ayuda', help='Muestra información sobre los comandos disponibles y cómo usarlos.')
async def ayuda(ctx):
    """
    Muestra los comandos disponibles del bot y una breve descripción de cómo usarlos.
    """
    help_message = "**🤖 Comandos disponibles de Neurocogniciones Bot:**\n\n"
    
    # Itera sobre todos los comandos registrados en el bot
    for command in bot.commands:
        # Excluye el comando 'help' predeterminado de Discord si existe, para evitar duplicidad
        if command.name == 'help':
            continue
        
        help_message += f"`&{command.name}`" # Muestra el prefijo y el nombre del comando
        
        # Si el comando tiene un uso definido (ej. argumentos esperados), lo añade
        if command.usage:
            help_message += f" `{command.usage}`"
        
        help_message += f": {command.help}\n" # Añade la descripción del comando

    help_message += "\n**Ejemplos de uso:**\n"
    help_message += "`&reporte <link_google_sheets> <nombre_hoja>` - Genera un análisis de la hoja 'MiHoja' en el Google Sheet proporcionado (actualmente con datos ficticios).\n"
    help_message += "`&ayuda` - Muestra este mensaje de ayuda."

    await ctx.send(help_message)

# --- Limpiar mensajes ---
@bot.command(name='limpiar', help='Elimina un número específico de mensajes del canal.')
async def limpiar(ctx, cantidad: int):
    """
    Elimina un número específico de mensajes del canal.
    """
    await ctx.channel.purge(limit=cantidad + 1) # Elimina la cantidad de mensajes especificada más el mensaje de inicio
    await ctx.send(f"✅ Se eliminaron {cantidad} mensajes del canal.", delete_after=3) # Respuesta breve que se eliminará después de 5 segundos

@limpiar.error
async def limpiar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Error: Faltan argumentos. Usa `&limpiar <cantidad>` para eliminar un número específico de mensajes.")

# --- NUEVAS FUNCIONALIDADES: Interacción con botones ---

# Clase para la vista de selección de recursos
class ResourcesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180) # La vista expira después de 3 minutos de inactividad
        # Los botones se añaden automáticamente a través de los decoradores @discord.ui.button
        # Por lo tanto, no es necesario usar self.add_item() aquí.
        # self.add_item(discord.ui.Button(label="Guías de Estudio", style=discord.ButtonStyle.secondary, custom_id="study_guides"))
        # self.add_item(discord.ui.Button(label="Material de Apoyo", style=discord.ButtonStyle.secondary, custom_id="support_material"))
        # self.add_item(discord.ui.Button(label="Preguntas Frecuentes (FAQ)", style=discord.ButtonStyle.secondary, custom_id="faq"))

    async def on_timeout(self):
        # Deshabilita los botones cuando la vista expira para evitar interacciones con botones inactivos
        for item in self.children:
            item.disabled = True
        # Edita el mensaje original para indicar que la interacción ha terminado
        if hasattr(self, 'message'):
            await self.message.edit(content="La selección de recursos ha expirado. Si necesitas más ayuda, usa `&iniciar` de nuevo.", view=self)

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
        # Opcional: Deshabilitar los botones después de la selección para evitar múltiples clics
        # for item in self.children:
        #     item.disabled = True
        # await interaction.message.edit(view=self)

    @discord.ui.button(label="Material de Apoyo", style=discord.ButtonStyle.secondary, custom_id="support_material")
    async def support_material_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Material de Apoyo'."""
        await interaction.response.send_message(
            "Accede a nuestro material de apoyo complementario aquí: "
            "[Colección de Artículos y Videos](https://www.ejemplo.com/material_apoyo)\n"
            "Este material está diseñado para reforzar tu aprendizaje.",
            ephemeral=False
        )
        # Opcional: Deshabilitar los botones después de la selección para evitar múltiples clics
        # for item in self.children:
        #     item.disabled = True
        # await interaction.message.edit(view=self)

    @discord.ui.button(label="Preguntas Frecuentes (FAQ)", style=discord.ButtonStyle.secondary, custom_id="faq")
    async def faq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Preguntas Frecuentes (FAQ)'."""
        await interaction.response.send_message(
            "Consulta nuestras Preguntas Frecuentes para encontrar respuestas rápidas a las dudas más comunes: "
            "[Ir a la Sección de Preguntas Frecuentes](https://www.ejemplo.com/faq_neurocogniciones)\n"
            "Es posible que tu pregunta ya esté resuelta allí.",
            ephemeral=False
        )
        # Opcional: Deshabilitar los botones después de la selección para evitar múltiples clics
        # for item in self.children:
        #     item.disabled = True
        # await interaction.message.edit(view=self)

# Clase para el menú principal con botones
class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180) # La vista expira después de 3 minutos de inactividad
        # Los botones se añaden automáticamente a través de los decoradores @discord.ui.button

    async def on_timeout(self):
        """Se llama cuando la vista expira por inactividad."""
        # Deshabilita todos los botones de la vista
        for item in self.children:
            item.disabled = True
        # Edita el mensaje original para indicar que la interacción ha expirado
        if hasattr(self, 'message'):
            await self.message.edit(content="La interacción ha expirado. Si necesitas ayuda, usa `&iniciar` de nuevo.", view=self)

    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help")
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'."""
        await interaction.response.send_message(
            "Por favor, describe tu problema técnico brevemente. "
            "Nuestro equipo revisará tu caso y te contactará si es necesario. "
            "Puedes escribir tu problema directamente en el chat.",
            ephemeral=False
        )
        # Para una implementación más avanzada, aquí podrías:
        # 1. Usar un `discord.ui.Modal` para recopilar una descripción estructurada.
        # 2. Usar `bot.wait_for('message')` para esperar la siguiente respuesta del usuario en el canal.
        # 3. Integrar con una base de conocimientos o un modelo de lenguaje para respuestas automáticas a problemas comunes.

    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource")
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'."""
        # Crea una nueva vista con opciones de recursos y la envía
        resources_view = ResourcesView()
        # Asigna el mensaje para que on_timeout pueda editarlo
        resources_view.message = await interaction.response.send_message(
            "¿Qué tipo de recurso necesitas?",
            view=resources_view,
            ephemeral=False
        )

    @discord.ui.button(label="Hablar con un Humano", style=discord.ButtonStyle.danger, custom_id="human_contact")
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'."""
        # Inicia el flujo de preguntas para el contacto humano
        await interaction.response.send_message(
            "Para poder ayudarte mejor y que un miembro de nuestro equipo te contacte, "
            "por favor, responde a las siguientes preguntas en mensajes separados en este chat:",
            ephemeral=False
        )
        # Usamos followups para enviar cada pregunta de forma secuencial
        await interaction.followup.send("1. ¿Cuál es el problema principal que tienes?", ephemeral=False)
        await interaction.followup.send("2. ¿Qué soluciones has intentado hasta ahora?", ephemeral=False)
        await interaction.followup.send("3. ¿Estás comprometido/a a seguir las indicaciones para resolverlo?", ephemeral=False)
        await interaction.followup.send(
            "Una vez que hayas respondido a estas preguntas, un miembro de nuestro equipo "
            "revisará tu caso y se pondrá en contacto contigo pronto. ¡Gracias por tu paciencia!",
            ephemeral=False
        )
        # Aquí, en una implementación real, podrías registrar estas preguntas y las respuestas
        # del usuario en una base de datos o enviarlas a un canal de soporte específico para los CSM.

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
# Asegúrate de que tu archivo .env contenga una línea como: TOKEN=TU_TOKEN_DE_DISCORD
bot.run(TOKEN)
