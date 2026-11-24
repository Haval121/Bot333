import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "9245634242:AAHYqDhd4wtme2E2MN0-xAQTBmAZ13_CQ4I"

SOURCE_CHANNEL = "mbvkfx"
SOURCE_MESSAGE_ID = 3
INTERVAL_SECONDS = 25 * 60  # 25 خولەک
GROUPS_FILE = "groups.json"

app = Client(
    "auto_sender_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


def load_groups() -> set[int]:
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(int(x) for x in data)
        except Exception:
            return set()
    return set()


def save_groups(groups: set[int]) -> None:
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(groups), f)


known_groups: set[int] = load_groups()


def add_group(chat_id: int, chat_type: ChatType | None) -> None:
    if chat_type in (ChatType.GROUP, ChatType.SUPERGROUP):
        if chat_id not in known_groups:
            known_groups.add(chat_id)
            save_groups(known_groups)
            print(f"گروپی نوێ زیاد کرا: {chat_id}")


@app.on_message(filters.group)
async def track_group_message(_, message):
    add_group(message.chat.id, message.chat.type)


@app.on_chat_member_updated()
async def track_group_member(_, update):
    if update.chat:
        add_group(update.chat.id, update.chat.type)


async def send_to_all_groups():
    while True:
        if not known_groups:
            print("هیچ گروپێک تۆمار نەکراوە. نامەیەک یان /start لە گروپەکان بنێرە.")
        else:
            print(f"دەستپێکردنی ناردن بۆ {len(known_groups)} گروپ...")

            for chat_id in list(known_groups):
                try:
                    await app.copy_message(
                        chat_id=chat_id,
                        from_chat_id=SOURCE_CHANNEL,
                        message_id=SOURCE_MESSAGE_ID,
                    )
                    print(f"نێردرا بۆ گروپ: {chat_id}")
                    await asyncio.sleep(1.5)
                except FloodWait as e:
                    print(f"FloodWait بۆ {e.value} چرکە...")
                    await asyncio.sleep(e.value + 1)
                except Exception as err:
                    print(f"هەڵە لە ناردن بۆ {chat_id}: {err}")

        await asyncio.sleep(INTERVAL_SECONDS)


async def main():
    await app.start()
    print("بۆتەکە بە سەرکەوتوویی کار دەکات...")
    asyncio.create_task(send_to_all_groups())
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
    
