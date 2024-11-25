import discord
from discord.ext import commands
import asyncio
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
discord_token = os.getenv("DISCORD_TOKEN")


async def load_extensions():
    await bot.load_extension("Cogs.music_cog")  # Replace with your cog's filename without .py


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Synced slash commands")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(discord_token)


if __name__ == "__main__":
    asyncio.run(main())

