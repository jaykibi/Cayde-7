import discord
import responses
import yt_dlp
import os
import asyncio
import sqlite3
import datetime
from discord.ext import tasks


# Global song queue dictionary (per guild)
song_queues = {}

async def send_message(message, user_message):
    try:
        response = responses.handle_response(user_message)
        await message.channel.send(response)
    except Exception as e:
        print(f"Error in send_message: {e}")

def get_song_queue(guild_id):
    """Retrieve the song queue for the given guild."""
    if guild_id not in song_queues:
        song_queues[guild_id] = []
    return song_queues[guild_id]

async def play_next_in_queue(vc, guild_id):
    """Play the next song in the queue, if any."""
    queue = get_song_queue(guild_id)
    if queue:
        next_url = queue.pop(0)  # Get the next song URL
        try:
            # Extract the direct audio stream URL
            with yt_dlp.YoutubeDL({"quiet": True, "format": "bestaudio"}) as ydl:
                info = ydl.extract_info(next_url, download=False)
                audio_url = info["url"]

            # Play the audio
            source = discord.FFmpegPCMAudio(
                audio_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn",
            )
            loop = asyncio.get_running_loop()  # Get the current event loop
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_in_queue(vc, guild_id), loop).result())
        except Exception as e:
            print(f"Error playing next song: {e}")

def clear_queue(guild_id):
    """Clear the song queue for the given guild."""
    if guild_id in song_queues:
        song_queues[guild_id] = []

