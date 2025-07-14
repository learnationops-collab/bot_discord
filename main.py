import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pandas as pd
import gspread # Librería para interactuar con Google Sheets (ahora opcional para la demo)

# Carga las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Configura los intents (permisos) para tu bot
# message_content es crucial para que el bot pueda leer el contenido de los mensajes (comandos)
intents = discord.Intents.default()
intents.message_content = True

# Inicializa el bot con un prefijo de comando y los intents
bot = commands.Bot(command_prefix='&', intents=intents)

# Evento que se dispara cuando el bot está listo y conectado a Discord
@bot.event
async def on_ready():
    """
    Se ejecuta cuando el bot ha iniciado sesión y está listo.
    Imprime el nombre y la ID del bot en la consola.
    """
    print(f'Bot conectado como {bot.user}')
    print(f'ID del bot: {bot.user.id}')
    print('------')

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

# Inicia el bot con el token cargado
bot.run(TOKEN)
