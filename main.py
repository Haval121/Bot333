import asyncio
import logging
import re

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = "8725595567:AAFodNkbxNNY5z9gnlFqCzIpRwaUK01PstI"
ADMIN_ID = 8734106005

DELETE_DELAY = 185
PHOTO_DELETE_DELAY = 600  # 3 hours

URL_REGEX = re.compile(
    r'(https?://\S+|t\.me/\S+|www\.\S+|@\w+)',
    re.IGNORECASE
)

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
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .build()
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
    
