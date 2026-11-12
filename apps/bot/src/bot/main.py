import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

tree = bot.tree


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await tree.sync()


@tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    await interaction.followup.send(f"Pong! {round(bot.latency * 1000)}ms")


try:
    bot.run(token=os.getenv("BOT_TOKEN"))
except Exception as e:
    print(f"Couldn't run bot {e}")
