import discord
from discord.ext import commands
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- Render用のダミーサーバー設定 ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check_server():
    # Renderは10000番ポートでの待機を期待します
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# ダミーサーバーを別スレッドで起動
threading.Thread(target=run_health_check_server, daemon=True).start()
# ----------------------------------

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GLOBAL_CH_NAME = "global-chat"

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.name == GLOBAL_CH_NAME:
        embed = discord.Embed(description=message.content, color=0x00ff00)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"送信元: {message.guild.name}")

        try:
            await message.delete()
        except:
            pass

        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name == GLOBAL_CH_NAME:
                    if channel.id != message.channel.id:
                        await channel.send(embed=embed)

# トークンの読み込みと起動
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
