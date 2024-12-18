import discord
import yt_dlp
import os
import asyncio

song_queues = {}

def get_song_queue(guild_id):
    if guild_id not in song_queues:
        song_queues[guild_id] = []
    return song_queues[guild_id]

async def handle_music_commands(message, client):
    user_message = message.content
    guild_id = message.guild.id
    vc = message.guild.voice_client

    # Play Command
    if user_message.lower().startswith("~play"):
        query = user_message[6:].strip()
        if not vc and message.author.voice:
            vc = await message.author.voice.channel.connect()
        if vc and query:
            queue = get_song_queue(guild_id)
            queue.append(query)
            if not vc.is_playing():
                await play_next_in_queue(vc, guild_id)

    elif user_message == "cayde vc" and message.author.voice:
        await message.author.voice.channel.connect()
        await message.channel.send(f"Joined {message.author.voice.channel.name}!")

    elif user_message == "cayde leave" and vc:
        await vc.disconnect()
        song_queues[guild_id] = []  # Clear the queue
        await message.channel.send("Disconnected and cleared the queue!")

    elif user_message == "~que":
        queue = get_song_queue(guild_id)
        if queue:
            queue_message = "\n".join([f"{i+1}. {url}" for i, url in enumerate(queue)])
            await message.channel.send(f"current que:\n{queue_message}")
        else:
            await message.channel.send("The queue is currently empty.")

async def play_next_in_queue(vc, guild_id):
    queue = get_song_queue(guild_id)
    if queue:
        query = queue.pop(0)
        with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
            info = ydl.extract_info(query, download=False)
            audio_url = info["url"]
        vc.play(discord.FFmpegPCMAudio(audio_url), after=lambda _: asyncio.run_coroutine_threadsafe(play_next_in_queue(vc, guild_id), asyncio.get_event_loop()))
