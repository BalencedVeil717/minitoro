import os
import discord

from pathlib import Path
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()


class MinitoroBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.none()
        )
        self.minecraft_dir = Path(
            os.getenv("MINITORO_MINECRAFT_DIR", "")
        ).resolve()

        if not os.getenv("MINITORO_MINECRAFT_DIR"):
            raise RuntimeError("MINITORO_MINECRAFT_DIR not set")

        if not self.minecraft_dir.is_dir():
            raise FileNotFoundError(
                f"Minecraft directory not found: {self.minecraft_dir}"
            )

    async def setup_hook(self):
        await bot.load_extension("bot.commands.ping")
        await bot.load_extension("bot.commands.metrics")
        await bot.load_extension("bot.commands.reload_hashes")
        await bot.load_extension("bot.commands.world")

        await self.tree.sync()


bot = MinitoroBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.tree.error
async def on_app_command_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CheckFailure):
        message = "You are not authorized to use this command."
    else:
        print(f"Error occurred in a command: {error}")
        message = "Error executing command, contact dev."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


token = os.getenv("BOT_TOKEN")

if not token:
    raise RuntimeError("BOT_TOKEN not set")

bot.run(token)
