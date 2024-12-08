import discord
import datetime
from Utils.bot_messages import BotMessages


def create_currently_playing_song_message(song: dict):
    start_time = str(datetime.timedelta(seconds=0))
    duration = str(datetime.timedelta(seconds=song['duration']))
    fields = {
        'Duration': f'{start_time}/{duration}',
    }
    embed = BotMessages.create_embed(BotMessages.CURRENTLY_PLAYING_SONG.value, description=f"[{song['title']}]({song['url']})", fields=fields)

    return embed


def update_current_playing_song_message(message: discord.Embed, time: int):
    duration = message.fields[0].value.split("/")[1]
    new_time = str(datetime.timedelta(seconds=time))
    message.set_field_at(0, name='Duration', value=f'{new_time}/{duration}')


def create_new_song_added_message(who: str, song: dict, song_number: int):
    title = song['title']
    url = song['url']
    duration = str(datetime.timedelta(seconds=song['duration']))
    fields = {
        'Duration': duration
    }
    embed = BotMessages.create_embed(BotMessages.NEW_SONG_ADDED.value, title=f"{who} Added a song to queue #{song_number}", description=f"[{title}]({url})", fields=fields)

    return embed


def create_queued_songs_message(music_queue):
    res = ""
    total_songs = len(music_queue)
    total_duration = 0

    for i in range(total_songs):
        if i < 4:
            res += f"{i + 1}. [{music_queue[i][0]['title']}]({music_queue[i][0]['url']})\n"
        total_duration += music_queue[i][0]['duration']

    if total_duration == 0:
        embed = BotMessages.create_embed(BotMessages.EMPTY_QUEUE.value)
    else:
        fields = {
            "Number of Songs": total_songs,
            "Duration": str(datetime.timedelta(seconds=total_duration))
        }

        embed = BotMessages.create_embed(BotMessages.LIST_QUEUE.value, description=res, fields=fields)

    return embed
