import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = "8816136841:AAGgYrBN5DP_mqTyaJ9ortKLJx2nlZXGGFQ"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in environment variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("سڵاو! ڤیدیۆیەک بنێرە تا لۆگۆی کەناڵەکەی بخەمە سەر و لەگەڵ لینکدا بۆت بنێرمەوە.")

@dp.message(F.video)
async def process_video(message: Message):
    status_msg = await message.answer("⏳ ڤیدیۆکە دابەزێنرا و سەرقاڵی دانانی لۆگۆم لەسەری...")
    
    video_file = await bot.get_file(message.video.file_id)
    input_video_path = f"input_{message.from_user.id}.mp4"
    output_video_path = f"output_{message.from_user.id}.mp4"
    logo_path = "logo.png"
    
    await bot.download_file(video_file.file_path, input_video_path)
    
    try:
        # پرۆسێسکردنی ڤیدیۆ بە MoviePy
        clip = VideoFileClip(input_video_path)
        
        # قەبارە و شوێنی لۆگۆ
        logo = ImageClip(logo_path).set_duration(clip.duration)
        logo = logo.resize(width=clip.w * 0.25) # پانیی لۆگۆ ٢٥٪ی ڤیدیۆکە دەبێت
        logo = logo.set_position(("right", "bottom")).margin(right=20, bottom=20, opacity=0)
        
        final_clip = CompositeVideoClip([clip, logo])
        
        # تۆمارکردنەوەی ڤیدیۆکە
        final_clip.write_videofile(
            output_video_path,
            codec="libx264",
            audio_codec="aac",
            fps=clip.fps,
            preset="ultrafast",
            logger=None
        )
        
        clip.close()
        final_clip.close()
        
        await status_msg.edit_text("📤 سەرقاڵی ناردنی ڤیدیۆکەم...")
        
        # کاپشن و لینکەکە بە مەرجی داواکراو
        caption_text = (
            "بینی ڤیدیۆی زیاتر 👇\n"
            "[بۆچوون و سەردانیکردنی کەناڵ](https://t.me/+1NHBFRGHW_oyOWE6)"
        )
        
        video_to_send = FSInputFile(output_video_path)
        await message.answer_video(
            video=video_to_send,
            caption=caption_text,
            parse_mode="Markdown"
        )
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ هەڵەیەک ڕویدا: {e}")
        
    finally:
        # پاککردنەوەی فایلە کاتییەکان لەسەر سێرڤەر بۆ ئەوەی ڕام پڕ نەبێت
        if os.path.exists(input_video_path):
            os.remove(input_video_path)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
