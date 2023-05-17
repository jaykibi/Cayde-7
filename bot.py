import discord
import responses


async def send_message(message, user_message):
    try:
        response = responses.handle_response(user_message)
        await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTA5OTcxMzUzMzQyMTMwOTk4Mg.G9zwZL.n2B7QBA6PpHzdT6M644UlXIGhj0I5H5CfFLbvk'
    intents = discord.Intents.default()
    intents.typing = True
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is online!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        await send_message(message,user_message)

    client.run(TOKEN)
