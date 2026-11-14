import os
import discord
import httpx
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

import workers
load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


minecraft_dir = Path(os.getenv("MINITORO_MINECRAFT_DIR", "")).resolve()
if not minecraft_dir.is_dir():
    raise RuntimeError(f"Invalid minecraft directory: {minecraft_dir}")



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await tree.sync()


@tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    await interaction.followup.send(f"Pong! {round(bot.latency * 1000)}ms")


@tree.command(name="metrics", description="Show server metrics")
async def metrics(interaction: discord.Interaction) -> None:
    await interaction.response.defer()

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://127.0.0.1:8000/metrics")
            response.raise_for_status()
            data = response.json()
            message = (
                "> ## M E T R I C S\n"
                f"- **CPU:** `{data['cpu_percentage']}%`\n"
                f"- **Memory:** `{data['ram_used']}/{data['ram_total']}GB`\n"
                f"- **Disk:** `{data['disk_percentage']}%`\n"
            )
    except httpx.HTTPError as err:
        print(f"Error getting metrics: {err}")
        await interaction.followup.send(f"Couldn't fetch metrics")
        return

    await interaction.followup.send(message)


async def player_name_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    players = await workers.get_players(minecraft_dir)
    return [app_commands.Choice(name=player, value=player) for player in players if
            player.lower().startswith(current.lower())][:25]


@tree.command(name="reload_hashes", description="Reload the uuid for players")
async def reload_hashes(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    try:
        await workers.reload_uuid(minecraft_dir)
        await interaction.followup.send(f"Successfully reloaded hashes for {minecraft_dir}", ephemeral=True)
    except Exception as err:
        await interaction.followup.send(f"Error reloading hashes for {minecraft_dir}\nError: {err}", ephemeral=True)


try:
    bot.run(token=os.getenv("BOT_TOKEN"))
except Exception as e:
    print(f"Couldn't run bot {e}")
