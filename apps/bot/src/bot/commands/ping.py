import discord
from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
