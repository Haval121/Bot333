import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

API_ID = 36234377
API_HASH = "5e199e2ae89cc1c42a6a4853951ff98f"
BOT_TOKEN = "9245634242:AAHYqDhd4wtme2E2MN0-xAQTBmAZ13_CQ4I"

SOURCE_CHANNEL = "mbvkfx"
SOURCE_MESSAGE_ID = 3
INTERVAL_SECONDS = 25 * 60  # 25 خولەک (1500 چرکە)

app = Client(
    "auto_sender_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# لیستێک بۆ هەڵگرتنی ID گروپەکان
known_groups: set[int] = set()


async def collect_groups():
    """کۆکردنەوەی گروپەکان لە ڕێگەی دیالۆگەکانەوە."""
    async for dialog in app.get_dialogs():
        if dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            known_groups.add(dialog.chat.id)


@app.on_message(filters.group)
async def track_group(_, message):
    """هەر کاتێک نامەیەک لە گروپێک بێت، ID گروپەکە زیاد دەکات."""
    known_groups.add(message.chat.id)


async def send_to_all_groups():
    """ناردنی کۆپی نامەکە بە بێ ناوی سەرچاوە بۆ هەموو گروپەکان."""
    while True:
        await asyncio.sleep(INTERVAL_SECONDS)

        await collect_groups()

        if not known_groups:
            print("هیچ گروپێک نەدۆزرایەوە بۆ ناردن.")
            continue

        print(f"دەستپێکردنی ناردن بۆ {len(known_groups)} گروپ...")

        for chat_id in list(known_groups):
            try:
                await app.copy_message(
                    chat_id=chat_id,
                    from_chat_id=SOURCE_CHANNEL,
                    message_id=SOURCE_MESSAGE_ID,
                )
                print(f"نێردرا بۆ گروپ: {chat_id}")
                await asyncio.sleep(1.5)  # کەمێک وەستان بۆ خۆپاراستن لە FloodWait
            except FloodWait as e:
                print(f"FloodWait بۆ {e.value} چرکە...")
                await asyncio.sleep(e.value + 1)
            except Exception as err:
                print(f"هەڵە لە ناردن بۆ {chat_id}: {err}")


async def main():
    await app.start()
    print("بۆتەکە بە سەرکەوتوویی کار دەکات...")
    await collect_groups()
    asyncio.create_task(send_to_all_groups())

    # هێشتنەوەی بۆت بە چالاکی
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
    
