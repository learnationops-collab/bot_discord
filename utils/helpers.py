# Archivo: utils/helpers.py
# Contiene funciones auxiliares para el bot.

def get_help_message(bot_commands: list) -> str:
    """
    Genera el mensaje de ayuda con los comandos disponibles del bot.

    Args:
        bot_commands (list): Una lista de objetos de comando del bot.

    Returns:
        str: El mensaje de ayuda formateado.
    """
    help_message = "**🤖 Comandos disponibles de Neurocogniciones Bot:**\n\n"

    # Ordenar los comandos alfabéticamente por su nombre para una visualización consistente
    sorted_commands = sorted(bot_commands, key=lambda cmd: cmd.name)

    for command in sorted_commands:
        # Excluir el comando 'help' predeterminado de Discord.py si existe
        # y cualquier comando que esté marcado como oculto.
        if command.name == 'help' or command.hidden:
            continue

        help_message += f"`&{command.name}`"

        # Añadir el uso si está definido
        if command.usage:
            help_message += f" `{command.usage}`"

        # Añadir la descripción del comando
        help_message += f": {command.help}\n"

    # Si no hay comandos listados después de filtrar, proporcionar un mensaje alternativo
    if not any(cmd.name != 'help' and not cmd.hidden for cmd in bot_commands):
        help_message += "No hay comandos disponibles en este momento."

    return help_message

# Puedes añadir más funciones auxiliares aquí a medida que las necesites.
# Por ejemplo, funciones para formatear mensajes, validar entradas, etc.