def setup_database():
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id TEXT PRIMARY KEY,
            birthday TEXT
        )
    ''')
    conn.commit()
    conn.close()

def run_discord_bot():
    TOKEN = "INSERT TOKEN HERE" 
    intents = discord.Intents.default()
    intents.typing = True
    intents.messages = True
    intents.message_content = True
    intents.voice_states = True  # Enable voice state intents
    client = discord.Client(intents=intents)

    @tasks.loop(hours=24)
    async def check_birthdays():
        """Check for users with birthdays today and post in a specific channel."""
        # Get today's month and day (ignoring the year)
        today = datetime.date.today()
        today_month_day = today.strftime("%m-%d")

        # Connect to the database
        conn = sqlite3.connect("birthdays.db")
        c = conn.cursor()

        # Query for users with matching month and day (ignores year)
        c.execute('''
            SELECT user_id FROM birthdays
            WHERE strftime('%m-%d', birthday) = ?
        ''', (today_month_day,))
        results = c.fetchall()
        conn.close()

        # Specify the channel ID where the message should be sent
        target_channel_id = 1192541797239492689  # Replace with your channel ID

        # Fetch the channel object
        channel = client.get_channel(target_channel_id)
        if not channel:
            print(f"Error: Could not find channel with ID {target_channel_id}")
            return

        # Send birthday messages to the channel
        if results:
            for row in results:
                user_id = row[0]
                user = await client.fetch_user(user_id)
                if user:
                    try:
                        await channel.send(f"Happy Birthday, {user.mention}!")
                        print(f"Sent birthday message for user {user_id} to channel {target_channel_id}")
                    except Exception as e:
                        print(f"Failed to send birthday message for {user_id}: {e}")
        else:
            print("No birthdays today.")


    @client.event
    async def on_ready():
        # Set the bot's activity
        activity = discord.Activity(type=discord.ActivityType.watching, name="the chat")
        await client.change_presence(activity=activity)
        print(f"{client.user} is online!")
        setup_database()
        check_birthdays.start() 


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        user_message = str(message.content)
        guild_id = message.guild.id
        user_id = str(message.author.id)


        # Command: Join voice channel
        if user_message == "cayde vc":
            if message.author.voice:
                channel = message.author.voice.channel
                vc = await channel.connect()
                await message.channel.send(f"Joined {channel.name}!")

                # Wait half a second before playing the MP3 file
                await asyncio.sleep(0.5)

                # Play an MP3 file when joining
                mp3_path = "assets/join.mp3"
                if os.path.exists(mp3_path):
                    vc.play(discord.FFmpegPCMAudio(mp3_path), after=lambda e: print(f"Finished playing join sound: {e}" if e else "Finished playing join sound."))
                else:
                    print("Join MP3 file not found.")
            else:
                await message.channel.send("You need to be in a voice channel for me to join!")

        # Command: Play and Join
        if user_message.lower().startswith("~play "):
            query = user_message[6:].strip()

            # Join the user's voice channel if not already connected
            vc = message.guild.voice_client
            if not vc:
                if message.author.voice:
                    channel = message.author.voice.channel
                    vc = await channel.connect()
                    await message.channel.send(f"Joined {channel.name}!")

                    # Wait half a second before playing the MP3 file
                    await asyncio.sleep(0.5)

                    # Play an MP3 file when joining
                    mp3_path = "assets/join.mp3"
                    if os.path.exists(mp3_path):
                        vc.play(discord.FFmpegPCMAudio(mp3_path), after=lambda e: print(f"Finished playing join sound: {e}" if e else "Finished playing join sound."))
                        while vc.is_playing():
                            await asyncio.sleep(1)  # Wait for the join sound to finish
                    else:
                        print("Join MP3 file not found.")
                else:
                    await message.channel.send("You need to be in a voice channel for me to join!")
                    return

            # Stream the requested audio
            if query.startswith("http"):
                url = query
            else:
                await message.channel.send(f"Searching for: {query}...")
                try:
                    with yt_dlp.YoutubeDL({"quiet": True, "format": "bestaudio"}) as ydl:
                        results = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"]
                        for entry in results:
                            if entry.get("availability") == "public":
                                url = entry["webpage_url"]
                                break
                        else:
                            await message.channel.send("No playable videos found for your query.")
                            return
                except Exception as e:
                    await message.channel.send("Error: Could not find a video.")
                    print(f"yt-dlp search error: {e}")
                    return

            await message.channel.send(f"Added to queue: {url}")

            # Add to the queue
            queue = get_song_queue(guild_id)
            queue.append(url)

            # If nothing is currently playing, start playback
            if not vc.is_playing():
                await play_next_in_queue(vc, guild_id)

        # Command: Show Queue
        if user_message == "~que":
            queue = get_song_queue(guild_id)
            if queue:
                queue_message = "\n".join([f"{i+1}. {url}" for i, url in enumerate(queue)])
                await message.channel.send(f"current que:\n{queue_message}")
            else:
                await message.channel.send("The queue is currently empty.")

        # Command: Leave voice channel
        if user_message == "cayde leave":
            if message.guild.voice_client:
                await message.guild.voice_client.disconnect()
                clear_queue(guild_id)  # Clear the queue
                await message.channel.send("Disconnected and cleared the queue!")
            else:
                await message.channel.send("I'm not in a voice channel!")


        # Command: Set Birthday
        if user_message.startswith("~setbirthday"):
            try:
                _, date = user_message.split(" ", 1)
                conn = sqlite3.connect("birthdays.db")
                c = conn.cursor()
                c.execute('''
                    INSERT INTO birthdays (user_id, birthday)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET birthday = excluded.birthday
                ''', (user_id, date))
                conn.commit()
                conn.close()
                await message.channel.send(f"Birthday set to {date} for {message.author.mention}!")
            except Exception as e:
                await message.channel.send("Error: Please use the format `~setbirthday YYYY-MM-DD`.")
                print(e)

        # Command: Get Birthday
        if user_message == "~getbirthday":
            conn = sqlite3.connect("birthdays.db")
            c = conn.cursor()
            c.execute('SELECT birthday FROM birthdays WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            if result:
                await message.channel.send(f"{message.author.mention}, your birthday is set to {result[0]}.")
            else:
                await message.channel.send(f"{message.author.mention}, you haven't set your birthday yet. Use `~setbirthday`!")

        # Command: List All Birthdays
        if user_message == "~listbirthdays":
            conn = sqlite3.connect("birthdays.db")
            c = conn.cursor()
            c.execute('SELECT user_id, birthday FROM birthdays')
            results = c.fetchall()
            conn.close()

            if results:
                birthday_list = "\n".join([f"<@{row[0]}>: {row[1]}" for row in results])
                await message.channel.send(f"Here are the saved birthdays:\n{birthday_list}")
            else:
                await message.channel.send("No birthdays saved yet!")

        await send_message(message, user_message)

    @client.event
    async def on_voice_state_update(member, before, after):
        # Check if the bot is in a voice channel
        voice_client = discord.utils.get(client.voice_clients, guild=member.guild)
        if voice_client and voice_client.channel:
            # Get the current members in the channel (excluding the bot itself)
            channel_members = [m for m in voice_client.channel.members if not m.bot]
            if len(channel_members) == 0:  # If no members left in the channel
                await voice_client.disconnect()
                clear_queue(member.guild.id)  # Clear the queue on manual disconnect
                print(f"Left {voice_client.channel.name} because it was empty.")

    client.run(TOKEN)
