# Archivo: cogs/events.py

import discord
from discord.ext import commands
import config # Importa la configuración desde el módulo config
from utils import notion_utils # Importa el módulo de utilidades de Notion
from datetime import datetime

class Events(commands.Cog):
    """
    Cog que maneja los eventos principales del bot de Discord.
    """
    def __init__(self, bot):
        self.bot = bot
        self.tracked_channels = {
            config.COWORKING_CHANNEL_ID,
            config.REUNIONES_CHANNEL_ID,
        }

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Se ejecuta cuando el bot ha iniciado sesión y está listo.
        Imprime el nombre y la ID del bot en la consola.
        """
        print(f'Bot conectado como {self.bot.user}')
        print(f'ID del bot: {self.bot.user.id}')
        print('------')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Se dispara cuando un nuevo miembro se une al servidor.
        Crea un nuevo canal privado para el miembro y le da la bienvenida.
        """
        #print(f"[DEBUG] Nuevo miembro detectado: {member} (ID: {member.id})")
        if member.bot:
            #print("[DEBUG] El miembro es un bot, no se crea canal.")
            return

        guild = member.guild
        category_id = config.NUEVO_INGRESO_CATEGORY_ID
        neuro_team = config.NEURO_TEAM_ROLE_ID

        #print(f"[DEBUG] category_id: {category_id}, neuro_team: {neuro_team}")

        if not all([category_id, neuro_team]):
            print("Advertencia: La categoría de nuevo ingreso, el rol de atención al cliente o el rol de neuro team no están configurados.")
            return

        category = guild.get_channel(category_id)
        neuro_team_role = guild.get_role(neuro_team)

        #print(f"[DEBUG] category: {category}, neuro_team_role: {neuro_team_role}")

        if not category or not neuro_team_role:
            print("Advertencia: No se pudo encontrar la categoría o los roles especificados.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"{member.name}"
        try:
            #print(f"[DEBUG] Creando canal: {channel_name} en categoría: {category.name}")
            new_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            #print(f"[DEBUG] Canal creado: {new_channel.name} (ID: {new_channel.id})")
            welcome_message = (

                f"Holaa {member.mention} ✨ !\n\n"
                f"Con todo el {neuro_team_role.mention} te damos la bienvenida a tu Chat Personal!🙌 \n"

                "En este canal vas a poder conversar con todos los especialistas de Neurocogniciones y además te podremos dar un seguimiento mucho más personalizado!✅ \n\n"
                "Estamos para todo por aquí, literalmente cualquier duda, feedback, dificultad o barrera que se te presente, nos lo comunicas por aquí y nosotros estaremos al pendiente.🧐 \n\n"
                "➡️ Puedes usar el @ para mencionar a cualquier miembro, eso ayuda porque nos llega la notificación de que nos etiquetaron!💕"
            )
            await new_channel.send(welcome_message)
            #print("[DEBUG] Mensaje de bienvenida enviado correctamente.")
        except discord.Forbidden as e:
            print(f"Error de permisos al crear o enviar mensajes en el canal de bienvenida: {e}")
        except Exception as e:
            print(f"Ha ocurrido un error al crear el canal de bienvenida: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"[DEBUG] on_voice_state_update triggered for member: {member.name}")
        print(f"[DEBUG] Before channel: {before.channel}, After channel: {after.channel}")

        if member.bot:
            print("[DEBUG] Member is a bot, ignoring.")
            return

        # User joins a voice channel
        if before.channel is None and after.channel is not None:
            print(f"[DEBUG] User {member.name} joined voice channel {after.channel.name}")
            if after.channel.id in self.tracked_channels:
                print(f"[DEBUG] Channel {after.channel.name} is a tracked channel.")
                notion_utils.add_activity_log(
                    id_member=str(member.id),
                    nombre=member.name,
                    entrada=True,
                    canal=after.channel.name
                )
            else:
                print(f"[DEBUG] Channel {after.channel.name} is not a tracked channel.")

        # User leaves a voice channel
        if before.channel is not None and after.channel is None:
            print(f"[DEBUG] User {member.name} left voice channel {before.channel.name}")
            if before.channel.id in self.tracked_channels:
                print(f"[DEBUG] Channel {before.channel.name} is a tracked channel.")
                last_connection = notion_utils.find_last_connection(str(member.id), before.channel.name)
                print(f"[DEBUG] Last connection found: {last_connection}")
                tiempo_coneccion = None
                if last_connection:
                    connection_time_str = last_connection['properties']['fecha_hora']['date']['start']
                    print(f"[DEBUG] Connection time string: {connection_time_str}")
                    connection_time = datetime.fromisoformat(connection_time_str)
                    tiempo_coneccion = int((datetime.now() - connection_time).total_seconds())
                    print(f"[DEBUG] Calculated connection time: {tiempo_coneccion} seconds")

                notion_utils.add_activity_log(
                    id_member=str(member.id),
                    nombre=member.name,
                    entrada=False,
                    canal=before.channel.name,
                    tiempo_coneccion=tiempo_coneccion
                )
            else:
                print(f"[DEBUG] Channel {before.channel.name} is not a tracked channel.")

# La función setup es necesaria para que Discord.py cargue el cog
async def setup(bot):
    """
    Función de configuración para añadir el cog de Eventos al bot.
    """
    await bot.add_cog(Events(bot))