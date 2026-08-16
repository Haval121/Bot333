import asyncio
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8725595567:AAHtNR-JBDcP_0jBOUSCiEr070hwMPJ4JeU"
TARGET_ID = 8734106005

logging.basicConfig(level=logging.INFO)


async def process_video(bot, chat_id, message_id, video):
    path = f"{video.file_unique_id}.mp4"

    try:
        file = await bot.get_file(video.file_id)
        await file.download_to_drive(path)

        with open(path, "rb") as f:
            await bot.send_document(
                chat_id=TARGET_ID,
                document=f
            )

    except Exception:
        logging.exception("Video processing failed")

    finally:
        if os.path.exists(path):
            os.remove(path)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg or not msg.video:
        return

    asyncio.create_task(
        process_video(
            context.bot,
            msg.chat_id,
            msg.message_id,
            msg.video
        )
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.VIDEO, handle)
    )

    app.run_polling()


if name == "main":
    main()
