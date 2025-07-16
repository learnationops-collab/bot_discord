# Archivo: utils/helpers.py

def get_help_message(bot_commands: list) -> str:
    """
    Genera el mensaje de ayuda con los comandos disponibles del bot.

    Args:
        bot_commands (list): Una lista de objetos de comando del bot.

    Returns:
        str: El mensaje de ayuda formateado.
    """
    help_message = "**🤖 Comandos disponibles de Neurocogniciones Bot:**\n\n"

    for command in bot_commands:
        # Excluir el comando 'help' predeterminado de Discord.py si existe
        if command.name == 'help':
            continue

        help_message += f"`&{command.name}`"

        # Añadir el uso si está definido
        if command.usage:
            help_message += f" `{command.usage}`"

        # Añadir la descripción del comando
        help_message += f": {command.help}\n"

    help_message += "\n**Ejemplos de uso:**\n"
    # Se eliminó la referencia al comando '&reporte'
    help_message += "`&ayuda` - Muestra este mensaje de ayuda."
    return help_message

# Puedes añadir más funciones auxiliares aquí a medida que las necesites.
# Por ejemplo, funciones para formatear mensajes, validar entradas, etc.
