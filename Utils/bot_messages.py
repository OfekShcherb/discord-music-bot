from enum import Enum
import discord
import datetime

embed_color = 0xd1a04c


class BotMessages(Enum):
    USER_NOT_IN_VOICE_CHANNEL = {
        "title": f"Error with command!",
        "description": f"Please connect to a voice channel"
    }

    CANT_DOWNLOAD_SONG = {
        "title": f"Error adding song!",
        "description": f"Could not download the song"
    }

    ALREADY_PAUSED = {
        "title": f"Bot already paused!",
        "description": "Can't pause the bot because it was already paused"
    }

    ALREADY_PLAYING = {
        "title": f"Bot already playing!",
        "description": "Can't resume the bot because it is already playing"
    }

    CURRENTLY_PLAYING_SONG = {
        "title": "Currently playing song"
    }

    NEW_SONG_ADDED = {
    }

    PAUSE_BOT = {
        "title": "Bot paused!",
        "description": "You can resume your bot by typing /resume"
    }

    RESUME_BOT = {
        "title": "Bot resumed!",
        "description": "The bot is playing again"
    }

    USER_IN_DIFFERENT_VOICE_CHANNEL = {
        "title": "Error with command!",
        "description": "Please connect to the same voice channel as the bot"
    }

    CONNECTION_FAILED_ERROR = {
        "title": "Connection failed!",
        "description": "Could not connect to the voice channel"
    }

    SKIP_SONG = {
        "title": "Skipping song!",
        "description": "Playing the next song"
    }

    SKIP_SONG_ERROR = {
        "title": "Can't skip song!",
        "description": "Can't skip song because the queue is empty"
    }

    EMPTY_QUEUE = {
        "title": "The Queue is empty!",
        "description": "You can add songs by typing /play"
    }

    LIST_QUEUE = {
        "title": "These are the songs in the queue"
    }

    CLEAR_QUEUE = {
        "title": "Queue cleared!",
        "description": "The queue is empty"
    }

    LEAVE = {
        "title": "I left the Channel",
        "description": "If you want to play a song, please type /play"
    }

    BOT_NOT_IN_VOICE_CHANNEL = {
        "title": "Bot is not in voice channel!",
        "description": "Bot is not in voice channel"
    }

    FINISHED_PLAYING = {
        "title": "Finished playing all the songs!",
        "description": "You can add more songs by typing /play"
    }

    GOODBYE = {
        "title": "Goodbye!",
        "description": "I'm leaving the channel due to inactivity"
    }

    @staticmethod
    def create_embed(message, title=None, description=None, fields=None):
        embed = discord.Embed(
            title=message.get("title", title),
            description=message.get("description", description),
            color=discord.Colour(embed_color)
        )
        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=fields.get("inline", False))

        return embed

