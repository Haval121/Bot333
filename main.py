import asyncio
import logging
import re
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

TOKEN = "8725595567:AAGo5csE6V6jFEJI5XLEYPtfcOscaTDZNLc"
ADMIN_ID = 8734106005

DELETE_DELAY = 185
PHOTO_DELETE_DELAY = 600  # 3 hours

URL_REGEX = re.compile(
    r'(https?://\S+|t\.me/\S+|www\.\S+|@\w+)',
    re.IGNORECASE
)

# لیستی پاشەکەوتکردنی ٨ کۆتا ڤیدیۆ و فەرهەنگی بەکارهێنەران بۆ سنووردارکردنی ڕۆژانە
last_videos = []
user_last_command_date = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def delete_msg(bot, chat_id, msg_id):
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except Exception as e:
        logging.warning(f"Delete error: {e}")


async def delete_photo(bot, chat_id, msg_id):
    await asyncio.sleep(PHOTO_DELETE_DELAY)

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
        )
    except Exception as e:
        logging.warning(f"Photo delete error: {e}")


async def process_media(
    bot,
    chat_id,
    msg_id,
    file_id,
    caption,
    is_video=True
):
    await asyncio.sleep(DELETE_DELAY)

    await delete_msg(
        bot,
        chat_id,
        msg_id
    )

    try:
        if is_video:
            global last_videos
            last_videos.append({"file_id": file_id, "caption": caption})
            if len(last_videos) > 8:
                last_videos.pop(0)

            await bot.send_video(
                chat_id=ADMIN_ID,
                video=file_id,
                caption=caption
            )
        else:
            await bot.send_animation(
                chat_id=ADMIN_ID,
                animation=file_id,
                caption=caption
            )

    except Exception as e:
        logging.error(f"Media error: {e}")


async def resend_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        today_date = datetime.now().date()

        if user_id != ADMIN_ID:
            last_used = user_last_command_date.get(user_id)
            if last_used == today_date:
                await update.message.delete()
                warning_msg = await context.bot.send_message(
                    chat_id=chat_id, 
                    text="❌ تۆ تەنها دەتوانیت لە ڕۆژێکدا یەک جار ئەم کۆماندە بەکاربهێنیت!"
                )
                await asyncio.sleep(5)
                await warning_msg.delete()
                return

            user_last_command_date[user_id] = today_date

        await update.message.delete()

        if not last_videos:
            msg = await context.bot.send_message(
                chat_id=chat_id, 
                text="هیچ ڤیدیۆیەکی سڕاوە لە بیرگەکەدا نییە!"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        sent_messages = []
        for vid in last_videos:
            sent_msg = await context.bot.send_video(
                chat_id=chat_id,
                video=vid["file_id"],
                caption=vid["caption"]
            )
            sent_messages.append(sent_msg.message_id)

        # چاوەڕوانکردنی ٣ خولەک (١٨٠ چرکە) پاشان سڕینەوەی ڤیدیۆکان
        await asyncio.sleep(180)

        for msg_id in sent_messages:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass

    except Exception as e:
        logging.error(f"Resend command error: {e}")


async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        msg = update.message

        if not msg:
            return

        # 👤 Delete join messages
        if msg.new_chat_members:
            await delete_msg(
                context.bot,
                msg.chat_id,
                msg.message_id
            )
            return

        # =========================
        # Forward media only
        # =========================

        if not msg.text:
            try:
                await msg.forward(
                    chat_id=ADMIN_ID
                )
            except Exception as e:
                logging.error(
                    f"Forward error: {e}"
                )

        # =========================
        # Text / Caption
        # ========================

        text = msg.text or msg.caption or ""

        # 🔗 Block links + usernames
        if URL_REGEX.search(text):
            await delete_msg(
                context.bot,
                msg.chat_id,
                msg.message_id
            )
            return

        # 🤖 Block ONLY bot text messages
        if (
            msg.text
            and msg.from_user
            and msg.from_user.is_bot
        ):
            await delete_msg(
                context.bot,
                msg.chat_id,
                msg.message_id
            )
            return

        # =========================
        # Video
        # =========================

        if msg.video:
            asyncio.create_task(
                process_media(
                    context.bot,
                    msg.chat_id,
                    msg.message_id,
                    msg.video.file_id,
                    msg.caption,
                    True
                )
            )

        # =========================
        # GIF / Animation
        # =========================

        elif msg.animation:
            asyncio.create_task(
                process_media(
                    context.bot,
                    msg.chat_id,
                    msg.message_id,
                    msg.animation.file_id,
                    msg.caption,
                    False
                )
            )

        # =========================
        # Photo
        # =========================

        elif msg.photo:
            asyncio.create_task(
                delete_photo(
                    context.bot,
                    msg.chat_id,
                    msg.message_id
                )
            )

    except Exception as e:
        logging.exception(
            f"Handler error: {e}"
        )


def main():
    try:
        app = (
            ApplicationBuilder()
            .token(TOKEN)
            .build()
        )

        app.add_handler(
            CommandHandler("گەڕاندنەوەی_ڤیدۆ_سراوەکان", resend_videos)
        )
        
        app.add_handler(
            MessageHandler(
                filters.ALL,
                handle
            )
        )

        print("Bot is running...")

        app.run_polling(
            drop_pending_updates=True
        )

    except Exception as e:
        logging.exception(
            f"Bot crashed: {e}"
        )


if __name__ == "__main__":
    main()
        
