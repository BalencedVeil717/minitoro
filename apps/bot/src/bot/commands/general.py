import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        embed = discord.Embed(
            title="P I N G",
            color=discord.Color.green(),
            description=f"{round(self.bot.latency * 1000)}ms"
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
