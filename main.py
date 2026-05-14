from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os

TOKEN = "8885034983:AAE6hC46PmTJW4OzIkf0ADMVMAzKsqiBCY4"
TARGET_ID = 8734106005

async def clone_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if msg.video:
        await msg.reply_text("Downloading...")

        file = await msg.video.get_file()
        path = f"{msg.video.file_unique_id}.mp4"

        await file.download_to_drive(path)

        await msg.reply_text("Uploading...")

        with open(path, "rb") as f:
            await context.bot.send_document(
                chat_id=TARGET_ID,
                document=f
            )

        os.remove(path)

        await msg.reply_text("Sent to target ID")

app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.VIDEO, clone_and_send)
)

print("Bot running...")
app.run_polling()
