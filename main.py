import discord
from discord.ext import commands
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- Render専用：ポート10000番で待機する設定 ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_check_server():
    # Renderは10000番ポートでの待機を期待します
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# 別スレッドでサーバーを起動
threading.Thread(target=run_health_check_server, daemon=True).start()
# ---------------------------------------------

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

        # Botが参加している全サーバーのチャンネルをループ
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name == GLOBAL_CH_NAME:
                    try:
                        await channel.send(embed=embed)
                    except Exception as e:
                        print(f"送信エラー: {e}")

# 環境変数からトークンを読み取って起動
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
