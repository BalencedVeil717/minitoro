import json
import discord

from discord import app_commands
from discord.ext import commands

from bot.workers import get_players

def get_category(stats: dict, category: str) -> dict:
    data = stats.get(category, {})
    return data if isinstance(data, dict) else {}


def get_stat(stats: dict, category: str, key: str) -> int:
    value = get_category(stats, category).get(key, 0)

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def get_total(stats: dict, category: str) -> int:
    return sum(
        int(value)
        for value in get_category(stats, category).values()
        if isinstance(value, (int, float))
    )


def get_top(stats: dict, category: str) -> tuple[str, int] | None:
    data = get_category(stats, category)

    if not data:
        return None

    key, value = max(data.items(), key=lambda item: item[1])
    return key, int(value)


def format_name(name: str) -> str:
    return name.removeprefix("minecraft:").replace("_", " ").title()


class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def player_name_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=player, value=player)
            for player in await get_players(self.bot.minecraft_dir)
            if current.lower() in player.lower()
        ][:25]

    @app_commands.command(name="whois", description="Get info about a player")
    @app_commands.describe(player_name="Username of the player")
    @app_commands.autocomplete(player_name=player_name_autocomplete)
    async def whois(self, interaction: discord.Interaction, player_name: str) -> None:
        await interaction.response.defer()

        player_hash_file = self.bot.minecraft_dir / "player_hash.json"

        if not player_hash_file.is_file():
            print(f"Files not found {player_hash_file}")
            return None

        try:
            hash_data = json.loads(player_hash_file.read_text(encoding="utf-8"))
        except json.decoder.JSONDecodeError:
            print("Cannot load player_hash.json")
            hash_data = {}

        if player_name not in hash_data.keys():
            await interaction.followup.send("Player not found in players list.")
            return None

        player_uuid = hash_data[player_name][0]

        try:
            advancements_data = json.loads(
                (self.bot.minecraft_dir / "advancements" / f"{player_uuid}.json")
                .read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error getting player advancements for {player_name}: {e}")
            raise
        try:
            stats = json.loads(
                (self.bot.minecraft_dir / "stats" / f"{player_uuid}.json")
                .read_text(encoding="utf-8")
            )["stats"]
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"Error getting player stats for {player_name}: {e}")
            raise

        stats_data = {
            "overview": {
                "play_time": round(get_stat(stats, "minecraft:custom", "minecraft:play_time") / 72000, 2),
                "deaths": get_stat(stats, "minecraft:custom", "minecraft:deaths"),
                "mob_kills": get_stat(stats, "minecraft:custom", "minecraft:mob_kills"),
                "player_kills": get_stat(stats, "minecraft:custom", "minecraft:player_kills"),
            },

            "combat": {
                "damage_dealt": round(get_stat(stats, "minecraft:custom", "minecraft:damage_dealt") / 20),
                "damage_taken": round(get_stat(stats, "minecraft:custom", "minecraft:damage_taken") / 20),
                "player_deaths": get_stat(stats, "minecraft:killed_by", "minecraft:player"),
                "most_killed": get_top(stats, "minecraft:killed"),
            },

            "mining": {
                "total": get_total(stats, "minecraft:mined"),
                "most_mined": get_top(stats, "minecraft:mined"),
                "diamonds": (
                        get_stat(stats, "minecraft:mined", "minecraft:diamond_ore")
                        + get_stat(stats, "minecraft:mined", "minecraft:deepslate_diamond_ore")
                ),
                "iron": (
                        get_stat(stats, "minecraft:mined", "minecraft:iron_ore")
                        + get_stat(stats, "minecraft:mined", "minecraft:deepslate_iron_ore")
                ),
            },

            "collection": {
                "items_picked_up": get_total(stats, "minecraft:picked_up"),
                "most_picked_up": get_top(stats, "minecraft:picked_up"),
                "items_crafted": get_total(stats, "minecraft:crafted"),
                "most_crafted": get_top(stats, "minecraft:crafted"),
            },

            "activity": {
                "animals_bred": get_stat(stats, "minecraft:custom", "minecraft:animals_bred"),
                "villager_trades": get_stat(stats, "minecraft:custom", "minecraft:traded_with_villager"),
                "fish_caught": get_stat(stats, "minecraft:custom", "minecraft:fish_caught"),
            },
        }
        movement_stats = {
            "walking": "walk_one_cm",
            "sprinting": "sprint_one_cm",
            "crouching": "crouch_one_cm",
            "swimming": "swim_one_cm",
            "underwater": "walk_under_water_one_cm",
            "on water": "walk_on_water_one_cm",
            "flying": "fly_one_cm",
            "elytra": "aviate_one_cm",
            "horse": "horse_one_cm",
            "boat": "boat_one_cm",
            "minecart": "minecart_one_cm",
            "climbing": "climb_one_cm",
        }

        movement_data: dict[str, int] = {
            name: round(get_stat(stats, "minecraft:custom", f"minecraft:{key}") / 100)
            for name, key in movement_stats.items()
        }

        embed = discord.Embed(
            title=f"WhoIs - {player_name}",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="**Overview**",
            value=(
                f"Play Time: `{stats_data['overview']['play_time']:,.2f} hrs`\n"
                f"Deaths: `{stats_data['overview']['deaths']:,}`\n"
                f"Mobs Killed: `{stats_data['overview']['mob_kills']:,}`\n"
                f"Players Killed: `{stats_data['overview']['player_kills']:,}`\n"
            ),
            inline=False
        )

        most_killed = stats_data['combat']['most_killed'] or ("Unknown", 0)

        embed.add_field(
            name="**Combat**",
            value=(
                f"Damage Dealt: `{stats_data['combat']['damage_dealt']:,} hearts`\n"
                f"Damage Taken: `{stats_data['combat']['damage_taken']:,} hearts`\n"
                f"Player Deaths: `{stats_data['combat']['player_deaths']:,}`\n"
                f"Most Killed: `{format_name(most_killed[0])} - {most_killed[1]:,}`\n"
            ),
            inline=False
        )

        most_mined = stats_data['mining']['most_mined'] or ("Unknown", 0)

        embed.add_field(
            name="**Mining**",
            value=(
                f"Total Mined: `{stats_data['mining']['total']:,}`\n"
                f"Most Mined: `{format_name(most_mined[0])} - {most_mined[1]:,}`\n"
                f"Diamonds: `{stats_data['mining']['diamonds']:,}`\n"
                f"Iron: `{stats_data['mining']['iron']:,}`\n"
            ),
            inline=False
        )

        most_picked = stats_data['collection']['most_picked_up'] or ("Unknown", 0)
        most_crafted = stats_data['collection']['most_crafted'] or ("Unknown", 0)

        embed.add_field(
            name="**Collection**",
            value=(
                f"Items Picked Up: `{stats_data['collection']['items_picked_up']:,}`\n"
                f"Most Picked: `{format_name(most_picked[0])} - {most_picked[1]:,}`\n"
                f"Items Crafted: `{stats_data['collection']['items_crafted']:,}`\n"
                f"Most Crafted: `{format_name(most_crafted[0])} - {most_crafted[1]:,}`\n"
            ),
            inline=False
        )

        embed.add_field(
            name="**Activity**",
            value=(
                f"Animals Bred: `{stats_data['activity']['animals_bred']:,}`\n"
                f"Villagers Traded: `{stats_data['activity']['villager_trades']:,}`\n"
                f"Fish Caught: `{stats_data['activity']['fish_caught']:,}`\n"
            ),
            inline=False
        )

        on_foot = sum(movement_data[k] for k in ("walking", "sprinting", "crouching", "horse"))
        via_water = sum(movement_data[k] for k in ("swimming", "underwater", "on water", "boat"))
        by_air = movement_data["flying"] + movement_data["elytra"]
        climbed = movement_data["climbing"]

        embed.add_field(
            name="**Movement**",
            value=(
                f"Blocks Covered: `{sum(movement_data.values()):,}`\n"
                f"On Foot: `{on_foot:,} blocks`\n"
                f"Via Water: `{via_water:,} blocks`\n"
                f"By Air: `{by_air:,} blocks`\n"
                f"Climbed: `{climbed:,} blocks`"
            ),
            inline=False
        )

        await interaction.followup.send(embed=embed)
        return None


async def setup(bot: commands.Bot):
    await bot.add_cog(Players(bot))
