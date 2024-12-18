import sqlite3
from music import handle_music_commands
from database import set_birthday, get_birthday, list_birthdays

async def handle_commands(message, client):
    user_message = message.content
    user_id = str(message.author.id)

    # Music Commands
    if user_message.lower().startswith("~play") or user_message in ["~que", "cayde vc", "cayde leave"]:
        await handle_music_commands(message, client)
        return

    # Birthday Commands
    if user_message.startswith("~setbirthday"):
        _, date = user_message.split(" ", 1)
        set_birthday(user_id, date)
        await message.channel.send(f"Birthday set to {date} for {message.author.mention}!")

    elif user_message == "~getbirthday":
        birthday = get_birthday(user_id)
        if birthday:
            await message.channel.send(f"{message.author.mention}, your birthday is set to {birthday}.")
        else:
            await message.channel.send(f"{message.author.mention}, you haven't set your birthday yet. Use `~setbirthday`!")

    elif user_message == "~listbirthdays":
        birthdays = list_birthdays()
        if birthdays:
            birthday_list = "\n".join([f"<@{user_id}>: {birthday}" for user_id, birthday in birthdays])
            await message.channel.send(f"Here are the saved birthdays:\n{birthday_list}")
        else:
            await message.channel.send("No birthdays saved yet!")
