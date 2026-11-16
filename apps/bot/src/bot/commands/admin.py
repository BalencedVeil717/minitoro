import discord
from discord import app_commands
from discord.ext import commands
from bot.workers import reload_uuid

async def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 903600880580968488


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload_hashes", description="Reload the uuid for players")
    @discord.app_commands.check(is_owner)
    async def reload_hashes(self, interaction: discord.Interaction) -> None:
        minecraft_dir = self.bot.minecraft_dir
        await interaction.response.defer(ephemeral=True)
        try:
            await reload_uuid(self.bot.minecraft_dir)
            await interaction.followup.send(f"Successfully reloaded hashes for `{minecraft_dir}`", ephemeral=True)
        except Exception as err:
            await interaction.followup.send(f"Error reloading hashes for `{minecraft_dir}`\nError: {err}",
                                            ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
