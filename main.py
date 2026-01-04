import discord
from discord.ext import commands
import os

# 接続に必要な設定
intents = discord.Intents.default()
intents.message_content = True # メッセージの内容を読み取る設定
bot = commands.Bot(command_prefix="!", intents=intents)

# グローバルチャットとして扱うチャンネル名
GLOBAL_CH_NAME = "global-chat"

@bot.event
async def on_ready():
    # 起動したらログ画面に通知が出る
    print(f'ログインしました: {bot.user.name}')

@bot.event
async def on_message(message):
    # Bot自身のメッセージには反応しない
    if message.author.bot:
        return

    # 指定したチャンネル名での発言かチェック
    if message.channel.name == GLOBAL_CH_NAME:
        # 他のサーバーの同名チャンネルに送るための準備（埋め込み形式）
        embed = discord.Embed(description=message.content, color=0x00ff00)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"送信元: {message.guild.name}")

        # 元のメッセージを消す（グローバルチャットっぽくするため）
        try:
            await message.delete()
        except:
            pass # 権限がない場合は消さずに続行

        # Botが参加している全サーバーのチャンネルをループ
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name == GLOBAL_CH_NAME:
                    # 同じチャンネル以外（他のサーバー）に送信
                    if channel.id != message.channel.id:
                        await channel.send(embed=embed)

# RenderのEnvironmentで設定した「DISCORD_TOKEN」を読み込む
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
