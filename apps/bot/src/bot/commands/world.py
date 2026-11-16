import discord
from discord import app_commands
from discord.ext import commands


class World(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="world", description="Provides world stats")
    async def world(self, interaction: discord.Interaction):
        await interaction.response.defer()
        from bot.workers import get_dat

        try:
            world_clocks = await get_dat(self.bot.minecraft_dir / "world-data" / "world_clocks.dat")
            weather = await get_dat(self.bot.minecraft_dir / "world-data" / "weather.dat")
        except Exception as e:
            print(f"Error getting world_clocks, weather dat files: {e}")
            raise e

        weather_data = weather["data"]
        clock_data = world_clocks["data"]

        world_name = "MasRalai_2.0"
        overworld_age = int(clock_data["minecraft:overworld"]["total_ticks"]) // 24000
        end_age = int(clock_data["minecraft:the_end"]["total_ticks"]) // 24000
        raining = bool(weather_data["raining"])
        thundering = bool(weather_data["thundering"])
        clear_time = int(weather_data["clear_weather_time"])

        if clear_time > 0:
            current_weather = "Clear"
        elif raining and thundering:
            current_weather = "Thunderstorm"
        elif raining:
            current_weather = "Rain"
        else:
            current_weather = "Clear"

        embed = discord.Embed(
            title=world_name,
            color=discord.Color.yellow()
        )

        embed.add_field(
            name="World Age",
            value=(
                f"> Overworld: `{overworld_age} days`\n"
                f"> The End: `{end_age} days`"
            ),
            inline=False
        )

        embed.add_field(
            name="Current Weather",
            value=f"> Condition: `{current_weather}`\n> Raining: `{raining}`\n> Thundering: `{thundering}`",
            inline=False
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(World(bot))
