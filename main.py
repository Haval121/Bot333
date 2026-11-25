import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "9245634242:AAHYqDhd4wtme2E2MN0-xAQTBmAZ13_CQ4I"

SOURCE_CHANNEL = "mbvkfx"
SOURCE_MESSAGE_ID = 3
INTERVAL_SECONDS = 5 * 60  # 5 خولەک
GROUPS_FILE = "groups.json"
LAST_MESSAGES_FILE = "last_messages.json"

REPLY_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "نارن 🔐🔞  0/5",
                url="https://t.me/mbvkfx/3",
            )
        ]
    ]
)

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


def load_last_messages() -> dict[int, int]:
    if os.path.exists(LAST_MESSAGES_FILE):
        try:
            with open(LAST_MESSAGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): int(v) for k, v in data.items()}
        except Exception:
            return {}
    return {}


def save_last_messages(messages: dict[int, int]) -> None:
    with open(LAST_MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in messages.items()}, f)


known_groups: set[int] = load_groups()
last_sent_messages: dict[int, int] = load_last_messages()


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


async def send_to_single_group(chat_id: int) -> None:
    prev_msg_id = last_sent_messages.get(chat_id)
    if prev_msg_id:
        try:
            await app.delete_messages(chat_id=chat_id, message_ids=prev_msg_id)
        except Exception:
            pass

    while True:
        try:
            sent = await app.copy_message(
                chat_id=chat_id,
                from_chat_id=SOURCE_CHANNEL,
                message_id=SOURCE_MESSAGE_ID,
                reply_markup=REPLY_MARKUP,
            )
            last_sent_messages[chat_id] = sent.id
            save_last_messages(last_sent_messages)
            print(f"نێردرا بۆ گروپ: {chat_id}")
            break
        except FloodWait as e:
            print(f"FloodWait بۆ {e.value} چرکە...")
            await asyncio.sleep(e.value + 1)
        except Exception as err:
            print(f"هەڵە لە ناردن بۆ {chat_id}: {err}")
            break


async def send_to_all_groups():
    while True:
        if not known_groups:
            print("هیچ گروپێک تۆمار نەکراوە. نامەیەک یان /start لە گروپەکان بنێرە.")
        else:
            print(f"دەستپێکردنی ناردن لە یەک کاتدا بۆ {len(known_groups)} گروپ...")
            await asyncio.gather(
                *(send_to_single_group(chat_id) for chat_id in list(known_groups))
            )

        await asyncio.sleep(INTERVAL_SECONDS)


async def main():
    await app.start()
    print("بۆتەکە بە سەرکەوتوویی کار دەکات...")
    asyncio.create_task(send_to_all_groups())
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
    
