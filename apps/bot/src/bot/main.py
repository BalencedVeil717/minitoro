import discord

intents = discord.Intents.default()

client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

client.run("MTU2OTY2MjYyNzk1NTc0MDcwMg.G8Rbsm.TAxZTaiomTqR8ZlQmx3tEceTmlPFTZgnYtMsE4")