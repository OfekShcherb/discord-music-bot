import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from discord import app_commands
import Utils.embed_util
from Utils.bot_messages import BotMessages
import Utils.validation
import asyncio
import time


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'extractaudio': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

    def search_youtube(self, item: str):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if 'https' in item:
                    url = item
                    info = ydl.extract_info(url, download=False)
                else:
                    url = f"ytsearch:{item}"
                    info = ydl.extract_info(url, download=False)['entries'][0]
            except Exception as e:
                print(e)
                return False

        return {'source': info['url'], 'url': info['webpage_url'], 'title': info['title'], 'duration': info['duration']}

    def play_next_song(self):
        self.music_queue.pop(0)

        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next_song())
        else:
            self.is_playing = False

    async def play_music(self, interaction: discord.Interaction):
        if len(self.music_queue) > 0:
            self.is_playing = True
            song = self.music_queue[0][0]

            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                print(f'Connected to {self.music_queue[0][1]}')

                if self.vc is None:
                    embed = BotMessages.create_embed(BotMessages.CONNECTION_FAILED_ERROR)
                    await interaction.channel.send(embed=embed)
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            try:
                self.music_queue.pop(0)
                embed = Utils.embed_util.create_currently_playing_song_message(song)
                await interaction.channel.send(embed=embed)
                self.vc.play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS),
                             after=lambda _: self.play_next_song())
            except Exception as e:
                print(f"Error while playing: {e}")
                self.is_playing = False
                return
        else:
            self.is_playing = False

    async def handle_playback_action(self, interaction: discord.Interaction, action: str):
        if action == "pause":
            if self.is_playing:
                self.is_playing = False
                self.is_paused = True
                self.vc.pause()
                embed = BotMessages.create_embed(BotMessages.PAUSE_BOT.value)
            elif self.is_paused:
                embed = BotMessages.create_embed(BotMessages.ALREADY_PAUSED.value)
        elif action == "resume":
            if self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
                embed = BotMessages.create_embed(BotMessages.RESUME_BOT.value)
            elif self.is_playing:
                embed = BotMessages.create_embed(BotMessages.ALREADY_PLAYING.value)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play song")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        embed = None

        if self.vc:
            error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
            if error_message:
                embed = error_message
        elif not Utils.validation.is_user_in_voice_channel(interaction):
            embed = BotMessages.create_embed(BotMessages.USER_NOT_IN_VOICE_CHANNEL.value)

        if embed is None:
            voice_channel = interaction.user.voice.channel
            if self.is_paused:
                self.vc.resume()
            song = self.search_youtube(query)
            if not song:
                embed = BotMessages.create_embed(BotMessages.CANT_DOWNLOAD_SONG)
            else:
                self.music_queue.append([song, voice_channel])
                embed = Utils.embed_util.create_new_song_added_message(interaction.user.mention, song, len(self.music_queue))

                if not self.is_playing:
                    await self.play_music(interaction)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="pauses the current playing song")
    async def pause(self, interaction: discord.Interaction):
        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            await interaction.response.send_message(embed=error_message)
        else:
            await self.handle_playback_action(interaction, action="pause")

    @app_commands.command(name="resume", description="Resumes playing the current song")
    async def resume(self, interaction: discord.Interaction):
        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            await interaction.response.send_message(embed=error_message)
        else:
            await self.handle_playback_action(interaction, action="resume")

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            embed = error_message
        else:
            if not self.music_queue and not self.is_playing:
                embed = BotMessages.create_embed(BotMessages.SKIP_SONG_ERROR.value)
            elif self.vc:
                self.vc.pause()
                await self.play_music(interaction)
                embed = BotMessages.create_embed(BotMessages.SKIP_SONG.value)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Displays all the songs in the queue")
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer()

        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            embed = error_message
        else:
            embed = Utils.embed_util.create_queued_songs_message(self.music_queue)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear", description="Clears the queue")
    async def clear(self, interaction: discord.Interaction):
        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            embed = error_message
        else:
            if self.vc and self.is_playing:
                self.vc.stop()
            self.music_queue.clear()
            embed = BotMessages.create_embed(BotMessages.CLEAR_QUEUE.value)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Kicks the bot from the voice channel")
    async def leave(self, interaction: discord.Interaction):
        error_message = Utils.validation.validate_voice_channel(interaction, self.vc)
        if error_message:
            embed = error_message
        else:
            self.is_playing = False
            self.is_playing = False
            self.music_queue.clear()
            await self.vc.disconnect()
            self.vc = None
            embed = BotMessages.create_embed(BotMessages.LEAVE.value)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="test", description="This is for testing purposes")
    async def test(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=interaction.user.mention,
            description="This is for testing purposes",
            color=discord.Colour(0xd1a04c)
        )
        embed.add_field(name="Artist", value="Tito", inline=False)
        embed.add_field(name="text", value="Tito is always wrong", inline=True)
        embed.add_field(name="Source", value="[YouTube](https://www.youtube.com/watch?v=dQw4w9WgXcQ)", inline=False)
        embed.set_footer(text="Tito is always wrong")
        await interaction.response.send_message(content=interaction.user.mention, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
