import discord
from Utils.bot_messages import BotMessages


def is_user_in_voice_channel(interaction: discord.Interaction):
    return interaction.user.voice is not None


def is_user_in_same_channel(interaction: discord.Interaction, bot_voice_channel: discord.VoiceChannel):
    return interaction.user.voice.channel == bot_voice_channel


def is_bot_in_voice_channel(bot_voice_client: discord.VoiceClient):
    return True if bot_voice_client else False


def validate_voice_channel(interaction: discord.Interaction, bot_voice_client: discord.VoiceClient):
    error = None

    if not is_user_in_voice_channel(interaction):
        error = BotMessages.create_embed(BotMessages.USER_NOT_IN_VOICE_CHANNEL.value)
    elif not is_bot_in_voice_channel(bot_voice_client):
        error = BotMessages.create_embed(BotMessages.BOT_NOT_IN_VOICE_CHANNEL.value)
    elif not is_user_in_same_channel(interaction, bot_voice_client.channel):
        error = BotMessages.create_embed(BotMessages.USER_IN_DIFFERENT_VOICE_CHANNEL.value)

    return error
