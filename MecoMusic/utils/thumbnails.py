import os
import re
import aiohttp
import aiofiles

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from unidecode import unidecode

from MecoMusic import app, YouTube
from config import YOUTUBE_IMG_URL

# ================= SETTINGS =================
CANVAS_SIZE = (1280, 720)

# ================ FONT LOAD ================
def load_font(name, size):
    try:
        return ImageFont.truetype(f"MecoMusic/assets/{name}", size)
    except:
        return ImageFont.load_default()

# ================ TEXT CLEAN ================
def clean_text(text):
    text = re.sub(r"\W+", " ", text or "")
    return unidecode(text).title()

# ================ MAIN CARD ================
async def generate_card(image_path, title, views, duration, channel):
    canvas = Image.new("RGB", CANVAS_SIZE, "black")

    # Background Blur
    bg = Image.open(image_path).resize(CANVAS_SIZE).filter(ImageFilter.GaussianBlur(25))
    canvas.paste(bg, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Fonts
    title_font = load_font("font2.ttf", 60)
    text_font = load_font("font.ttf", 40)
    small_font = load_font("font.ttf", 32)

    # ===== LEFT CIRCLE IMAGE =====
    img = Image.open(image_path).resize((400, 400)).convert("RGB")

    mask = Image.new("L", (400, 400), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, 400, 400), fill=255)

    circle_img = Image.new("RGB", (400, 400))
    circle_img.paste(img, (0, 0), mask)

    canvas.paste(circle_img, (120, 160))

    # Green Border
    border = ImageDraw.Draw(canvas)
    border.ellipse((110, 150, 530, 570), outline="green", width=10)

    # ===== RIGHT TEXT =====
    draw.text((700, 140), "NOW PLAYING", font=title_font, fill="white")

    draw.text((700, 260), title, font=text_font, fill="white")

    draw.text((700, 350), f"Views : {views}", font=small_font, fill="white")
    draw.text((700, 400), f"Duration : {duration}", font=small_font, fill="white")
    draw.text((700, 450), f"Channel : {channel}", font=small_font, fill="white")

    # ===== TOP LEFT NAME =====
    draw.text((40, 40), "@ITZZ_ISTKHAR", font=small_font, fill="white")

    output = "cache/final.png"
    canvas.save(output)

    return output


# ================ GET THUMB ================
async def get_thumb(videoid, user_id):
    os.makedirs("cache", exist_ok=True)

    raw_thumb = f"cache/{videoid}.jpg"
    final_path = f"cache/{videoid}_{user_id}.png"

    if os.path.isfile(final_path):
        return final_path

    try:
        title, duration, _, thumbnail, _ = await YouTube.details(videoid, True)

        title = clean_text(title)
        views = "Unknown"
        channel = "YouTube"

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail or YOUTUBE_IMG_URL) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(raw_thumb, "wb")
                    await f.write(await resp.read())
                    await f.close()

        # Generate card
        final = await generate_card(
            raw_thumb,
            title,
            views,
            duration,
            channel
        )

        return final

    except Exception as e:
        print("Error:", e)
        return YOUTUBE_IMG_URL
