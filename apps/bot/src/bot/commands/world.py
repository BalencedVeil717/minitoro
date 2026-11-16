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

        world_border = await get_dat(self.bot.minecraft_dir / "world-data" / "world_border.dat")
        world_clocks = await get_dat(self.bot.minecraft_dir / "world-data" / "world_clocks.dat")
        world_gen_settings = await get_dat(self.bot.minecraft_dir / "world-data" / "world_gen_settings.dat")

        world_name = "RasMalai_2.0"
        overworld_age = int(world_clocks["data"]["minecraft:overworld"]["total_ticks"]) // 24000
        end_age = int(world_clocks["data"]["minecraft:the_end"]["total_ticks"]) // 24000
        border = int(world_border["data"]["lerp_target"])

        weather = await get_dat(self.bot.minecraft_dir / "world-data" / "weather.dat")
        data = weather["data"]
        border_center_x = float(world_border["data"]['center_x'])
        border_center_z = float(world_border["data"]['center_z'])

        raining = bool(data["raining"])
        thundering = bool(data["thundering"])
        clear_time = int(data["clear_weather_time"])

        if clear_time > 0:
            current_weather = "Clear"
        elif raining and thundering:
            current_weather = "Thunderstorm"
        elif raining:
            current_weather = "Rain"
        else:
            current_weather = "Clear"

        embed = discord.Embed(
            title="World Information",
            color=discord.Color.blurple()
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

        embed.add_field(
            name="World Border",
            value=(
                f"> Diameter: `{border:,} blocks`\n"
                f"> Center: `{border_center_x}, {border_center_z}`\n"
            ),
            inline=False
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(World(bot))
