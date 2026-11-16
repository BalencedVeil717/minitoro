import discord
from discord import app_commands
import httpx
from discord.ext import commands


class Metrics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="metrics", description="Show server metrics")
    async def metrics(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                lastcall_response = await client.get("http://127.0.0.1:8000/lastcall")
                lastcall_response.raise_for_status()

                try:
                    lastcall_data = lastcall_response.json()
                except ValueError:
                    await interaction.followup.send("API returned an invalid response")
                    return
                if not isinstance(lastcall_data, dict) or lastcall_data.get("status") != "ok":
                    await interaction.followup.send(
                        "Couldn't fetch metrics, agent is not responding or still booting up.")
                    return

                metric_response = await client.get("http://127.0.0.1:8000/metrics")
                metric_response.raise_for_status()
                try:
                    data = metric_response.json()
                    message = (
                        "> ## M E T R I C S\n"
                        f"- **CPU:** `{data['cpu_percentage']}%`\n"
                        f"- **Memory:** `{data['ram_used']}/{data['ram_total']}GB`\n"
                        f"- **Disk:** `{data['disk_percentage']}%`\n"
                    )
                except ValueError:
                    await interaction.followup.send("API returned an invalid response")
                    return
                except KeyError:
                    message = "Couldn't fetch metrics, invalid response."

        except httpx.HTTPError as err:
            print(f"Error getting metrics: {err}")
            await interaction.followup.send(f"Couldn't fetch metrics, api blocked")
            return

        await interaction.followup.send(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Metrics(bot))