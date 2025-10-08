# cogs/scheduled_message_task.py

import discord, discord.errors
from discord.ext import commands, tasks
import datetime
import pytz
from database.db_manager import DBManager
from utils import notion_utils
import config
from collections import defaultdict

class ScheduledMessageTask(commands.Cog):
    """
    Un cog que revisa periódicamente la base de datos de Notion en busca de mensajes
    programados para enviar a canales específicos de Discord.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()
        self.timezone = pytz.timezone('UTC')
        self.send_scheduled_messages.start()
        self.daily_activity_report.start()

    def cog_unload(self):
        self.send_scheduled_messages.cancel()
        self.daily_activity_report.cancel()

    @tasks.loop(seconds=60)  # Revisa cada 60 segundos
    async def send_scheduled_messages(self):
        """
        Tarea principal que se ejecuta en bucle para buscar y enviar mensajes.
        """
        #print("\nBuscando mensajes programados...")
        now_utc = datetime.datetime.now(self.timezone)
        
        try:
            messages_to_send = self.db_manager.get_scheduled_messages()
            if not messages_to_send:
                #print("No se encontraron mensajes pendientes.")
                return

            #print(f"\nSe encontraron {len(messages_to_send)} mensajes activos y pendientes.")

            for msg in messages_to_send:
                try:
                    scheduled_time_aware = datetime.datetime.fromisoformat(msg['fecha'])

                    if now_utc >= scheduled_time_aware:
                        #print(f"  - Procesando mensaje '{msg['page_id']}' para el canal {msg['canal_id']}")
                        channel = self.bot.get_channel(msg['canal_id'])
                        if channel:
                            try:
                                await channel.send(msg['cuerpo'])
                                #print(f"    ✅ Mensaje enviado al canal '{channel.name}'.")
                                
                                # --- Lógica de Frecuencia ---
                                frecuencia = msg.get("frecuencia", "unico").lower()
                                page_id = msg['page_id']

                                if frecuencia == "diario":
                                    new_date = scheduled_time_aware + datetime.timedelta(days=1)
                                    #print(f"    - Frecuencia: Diario. Reprogramando para {new_date.strftime('%Y-%m-%d')}")
                                    self.db_manager.reschedule_message(page_id, new_date)

                                elif frecuencia == "semanal":
                                    new_date = scheduled_time_aware + datetime.timedelta(weeks=1)
                                    #print(f"    - Frecuencia: Semanal. Reprogramando para {new_date.strftime('%Y-%m-%d')}")
                                    self.db_manager.reschedule_message(page_id, new_date)

                                else: # "unico" o cualquier otro valor
                                    #print("    - Frecuencia: Único. Marcando como enviado.")
                                    self.db_manager.mark_message_as_sent(page_id)

                            except discord.errors.Forbidden:
                                #print(f"    ❌ Error de permisos: No se pudo enviar el mensaje al canal '{channel.name}' (ID: {msg['canal_id']}).")
                                #print("    - El bot no tiene los permisos necesarios en este canal.")
                                #print("    - Marcando como enviado para no reintentar.")
                                self.db_manager.mark_message_as_sent(msg['page_id'])
                        
                        else:
                            #print(f"    ❌ Error: No se encontró el canal con ID {msg['canal_id']}.")
                            #print("    - Marcando como enviado para no reintentar.")
                            self.db_manager.mark_message_as_sent(msg['page_id'])

                except Exception as e:
                    print(f"❌ Error procesando un mensaje individual (Page ID: {msg.get('page_id', 'N/A')}): {e}")

        except Exception as e:
            print(f"❌ Error general en la tarea de envío de mensajes: {e}")

    @tasks.loop(time=datetime.time(hour=22, minute=0, tzinfo=pytz.timezone('America/Argentina/Buenos_Aires')))
    async def daily_activity_report(self):
        """
        Genera y envía un reporte diario de actividad en los canales de voz.
        """
        print("Generando reporte diario de actividad...")
        logs = notion_utils.get_activity_logs_for_today()
        if not logs:
            print("No hay actividad para reportar hoy.")
            return

        user_time = defaultdict(lambda: defaultdict(datetime.timedelta))
        user_connections = {}

        for log in sorted(logs, key=lambda x: x['properties']['fecha_hora']['date']['start']):
            props = log['properties']
            user_id = props['id_member']['title'][0]['text']['content']
            channel_name = props['canal']['rich_text'][0]['text']['content']
            timestamp = datetime.datetime.fromisoformat(props['fecha_hora']['date']['start'])
            is_entry = props['entrada']['checkbox']

            if is_entry:
                user_connections[(user_id, channel_name)] = timestamp
            elif (user_id, channel_name) in user_connections:
                connection_time = user_connections.pop((user_id, channel_name))
                duration = timestamp - connection_time
                user_time[user_id][channel_name] += duration

        report_channel = self.bot.get_channel(config.TEST_CHANNEL_ID)
        if not report_channel:
            print(f"Error: No se encontró el canal de reporte con ID {config.TEST_CHANNEL_ID}")
            return

        embed = discord.Embed(title="Reporte de Actividad Diario", color=discord.Color.blue())
        for user_id, channels in user_time.items():
            try:
                member = await self.bot.fetch_user(int(user_id))
                user_name = member.display_name
            except discord.NotFound:
                user_name = f"Usuario: <@{user_id}>"
            
            report_lines = []
            for channel, total_time in channels.items():
                hours, remainder = divmod(total_time.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                report_lines.append(f"- **{channel}**: {int(hours)}h {int(minutes)}m")
            
            if report_lines:
                embed.add_field(name=user_name, value="\n".join(report_lines), inline=False)

        if embed.fields:
            await report_channel.send(embed=embed)
        else:
            await report_channel.send("No se registró actividad medible hoy.")

    @send_scheduled_messages.before_loop
    async def before_task_starts(self):
        """
        Se asegura de que el bot esté listo y el cliente de Notion conectado
        antes de que comience el bucle de la tarea.
        """
        await self.bot.wait_until_ready()
        print("ℹ️ Bot listo. Conectando a Notion para la tarea de mensajes programados...")
        try:
            self.db_manager.connect()
            print("✅ Conexión a Notion establecida para la tarea de mensajes.")
        except Exception as e:
            print(f"❌ Error al conectar con Notion en el inicio de la tarea: {e}")
        print("ℹ️ Tarea de mensajes programados iniciada. Buscando mensajes para enviar...")

async def setup(bot):
    await bot.add_cog(ScheduledMessageTask(bot))